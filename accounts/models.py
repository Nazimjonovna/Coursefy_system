from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField
from accounts.managers import CustomUserManager
from django.db import models


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = PhoneNumberField(db_index=True, unique=True)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    is_online = models.BooleanField(default=False)
    last_online = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"(User ID : {self.id}) {self.phone_number}"

    @property
    def all_groups(self):
        if self.groups:
            return list(self.groups.all())


class Profile(models.Model):
    LANG_EXT = (
        ('uz', 'Uzbek'),
        ('ru', 'Russian'),
        ('en', 'English'),
        ('qr', 'Karakalpak'),
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    picture = models.ImageField(
        upload_to='account/images/', null=True, blank=True)
    first_name = models.CharField(max_length=240)
    last_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    parent_phone_number = PhoneNumberField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=2, choices=LANG_EXT, default='uz')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name = 'User profile'
        verbose_name_plural = 'Users profiles'


class Verification(models.Model):
    STATUS = (
        ('send', 'send'),
        ('confirmed', 'confirmed'),
    )
    phone_number = PhoneNumberField()
    verify_code = models.SmallIntegerField(unique=True)
    is_verified = models.BooleanField(default=False)
    step_reset = models.CharField(
        max_length=10, null=True, blank=True, choices=STATUS)
    step_change_phone = models.CharField(
        max_length=30, null=True, blank=True, choices=STATUS)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone_number} --- {self.verify_code}"


class HistoryOfEntries(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='entries')
    ip = models.GenericIPAddressField()
    device = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    entered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip} {self.entered}"
