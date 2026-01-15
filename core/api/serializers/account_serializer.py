from rest_framework import serializers
from core.models import Account

class AccountSerializer(serializers.ModelSerializer):
    is_primary = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ('id', 'name', 'number', 'type', 'balance', 'currency', 'is_primary')
        read_only_fields = ('id', 'balance', 'currency', 'is_primary')

    def get_is_primary(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.number == request.user.phone_number
        return False

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
