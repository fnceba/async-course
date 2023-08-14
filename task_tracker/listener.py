import json
import pika
import threading

from ates_auth.models import User


class EventListener(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = connection.channel()
        result = self.channel.queue_declare(queue='default')
        queue_name = result.method.queue
        self.channel.basic_consume(queue=queue_name, on_message_callback=self.callback)
        

    def CUD_callback(self, channel, method, properties, body):
        content_type_mapping = {
            'User': User
        }
        if Model:=content_type_mapping.get(body['content_type']):
            if body['action'] == 'create':
                Model.objects.create(**body['kwargs'])
            elif body['action'] == 'update':
                Model.objects.filter(id=body['kwargs']['id']).update(**body['kwargs'])

    def business_event_callback(self, channel, method, properties, body):
        pass

    def callback(self, channel, method, properties, body):
        body = json.loads(body)
        if(body['event_type'] == 'CUD'):
            self.CUD_callback(channel, method, properties, body)
        elif(body['event_type'] == 'business_event'):
            self.business_event_callback(channel, method, properties, body)
        channel.basic_ack(delivery_tag=method.delivery_tag)
        
    def run(self):
        self.channel.start_consuming()