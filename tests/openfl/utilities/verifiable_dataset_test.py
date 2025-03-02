import json
from openfl.utilities.verifdataset.local_data_source import LocalDataSource
from openfl.utilities.verifdataset.verifiable_dataset import DatasetFormat, VerifiableDataset
import pytest
import os
import shutil
import types
from pathlib import Path
from typing import Tuple

@pytest.fixture(scope="class")
def data_sources(tmp_path_factory) -> Tuple[Path, Path]:
    """Fixture to create two data sources with a file tree structure."""
    base_tmp = tmp_path_factory.mktemp("test_data")

    # Define datasource paths
    ds1 = base_tmp / "datasource1"
    ds2 = base_tmp / "datasource2"

    for ds in [ds1, ds2]:
        os.makedirs(ds / "1")
        os.makedirs(ds / "2")

        for subdir in ["1", "2"]:
            for i in range(1, 4):
                file_path = ds / subdir / f"file{i}.txt"
                with open(file_path, "w") as f:
                    f.write(f"Hello world! {ds.name} dir {subdir} file{i}\n")

    yield ds1, ds2  # Yield the paths to the test functions

    # Cleanup
    shutil.rmtree(base_tmp)


@pytest.mark.usefixtures("data_sources")
class TestVerifiableDataset:

    """ Concise tests """
    def test_one_local_datasource_concise(self, data_sources):
        ds1, _ = data_sources
        datasource = LocalDataSource(base_path=ds1)
        verifiable = VerifiableDataset(data_sources=[datasource], label="my_dataset", dataset_format=DatasetFormat.CONCISE)
        hash = verifiable.create_dataset_hash()
        assert isinstance(hash, str), f"Expected str, got {type(hash)}"
        verifaible_json = verifiable.to_json()
        print(f"verifaible_json: {verifaible_json}")
        assert VerifiableDataset.validate_dataset(verifaible_json)

    def test_two_local_datasource_concise(self, data_sources):
        ds1, ds2 = data_sources
        datasource1 = LocalDataSource(base_path=ds1)
        datasource2 = LocalDataSource(base_path=ds2)
        verifiable = VerifiableDataset(data_sources=[datasource1, datasource2], label="my_dataset", dataset_format=DatasetFormat.CONCISE)
        hash = verifiable.create_dataset_hash()
        assert isinstance(hash, str), f"Expected str, got {type(hash)}"
        verifaible_json = verifiable.to_json()
        print(f"verifaible_json: {verifaible_json}")
        assert VerifiableDataset.validate_dataset(verifaible_json)

    def test_one_local_datasource_one_folder_concise(self, data_sources):
        ds1, _ = data_sources
        datasource = LocalDataSource(base_path=ds1 / "1")
        verifiable = VerifiableDataset(data_sources=[datasource], label="my_dataset", dataset_format=DatasetFormat.CONCISE)
        hash = verifiable.create_dataset_hash()
        assert isinstance(hash, str), f"Expected str, got {type(hash)}"
        verifaible_json = verifiable.to_json()
        print(f"verifaible_json: {verifaible_json}")
        assert VerifiableDataset.validate_dataset(verifaible_json)

    def test_one_local_datasource_one_file_concise(self, data_sources):
        ds1, _ = data_sources
        datasource = LocalDataSource(base_path=ds1 / "1" / "file2.txt")
        verifiable = VerifiableDataset(data_sources=[datasource], label="my_dataset", dataset_format=DatasetFormat.CONCISE)
        hash = verifiable.create_dataset_hash()
        assert isinstance(hash, str), f"Expected str, got {type(hash)}"
        verifaible_json = verifiable.to_json()
        print(f"verifaible_json: {verifaible_json}")
        assert VerifiableDataset.validate_dataset(verifaible_json)

    def test_two_local_datasource_two_dirs_concise(self, data_sources):
        ds1, ds2 = data_sources
        datasource1 = LocalDataSource(base_path=ds1 / "1")
        datasource2 = LocalDataSource(base_path=ds2 / "1")
        verifiable = VerifiableDataset(data_sources=[datasource1, datasource2], label="my_dataset", dataset_format=DatasetFormat.CONCISE)
        hash = verifiable.create_dataset_hash()
        assert isinstance(hash, str), f"Expected str, got {type(hash)}"
        verifaible_json = verifiable.to_json()
        print(f"verifaible_json: {verifaible_json}")
        assert VerifiableDataset.validate_dataset(verifaible_json)

    def test_two_local_datasource_two_files_concise(self, data_sources):
        ds1, ds2 = data_sources
        datasource1 = LocalDataSource(base_path=ds1 / "1" / "file2.txt")
        datasource2 = LocalDataSource(base_path=ds2 / "1" / "file2.txt")
        verifiable = VerifiableDataset(data_sources=[datasource1, datasource2], label="my_dataset", dataset_format=DatasetFormat.CONCISE)
        hash = verifiable.create_dataset_hash()
        assert isinstance(hash, str), f"Expected str, got {type(hash)}"
        verifaible_json = verifiable.to_json()
        print(f"verifaible_json: {verifaible_json}")
        assert VerifiableDataset.validate_dataset(verifaible_json)
        
    def test_one_local_datasource_two_files_concise(self, data_sources):
        ds1, _ = data_sources
        datasource1 = LocalDataSource(base_path=ds1 / "1" / "file1.txt")
        datasource2 = LocalDataSource(base_path=ds1 / "1" / "file2.txt")
        verifiable = VerifiableDataset(data_sources=[datasource1, datasource2], label="my_dataset", dataset_format=DatasetFormat.CONCISE)
        hash = verifiable.create_dataset_hash()
        assert isinstance(hash, str), f"Expected str, got {type(hash)}"
        verifaible_json = verifiable.to_json()
        print(f"verifaible_json: {verifaible_json}")
        assert VerifiableDataset.validate_dataset(verifaible_json)

    """ Verbose tests """
    def test_one_local_datasource_verbose_verify_single_file(self, data_sources):
        ds1, _ = data_sources
        datasource = LocalDataSource(base_path=ds1)
        verifiable = VerifiableDataset(data_sources=[datasource], label="my_dataset", dataset_format=DatasetFormat.VERBOSE)
        hashes = verifiable.create_dataset_hash()
        assert isinstance(hashes, dict), f"Expected dict, got {type(hashes)}"
        verifaible_json = verifiable.to_json()
        verifiable = VerifiableDataset.from_dict(json.loads(verifaible_json))
        for file_path, hash in hashes.items():
            assert verifiable.verify_file_verbose(file_path, hash)

    def test_one_local_datasource_verbose(self, data_sources):
        ds1, _ = data_sources
        datasource = LocalDataSource(base_path=ds1)
        verifiable = VerifiableDataset(data_sources=[datasource], label="my_dataset", dataset_format=DatasetFormat.VERBOSE)
        hashes = verifiable.create_dataset_hash()
        assert isinstance(hashes, dict), f"Expected dict, got {type(hashes)}"
        verifaible_json = verifiable.to_json()
        print(f"verifaible_json: {verifaible_json}")
        assert VerifiableDataset.validate_dataset(verifaible_json)

    # def test_two_local_datasource_verbose(self, data_sources):
    #     ds1, ds2 = data_sources
    #     datasource1 = LocalDataSource(base_path=ds1)
    #     datasource2 = LocalDataSource(base_path=ds2)
    #     verifiable = VerifiableDataset(data_sources=[datasource1, datasource2], label="my_dataset", dataset_format=DatasetFormat.VERBOSE)
    #     hash = verifiable.create_dataset_hash()
    #     assert isinstance(hash, str), f"Expected str, got {type(hash)}"
    #     verifaible_json = verifiable.to_json()
    #     print(f"verifaible_json: {verifaible_json}")
    #     assert VerifiableDataset.validate_dataset(verifaible_json)

    # def test_one_local_datasource_one_folder_verbose(self, data_sources):
    #     ds1, _ = data_sources
    #     datasource = LocalDataSource(base_path=ds1 / "1")
    #     verifiable = VerifiableDataset(data_sources=[datasource], label="my_dataset", dataset_format=DatasetFormat.VERBOSE)
    #     hash = verifiable.create_dataset_hash()
    #     assert isinstance(hash, str), f"Expected str, got {type(hash)}"
    #     verifaible_json = verifiable.to_json()
    #     print(f"verifaible_json: {verifaible_json}")
    #     assert VerifiableDataset.validate_dataset(verifaible_json)

    # def test_one_local_datasource_one_file_verbose(self, data_sources):
    #     ds1, _ = data_sources
    #     datasource = LocalDataSource(base_path=ds1 / "1" / "file2.txt")
    #     verifiable = VerifiableDataset(data_sources=[datasource], label="my_dataset", dataset_format=DatasetFormat.VERBOSE)
    #     hash = verifiable.create_dataset_hash()
    #     assert isinstance(hash, str), f"Expected str, got {type(hash)}"
    #     verifaible_json = verifiable.to_json()
    #     print(f"verifaible_json: {verifaible_json}")
    #     assert VerifiableDataset.validate_dataset(verifaible_json)

    # def test_two_local_datasource_two_dirs_concise(self, data_sources):
    #     ds1, ds2 = data_sources
    #     datasource1 = LocalDataSource(base_path=ds1 / "1")
    #     datasource2 = LocalDataSource(base_path=ds2 / "1")
    #     verifiable = VerifiableDataset(data_sources=[datasource1, datasource2], label="my_dataset", dataset_format=DatasetFormat.VERBOSE)
    #     hash = verifiable.create_dataset_hash()
    #     assert isinstance(hash, str), f"Expected str, got {type(hash)}"
    #     verifaible_json = verifiable.to_json()
    #     print(f"verifaible_json: {verifaible_json}")
    #     assert VerifiableDataset.validate_dataset(verifaible_json)

    # def test_two_local_datasource_two_files_verbose(self, data_sources):
    #     ds1, ds2 = data_sources
    #     datasource1 = LocalDataSource(base_path=ds1 / "1" / "file2.txt")
    #     datasource2 = LocalDataSource(base_path=ds2 / "1" / "file2.txt")
    #     verifiable = VerifiableDataset(data_sources=[datasource1, datasource2], label="my_dataset", dataset_format=DatasetFormat.VERBOSE)
    #     hash = verifiable.create_dataset_hash()
    #     assert isinstance(hash, str), f"Expected str, got {type(hash)}"
    #     verifaible_json = verifiable.to_json()
    #     print(f"verifaible_json: {verifaible_json}")
    #     assert VerifiableDataset.validate_dataset(verifaible_json)
        
    # def test_one_local_datasource_two_files_verbose(self, data_sources):
    #     ds1, _ = data_sources
    #     datasource1 = LocalDataSource(base_path=ds1 / "1" / "file1.txt")
    #     datasource2 = LocalDataSource(base_path=ds1 / "1" / "file2.txt")
    #     verifiable = VerifiableDataset(data_sources=[datasource1, datasource2], label="my_dataset", dataset_format=DatasetFormat.VERBOSE)
    #     hash = verifiable.create_dataset_hash()
    #     assert isinstance(hash, str), f"Expected str, got {type(hash)}"
    #     verifaible_json = verifiable.to_json()
    #     print(f"verifaible_json: {verifaible_json}")
    #     assert VerifiableDataset.validate_dataset(verifaible_json)