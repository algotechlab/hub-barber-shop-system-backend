from django.db import models

class User(models.Model):
    name = models.CharField(max_length=120 , blank=False, null=False)
    email = models.EmailField(max_length=100, blank=False, null=False)
    password = models.CharField(max_length=300, blank=False, null=False)
    phone = models.CharField(max_length=40, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.IntegerField(blank=True, null=True)
    deleted_by = models.IntegerField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<User name={self.name} email={self.email}>"
