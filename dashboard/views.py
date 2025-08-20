from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import UserInfos
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
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

# Create your views here.

User = get_user_model()

def authenticator(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):

        # Get password from session
        newPass = request.session.get('pending_password')
        if newPass:
            user.set_password(newPass)
            user.save()

            # Clean up session
            del request.session['pending_password']

            return render(request, 'auth/password.html', {"message": "Password successfully changed!"})

    return render(request, 'auth/password.html', {"message": "Invalid or expired link."})

def homePage(request):
    return render(request, 'home.html')

def archievePage(request):
    return render(request, 'archieve.html')

def messagesPage(request):
    return render(request, 'messages.html')

@login_required(login_url='/login')
def settingsPage(request):
    profile, created = UserInfos.objects.get_or_create(user=request.user)
    if request.method == "POST" and request.FILES.get("profile_pic"):
        profile.profile_pic = request.FILES["profile_pic"]
        profile.save()
        return redirect('/dashboard/settings') 
    return render(request, 'settings.html', {"profile": profile})

@login_required(login_url='/login')
def authEmail(request):
    if request.method == "POST":
        newEmail = request.POST.get('email')
          # Check if email exists
        if User.objects.filter(email=newEmail).exists():
            return render(request, "signup.html", {"error": "Email already taken."})
        
        obj = User.objects.get(id = request.user.id)
        obj.email = newEmail
        obj.save()

        return render(request, 'auth/email.html', {"message": "New Email Saved! "})
    
    return render(request, 'auth/email.html')

@login_required(login_url='/login')
def authUser(request):
    if request.method == "POST":
        newUname = request.POST.get('username')
          # Check if username exists
        if User.objects.filter(username=newUname).exists():
            return render(request, "signup.html", {"error": "Username already taken."})
        obj = User.objects.get(id = request.user.id)
        obj.username = newUname
        obj.save()
        return render(request, 'auth/user.html', {"message": "New Username Saved! "})

    return render(request, 'auth/user.html')

@login_required(login_url='/login')
def authPassword(request):
    if request.method == "POST":
        newPass = request.POST.get('password')

        # Store the new password temporarily in session
        request.session['pending_password'] = newPass 

        # Create Password Change Link
        uid = urlsafe_base64_encode(force_bytes(request.user.pk))
        token = default_token_generator.make_token(request.user)

        auth_link = request.build_absolute_uri(
            reverse("authenticator", kwargs={"uidb64": uid, "token": token})
        )

        send_mail(
            subject="Authorize Password Change",
            message=f"Hi {request.user.username}, please click the link to Change your password: {auth_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
        )
        obj = User.objects.get(id = request.user.id)
        obj.password = newPass
        obj.save()
        return render(request, 'auth/password.html', {"message": "Check your email to confirm password change."})

    return render(request, 'auth/password.html')

def signout(request):
    logout(request)
    return redirect('/login')