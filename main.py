from src.logger_config.logger import logging
from src.exception_config.exception import CustomException
from src.components.data_extraction import DataExtraction
from src.components.data_ingestion import DataIngestionConfig,DataIngest
from src.components.data_validation import DatavalidationConfig,DataValidation
from src.components.data_transformation import DataTransform,DataTransformationConfig
from dotenv import load_dotenv
load_dotenv()

if __name__=="__main__":
    try:
        logging.info("Starting Data Ingestion Pipeline...")

        ingest=DataIngest()
        df=ingest.fetch_df_from_Mongo()
        train_set,valid_set,test_set=ingest.split_data(df)
         
        validation_config=DatavalidationConfig()
        validation=DataValidation()
        validation.create_data_schema(validation_config.raw_csv_dir)
        validation.initiate_data_validation()

        logging.info("Data ingestion and validation pipeline completed successfully.")
    except Exception as e:
        raise CustomException(e)
    
    try:
        logging.info("Starting Data Transformation Pipeline...")

        transform=DataTransform()
        transform.get_col_preprocess()
        train_trans,valid_trans,test_trans,processor_path=transform.trans_initiate(validation_config.train_validated,
                                                                                   validation_config.valid_validated,
                                                                                   validation_config.test_validated )
                                                                                   



    except Exception as e:
        raise CustomException(e)


    


    


