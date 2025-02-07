from datetime import timezone
from pyexpat.errors import messages
from django.conf import settings
from django.shortcuts import render,redirect,get_object_or_404
from .models import Profile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login as auth_login
from.forms import UserLoginForm,UserRegistrationForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseNotAllowed,Http404
import requests
import json
from .forms import DepositForm
from .models import Profile,Transaction
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.forms import PasswordResetForm
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from requests.exceptions import RequestException
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
import base64
from django.conf import settings
import os
from django.contrib import messages
from django.core.mail import send_mail  # For sending emails via Django
from .forms import CustomPasswordResetForm  # Import your custom form
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ValidationError
from smtplib import SMTPConnectError
import smtplib
from .forms import SendMoneyForm
from .models import Transaction,Notification,Deposit,Wallet
from django.db.models import F
from decimal import Decimal, InvalidOperation


@login_required
def profile(request):
    if request.method == "POST":
        form = SendMoneyForm(request.POST)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            amount = form.cleaned_data['amount']

            # Check if sender has sufficient balance
            if request.user.profile.balance < amount:
                messages.error(request, "Insufficient balance.")
            else:
                # Deduct from sender
                request.user.profile.balance -= amount
                request.user.profile.save()

                # Add to recipient
                recipient.profile.balance += amount
                recipient.profile.save()

                # Record the transaction
                Transaction.objects.create(sender=request.user, recipient=recipient, amount=amount)

                # Send email notifications
                send_mail(
                    subject="Transaction Notification",
                    message=f"Hi {request.user.username},\n\nYou have successfully sent ${amount} to {recipient.username}.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=False,
                )

                send_mail(
                    subject="Transaction Notification",
                    message=f"Hi {recipient.username},\n\nYou have received ${amount} from {request.user.username}.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )

                messages.success(request, f"Successfully sent ${amount} to {recipient.username}.")
                return redirect('profile')
    else:
        form = SendMoneyForm()

    return render(request, 'profile.html', {'form': form})





# Create your own password reset form or use Django's built-in PasswordResetForm
# Your custom views
'''
def password_reset(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                email_template_name='p-reset/password_reset_email.txt',
                subject_template_name='p-reset/password_reset_email.txt',
            )
            messages.success(request, "Password reset email sent.")
            return redirect('password_reset_done')  # Correct redirect URL name
    else:
        form = PasswordResetForm()
    
    return render(request, 'p-reset/password_reset.html', {'form': form})
'''
'''
def password_reset(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            try:
                form.save(
                    request=request,
                    email_template_name='p-reset/password_reset_email.txt',
                )
                messages.success(request, "Password reset email sent.")
                return redirect('password_reset_done')
            except SMTPConnectError:
                # Handle SMTP connection errors gracefully
                messages.error(request, "There was a problem connecting to the email server. Please try again later.")
                return redirect('password_reset')
            except Exception as e:
                # Catch any other exceptions and handle them
                messages.error(request, f"An unexpected error occurred: {str(e)}")
                return redirect('password_reset')
    else:
        form = PasswordResetForm()
    
    return render(request, 'p-reset/password_reset.html', {'form': form})
'''
def password_reset(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            try:
                # Send email with fail_silently=False so errors are raised if something goes wrong
                form.save(
                    request=request,
                    email_template_name='p-reset/password_reset_email.txt',
                )

                # If the email is sent without exceptions, we can show a success message
                messages.success(request, "Password reset email sent.")
                return redirect('password_reset_done')

            except SMTPConnectError as e:
                # Handle specific SMTP connection errors
                messages.error(request, f"Error: Unable to connect to the email server. {e}. Please try again later.")
                return redirect('password_reset')

            except Exception as e:
                # Catch any other exceptions and handle them gracefully
                messages.error(request, f"An unexpected error occurred: {str(e)}")
                return redirect('password_reset')

    else:
        form = PasswordResetForm()

    return render(request, 'p-reset/password_reset.html', {'form': form})

def password_reset_confirm(request, uidb64, token):
    try:
        # Decode the uidb64 to get the user id
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(id=uid)
        
        # Check if the token is valid
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Your password has been reset successfully.")
                    return redirect('login')  # Redirect to login after successful reset
            else:
                form = SetPasswordForm(user)
            return render(request, 'p-reset/password_reset_confirm.html', {'form': form})
        else:
            messages.error(request, "The reset link is invalid or has expired.")
            return redirect('password_reset')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('password_reset')

'''
def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                email_template_name='p-reset/password_reset_email.html',
                subject_template_name='p-reset/password_reset_subject.txt',
            )
            messages.success(request, "Password reset email sent.")
            return redirect('password_reset_done')
    else:
        form = CustomPasswordResetForm()
    return render(request, 'p-reset/password_reset.html', {'form': form})
'''




def password_reset_done(request):
    return render(request, 'password_reset_done.html')  # Ensure this template exists






def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def services(request):
    return render(request, 'services.html')

def contact(request):
    return render(request, 'contact.html')


# Create your views here.
@login_required
def profile(request):
    # Ensure the profile exists or create it if it doesn't
    profile, created = Profile.objects.get_or_create(user=request.user)

    # Get recent transactions
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:5]

    context = {
        'username': request.user.username,
        'balance': profile.balance,  # Add balance
        'transactions': transactions,  # Add transactions
    }
    return render(request, 'profile.html', context)


'''
def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('profile')  # Redirect to profile after successful login
            else:
                return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})
'''


def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Create the user but don't save it yet
            user.is_active = False  # Deactivate the account until email verification
            user.save()  # Save the user
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')

            # Generate email verification token and URL
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_url = request.build_absolute_uri(
                reverse('activate', kwargs={'uidb64': uid, 'token': token})
            )

            # Send the verification email
            try:
                send_mail(
                    subject="Verify your PeerBank account",
                    message=f"Hi {username},\n\nPlease verify your email by clicking on the link below:\n\n{verification_url}\n\nThank you for joining PeerBank!",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                messages.success(request, "Account created successfully! Check your email for the verification link.")
            except Exception as e:
                messages.error(request, f"Account created successfully, but we couldn't send an email. Error: {e}")

            return redirect('login')  # Redirect to login after sending the email
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})



