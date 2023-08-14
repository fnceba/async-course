from hashlib import md5
import json
from django.db import models
from cryptography.fernet import Fernet
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='default')

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
        kwargs = dict(role=role, name=name, email=email, password_md5 = md5(password).hexdigest())
        user = User.objects.create(**kwargs)
        
        #-----------------------------CUD event--------------------------------
        kwargs.pop('password_md5')
        kwargs['id'] = user.id
        channel.basic_publish(
            exchange='', 
            routing_key='default', 
            body=json.dumps(dict(event_type='CUD', content_type='User', action='create', kwargs=kwargs)))
        #----------------------------------------------------------------------

        return user

    @staticmethod
    def get_user_token(email:str, password:str) -> str|None: #authenticate
        user = User.objects.filter(email=email, password_md5= md5(password).hexdigest()).first()
        if not user:
            return
        return fernet.encrypt(str(user.id).encode()).decode()
    
