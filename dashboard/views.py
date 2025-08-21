from django.shortcuts import render, redirect, get_object_or_404
from .models import UserInfos, Messages
from django.contrib.auth import logout
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
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from datetime import timedelta

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

@login_required(login_url='/login')
def homePage(request):
    return render(request, 'home.html')

def archievePage(request):
    return render(request, 'archieve.html')

@login_required(login_url='/login')
def messagesPage(request):

    cutoff_date = timezone.now().date() - timedelta(days=5)
    userMessages = Messages.objects.filter(user=request.user.username, date__gte=cutoff_date)

    return render(request, 'messages.html', {"usermessages": userMessages})

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
        password = request.POST.get('password')
        # Check if password is correct
        if check_password(password, request.user.password):
            # Check if email exists
            if User.objects.filter(email=newEmail).exists():
                return render(request, "auth/email.html", {"error": "Email already taken."})
            
            obj = User.objects.get(id = request.user.id)
            obj.email = newEmail
            obj.save()
        else:
            return render(request, "auth/email.html", {"error": "Password Is Incorrect."})

        return render(request, 'auth/email.html', {"message": "New Email Saved! "})
    
    return render(request, 'auth/email.html')

@login_required(login_url='/login')
def authUser(request):
    if request.method == "POST":
        newUname = request.POST.get('username')
        password = request.POST.get('password')
        # Check if password is correct
        if check_password(password, request.user.password):
            # Check if username exists
            if User.objects.filter(username=newUname).exists():
                return render(request, "auth/user.html", {"error": "Username already taken."})
            obj = User.objects.get(id = request.user.id)
            obj.username = newUname
            obj.save()
            return render(request, 'auth/user.html', {"message": "New Username Saved! "})
        else:
           return render(request, "auth/user.html", {"error": "Password Is Incorrect"})


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

 

def user_screen(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == "POST":
        message = request.POST.get('message')
        Messages.objects.create(message=message, user=username)
        return render(request,"screen.html", {"user": user, "messages": "Your message has been sent!"} )
    return render(request, "screen.html", {"user": user})



@login_required(login_url='/login')
def delete_message(request, message_id):
    message = get_object_or_404(Messages, id=message_id)

    message.delete()

    return redirect('messagesPage')

def signout(request):
    logout(request)
    return redirect('/login')
