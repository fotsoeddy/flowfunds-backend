from django.contrib import admin
from .models import User, Account, Transaction

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'first_name', 'last_name', 'is_staff', 'is_active', 'created')
    search_fields = ('phone_number', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active')

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'type', 'balance', 'currency', 'user', 'created')
    search_fields = ('name', 'number', 'user__phone_number')
    list_filter = ('type', 'currency')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('type', 'amount', 'category', 'reason', 'date', 'account', 'user')
    search_fields = ('reason', 'category', 'user__phone_number', 'account__name')
    list_filter = ('type', 'date')
