from src.logger_config.logger import logging
from src.exception_config.exception import CustomException
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import certifi ## provides a set of rules certification
import json
import os
import sys
from urllib.parse import quote_plus
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi



class DataExtraction():
    def __init__(self):
        try:
              load_dotenv()

              user=os.getenv("MONGO_ATLAS_USER")
              password=os.getenv("MONGO_ATLAS_PASSWORD")
              host=os.getenv("MONGO_ATLAS_HOST")
              params=os.getenv("MONGO_ATLAS_PARAMS","?retryWrites=true&w=majority")

              self.database=os.getenv("DATABASE")
              self.collection=os.getenv("COLLECTION")

              if not all([user,password,host,self.database,self.collection]):
                  raise ValueError ("Missing MongoDB credentials or database info in .env")
              
              password_quoted=quote_plus(password)
              uri = f"mongodb+srv://{user}:{password_quoted}@{host}/{params}"

              ca=certifi.where()

              
              self.client=MongoClient(uri,server_api=ServerApi('1'),tlsCAFile=ca)
              logging.info("MongoDB client initialized successfully ")

        except Exception as e:
            raise CustomException(e)
        
    def csv_to_json_conventor(self,filepath:str):
        try:
            data=pd.read_csv(filepath)
            data=data.reset_index(drop=True)
            records=json.loads(data.to_json(orient='records'))
            logging.info(f"Successfully converted {len(records)} rows from {filepath} to JSON")
            return records
        except Exception as e:
            raise CustomException(e)
        
    def insert_into_MongoDB(self,records:list):
        try:
            db=self.client[self.database]
            coll=db[self.collection]
            results=coll.insert_many(records)
            logging.info(f"Inserted {len(results.inserted_ids)} records into {self.database}.{self.collection}")
            return (len(results.inserted_ids))  
        except Exception as e:
            raise CustomException(e)
        
    def extract_from_MongoDB(self):

        try:
            db=self.client[self.database]
            coll=db[self.collection]
            data=list(coll.find())
            df=pd.DataFrame(data)
            df=df.drop(columns=['_id'])
            logging.info(f"fetched {len(df)} documents from {self.database}.{self.collection}")
            return df
        except Exception as e:
            raise CustomException(e)
        

#if __name__=="__main__":
 #   FILE_PATH="notebook\data\phisingData.csv"
 #   DATABASE="KNAS68"
 #   COLLECTION="NetworkData"
 #   data_obj=DataExtraction()
 #   record=data_obj.csv_to_json_conventor(filepath=FILE_PATH)
  #  print(record)
   # no_records=data_obj.insert_into_MongoDB(records=record,database=DATABASE,collection=COLLECTION)
   # print(no_records)


