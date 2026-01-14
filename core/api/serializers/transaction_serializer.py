from rest_framework import serializers
from django.db import transaction
from core.models import Transaction, Account

class TransactionSerializer(serializers.ModelSerializer):
    account_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Transaction
        fields = ('id', 'type', 'amount', 'category', 'reason', 'date', 'account', 'account_id')
        read_only_fields = ('id', 'account')

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

        with transaction.atomic():
            ticket = Transaction.objects.create(**validated_data)
            
            if trans_type == 'income':
                account.balance += amount
            elif trans_type in ['expense', 'save']:
                account.balance -= amount
            
            account.save()
            return ticket
