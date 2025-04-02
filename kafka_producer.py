from kafka import KafkaProducer
import pandas as pd
import json

# To get and parse the data
class Parser:
    @staticmethod
    def read_data(ticker):
        # Rest API Url
        url = "https://www.pschatzmann.ch/edgar/db/companyValues?tradingSymbol="+ticker+"&periods=Y&format=csv"

        # Data to pandas dataframe with only columns that will be required to calculate the financial ratios
        data = pd.read_csv(url, sep = ';', usecols = ["date", "AssetsCurrent", "LiabilitiesCurrent", "Assets", "Liabilities", "Revenues", "LongTermDebt", "NetIncomeLoss", "OperatingIncomeLoss", "SalesRevenueNet"])
        
        # Calculate financial ratios
        data["year"] = pd.DatetimeIndex(data['date']).year
        data["currentRatio"] = data["AssetsCurrent"] /  data["LiabilitiesCurrent"]
        data["debtEquityRatio"] = data["LongTermDebt"] /  (data["Assets"] - data["Liabilities"])
        data["debtRatio"] = data["Liabilities"] /  data["Assets"]
        data["netProfitMarginRatio"] = data["NetIncomeLoss"] /  data["Revenues"]
        data["operatingProfitMarginRatio"] = data["OperatingIncomeLoss"] /  data["SalesRevenueNet"]

        # If data is missiong or NaN then insert zero
        data.fillna(0, inplace=True)

        # Return only required data
        return (data[["year", "NetIncomeLoss", "currentRatio", "debtEquityRatio", "debtRatio", "netProfitMarginRatio", "operatingProfitMarginRatio"]])

if __name__ == '__main__':

    # Kafka Producer configuration
    bootstrap_servers = ["localhost:9092"]
    topicname = 'ratio'
    producer = KafkaProducer(bootstrap_servers = bootstrap_servers)
    producer = KafkaProducer()

    # Get data and transform
    file = Parser.read_data("AAPL")

    # Convert to dict
    fileDict = file.to_dict("records")

    # Send data to producer
    for obj in fileDict:
        print("Message is :: {}".format(obj))
        producer.send(topicname, json.dumps(obj).encode('utf-8'))

