from census.logger import logging
from census.exception import CensusException
from census.entity.entity_config import DataIngestionConfig
import sys,os
import pandas as pd
from census.entity.artifact_entity import DataIngestionArtifact
from sklearn.model_selection import StratifiedShuffleSplit
import numpy as np
import tarfile # extract zip files
from six.moves import urllib
import pandas as pd



class DataIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try:
            logging.info(f"{'>>'*20}Data Ingestion log started.{'<<'*20} ")
            self.data_ingestion_config=data_ingestion_config
        except Exception as e:
            raise CensusException(e,sys) from e


    def download_census_data(self,) -> str:
        try:
            #extraction remote url to download dataset
            download_url = self.data_ingestion_config.dataset_download_url

            #folder location to download file
            tgz_download_dir = self.data_ingestion_config.tgz_download_dir
            
            if os.path.exists(tgz_download_dir):
                os.remove(tgz_download_dir)

            os.makedirs(tgz_download_dir,exist_ok=True)

            census_file_name = os.path.basename(download_url)

            tgz_file_path = os.path.join(tgz_download_dir, census_file_name)

            logging.info(f"Downloading file from :[{download_url}] into :[{tgz_file_path}]")
            urllib.request.urlretrieve(download_url, tgz_file_path)
            logging.info(f"File :[{tgz_file_path}] has been downloaded successfully.")
            return tgz_file_path

        except Exception as e:
            raise CensusException(e,sys) from e

    def extract_tgz_file(self,tgz_file_path:str):
        try:
            raw_data_dir = self.data_ingestion_config.raw_data_dir

            if os.path.exists(raw_data_dir):
                os.remove(raw_data_dir)

            os.makedirs(raw_data_dir,exist_ok=True)

            logging.info(f"Extracting tgz file: [{tgz_file_path}] into dir: [{raw_data_dir}]")
            with tarfile.open(tgz_file_path) as census_tgz_file_obj:
                
                import os
                
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(census_tgz_file_obj, path=raw_data_dir)
            logging.info(f"Extraction completed")

        except Exception as e:
            raise CensusException(e,sys) from e
        
    def split_data_as_train_test(self) -> DataIngestionArtifact:
        try:
            raw_data_dir = self.data_ingestion_config.raw_data_dir

            file_name = os.listdir(raw_data_dir)[0]

            census_file_path = os.path.join(raw_data_dir,file_name)


            logging.info(f"Reading csv file: [{census_file_path}]")
            census_data_frame = pd.read_csv(census_file_path)

            census_data_frame["age_add"] = pd.cut(
                census_data_frame["age"],
                bins=[17.0, 24.3, 31.6, 38.9, 46.2,53.5,60.8,58.1,75.4,82.7, np.inf],
                labels=[1,2,3,4,5,6,7,8,9]
            )
            

            logging.info(f"Splitting data into train and test")
            strat_train_set = None
            strat_test_set = None

            split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)

            for train_index,test_index in split.split(census_data_frame, census_data_frame["age_add"]):
                strat_train_set = census_data_frame.loc[train_index].drop(["age_add"],axis=1)
                strat_test_set = census_data_frame.loc[test_index].drop(["age_add"],axis=1)

            train_file_path = os.path.join(self.data_ingestion_config.ingested_train_dir,
                                            file_name)

            test_file_path = os.path.join(self.data_ingestion_config.ingested_test_dir,
                                        file_name)
            
            if strat_train_set is not None:
                os.makedirs(self.data_ingestion_config.ingested_train_dir,exist_ok=True)
                logging.info(f"Exporting training datset to file: [{train_file_path}]")
                strat_train_set.to_csv(train_file_path,index=False)

            if strat_test_set is not None:
                os.makedirs(self.data_ingestion_config.ingested_test_dir, exist_ok= True)
                logging.info(f"Exporting test dataset to file: [{test_file_path}]")
                strat_test_set.to_csv(test_file_path,index=False)
            

            data_ingestion_artifact = DataIngestionArtifact(train_file_path=train_file_path,
                                test_file_path=test_file_path,
                                is_ingested=True,
                                message=f"Data ingestion completed successfully."
                                )
            logging.info(f"Data Ingestion artifact:[{data_ingestion_artifact}]")
            return data_ingestion_artifact

        except Exception as e:
            raise CensusException(e,sys) from e
    def initiate_data_ingestion(self)->DataIngestionArtifact:
        try:
            tgz_file_path =  self.download_income_prediction_data()
            self.extract_tgz_file(tgz_file_path=tgz_file_path)
            return self.split_data_as_train_test()
        except Exception as e:
            raise CensusException(e,sys) from e

    def __del__(self):
        logging.info(f"{'='*20}Data Ingestion log completed.{'='*20} \n\n")