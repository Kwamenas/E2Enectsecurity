from src.logger_config.logger import logging
from src.exception_config.exception import CustomException
from pathlib import Path
import os
from dataclasses import dataclass
import pandas as pd
import numpy as np
from pandas import DataFrame,Series
import yaml
from src.utils.main_utils.calls_utils import creat_yaml_file,validate_number_of_cols,drift_check
from src.components.data_ingestion import DataIngestionConfig,DataIngest
from typing import List
from scipy.stats import ks_2samp

@dataclass

class DatavalidationConfig:
    artifact_dir :Path= Path("artifacts")
    data_validation_dir:Path= artifact_dir/"validation"
    validated_file:Path= data_validation_dir/"validated"
    invalid_file:Path=data_validation_dir/"invalid"

    train_validated: Path =validated_file/"train.csv"
    valid_validated: Path = validated_file/"valid.csv"
    test_validated: Path= validated_file/"test.csv"

    train_invalid: Path =invalid_file/"train.csv"
    valid_invalid: Path = invalid_file/"valid.csv"
    test_invalid: Path= invalid_file/"test.csv"

    drift_report:Path= data_validation_dir/"drift_report"
    drift_file:Path=drift_report/"report.yaml"
    raw_csv_dir:Path= artifact_dir/"feature_Store"
    data_schema: Path= Path("data_schema")
    data_schema_path:Path=data_schema/"data_schema.yaml"
 

class DataValidation:
    def __init__(self):
        try:
            self.config = DatavalidationConfig()
            self.ingest=DataIngestionConfig()
            os.makedirs(self.config.artifact_dir, exist_ok=True)
            os.makedirs(self.config.data_schema, exist_ok=True)
            os.makedirs(self.config.data_validation_dir, exist_ok=True)
            os.makedirs(self.config.validated_file, exist_ok=True)
            os.makedirs(self.config.invalid_file, exist_ok=True)
            os.makedirs(self.config.drift_report, exist_ok=True)
            os.makedirs(self.config.raw_csv_dir, exist_ok=True)
            logging.info("All validation directories created successfully.")
        except Exception as e:
            raise CustomException(e)
    
        
    def create_data_schema(self,filepath:Path)-> Path:
        try:
            files=list(Path(filepath).glob("*.csv"))
            if not files:
                raise CustomException(f"no CSV file in {filepath}")
            df=[pd.read_csv(file) for file in files]
            combined=pd.concat(df,ignore_index=True)
            schema = {col: str(dtype) for col, dtype in combined.dtypes.astype(str).to_dict().items()}
            creat_yaml_file(self.config.data_schema_path,content=schema,replace=True)
            logging.info(f"Data schema created at: {self.config.data_schema_path}")
            return self.config.data_schema_path
        
        except Exception as e:
           raise CustomException(e)


    
    
    def initiate_data_validation(self):
        try:
            train_file_path= self.ingest.train_path
            test_file_path=self.ingest.test_path
            valid_file_path=self.ingest.valid_path

            train_dataframe=pd.read_csv(train_file_path)
            test_dataframe=pd.read_csv(test_file_path)
            valid_dataframe=pd.read_csv(valid_file_path)

            errors=[]

            ok_train=validate_number_of_cols(self.config.data_schema_path,dataframe_path=train_dataframe)
            if not ok_train:
                errors.append(f"Data in {train_file_path} does not contain all columns. \n")
                
            ok_test =validate_number_of_cols(self.config.data_schema_path,dataframe_path=test_dataframe)
            if not ok_test:
                errors.append(f"Data in {test_dataframe} does not contain all columns. \n")

            ok_valid =validate_number_of_cols(self.config.data_schema_path,dataframe_path=valid_dataframe)
            if not ok_valid:
                errors.append(f"Data in {valid_dataframe} does not contain all columns. \n")

            if errors:
                for e in errors:
                    logging.error(e)
                raise CustomException(e)
            
            
            status=drift_check(self.config.drift_file,train_dataframe,test_dataframe)

            if not status:
                train_dataframe.to_csv(self.config.train_invalid,index=False,header=True)
                valid_dataframe.to_csv(self.config.valid_invalid,index=False,header=True)
                test_dataframe.to_csv(self.config.test_invalid,index=False,header=True)
            else:
                train_dataframe.to_csv(self.config.train_validated,index=False,header=True)
                valid_dataframe.to_csv(self.config.valid_validated,index=False,header=True)
                test_dataframe.to_csv(self.config.test_validated,index=False,header=True)

            logging.info(f"Validated files saved to: {self.config.validated_file}")

            return self.config.validated_file


        except Exception as e:
            raise CustomException(e)
        

        
    
