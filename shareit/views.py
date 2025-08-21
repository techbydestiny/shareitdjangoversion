from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from urllib.parse import urlencode
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str 
from django.utils.http import urlsafe_base64_decode

def activate(request, uidb64, token):
    UserModel = get_user_model()
    user = None

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if not user.is_active:
            user.is_active = True
            user.save()

        # Send a message to the login page via query param
        qs = urlencode({"msg": "Your account has been activated. You can now log in."})
        # If your login URL is namespaced, use reverse("accounts:login")
        return redirect(f"{reverse('login')}?{qs}")
    else:
        # Invalid / expired token
        return render(request, "activation_invalid.html", status=400)

def home(request):
    return render(request, 'index.html')

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  
    message = request.GET.get("msg")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("upassword")
        userr = authenticate(request, username=username, password=password)
        if userr is not None:
            # Check if email is verified 
            if not userr.is_active:
                return render(request, "login.html", {"erorr": "Verify account before you login"})
            login(request, userr)
            return redirect("/dashboard")
        else:
           return render(request, "login.html", {"error": "Invalid username or password"})
        
    return render(request, "login.html", {"message": message})

def signUp(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  
    if request.method == "POST":
        name = request.POST.get("username")
        email = request.POST.get("uemail").lower()
        password = request.POST.get("upassword")

         # Check if username exists
        if User.objects.filter(username=name).exists():
            return render(request, "signup.html", {"error": "Username already taken."})

        # Check if email exists
        if User.objects.filter(email=email).exists():
            return render(request, "signup.html", {"error": "Email already registered."})
        
        # Create user
        user = User.objects.create_user(
            username=name,
            email=email,
            password=password,
            is_active = False
        )
        # Create Activation Link
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        activation_link = request.build_absolute_uri(
            reverse("activate", kwargs={"uidb64": uid, "token": token})
        )

        send_mail(
            subject="Verify your account",
            message=f"Hi {user.username}, please click the link to verify your account: {activation_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        query = urlencode({"msg": "A verification link has been sent to your email."})
        login_url = f"{reverse('login')}?{query}"
        return redirect(login_url)
    return render(request, 'signup.html')

def contact(request):
    return render(request, 'contact.html')


