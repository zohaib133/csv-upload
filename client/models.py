from django.db import models
from django.contrib.auth.models import AbstractUser
from django_userforeignkey.models.fields import UserForeignKey
import uuid
GENDER = (("M", "MALE"), ("F", "FEMALE"))


class Country(models.Model):
    name = models.CharField(max_length=255, db_column='name')

    class Meta:
        db_table = 'Country'


class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, db_column='country')
    name = models.CharField(max_length=255, db_column='name')

    class Meta:
        db_table = 'City'


class User(AbstractUser):
    gender = models.CharField(max_length=1, choices=GENDER, null=True, db_column='gender')
    email = models.EmailField(null=True, db_column='email')
    created_by = UserForeignKey(auto_user_add=True, related_name="user_created_by")
    updated_by = UserForeignKey(auto_user=True, related_name="user_updated_by")
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(null=True, db_column='updated_at', auto_now=True)
    is_removed = models.BooleanField(default=False, db_column='is_removed')

    def __str__(self):
        return self.get_username()

    class Meta:
        db_table = 'User'


class LogEntryForException(models.Model):
    id = models.UUIDField(primary_key=True, db_column='id', default=uuid.uuid1)
    exception = models.TextField(null=False, db_column='exception')
    url = models.TextField(default='', db_column='url')
    user_agent = models.TextField(default='', db_column='user_agent')
    ip_address = models.TextField(default='', db_column='ip_address')
    created_at = models.DateTimeField(db_column='created_at', auto_created=True)

    class Meta:
        db_table = 'LogEntryForException'


class Sale(models.Model):
    product = models.CharField(max_length=255, db_column='product')
    revenue = models.FloatField(default=0.0)
    sales_number = models.IntegerField(default=0)
    date = models.DateField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    created_by = UserForeignKey(auto_user_add=True, related_name="sale_created_by")
    updated_by = UserForeignKey(auto_user=True, related_name="sale_updated_by")
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(null=True, db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'Sale'
