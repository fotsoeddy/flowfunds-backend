from rest_framework import serializers
from core.models import Account

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'name', 'number', 'type', 'balance', 'currency')
        read_only_fields = ('id', 'balance', 'currency')  # Balance should not be editable directly via serializer update

class CreateAccountSerializer(serializers.ModelSerializer):
    initial_balance = serializers.DecimalField(max_digits=12, decimal_places=2, write_only=True)

    class Meta:
        model = Account
        fields = ('name', 'number', 'type', 'initial_balance')

    def create(self, validated_data):
        initial_balance = validated_data.pop('initial_balance')
        user = self.context['request'].user
        
        account = Account.objects.create(
            user=user,
            **validated_data,
            balance=initial_balance
        )
        return account
