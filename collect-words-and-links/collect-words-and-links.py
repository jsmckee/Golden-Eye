#!/usr/bin/env python
import pika
import requests
import json
import pymongo
from bs4 import BeautifulSoup
import re
from datetime import datetime, timezone

rabbit_mq_broker = 'localhost'
rabbit_mq_queue_collect = 'collect-page'
rabbit_mq_queue_process = 'process-page'

mongo_db_address = 'mongodb://localhost:27017/golden-eye'
mongo_db_catalog = 'golden_eye'
mongo_db_document_store = 'pages'

mqtt_broker = 'localhost'
mqtt_port = 1883
mqttTopic = "target"

connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_mq_broker))
channel = connection.channel()

channel.queue_declare(queue=rabbit_mq_queue_collect)

def callback(ch, method, properties, body): 
    data = json.loads(body)
    page = requests.get(data['target'])    
    if page.url != 'https://aka.ms/yourcaliforniaprivacychoices':
        myclient = pymongo.MongoClient(mongo_db_address)
        mydb = myclient[mongo_db_catalog]
        mycol = mydb[mongo_db_document_store]
        
        # Parse Page    
        page_data = {}
        page_data["raw"] = page.text
        page_data["encoding"] = page.encoding
        page_data["read"] = datetime.now(timezone.utc)


        pageData = BeautifulSoup(page.content, 'lxml')        
        page_data["title"] = page.url
        page_data["processed"] = False
        page_data["links"] = []
        wordData = set()

        # Words
        for w in pageData.text.split(' '):
            for w2 in w.split('\n'):
                if w2.strip() != '':
                    if re.match(r'^[A-Za-z_]+$', w2.strip()):
                        wordData.add(w2.strip())

        page_data["words"] = list(wordData)

        # Links
        links = pageData.find_all('a')
        textLinks = []
        for l in links:
            val = l.get('href')
            if val is not None and val.startswith('http'):
                textLinks.append(val)

        page_data["links"] = textLinks

        # Save Page
        print(mycol.insert_one(page_data))

channel.basic_consume(queue=rabbit_mq_queue_collect,
                      auto_ack=True,
                      on_message_callback=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
