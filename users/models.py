from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class UserRoles(models.TextChoices):
    ADMIN = "admin", "Admin"
    SERVICE_PROVIDER = "service_provider", "Service Provider"
    CUSTOMER = "customer", "Customer"

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, role=UserRoles.CUSTOMER, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, role=UserRoles.ADMIN, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    phone = PhoneNumberField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=UserRoles.choices,
        default=UserRoles.CUSTOMER,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.role})"
