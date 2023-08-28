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
    

    @staticmethod
    def create_task(description):
        task = Task.objects.create(description=description)

        #-----------------------------Streaming event--------------------------------
        kwargs = {'status': task.status, 'description': task.description, 'public_id':task.public_id.hex}
        channel.basic_publish(
            exchange='', 
            routing_key='default', 
            body=json.dumps(dict(event_type='Streaming', content_type='Task', action='create', kwargs=kwargs)))
        #----------------------------------------------------------------------

        kwargs = {'status': task.status, 'description': task.description, 'public_id':task.public_id.hex}
        channel.basic_publish(
            exchange='', 
            routing_key='default', 
            body=json.dumps(dict(event_type='Business', content_type='Task', action='create', kwargs=kwargs)))


        task.reassign()

    def reassign(self):
        users = User.objects.exclude(role__in=[UserRole.ADMIN, UserRole.MANAGER])
        user = random.choice(users)
        self.user = user
        self.save(update_fields=['user'])

        #-----------------------------Streaming event--------------------------------
        kwargs = {'public_id':self.public_id.hex, 'user_public_id':self.user.public_id.hex}
        channel.basic_publish(
            exchange='', 
            routing_key='default', 
            body=json.dumps(dict(event_type='Streaming', content_type='Task', action='update', kwargs=kwargs)))
        #----------------------------------------------------------------------

        kwargs = {'public_id':self.public_id.hex, 'user_public_id':self.user.public_id.hex}
        channel.basic_publish(
            exchange='', 
            routing_key='default', 
            body=json.dumps(dict(event_type='Business', content_type='Task', action='reassign', kwargs=kwargs)))
    
    def complete(self):
        self.status = TaskStatus.DONE
        self.save(update_fields='status')

         #-----------------------------Streaming event--------------------------------
        kwargs = {'public_id':self.public_id.hex, 'status':self.status}
        channel.basic_publish(
            exchange='', 
            routing_key='default', 
            body=json.dumps(dict(event_type='Streaming', content_type='Task', action='update', kwargs=kwargs)))
        #----------------------------------------------------------------------


        kwargs = {'public_id':self.public_id.hex,}
        channel.basic_publish(
            exchange='', 
            routing_key='default', 
            body=json.dumps(dict(event_type='Business', content_type='Task', action='complete', kwargs=kwargs)))
