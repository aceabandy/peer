from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal,InvalidOperation
from django.conf import settings
import requests
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.utils import timezone
# Create your models here.

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=20, decimal_places=8, default=0.00)

    def formatted_balance(self):
        return int(self.balance)  # Always returns whole number

    def __str__(self):
        return f"{self.user.username} - Balance: {self.formatted_balance()}"

class Signup(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name      
    
'''
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=[('Deposit', 'Deposit'), ('Withdraw', 'Withdraw')])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=[('Success', 'Success'), ('Failed', 'Failed')])

    def __str__(self):
        return f"{self.user.username} - {self.type} - ${self.amount}"
'''

class Transaction(models.Model):
    SENT = 'sent'
    RECEIVED = 'received'
    WITHDRAWAL = 'withdrawal'

    TYPES = [
        (SENT, 'Sent'),
        (RECEIVED, 'Received'),
        (WITHDRAWAL, 'Withdrawal'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=TYPES)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    method = models.CharField(max_length=50, blank=True, null=True)  # Bitcoin, Ethereum, etc.
    address = models.TextField(blank=True, null=True)  # Crypto wallet or bank details

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.amount} - {self.status}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    crypto_address = models.CharField(max_length=200, unique=True, blank=True, null=True)

    def __str__(self):
        return self.user.username

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)




class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # Added is_read field

    def __str__(self):
        return self.message

    def is_recent(self):
        # Check if the notification is within the last 24 hours
        return timezone.now() - self.created_at <= timezone.timedelta(days=1)
    
class Deposit(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Rejected", "Rejected"),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    crypto_address = models.CharField(max_length=255)  # NEW FIELD
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - ${self.amount} ({self.status})"



 