from src.logger_config.logger import logging
from src.exception_config.exception import CustomException
from pathlib import Path
import os
import yaml
from pandas import DataFrame
from scipy.stats import ks_2samp
import pickle as pk
import numpy as np

def creat_yaml_file(file_path:str|Path, content:object,replace: bool=False) ->None:
    try:
        file_path=str(file_path)
        if replace and os.path.exists(file_path):
                os.remove(file_path)
        os.makedirs(os.path.dirname(file_path),exist_ok=True)

        with open(file_path,'w') as yaml_file:
            yaml.dump(content,yaml_file,default_flow_style=False)

    except Exception as e:
        raise CustomException(e)


def read_yaml_file(file_path:str|Path) -> dict:
    try:
        with open (file_path,'rb') as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise CustomException(e)


def validate_number_of_cols(file_path:str|Path,dataframe_path:DataFrame)->bool:
    try:
        schema=read_yaml_file(file_path)
        len_schema=len(schema)
        logging.info(f"Required number of cols:{len_schema}")
        logging.info(f"DataFrame has columns:{dataframe_path.columns}")
        if len(dataframe_path.columns)==len_schema:
            return True
        return False
    except Exception as e:
        raise CustomException(e)

def drift_check(drift_file_path,base_df,current_df,threshold=0.05)-> bool:
    try:
        status=True
        report={}
        for column in base_df.columns:
            d1=base_df[column].dropna()
            d2=current_df[column].dropna()

            is_sample_dist=ks_2samp(d1,d2)
            p_value=float(is_sample_dist.pvalue)

            drift_detected=p_value<threshold

            if drift_detected:
                status=False

            report[column]={
                "p_value":p_value,
                "drift_detected":bool(drift_detected)
                    }
        creat_yaml_file(drift_file_path,content=report,replace=True)
        logging.info(f"Drift report written to: {drift_file_path}")
        return status

    except Exception as e:
        raise CustomException(e)
    

def save_object(file_path:str|Path,obj):
    try:
        dir_path=Path(file_path).parent
        dir_path.mkdir(parents=True,exist_ok=True)

        with open(file_path,"wb") as file_obj:
            pk.dump(obj,file_obj)
    except Exception as e:
        raise CustomException(e)
    
def load_object(file_path:str|Path):
    try:
        with open(file_path,"rb") as file_obj:
          return pk.load (file_obj)
    except Exception as e:
        raise CustomException(e)
    
def save_numpy_array_data(file_path:str|Path,array: np.array):
    try:
        dir_path=Path(file_path).parent
        dir_path.mkdir(parents=True,exist_ok=True)

        with open(file_path,"wb") as file_obj:
            np.save(file_obj,array)
    except Exception as e:
        raise CustomException(e)
def load_numpy_array_data(file_path:str|Path):
    try:
        with open(file_path,"rb") as file_obj:
           return np.load (file_obj)
    except Exception as e:
        raise CustomException(e)