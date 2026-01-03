from src.logger_config.logger import logging
from src.exception_config.exception import CustomException
from src.components.data_extraction import DataExtraction
from src.components.data_ingestion import DataIngestionConfig,DataIngest
from src.components.data_validation import DatavalidationConfig,DataValidation
from src.components.data_transformation import DataTransform,DataTransformationConfig
from src.components.model_trainer import Modelconfig,Modelinitiation
from src.cloud.s3_syncer import S3Sync
from pathlib import Path
from dotenv import load_dotenv
import os
load_dotenv()


class train_pipe():
    def __init__(self):
        self.artifact_dir :Path= Path("artifacts")
        self.final_dir :Path=Path("final_model")
        self.aws_bucket_name=os.getenv("AWS_BUCKET_NAME")
        self.S3_sync=S3Sync()

    def start_ingest(self):
        try:
            logging.info("Starting Data Ingestion Pipeline...")

            ingest=DataIngest()
            df=ingest.fetch_df_from_Mongo()
            train_set,valid_set,test_set=ingest.split_data(df)
            return train_set,valid_set,test_set
        except Exception as e:
            raise CustomException(e)
        
    def start_validation(self):
        try:
    
            validation_config=DatavalidationConfig()
            validation=DataValidation()
            validation.create_data_schema(validation_config.raw_csv_dir)
            validation.initiate_data_validation()

            logging.info("Data ingestion and validation pipeline completed successfully.")

            return validation_config
        except Exception as e:
            raise CustomException(e)

    def start_transformation(self):
        try:
            validation_config=self.start_validation()
            logging.info("Starting Data Transformation Pipeline...")

            transform=DataTransform()
            transform.get_col_preprocess()
            train_trans,valid_trans,test_trans,processor_path=transform.trans_initiate(validation_config.train_validated,
                                                                                        validation_config.valid_validated,
                                                                                        validation_config.test_validated )
            logging.info("Data Transformation Pipeline Completed...")
            return  train_trans,valid_trans,test_trans,processor_path
        except Exception as e:
            raise CustomException(e)

    def start_model_trainer(self):
        try:
            model_trainer=Modelinitiation()
            best_model_name, best_model_score, best_model = model_trainer.evaluate_train_model()
            logging.info(f"✅ Training complete. Best model: {best_model_name} (F1: {best_model_score:.4f})")
            logging.info(f"✅ Training complete. Best model: {best_model} )")
            return best_model_name, best_model_score, best_model
        except Exception as e:
            raise CustomException(e)
        
    def sync_artifact_dir_to_s3(self):
        try:
            from datetime import datetime
            timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
            aws_bucket_url=f"s3://{self.aws_bucket_name}/artifact/{timestamp}"
            self.S3_sync.sync_folder_to_s3(self.artifact_dir,aws_bucket_url)

        except Exception as e:
            raise CustomException(e)
        
    def sync_model_dir_to_s3(self):
        try:
            from datetime import datetime
            timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
            aws_bucket_url=f"s3://{self.aws_bucket_name}/final_model/{timestamp}"
            self.S3_sync.sync_folder_to_s3(self.final_dir,aws_bucket_url)

        except Exception as e:
            raise CustomException(e)

        
    def run_pipeline(self):
        try:
            self.start_ingest()
            self.start_validation()
            self.start_transformation()
            self.start_model_trainer()
            self.sync_artifact_dir_to_s3()
            self.sync_model_dir_to_s3()
            logging.info("Full pipeline run completed successfully.")
        except Exception as e:
            raise CustomException(e)
