from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    username = None  # <--- Remove username
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150, null=True, blank=True)

    farm_name = models.CharField(_('farm name'), max_length=255, blank=True, null=True)
    farm_location = models.CharField(_('farm location'), max_length=255, blank=True, null=True)
    farm_size = models.FloatField(_('farm size (acres)'), blank=True, null=True)

    preferred_language = models.CharField(_('preferred language'), max_length=10,
                                          choices=[('en', 'English'), ('ur', 'Urdu')],
                                          default='en')

    is_farm_owner = models.BooleanField(_('farm owner status'), default=True)

    role = models.CharField(_('role'), max_length=50,
                            choices=[
                                ('owner', 'Farm Owner'),
                                ('manager', 'Farm Manager'),
                                ('veterinarian', 'Veterinarian'),
                                ('worker', 'Farm Worker'),
                                ('accountant', 'Accountant')
                            ],
                            default='owner')

    employer = models.ForeignKey('self', on_delete=models.CASCADE,
                                 null=True, blank=True,
                                 related_name='employees',
                                 verbose_name=_('employer'))

    hire_date = models.DateField(_('hire date'), null=True, blank=True)
    job_title = models.CharField(_('job title'), max_length=100, blank=True, null=True)
    contact_number = models.CharField(_('contact number'), max_length=20, blank=True, null=True)

    can_manage_animals = models.BooleanField(_('can manage animals'), default=False)
    can_manage_health = models.BooleanField(_('can manage health records'), default=False)
    can_manage_feeding = models.BooleanField(_('can manage feeding'), default=False)
    can_manage_inventory = models.BooleanField(_('can manage inventory'), default=False)
    can_manage_sales = models.BooleanField(_('can manage sales'), default=False)
    can_manage_employees = models.BooleanField(_('can manage employees'), default=False)
    can_view_reports = models.BooleanField(_('can view reports'), default=False)

    USERNAME_FIELD = 'email'  # <--- Email is now login field
    REQUIRED_FIELDS = []      # No required extra fields for createsuperuser

    objects = UserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Automatically assign permissions based on role
        role_config = {
            'owner':       [True, True, True, True, True, True, True, True],
            'manager':     [False, True, True, True, True, True, False, True],
            'veterinarian':[False, True, True, False, False, False, False, False],
            'worker':      [False, True, False, True, False, False, False, False],
            'accountant':  [False, False, False, False, True, True, False, True],
        }

        config = role_config.get(self.role, [False]*8)
        self.is_farm_owner, self.can_manage_animals, self.can_manage_health, self.can_manage_feeding, \
        self.can_manage_inventory, self.can_manage_sales, self.can_manage_employees, self.can_view_reports = config

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
