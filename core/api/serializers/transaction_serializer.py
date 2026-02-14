from decimal import Decimal
from rest_framework import serializers
from django.db import transaction
from core.models import Transaction, Account
from core.utils.ai_helper import categorize_transaction

class TransactionSerializer(serializers.ModelSerializer):
    account_name = serializers.ReadOnlyField(source='account.name')
    account_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Transaction
        fields = ('id', 'type', 'amount', 'reason', 'category', 'date', 'account', 'account_id', 'account_name')
        read_only_fields = ('id', 'account', 'account_name')

    def validate(self, attrs):
        user = self.context['request'].user
        account_id = attrs.get('account_id')
        
        try:
            account = Account.objects.get(id=account_id, user=user)
            attrs['account'] = account
        except Account.DoesNotExist:
            raise serializers.ValidationError({"account_id": "Invalid account."})

        if attrs['type'] in ['expense', 'save']:
            if account.balance < attrs['amount']:
                raise serializers.ValidationError({"amount": "Insufficient funds."})
            
        return attrs

    def create(self, validated_data):
        account = validated_data['account']
        amount = validated_data['amount']
        trans_type = validated_data['type']
        
        validated_data.pop('account_id') # Remove from data meant for model
        validated_data['user'] = self.context['request'].user

        # AI Categorization if not provided
        if not validated_data.get('category') and validated_data.get('reason'):
            validated_data['category'] = categorize_transaction(validated_data['reason'])

        with transaction.atomic():
            ticket = Transaction.objects.create(**validated_data)
            
            if trans_type == 'income':
                account.balance += amount
            elif trans_type == 'expense':
                account.balance -= amount
            elif trans_type == 'save':
                account.balance -= amount
                # Find or create a savings account for the user
                savings_account, created = Account.objects.get_or_create(
                    user=self.context['request'].user,
                    type='savings',
                    defaults={
                        'name': 'Main Savings',
                        'number': f'SAV-{self.context["request"].user.phone_number[-4:]}',
                        'currency': account.currency
                    }
                )
                savings_account.balance += Decimal(str(amount))
                savings_account.save()
            
            account.save()
            return ticket
