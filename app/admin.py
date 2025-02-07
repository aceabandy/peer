from django.contrib import admin
from .models import Profile, Signup,Notification,Transaction,Deposit,Wallet

admin.site.register(Signup)

# Register the Profile model
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')  # Show these fields in the admin list view
    search_fields = ('user__username', 'user__email')  # Allow searching by username or email
    list_filter = ('balance',)  # Add a filter for balance
    ordering = ('user',)  # Default ordering by user

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'type', 'amount', 'status', 'method', 'address')
    list_filter = ('status', 'type', 'method')
    search_fields = ('user__username', 'address')
# Create a custom admin class for Notification model
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')  # Fields to display in list view
    list_filter = ('created_at', 'is_read')  # Filters for the admin view
    search_fields = ('message',)  # Allow search by message content
    ordering = ('-created_at',)  # Default ordering by creation date, descending
    date_hierarchy = 'created_at'  # Display notifications with a date hierarchy for easy navigation

# Register the Notification model with the admin panel using the custom admin class
admin.site.register(Notification, NotificationAdmin)


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "status", "timestamp")
    list_filter = ("status",)
    search_fields = ("user__username",)
    actions = ["approve_deposit", "reject_deposit"]

    def approve_deposit(self, request, queryset):
        for deposit in queryset:
            if deposit.status == "Pending":
                deposit.user.profile.balance += deposit.amount
                deposit.user.profile.save()
                deposit.status = "Completed"
                deposit.save()
        self.message_user(request, "Selected deposits approved and balances updated.")

    def reject_deposit(self, request, queryset):
        queryset.update(status="Rejected")
        self.message_user(request, "Selected deposits rejected.")

    approve_deposit.short_description = "Approve selected deposits"
    reject_deposit.short_description = "Reject selected deposits"


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')  # Show user and balance in the admin panel
