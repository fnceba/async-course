from hashlib import md5
from django.db import models

# Create your models here.
class User(models.Model):
    ROLE_CHOICES = (
        (1, "Admin"),
        (2, "Boss"),
        (3, "Developer"),
        (4, "Manager"),
        (5, "Accountant"),
    )
    role = models.PositiveSmallIntegerField("Роль", choices=ROLE_CHOICES)
    name = models.CharField("Имя", max_length=50, blank=True, default='')
    email = models.EmailField('Email', max_length=254, unique=True)
    password_md5 = models.CharField("MD5 Пароля", max_length=50, blank=True)
    
    # default id is used as public id

    
    def set_password(self, new_password):
        self.password_md5 =
        self.save()

    @staticmethod
    def create_user(role, email, password, name=''):
        user = User.objects.create(role=role, name=name, email=email, password = md5(password).hexdigest())
        # send CUD event
        return user

    @staticmethod
    def authenticate(email, password):
        user = User.objects.filter(email=email, password= md5(password).hexdigest()).first()
        if not user:
            return
        
        
