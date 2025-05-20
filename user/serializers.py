from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from allauth.account import app_settings as allauth_account_settings
from allauth.account.adapter import get_adapter
from dj_rest_auth.registration.serializers import RegisterSerializer

User = get_user_model()

class CustomRegisterSerializer(RegisterSerializer):
    username = None  # REMOVE username field

    def get_cleaned_data(self):
        return {
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
        }

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""

    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True, required=False)
    password2 = serializers.CharField(write_only=True, required=False)
    employer_email = serializers.ReadOnlyField(source='employer.email', allow_null=True)
    role_display = serializers.ReadOnlyField(source='get_role_display')
    employees_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'password1', 'password2', 'first_name', 'last_name',
            'farm_name', 'farm_location', 'farm_size', 'preferred_language',
            'is_farm_owner', 'role', 'role_display', 'employer', 'employer_email',
            'hire_date', 'job_title', 'contact_number', 'employees_count',
            'can_manage_animals', 'can_manage_health', 'can_manage_feeding',
            'can_manage_inventory', 'can_manage_sales', 'can_manage_employees',
            'can_view_reports', 'is_active', 'date_joined'
        ]
        read_only_fields = [
            'id', 'is_active', 'date_joined', 'is_farm_owner', 'role',
            'can_manage_animals', 'can_manage_health', 'can_manage_feeding',
            'can_manage_inventory', 'can_manage_sales', 'can_manage_employees',
            'can_view_reports'
        ]

    def get_employees_count(self, obj):
        return obj.employees.count() if hasattr(obj, 'employees') else 0

    def validate(self, data):
        password1 = data.get('password1')
        password2 = data.get('password2')

        if password1 or password2:
            if password1 != password2:
                raise serializers.ValidationError({"password2": _("Passwords do not match.")})

        # 👇 Remove username if accidentally passed
        data.pop('username', None)

        return data

    def save(self, request=None):
        password1 = self.validated_data.pop('password1', None)
        self.validated_data.pop('password2', None)

        # 👇 Remove username just to be safe
        self.validated_data.pop('username', None)

        user = User.objects.create(**self.validated_data)
        if password1:
            user.set_password(password1)
            user.save()
        return user

    def update(self, instance, validated_data):
        password1 = validated_data.pop('password1', None)
        validated_data.pop('password2', None)

        # 👇 Remove username just to be safe
        validated_data.pop('username', None)

        user = super().update(instance, validated_data)
        if password1:
            user.set_password(password1)
            user.save()
        return user



class EmployeeSerializer(UserSerializer):
    """Serializer for employees."""

    class Meta(UserSerializer.Meta):
        exclude = ['farm_name', 'farm_location', 'farm_size', 'is_farm_owner']

    def validate(self, data):
        if not data.get('employer') and not self.instance:
            raise serializers.ValidationError(_("Employees must have an employer."))

        if data.get('is_farm_owner'):
            raise serializers.ValidationError(_("Employees cannot be farm owners."))

        return data


class EmployerSerializer(UserSerializer):
    """Serializer for employers with nested employees."""
    employees = EmployeeSerializer(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['employees']

    def validate(self, data):
        if data.get('employer'):
            raise serializers.ValidationError(_("Farm owners cannot have employers."))
        return data
