from Network_Security.components.data_ingestion import DataIngestion
from Network_Security.components.data_validation import DataValidation
from Network_Security.components.data_tranformation import DataTransformation
from Network_Security.components.model_trainer import ModelTrainer

from Network_Security.exception.exception import NetworkSecurityException
from Network_Security.logging.logger import logging
from Network_Security.entity.config_entity import DataIngestionConfig  , DataValidationConfig, DataTransformationConfig , ModelTrainerConfig
from Network_Security.entity.config_entity import TrainingPipelineConfig

import sys

if __name__=="__main__":
    try:
        training=TrainingPipelineConfig()
        dataingestionconfig=DataIngestionConfig(training)
        data_ingestion=DataIngestion(dataingestionconfig)
        logging.info("Initiating the data ingestion")
        data_ingestion_artifact=data_ingestion.initiate_data_ingestion() 
        print(data_ingestion_artifact)
        data_validation_config=DataValidationConfig(training)
        data_validation=DataValidation(data_ingestion_artifact , data_validation_config)
        logging.info("Initiating the data validation")
        data_validation_artifacts=data_validation.initiate_data_validation()
        logging.info("data validation done")
        logging.info("Initiating the data tranformation")

        data_tranformation_config=DataTransformationConfig(training)
        data_transformation=DataTransformation(data_validation_artifacts, data_tranformation_config)
        data_transformation_artifact=data_transformation.initiate_data_transformation()
        logging.info("data tranformation done")
        print(data_transformation_artifact)

        logging.info("Model Training sstared")
        model_trainer_config=ModelTrainerConfig(training)
        model_trainer=ModelTrainer(model_trainer_config=model_trainer_config,data_transformation_artifact=data_transformation_artifact)
        model_trainer_artifact=model_trainer.initiate_model_trainer()

        logging.info("Model Training artifact created")

    except Exception as e:
        raise NetworkSecurityException(e,sys)


        
