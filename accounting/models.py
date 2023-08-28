import json
import random
import uuid
from django.db import models
from cryptography.fernet import Fernet
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='default')

fernet = Fernet(b'fnEzdP1WtdWv1MtigCnDMHKod-EzumbYM8R2Izz6gyA=')

# Create your models here.

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
    public_id = models.UUIDField('Public ID', blank=True, null=True)
    balance = models.FloatField('Баланс', default=0)
    def get_user_by_token(self, token):
        return User.objects.get(id=int(fernet.decrypt(token.encode()).decode()))



class TaskStatus(models.IntegerChoices):
    IN_PROGRESS = 1, "In Progress"
    DONE = 2, "Done"

class Task(models.Model):
    description = models.TextField('Описание задачи')
    status = models.PositiveSmallIntegerField('Статус задачи', choices=TaskStatus.choices, default=0)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Ответственный за выполнение задачи')
    public_id = models.UUIDField('Public ID', default=uuid.uuid4, editable=False)
    
    reassign_fee = models.SmallIntegerField('Fee', default=0)
    price = models.SmallIntegerField('Price', default=0)

    def created(self): # business callback
        self.reassign_fee = random.randint(-20, -10)
        self.price = random.randint(20, 40)
        self.save(update_fields=['price', 'reassign_fee'])
    def reassigned(self): # business callback
        BalanceChangeLog.create_log(self.user, self.reassign_fee)


class BalanceChangeLog(models.Model):
    dt = models.DateTimeField('Create dt', auto_now_add=False)
    change = models.FloatField('Change')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Чей баланс изменился')
    public_id = models.UUIDField('Public ID', default=uuid.uuid4, editable=False)
    
    @staticmethod
    def create_log(user, change):
        chlog = BalanceChangeLog.objects.create(user=user, change=change)
        #-----------------------------Streaming event--------------------------------
        kwargs = {'public_id':chlog.public_id, 'user_public_id':user.public_id, 'change':change}
        channel.basic_publish(
            exchange='', 
            routing_key='default', 
            body=json.dumps(dict(event_type='Streaming', content_type='BalanceChangeLog', action='create', kwargs=kwargs)))
        #----------------------------------------------------------------------
        channel.basic_publish(
            exchange='', 
            routing_key='default', 
            body=json.dumps(dict(event_type='Business', content_type='BalanceChangeLog', action='create', kwargs=kwargs)))

        user.balance += change
        user.save(update_fields=['balance'])

        #-----------------------------Streaming event--------------------------------
        kwargs = {'public_id': user.public_id, 'balance':user.balance}
        channel.basic_publish(
            exchange='', 
            routing_key='default', 
            body=json.dumps(dict(event_type='Streaming', content_type='User', action='update', kwargs=kwargs)))
        #----------------------------------------------------------------------
        channel.basic_publish(
            exchange='', 
            routing_key='default', 
            body=json.dumps(dict(event_type='Business', content_type='User', action='balance_updated', kwargs=kwargs)))

    