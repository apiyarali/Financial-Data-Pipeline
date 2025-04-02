from elasticsearch import Elasticsearch
from kafka import KafkaConsumer
from json import loads

if __name__ == '__main__':
    # Elasticsearch configuration
    es = Elasticsearch('https://localhost:9200',
                   ca_certs="./http_ca.crt",
                   http_auth=('elastic', 'ccSyeUpfoth=S2apj1*3'))
    
    # Kafka consumer configuration
    bootstrap_servers = ['localhost:9092']
    topicName = 'ratio'
    consumer = KafkaConsumer (topicName, group_id = 'my_group_id1',bootstrap_servers = bootstrap_servers,
        auto_offset_reset = 'earliest',value_deserializer=lambda x: loads(x.decode('utf-8'))) 

    # Kafka consumer receiving message and pushing message data to elasticsearch
    for message in consumer:
        print (message)
        response = es.index(
                index="ratio",
                body=message.value
            )