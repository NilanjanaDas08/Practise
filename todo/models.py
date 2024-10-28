from django.db import models
from django.utils import timezone

# Create your models here.
class User(models.Model):
    first_name=models.CharField(max_length=255)
    middle_name=models.CharField(max_length=255)
    last_name=models.CharField(max_length=255)
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=255)
    status=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Task(models.Model):
    name=models.CharField(max_length=255)
    STATUS_CHOICES=[
        ('PENDING','pending'),
        ('COMPLETED','completed')
    ]
    status=models.CharField(max_length=255,choices=STATUS_CHOICES,default='PENDING')
    user=models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"
