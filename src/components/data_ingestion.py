from src.logger_config.logger import logging
from src.exception_config.exception import CustomException
from src.components.data_extraction import DataExtraction
import os
import sys
from dotenv import load_dotenv
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
from pandas import DataFrame,Series
from sklearn.model_selection import train_test_split

load_dotenv()

@dataclass

class DataIngestionConfig:
    
    artifact_dir :Path= Path("artifacts")
    feature_store:Path=artifact_dir/"feature_Store"
    ingest:Path=artifact_dir/"Ingest"
    train_path: Path=ingest/"train.csv"
    valid_path: Path=ingest/"valid.csv"
    test_path: Path=ingest/"test.csv"

class DataIngest:
    def __init__(self):
        try:
            self.data_ingest=DataIngestionConfig()
            self.extractor=DataExtraction()

            os.makedirs(self.data_ingest.artifact_dir,exist_ok=True)
            os.makedirs(self.data_ingest.feature_store,exist_ok=True)
            os.makedirs(self.data_ingest.ingest,exist_ok=True)

            logging.info("DataIngest class initialized successfully.")
        except Exception as e:
            raise CustomException(e)

    
    def fetch_df_from_Mongo(self):
        try:
            df=self.extractor.extract_from_MongoDB()
            logging.info(f"Successfully fetched {len(df)} records from MongoDB.")
            df.to_csv(self.data_ingest.feature_store/"raw_data.csv",index=False)
            logging.info(f"Data successfully fetched and saved to feature store")
            return df
        except Exception as e:
            raise CustomException(e)
        
    def split_data(self,df:DataFrame):
        try:
            logging.info("Train test split initiation")
            train_set,temp_set=train_test_split(df,test_size=0.2,random_state=42)
            valid_set,test_set=train_test_split(temp_set,test_size=0.5,random_state=42)

            train_set.to_csv(self.data_ingest.train_path,index=False,header=True)
            valid_set.to_csv(self.data_ingest.valid_path,index=False,header=True)
            test_set.to_csv(self.data_ingest.test_path,index=False,header=True)

            logging.info(f"Train data saved to {self.data_ingest.train_path}")
            logging.info(f"Valid data saved to {self.data_ingest.valid_path}")
            logging.info(f"Test data saved to {self.data_ingest.test_path}")
            logging.info(f"Data Split Conpleted")

            return train_set,valid_set,test_set
        
        except Exception as e:
            raise CustomException(e)


        
        
    



