from src.logger_config.logger import logging
from src.exception_config.exception import CustomException
from src.components.data_extraction import DataExtraction
from src.components.data_ingestion import DataIngestionConfig,DataIngest
from dotenv import load_dotenv
load_dotenv()

if __name__=="__main__":
    try:
        logging.info("Starting Data Ingestion Pipeline...")

        ingest=DataIngest()
        df=ingest.fetch_df_from_Mongo()
        train_set,valid_set,test_set=ingest.split_data(df)

        logging.info("Data ingestion pipeline completed successfully.")
    except Exception as e:
        raise CustomException(e)

    


    


