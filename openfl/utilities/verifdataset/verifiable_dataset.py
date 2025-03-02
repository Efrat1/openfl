from enum import Enum
from hashlib import sha384
import json
from pathlib import Path
from typing import List
import uuid

from openfl.utilities.verifdataset.data_source import DataSource, DataSourceType
from openfl.utilities.verifdataset.local_data_source import LocalDataSource

class DatasetFormat(Enum):
    VERBOSE = "verbose_dataset"
    CONCISE = "concise_dataset"
 
class VerifiableDataset:
    def __init__(self, data_sources: List[DataSource], label: str, dataset_format: DatasetFormat):
        self.data_sources = data_sources
        self.label = label
        self.metadata = dict()
        # if mount_points:
        #     self.mount_points = mount_points
        # else:
        #     self.mount_points = [ds.compute_mount_point() for ds in data_sources]
        self.dataset_format = dataset_format
        # self.hash = self.create_dataset_hash()
        # if hash != checksum:
        #     raise ValueError("Checksum does not match the hash of the dataset")
 
    def _create_verbose_dataset_hash(self):
        # all_file_hashes = (ds.compute_object_hash(file) for ds in self.data_sources for file in ds.enumerate_objects())
        all_file_hashes = {
            str(file_path): ds.compute_object_hash(file_path)
            for ds in self.data_sources
            for file_path in ds.enumerate_objects()
        }
        # TODO (efrat): does it make sense to save hash_of_abs_path->abs_path ?
        return all_file_hashes
    
    def _create_concise_dataset_hash(self):
        all_file_hashes = (ds.compute_object_hash(file) for ds in self.data_sources for file in ds.enumerate_objects())
        sorted_file_hashes = sorted(all_file_hashes)
        joined_hashes = ''.join(sorted_file_hashes)
        return sha384(joined_hashes.encode()).hexdigest()
    
    def create_dataset_hash(self):
        if self.dataset_format == DatasetFormat.VERBOSE:
            return self._create_verbose_dataset_hash()
        elif self.dataset_format == DatasetFormat.CONCISE:
            return self._create_concise_dataset_hash()
        else:
            raise ValueError("Unknown dataset format")

    def _validate_verbose_dataset_info(self, dataset_info):
        hashes = self._create_verbose_dataset_hash()
        # print(f"hashes: {hashes}")
        # print(f"dataset_info['hashes']: {dataset_info['hashes']}")
        return hashes == dataset_info['hash']
    
    def _validate_concise_dataset_info(self, dataset_info):
        hash = self._create_concise_dataset_hash()
        return hash == dataset_info['hash']    

    def verify_dataset(self, dataset_info):
        if self.dataset_format == DatasetFormat.VERBOSE:
            return self._validate_verbose_dataset_info(dataset_info)
        elif self.dataset_format == DatasetFormat.CONCISE:
            return self._validate_concise_dataset_info(dataset_info)
        else:
            raise ValueError("Unknown dataset format")
 
    def verify_file_verbose(self, file_path, hash):
        if self.dataset_format != DatasetFormat.VERBOSE:
            raise ValueError("This method is only valid for verbose datasets")
        all_hashes = self.create_dataset_hash()
        if file_path not in all_hashes:
            return False
        return all_hashes[file_path] == hash

    def filter_non_serializable(self, obj):
        """Filter out methods and non-serializable objects."""
        serializable_dict = {}
        for k, v in obj.__dict__.items():
            if callable(v):
                continue  # Skip methods
            if isinstance(v, Enum):
                v = v.value  # Convert Enum to its value (string or int)
            elif isinstance(v, Path):
                v = str(v)  # Convert Path to string
            serializable_dict[k] = v
        return serializable_dict

    def to_json(self):
        """Serialize the VerifiableDataset to JSON"""
        dataset_dict = {
            'data_sources': [self.filter_non_serializable(ds) for ds in self.data_sources],
            # 'mount_points': self.mount_points,
            'label': self.label,
            'format': self.dataset_format.value,
        }
        dataset_dict['hash'] = self.create_dataset_hash()
        # if self.dataset_format == DatasetFormat.VERBOSE:
        #     dataset_dict['hashes'] = self.create_dataset_hash()
        # elif self.dataset_format == DatasetFormat.CONCISE:
        #     dataset_dict['hash'] = self.create_dataset_hash()
        return json.dumps(dataset_dict, sort_keys=True, indent=4)
 
    @staticmethod
    def from_dict(data_dict):
        """Deserialize the VerifiableDataset from JSON"""
 
        # Create appropriate data source based on dictionary information
        data_sources = []
        for ds in data_dict['data_sources']:
            if ds['datasource_type'] == DataSourceType.LOCAL.value:
                data_source = LocalDataSource.from_dict(ds_dict=ds)
            # elif ds['datasource_type'] == DataSourceType.S3.value:
            #     data_source = S3DataSource.from_dict(ds_dict=ds)
            else:
                raise ValueError(f"Unknown storage type: {ds['datasource_type']}")
            data_sources.append(data_source)
 
        # mount_points = data_dict['mount_points']
        return VerifiableDataset(data_sources, data_dict['label'], DatasetFormat(data_dict['format']))
    
    @staticmethod
    def validate_dataset(json_str):
        data_dict = json.loads(json_str)
        vds = VerifiableDataset.from_dict(data_dict)
        return vds.verify_dataset(data_dict)

        