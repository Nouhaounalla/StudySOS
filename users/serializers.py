from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailTokenObtainSerializer(TokenObtainPairSerializer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
    
    def validate(self, attrs):
        username_or_email = attrs.get(self.username_field)
        print(f"Validating login for: {username_or_email}")
        
        # If email provided, keep it as-is since USERNAME_FIELD is email
        if username_or_email and '@' in str(username_or_email):
            try:
                user = User.objects.get(email=username_or_email)
                print(f"Found user by email: {user.username}, active: {user.is_active}")
                # Keep email in attrs, do NOT convert to username
            except User.DoesNotExist:
                print(f"No user found with email: {username_or_email}")
                pass
        
        try:
            return super().validate(attrs)
        except Exception as e:
            print(f"Validation error: {str(e)}")
            raise


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'role']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 
                  'date_of_birth', 'role', 'purpose', 'bio', 'profile_photo']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone']

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data.get('phone', "")
        )


class ProfileSerializer(serializers.ModelSerializer):
    profile_photo = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'date_of_birth',
            'role', 'purpose', 'bio', 'profile_photo'
        ]


class UserMeSerializer(serializers.ModelSerializer):
    profile_photo = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone',
            'first_name', 'last_name', 'date_of_birth',
            'role', 'purpose', 'bio', 'profile_photo'
        ]
        read_only_fields = fields


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mot de passe actuel incorrect.")
        return value