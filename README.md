# Financial Data Pipeline

This project demonstrates how to build a system that collects financial data for a selected company, indexes the data in Elasticsearch, and analyzes financial ratios on a yearly basis.

<img src="https://github.com/apiyarali/Financial-Data-Pipeline/blob/2a12b44d40f1c6e716c3c90cc7cfff09351e570a/Screenshots/kibana.jpg" alt="kibana" width="350">

## Big Data Source
- **Data Source:** [SEC EDGAR Database](https://www.sec.gov/os/accessing-edgar-data)
- **API:** [Smart Edgar](https://pschatzmann.ch/edgar/index.html#/)
  - Endpoint: `GET/db/companyValues{tradingSymbol,periods,format}`
- **Data Format:** JSON, XML, or CSV
- **Data Size:**
  - File Size: ~1MB
  - ~551 CSV columns or JSON keys (varies by period selected)
  - Financial identifiers include Assets, Liabilities, Net Income, Equity, and others.

## Expected Results
The processing pipeline will display a company's year-over-year financial ratios in tabular or graphical format. Example financial ratios include:
- Net Income Loss
- Current Ratio (ability to pay current debt)
- Debt to Equity Ratio (financing structure of company assets)
- Debt Ratio (ability to pay all debt)
- Net Profit Margin
- Operating Profit Margin

## Pipeline Overview and Technologies Used

<img src="https://github.com/apiyarali/Financial-Data-Pipeline/blob/9964155326db6341f25d74bcff60f961be0c733c/Screenshots/pipeline.jpg" alt="data-pipeline" width="350">

### **Collection Tier:** REST API
- Python and Pandas used to extract and modify data

### **Messaging Tier:** Kafka
- Pandas DataFrame pushes data to Kafka Producer

### **Stream Processing Tier:** Kafka Connect
- Kafka Consumer connects data to Elasticsearch index

### **Visualization Tier:** Elasticsearch and Kibana
- Data visualization in Kibana with Elasticsearch

### **New Technologies/Frameworks Used:**
- Python Kafka API
- Kafka Connect for indexing data into Elasticsearch
- Docker for containerized deployment

## Implementation
### **Dockerized Kafka and Elasticsearch Deployment**
- Kafka and Elasticsearch implemented using Docker Compose.
- Referenced from Elastic Stack’s [Docker Guide](https://www.elastic.co/guide/en/elastic-stack-get-started/current/get-started-stack-docker.html#run-docker-secure)

<img src="https://github.com/apiyarali/Financial-Data-Pipeline/blob/9964155326db6341f25d74bcff60f961be0c733c/Screenshots/docker.jpg" alt="docker" width="250">

### **Docker Commands Used:**
```
docker pull docker.elastic.co/elasticsearch/elasticsearch:8.1.2
docker pull docker.elastic.co/kibana/kibana:8.1.2
docker network create elastic
docker run --name es01 --net elastic -p 9200:9200 -it docker.elastic.co/elasticsearch/elasticsearch:8.1.2
docker run --name kibana --net elastic -p 5601:5601 docker.elastic.co/kibana/kibana:8.1.2
```

## Kafka Producer (kafka_producer.py)
Python script that fetches financial data, calculates key financial ratios, and sends them to Kafka.

```python
from kafka import KafkaProducer
import pandas as pd
import json

class Parser:
    @staticmethod
    def read_data(ticker):
        url = "https://www.pschatzmann.ch/edgar/db/companyValues?tradingSymbol=" + ticker + "&periods=Y&format=csv"
        data = pd.read_csv(url, sep=';', usecols=["date", "AssetsCurrent", "LiabilitiesCurrent", "Assets", "Liabilities", "Revenues", "LongTermDebt", "NetIncomeLoss", "OperatingIncomeLoss", "SalesRevenueNet"])
        
        data["year"] = pd.DatetimeIndex(data['date']).year
        data["currentRatio"] = data["AssetsCurrent"] / data["LiabilitiesCurrent"]
        data["debtEquityRatio"] = data["LongTermDebt"] / (data["Assets"] - data["Liabilities"])
        data["debtRatio"] = data["Liabilities"] / data["Assets"]
        data["netProfitMarginRatio"] = data["NetIncomeLoss"] / data["Revenues"]
        data["operatingProfitMarginRatio"] = data["OperatingIncomeLoss"] / data["SalesRevenueNet"]
        
        data.fillna(0, inplace=True)
        return data[["year", "NetIncomeLoss", "currentRatio", "debtEquityRatio", "debtRatio", "netProfitMarginRatio", "operatingProfitMarginRatio"]]

if __name__ == '__main__':
    producer = KafkaProducer(bootstrap_servers=["localhost:9092"])
    data = Parser.read_data("AAPL")
    for obj in data.to_dict("records"):
        producer.send('ratio', json.dumps(obj).encode('utf-8'))
```

## Kafka Consumer (kafka_consumer_es.py)
Python script that consumes Kafka messages and indexes them into Elasticsearch.

```python
from elasticsearch import Elasticsearch
from kafka import KafkaConsumer
from json import loads

if __name__ == '__main__':
    es = Elasticsearch('https://localhost:9200', ca_certs="./http_ca.crt", http_auth=('elastic', 'yourpassword'))
    consumer = KafkaConsumer('ratio', group_id='my_group', bootstrap_servers=['localhost:9092'], auto_offset_reset='earliest', value_deserializer=lambda x: loads(x.decode('utf-8')))
    for message in consumer:
        es.index(index="ratio", body=message.value)
```

## Results
- Successfully deployed Kafka, Elasticsearch, and Kibana using Docker.
- Data from SEC EDGAR database processed and analyzed for Apple Inc.
- Financial ratios calculated and visualized using Kibana.

<img src="https://github.com/apiyarali/Financial-Data-Pipeline/blob/2a12b44d40f1c6e716c3c90cc7cfff09351e570a/Screenshots/kibana.jpg" alt="kibana" width="350">
<img src="https://github.com/apiyarali/Financial-Data-Pipeline/blob/9964155326db6341f25d74bcff60f961be0c733c/Screenshots/elasticsearch.jpg" alt="elasticsearch" width="350">

## Challenges and Lessons Learned
### **Issues Encountered:**
- Inconsistent column names in SEC EDGAR data due to missing values or different company naming conventions.

### **Technological Limitations:**
- `confluent_kafka` API is easier to use than `kafka-python`, but does not work on Windows Operating System.

### **Alternative Technologies:**
- Instead of direct Kafka ingestion, data could be stored in AWS S3 and pushed to Elasticsearch via Kafka.

## Future Improvements
- Implement additional financial ratios.
- Enable user-defined financial ratios.
- Build a data cleanup layer to standardize column names.
- Develop a comparative analysis feature for multiple companies.

## Conclusion
This project demonstrates an end-to-end pipeline for collecting, processing, and analyzing financial data using REST APIs, Kafka, Elasticsearch, and Kibana. Future improvements will focus on data quality, user customization, and expanding the financial analysis capabilities.

