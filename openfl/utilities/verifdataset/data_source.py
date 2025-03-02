# Base class for different types of data sources
from abc import ABC, abstractmethod
from enum import Enum
# from typing import List

class DataSourceType(Enum):
    LOCAL = "local"
    S3 = "s3"

class DataSource(ABC):
    """
    Base class for different types of data sources.
  
    Attributes:
        storage_type (str): The storage type of the data source (e.g., "local", "s3", etc.)
    """
    def __init__(self, datasource_type: DataSourceType):
        """
        Initialize a DataSource.
  
        Args:
            datasource_type (DataSourceType): The storage type of the data source.
        """
        self.datasource_type = datasource_type
     
    @abstractmethod
    def compute_object_hash(self, file_path: str) -> str:
        """
        Compute the hash of the object or file.
  
        Args:
            file_path (str): Path to the file.
  
        Returns:
            str: The file's hash.
        """
        pass
 
    # @abstractmethod
    # def determine_mount_point(self) -> str:
    #     """
    #     Determine the mount point for accessing data.
  
    #     Returns:
    #         str: The mount point path.
    #     """
    #     pass
      
    @abstractmethod
    def enumerate_objects(self):
        """
        Enumerate all files in the data source.
  
        Returns:
            list: A list of objects.
        """
        yield
 
    @classmethod
    @abstractmethod
    def from_dict(cls, ds_dict: dict):
        """
        Create a DataSource from a dictionary. This method is used when deserializing a VerifiableDataset from JSON.
  
        Args:
            ds_dict (dict): The dictionary to convert.
  
        Returns:
            DataSource: The created DataSource.
        """
        pass