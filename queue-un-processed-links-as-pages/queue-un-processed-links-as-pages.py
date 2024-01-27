#!/usr/bin/env python

import pika
import requests
import json
import pymongo
from datetime import datetime, timezone
import time

"""    
    This processor is responsible for listening to inbound MQTT topics for 
    target URL's to be processed. It will queue the request up for processing into our Page Parser.
"""

rabbit_mq_broker = 'localhost'
rabbit_mq_queue_collect = 'collect-page'
rabbit_mq_queue_process = 'process-page'

mongo_db_address = 'mongodb://localhost:27017/golden-eye'
mongo_db_catalog = 'golden_eye'
mongo_db_document_store = 'pages'        

def run():
    myclient = pymongo.MongoClient(mongo_db_address)
    mydb = myclient[mongo_db_catalog]
    mycol = mydb[mongo_db_document_store]

    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_mq_broker))
    channel = connection.channel()

    channel.queue_declare(queue=rabbit_mq_queue_collect)
    
    while True:     

        print('start')
        for v in mycol.find({"processed": False}): 
            print(v['title'])
            
            for l in v['links']:
                data = {}
                data['target'] = f"{l}"
                channel.basic_publish(exchange='',
                                    routing_key=rabbit_mq_queue_collect,
                                    body=json.dumps(data))

            
            newvalues = { "$set": { 'processed': True } }
            print(mycol.update_one(v, newvalues))
        time.sleep(10)
    connection.close()

if __name__ == '__main__':
    run()
