import glob
from hashlib import sha384
import os
from pathlib import Path
from openfl.utilities.verifdataset.data_source import DataSource, DataSourceType


class LocalDataSource(DataSource):
    def __init__(self, base_path: Path):
        super().__init__(DataSourceType.LOCAL)
        self.base_path = base_path
        self.base_path = self.base_path.resolve()  #TODO (efrat): Normalize path to an absolute path?
         
    # def __dict__(self):
    #     return {k: str(v) if isinstance(v, Path) else v for k, v in self.__dict__.items() if not callable(v)}
 
    def enumerate_objects(self):
        """Walk through the data directory and collect all files."""
        dataset_files = []
        relative_path = []
        # maxDatasetSize = kwargs.get("maxDatasetSize", 0)  # TODO (efrat): add to the class attributes? maybe with default value
        maxDatasetSize = 1000000
        total_size_bytes = 0
        print("Calculating the total size of the dataset")
        if self.base_path.is_dir():
            dataset = self.base_path
            all_files_in_dir = list(dataset.glob("**/*.*"))
            
            relative_path += [file_path.relative_to(dataset).as_posix() for file_path in all_files_in_dir]
            dataset_files += all_files_in_dir
            if maxDatasetSize > 0:
                for file_path in all_files_in_dir:
                    total_size_bytes += file_path.stat().st_size
        elif self.base_path.is_file():
            dataset_files.append(self.base_path)
            relative_path.append(self.base_path.name)
            if maxDatasetSize > 0:
                total_size_bytes += self.base_path.stat().st_size
        else:
            raise ValueError(f"skip local dataset: {self.base_path} is not a valid file or directory")
        
        if maxDatasetSize > 0:
            total_size_gb = total_size_bytes / (1024 ** 3)
            print(f"Total dataset size is {total_size_gb:.2f} GB")
            print(f"Total dataset size is {total_size_bytes:.2f} Bytes")
            if total_size_gb > maxDatasetSize:
                raise ValueError(f"Total dataset size is {total_size_gb:.2f} GB exceeds {maxDatasetSize} GB.")  
            
        return dataset_files
        # return dataset_files, relative_path

    def compute_object_hash(self, file_path: str) -> str:
        """Compute the hash of the file. Return hash on hexstring format."""
        hash_obj = sha384()  # TODO (efrat): should be input to class?
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                hash_obj.update(byte_block)
            return hash_obj.hexdigest()

    @classmethod
    def from_dict(cls, ds_dict: dict):
        return cls(base_path=Path(ds_dict['base_path']))