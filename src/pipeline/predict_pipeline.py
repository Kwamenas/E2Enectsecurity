from src.logger_config.logger import logging
from src.exception_config.exception import CustomException
from src.utils.main_utils.calls_utils import load_object
from dataclasses import dataclass
from pathlib import Path
import os

@dataclass
class PredictionConfig:
    """Configuration for prediction pipeline"""
    model_path: Path = Path("final_model/model.pkl")
    preprocessor_path: Path = Path("final_model/preprocess.pkl")

class PredictionPipeline:
    def __init__(self):
        try:
            self.config = PredictionConfig()
            self.model = load_object(self.config.model_path)
            self.preprocessor = load_object(self.config.preprocessor_path)
            logging.info("Successfully loaded objects")
        except Exception as e:
            raise CustomException(e)
    
    def predict(self, df):
        # preprocess/transform the data
        try:
            transformed_data = self.preprocessor.transform(df)
            ## make predictions
            predictions = self.model.predict(transformed_data)
            df_copy = df.copy()
            df_copy['Predicted_Results'] = predictions
            return df_copy
        except Exception as e:
            raise CustomException(e)