from src.logger_config.logger import logging
from src.exception_config.exception import CustomException
from src.components.data_validation import DatavalidationConfig
import pandas as pd
import os
import sys
from pathlib import Path
import numpy as np
from sklearn.impute import SimpleImputer,KNNImputer
from sklearn.preprocessing import StandardScaler,RobustScaler
from dataclasses import dataclass
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from src.utils.main_utils.calls_utils import save_object,save_numpy_array_data

@dataclass

class DataTransformationConfig:
    artifact_dir :Path= Path("artifacts")
    final_model :Path=Path("final_model")
    data_transformation_dir:Path= artifact_dir/"data_transformation"
    transformed_object:Path= data_transformation_dir/"transformed"
    transformed_files= data_transformation_dir/"transformedfiles"
    preprocessing_path: Path=transformed_object/"preprocess.pkl"
    final_preprocessing_path: Path=final_model/"preprocess.pkl"

class DataTransform:
    def __init__(self):
        try:
            self.trans_config=DataTransformationConfig()
            self.config=DatavalidationConfig()
            os.makedirs(self.trans_config.artifact_dir,exist_ok=True)
            os.makedirs(self.trans_config.final_model,exist_ok=True)
            os.makedirs(self.trans_config.data_transformation_dir,exist_ok=True)
            os.makedirs(self.trans_config.transformed_object,exist_ok=True)
            os.makedirs(self.trans_config.transformed_files,exist_ok=True)
        except Exception as e:
            raise CustomException(e)
        
    def get_col_preprocess(self):
        try:
            df=pd.read_csv(self.config.train_validated)
            logging.info(f"Loaded train data from {self.config.validated_file} successfully")
            cat_cols=df.select_dtypes(include='O').columns.to_list()
            numeric_cols=df.select_dtypes(exclude='O').drop(columns='Result').columns.to_list()
            logging.info(f"Columns have been split into cat_cols: {cat_cols} and numeric_cols: {numeric_cols}")

            num_transform=make_pipeline(KNNImputer(missing_values=np.nan,n_neighbors=3,weights='uniform'),StandardScaler())
            cat_transform=make_pipeline(SimpleImputer(strategy='constant'),StandardScaler())

            feature_transformer=ColumnTransformer(
                transformers=[
                    ('num',num_transform,numeric_cols),
                    ('cat',cat_transform,cat_cols)
                ]
            )

            return feature_transformer

        except Exception as e:
            raise CustomException(e)
        
    def trans_initiate(self,train_path,valid_path,test_path):
        try:
            df_train=pd.read_csv(train_path)
            df_valid=pd.read_csv(valid_path)
            df_test=pd.read_csv(test_path)

            preproccessor=self.get_col_preprocess()

            X_train=df_train.drop(columns=['Result'],axis=1)
            y_train=df_train['Result']

            X_valid=df_valid.drop(columns=['Result'],axis=1)
            y_valid=df_valid['Result']

            X_test=df_test.drop(columns=['Result'],axis=1)
            y_test=df_test['Result']

            logging.info("Applying preprocessing object on datasets")

            X_train=preproccessor.fit_transform(X_train)
            X_valid=preproccessor.transform(X_valid)
            X_test=preproccessor.transform(X_test)

            """train_combined= pd.concat([
                pd.DataFrame(X_train,columns=preproccessor.get_feature_names_out()),y_train.reset_index(drop=True)
            ])
            valid_combined= pd.concat([
                pd.DataFrame(X_valid,columns=preproccessor.get_feature_names_out()),y_valid.reset_index(drop=True)
            ])
            test_combined= pd.concat([
                pd.DataFrame(X_test,columns=preproccessor.get_feature_names_out()),y_test.reset_index(drop=True)
            ])"""

            train_trans=np.concatenate((X_train,np.array(y_train).reshape(-1,1)),axis=1)
            valid_trans=np.concatenate((X_valid,np.array(y_valid).reshape(-1,1)),axis=1)
            test_trans=np.concatenate((X_test,np.array(y_test).reshape(-1,1)),axis=1)

            #train_combined.to_csv(self.trans_config.transformed_files/'trans_train.csv',index=False,header=True)
            #valid_combined.to_csv(self.trans_config.transformed_files/'trans_valid.csv',index=False,header=True)
            #test_combined.to_csv(self.trans_config.transformed_files/'trans_test.csv ',index=False,header=True)
            save_numpy_array_data(self.trans_config.transformed_files/"train.npy",array=train_trans)
            save_numpy_array_data(self.trans_config.transformed_files/"valid.npy",array=valid_trans)
            save_numpy_array_data(self.trans_config.transformed_files/"test.npy",array=test_trans)



            save_object(file_path=self.trans_config.preprocessing_path,obj=preproccessor)
            save_object(file_path=self.trans_config.final_preprocessing_path,obj=preproccessor)

            return(train_trans,valid_trans,test_trans,self.trans_config.preprocessing_path)




        except Exception as e:
            raise CustomException(e)




