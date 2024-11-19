from django.db import models
import datetime
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name
    
class Story(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    name = models.CharField(max_length=250, unique=True)
    author =  models.CharField(max_length=250)
    url = models.URLField(unique=True)
    content = models.TextField()
    public_day = models.DateField(default=datetime.date.today)
    image = models.ImageField(upload_to='stories/images', default='stories/images/default.jpg')
    info = CKEditor5Field('Text', config_name='extends')
    def __str__(self):
        return self.name
    
class Contact(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number= models.CharField(max_length=20, null=True)
    subject = models.CharField(max_length=264)
    message = models.TextField()

    def __str__(self):
        return self.name + ", " + self.subject


class UserProfileInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT )
    portfolio = models.URLField(blank=True)
    image = models.ImageField(upload_to="store/images", default="store/images/people_default.png")

    def __str__(self):
        return self.user.username
    
