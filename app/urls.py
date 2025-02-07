from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from app.forms import UserLoginForm
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .views import password_reset, password_reset_confirm
# Ensure that the necessary views for password reset are imported
# If you want to use default Django views for password reset, you don't need to define them yourself
# Otherwise, you can create custom views like PasswordResetDoneView, PasswordResetConfirmView, and PasswordResetCompleteView

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('services/', views.services, name='services'),
    path("deposit/", views.deposit, name="deposit"),
    path('withdraw/', views.withdraw_request, name='withdraw'),
    path('login/', auth_views.LoginView.as_view(template_name="registration/login.html", authentication_form=UserLoginForm), name='login'),
    path('signup/', views.signup, name='signup'),
    path('activate/<uidb64>/<token>/',views.activate, name='activate'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/profile/', views.profile, name='profile'),
    path('profile/', views.profile, name='profile'),
    path('send-money/', views.send_money, name='send_money'), 
    path('accounts/password_reset/', password_reset, name='password_reset'),
    path('accounts/password_reset/done/', TemplateView.as_view(template_name='p-reset/password_reset_done.html'), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('accounts/reset/done/', TemplateView.as_view(template_name='p-reset/password_reset_complete.html'), name='password_reset_complete'),
    
    
    ]

    