def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True  # Activate the user's account
        user.save()
        messages.success(request, "Your email has been verified. You can now log in.")
        return redirect('login')
    else:
        messages.error(request, "The activation link is invalid or has expired.")
        return redirect('signup')

    
@login_required
def send_money(request):
    if request.method == "POST":
        recipient_username = request.POST.get('recipient')
        amount = request.POST.get('amount')

        try:
            recipient = User.objects.get(username=recipient_username)
            sender_profile = request.user.profile
            recipient_profile = recipient.profile

            # Convert amount to Decimal
            try:
                amount = Decimal(amount)
                if amount <= 0:
                    raise ValueError("Amount must be positive.")
            except (ValueError, Decimal.InvalidOperation):
                messages.error(request, "Invalid amount.")
                return redirect('profile')

            if sender_profile.balance < amount:
                messages.error(request, "Insufficient balance.")
            else:
                # Perform the transfer
                sender_profile.balance -= amount
                recipient_profile.balance += amount
                sender_profile.save()
                recipient_profile.save()

                # ✅ Save transactions
                Transaction.objects.create(user=request.user, type="Transfer Out", amount=amount, status="Success")
                Transaction.objects.create(user=recipient, type="Transfer In", amount=amount, status="Success")

                # ✅ Record notifications
                Notification.objects.create(user=request.user, message=f"You sent ${amount} to {recipient.username}.")
                Notification.objects.create(user=recipient, message=f"You received ${amount} from {request.user.username}.")

                # ✅ Send email to sender
                send_mail(
                    subject="Money Sent",
                    message=f"Hi {request.user.username},\n\nYou have successfully sent ${amount} to {recipient.username}.",
                    from_email='your-email@gmail.com',
                    recipient_list=[request.user.email],
                )

                # ✅ Send email to recipient
                send_mail(
                    subject="Money Received",
                    message=f"Hi {recipient.username},\n\nYou have received ${amount} from {request.user.username}.",
                    from_email='your-email@gmail.com',
                    recipient_list=[recipient.email],
                )

                messages.success(request, f"Successfully sent ${amount} to {recipient.username}!")
        except User.DoesNotExist:
            messages.error(request, "Recipient not found.")

        return redirect('profile')

    return redirect('profile')





@login_required
def withdraw_request(request):
    if request.method == "POST":
        method = request.POST.get("withdraw_method")
        address = request.POST.get("withdraw_address")
        # Convert the withdrawal amount to Decimal
        amount = Decimal(request.POST.get("withdraw_amount"))

        user = request.user
        wallet, created = Wallet.objects.get_or_create(user=user)  # Get or create the user's wallet

        if wallet.balance < amount:
            messages.error(request, "Insufficient balance for withdrawal.")
            return redirect("profile")  # Redirect user back to dashboard

        # Deduct the withdrawal amount
        wallet.balance -= amount
        wallet.save()

        # Log the withdrawal transaction
        Transaction.objects.create(
            user=user,
            type="withdrawal",
            amount=amount,
            status="Pending",
            method=method,
            address=address,
        )

        messages.success(request, "Withdrawal request submitted successfully.")
        return redirect("profile")  # Redirect user to dashboard

    return redirect("profile")


@login_required
def deposit(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        crypto_address = request.POST.get("crypto_address")  # Get from form

        try:
            amount = Decimal(amount)
            if amount < 100:
                messages.error(request, "Minimum deposit is $100.")
                return redirect("profile")
        except:
            messages.error(request, "Invalid amount.")
            return redirect("profile")

        # Create deposit record with crypto address
        Deposit.objects.create(
            user=request.user,
            amount=amount,
            crypto_address=crypto_address,
            status="Pending"
        )

        messages.success(request, "Deposit request submitted. Wait for confirmation.")
        return redirect("profile")

    return redirect("profile")
