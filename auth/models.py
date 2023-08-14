from hashlib import md5
from django.db import models
from cryptography.fernet import Fernet

fernet = Fernet(b'fnEzdP1WtdWv1MtigCnDMHKod-EzumbYM8R2Izz6gyA=')

# Create your models here.
class UserRole(models.IntegerChoices):
    ADMIN = 1, "Admin"
    BOSS = 2, "Boss"
    DEVELOPER = 3, "Developer"
    MANAGER = 4, "Manager"
    ACCOUNTANT = 5, "Accountant"

class User(models.Model):
    ROLE_CHOICES = (
        (1, "Admin"),
        (2, "Boss"),
        (3, "Developer"),
        (4, "Manager"),
        (5, "Accountant"),
    )
    role = models.PositiveSmallIntegerField("Роль", choices=UserRole.choices)
    name = models.CharField("Имя", max_length=50, blank=True, default='')
    email = models.EmailField('Email', max_length=254, unique=True)
    password_md5 = models.CharField("MD5 Пароля", max_length=50, blank=True)
    
    # default id is used as public id

    @staticmethod
    def create_user(role, email:str, password:str, name:str='') -> 'User':
        user = User.objects.create(role=role, name=name, email=email, password = md5(password).hexdigest())
        # TODO: send CUD event
        return user

    @staticmethod
    def get_user_token(email:str, password:str) -> str|None: #authenticate
        user = User.objects.filter(email=email, password= md5(password).hexdigest()).first()
        if not user:
            return
        return fernet.encrypt(str(user.id).encode()).decode()
    
