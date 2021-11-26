from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import *

admin.site.register(Code)

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    User table in admin panel
    """

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'middle_name','phone', 'favourites', 'viewed' , 'Venezia', 'Quartz', 'Charme')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'middle_name', 'is_staff','last_login', 'phone',)
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('email',)