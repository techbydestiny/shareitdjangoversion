from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.homePage),
    path('dashboard/archieve', views.archievePage),
    path('dashboard/messages', views.messagesPage, name='messagesPage'),
    path('dashboard/settings', views.settingsPage),
    path('dashboard/auth/email', views.authEmail),
    path('dashboard/auth/user', views.authUser),
    path('dashboard/auth/password', views.authPassword),
    path('logout/', views.signout),
    path("authenticator/<uidb64>/<token>/", views.authenticator, name="authenticator"),
    path('<str:username>/', views.user_screen, name='user_screen'),
    path('delete/<int:message_id>/', views.delete_message, name='delete_message'),
]
