from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #portfolio_site = models.URLField(blank=True)
    #profile_pic = models.ImageField(upload_to='profile_pics', blank=True)
    def __str__(self):
        return self.user.username

class Loopa(models.Model):
   csvfile = models.ImageField(upload_to = 'csv')
   class Meta:
      db_table = "profile"


class Document(models.Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

