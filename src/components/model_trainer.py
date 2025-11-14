from src.logger_config.logger import logging
from src.exception_config.exception import CustomException
from src.components.data_transformation import DataTransformationConfig,DataTransform
import pandas as pd
import os
import sys
from pathlib import Path
import numpy as np
from dataclasses import dataclass
from src.utils.main_utils.calls_utils import load_numpy_array_data,save_object
from src.utils.ml_utils.ml_calls import train_evaluate_model
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier,AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

@dataclass

class Modelconfig:
    final_model :Path= Path("final_model")
    model_path: Path=final_model/"model.pkl"

class Modelinitiation:
    def __init__(self):
        try:
            self.modelconfig=Modelconfig()
            self.trans_config=DataTransformationConfig()

            os.makedirs(self.modelconfig.final_model,exist_ok=True)
            #os.makedirs(self.modelconfig.model_path,exist_ok=True)


        except Exception as e:
            raise CustomException(e)
        
    
    def initiate_model_trainer(self):
        try:
            logging.info("Loading numpy files from transformed path")
            train_arr=load_numpy_array_data(self.trans_config.transformed_files/"train.npy")
            valid_arr=load_numpy_array_data(self.trans_config.transformed_files/"valid.npy")
            test_arr=load_numpy_array_data(self.trans_config.transformed_files/"test.npy")

            logging.info("resplitting the array in to X_train,y_train")

            X_train,y_train,X_valid,y_valid,X_test,y_test=(
                train_arr[:,:-1],
                train_arr[:,-1],
                valid_arr[:,:-1],
                valid_arr[:,-1],
                test_arr[:,:-1],
                test_arr[:,-1],
            )

            y_train = np.where(y_train == -1, 0, y_train)
            y_valid = np.where(y_valid == -1, 0, y_valid)
            y_test = np.where(y_test == -1, 0, y_test)

            return X_train,y_train,X_valid,y_valid,X_test,y_test


        except Exception as e:
            raise CustomException(e)
        
    def evaluate_train_model(self):
        X_train, y_train, X_valid, y_valid, X_test, y_test = self.initiate_model_trainer()
        models={
            "Random Forest":RandomForestClassifier(verbose=1),
            "Decision Tree": DecisionTreeClassifier(),
            "Gradient Boosting": GradientBoostingClassifier(verbose=1),
            "Logistic Regression": LogisticRegression(verbose=1),
            "Adaboost":AdaBoostClassifier(),
            "Xgboost":XGBClassifier()
        }

        param_grid={
            "Random Forest":{
                'n_estimators':[8,16,32,64,128,256],
                'max_features':['sqrt', 'log2'],
            },
            "Decision Tree":{
                'criterion':['gini', 'entropy', 'log_loss']
            },
            "Gradient Boosting":{
                'learning_rate':[.1,.01,.05,.001],
                'subsample':[0,6,0.7,0.75,0.85,0.9],
                'n_estimators':[8,16,32,64,128,256]
            },
            "Logistic Regression":{},
            "Adaboost":{
                'learning_rate':[.1,.01,.05,.001],
                'n_estimators':[8,16,32,64,128,256]
            },
            "Xgboost":
            {
                'n_estimators':[8,16,32,64,128,256],
                'learning_rate':[.1,.01,.05,.001],
                'booster':['gbtree', 'gblinear', 'dart']
            }


        }

        df=train_evaluate_model(models=models,X_train=X_train,y_train=y_train,
                                X_valid=X_valid,y_valid=y_valid,X_test=X_test,y_test=y_test,
                                param_grid=param_grid)
        #result_df=df.reset_index()
        #result_df.columns=["Model", "Dataset", "f1", "recall", "precision"]
        test_df=df[df['Dataset']=="Test"]

        best_row = test_df.iloc[0]
        best_model_name=best_row["Model"]
        best_model_score=best_row['f1']
        best_model=models[best_model_name]

        if best_model_score < 0.6:
            raise CustomException("No best model found")
        
        logging.info(f"Best model is {best_model_name}")
        
        save_object(self.modelconfig.model_path,best_model)

        return best_model_name,best_model_score,best_model