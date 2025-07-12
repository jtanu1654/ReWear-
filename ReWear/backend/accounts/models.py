from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class User(AbstractUser):
    """Custom User model for ReWear application"""
    
    # User roles
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    points = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    bio = models.TextField(blank=True, max_length=500)
    location = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    # Override username to use email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
    
    def add_points(self, points_to_add):
        """Add points to user account"""
        self.points += points_to_add
        self.save()
    
    def deduct_points(self, points_to_deduct):
        """Deduct points from user account"""
        if self.points >= points_to_deduct:
            self.points -= points_to_deduct
            self.save()
            return True
        return False
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
