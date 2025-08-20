from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.homePage),
    path('dashboard/archieve', views.archievePage),
    path('dashboard/messages', views.messagesPage),
    path('dashboard/settings', views.settingsPage),
    path('dashboard/auth/email', views.authEmail),
    path('dashboard/auth/user', views.authUser),
    path('dashboard/auth/password', views.authPassword),
    path('logout/', views.signout),


]
