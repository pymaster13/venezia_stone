from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from View1C.models import *
from VeneziaStone.settings import EMAIL_HOST_USER as host_email


class UserManager(BaseUserManager):
    """
    Definition of django user model manager
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """

        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    """
    Definition of django user model:
    - delete field 'username';
    - change email - unique;
    - add phone with valid phone format;
    - add 3-d name (middle name).
    """

    username = None
    email = models.EmailField(_('Email address'),null = False, blank=False, unique=True)
    phone = PhoneNumberField(null=True, blank=True, unique=True)
    middle_name = models.CharField(_('middle name'), max_length=150, blank=True, null=True)
    favourites = models.ManyToManyField(Products, null=True, blank=True, verbose_name='Избранное', related_name='favorites')
    viewed = models.ManyToManyField(Products, null=True, blank=True, verbose_name='Просмотренное', related_name='viewed')
    Venezia = models.ForeignKey(Project, null=True, blank=True, on_delete=models.CASCADE,
        related_name='usersVenezia', verbose_name='Уровень доступа к проекту Venezia')
    Quartz = models.ForeignKey(Project,null=True, blank=True, on_delete=models.CASCADE,
        related_name='usersQuartz', verbose_name='Уровень доступа к проекту Quartz')
    Charme = models.ForeignKey(Project, null=True, blank=True, on_delete=models.CASCADE,
        related_name='usersCharme', verbose_name='Уровень доступа к проекту Charme')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # removes email from REQUIRED_FIELDS
    objects = UserManager()

def __str__(self):
    return self.email


class Code(models.Model):
    """
    Definition of code model - for reset password by phone
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userscode', verbose_name='Пользователь')
    code = models.CharField(max_length=6)
    created = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name = "Код"
        verbose_name_plural = "Коды"

    def __str__(self):
        return "{} - {}".format(self.user.phone, self.code)
