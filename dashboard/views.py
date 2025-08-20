from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import UserInfos
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

# Create your views here.

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
        obj = User.objects.get(id = request.user.id)
        obj.password = newPass
        obj.save()
        return render(request, 'auth/password.html', {"message": "New Password Saved! "})

    return render(request, 'auth/password.html')

def signout(request):
    logout(request)
    return redirect('/login')