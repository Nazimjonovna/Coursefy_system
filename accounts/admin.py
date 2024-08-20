from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from accounts.models import Profile, Verification, HistoryOfEntries
# from rest_framework_simplejwt.models import TokenUser


# admin.site.register(TokenUser)


@admin.register(HistoryOfEntries)
class HistoryOfEntriesAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip', 'device', 'address', 'entered')
    list_filter = ('user', 'ip', 'device', 'address', 'entered')
    

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user','picture', 'first_name', 'last_name', 'middle_name', 'birth_date', 'parent_phone_number')
    list_editable = ('user', 'first_name', 'last_name', 'middle_name', 'birth_date', 'parent_phone_number')
    search_fields = ('first_name', 'last_name', 'middle_name', 'birth_date', 'parent_phone_number')
    ordering = ('first_name', 'last_name', 'middle_name', 'birth_date', 'parent_phone_number')


@admin.register(get_user_model())
class CustomUserAdmin(UserAdmin):
    readonly_fields=('last_online',)
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions', 'is_online')}),
        (_('Important dates'), {'fields': ('last_login','last_online',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2'),
        }),
    )
    list_display = ('id', 'phone_number', 'is_staff', 'is_superuser', 'all_groups',)
    list_editable = ('phone_number', 'is_staff', 'is_superuser')
    search_fields = ('phone_number',)
    ordering = ('phone_number',)


@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_verified', 'step_reset', 'step_change_phone', 'phone_number', 'verify_code', 'created')
    read_only_fields = ('id', 'is_verified', 'step_reset', 'created')
