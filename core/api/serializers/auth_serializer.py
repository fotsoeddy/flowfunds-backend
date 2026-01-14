from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import Account

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'first_name', 'last_name', 'profile_image')
        read_only_fields = ('id',)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    initial_amount = serializers.DecimalField(max_digits=12, decimal_places=2, write_only=True)

    class Meta:
        model = User
        fields = ('phone_number', 'password', 'first_name', 'initial_amount', 'profile_image')

    def create(self, validated_data):
        initial_amount = validated_data.pop('initial_amount')
        password = validated_data.pop('password')
        
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Create initial account
        Account.objects.create(
            user=user,
            name="My Account",
            number=user.phone_number,
            type='momo', # Default to MoMo as per requirements or inference
            balance=initial_amount
        )
        return user
