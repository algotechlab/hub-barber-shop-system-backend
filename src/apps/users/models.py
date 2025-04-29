from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=40, blank=False, null=False)
    
    def __str__(self):
        return self.user
    
    def __repr__(self):
        return f"""<UserProfile user={self.user} phone={self.phone}>"""

