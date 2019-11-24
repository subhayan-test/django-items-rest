from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin)
from django.conf import settings
from django.db.models.signals import pre_save


class UserManager(BaseUserManager):
    def create_user(self, email, password=None,
                    role=None, **extra_fields):
        """Creates and saves a new user """
        if not email:
            raise ValueError('Users must have an email address')
        if not role or role not in ('Supplier', 'Purchaser', 'Superuser'):
            raise ValueError(
                'User must have a role in the system and it has to be either Supplier or Purchaser')
        user = self.model(email=self.normalize_email(email),
                          role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Creates and saves a new super user"""
        user = self.create_user(
            email=email, password=password, role='Superuser', is_staff=True, is_superuser=True)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model which supports using email instead of username"""
    ROLES = (
        ('Supplier', 'Supplier'),
        ('Purchaser', 'Purchaser'),
        ('Superuser', 'Superuser')
    )
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


def check_role(sender, instance, **kwargs):
    if instance.role == 'Superuser':
        if not instance.is_superuser:
            raise ValueError("Only a super user can have role as Superuser")


pre_save.connect(check_role, sender=User)


class Item(models.Model):
    """Custom Item model"""
    name = models.CharField(max_length=255, unique=True)
    price = models.IntegerField()
    description = models.TextField()
    is_draft = models.BooleanField(default=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class ShoppingCart(models.Model):
    """Custom shopping cart model"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.user.name}__{self.item.name}"
