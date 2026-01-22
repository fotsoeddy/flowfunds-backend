from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import Account

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'first_name', 'last_name', 'profile_image', 'created')
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

        # Helper to detect carrier
        def get_carrier_from_number(number):
            # Remove spaces and +237
            clean_number = number.replace(' ', '').replace('+237', '').replace('237', '')
            
            if not clean_number.isdigit() or len(clean_number) != 9:
                return 'momo' # Default fallback
                
            prefix = int(clean_number[:2])
            full_prefix = int(clean_number[:3])
            
            # Orange: 69X, 655-659
            if prefix == 69 or (655 <= full_prefix <= 659):
                return 'om'
            
            # MTN: 67X, 650-654, 680-689
            if prefix == 67 or (650 <= full_prefix <= 654) or (680 <= full_prefix <= 689):
                return 'momo'
                
            return 'momo' # Default fallback

        carrier = get_carrier_from_number(user.phone_number)

        # Create initial account (MoMo/OM based on number)
        Account.objects.create(
            user=user,
            name="My Account",
            number=user.phone_number,
            type=carrier,
            balance=initial_amount
        )

        # Create default Cash account
        Account.objects.create(
            user=user,
            name="Cash Account",
            number=user.phone_number, # Cash account still needs a number reference usually, or can be distinct. Reusing phone for now.
            type='cash',
            balance=0
        )
        return user
