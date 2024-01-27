#!/usr/bin/env python

"""    
    This processor is responsible for listening to inbound MQTT topics for 
    target URL's to be processed. It will queue the request up for processing into our Page Parser.

    Would be ideal to leverage the RabbitMQ MQTT plugin and avoid the need for this processor.
"""

import json
import pika
import random
from paho.mqtt import client as mqtt_client

rabbit_mq_broker = 'localhost'
rabbit_mq_queue_collect = 'collect-page'
mqtt_broker = 'localhost'
mqtt_port = 1883
mqttTopic = rabbit_mq_queue_collect

mqtt_client_id = f'subscribe-{random.randint(0, 100)}'

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(mqtt_client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(mqtt_broker, mqtt_port)
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_mq_broker))
        channel = connection.channel()

        channel.queue_declare(queue=rabbit_mq_queue_collect)

        data = {}
        data['target'] = f"{msg.payload.decode()}"
        channel.basic_publish(exchange='',
                            routing_key=rabbit_mq_queue_collect,
                            body=json.dumps(data))
        connection.close()

    client.subscribe(mqttTopic)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

if __name__ == '__main__':
    run()