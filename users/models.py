from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('writer', 'Writer'),
        ('user', 'Standard User'),
    ]
    
    PREFERRED_LANGUAGE_CHOICES = [
        ('ar', 'العربية'),
        ('en', 'English'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    preferred_language = models.CharField(max_length=5, choices=PREFERRED_LANGUAGE_CHOICES, default='ar')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    facebook_url = models.URLField(max_length=500, blank=True, null=True)
    linkedin_url = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        permissions = [
            ("can_publish", "Can publish articles/brokers"),
            ("can_edit", "Can edit articles/brokers"),
            ("can_manage_brokers", "Can manage brokers"),
        ]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
