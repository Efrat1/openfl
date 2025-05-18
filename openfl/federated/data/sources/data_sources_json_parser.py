# Copyright 2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0


import json
import os
from pathlib import Path

from openfl.federated.data.sources.azure_blob_data_source import AzureBlobDataSource
from openfl.federated.data.sources.local_data_source import LocalDataSource
from openfl.federated.data.sources.s3_data_source import S3DataSource
from openfl.federated.data.sources.verifiable_dataset_info import VerifiableDatasetInfo


class DataSourcesJsonParser:
    @staticmethod
    def parse(json_string: str, label="", metadata="") -> VerifiableDatasetInfo:
        """
        Parse a JSON string into a dictionary.

        Args:
            json_string (str): The JSON string to parse.

        Returns:
            VerifiableDatasetInfo: An instance of VerifiableDatasetInfo containing
            the parsed data sources.
        """
        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

        datasources = DataSourcesJsonParser.process_data_sources(data)
        if not datasources:
            raise ValueError("No data sources were found.")
        return VerifiableDatasetInfo(
            data_sources=datasources,
            label=label,
            metadata=metadata,
        )

    @staticmethod
    def process_data_sources(data):
        """Process and validate data sources."""
        os.getcwd()
        datasources = []
        local_datasources = {}
        for source_name, source_info in data.items():
            source_type = source_info.get("type", None)
            if source_type is None:
                raise ValueError(f"Missing 'type' key in data source configuration: {source_info}")
            params = source_info.get("params", {})
            if source_type == "local":
                local_datasources[source_name] = params
            elif source_type == "s3":
                datasources.append(DataSourcesJsonParser.process_s3_source(source_name, params))
            elif source_type == "azure_blob":
                datasources.append(
                    DataSourcesJsonParser.process_azure_blob_source(source_name, params)
                )
        if local_datasources:
            DataSourcesJsonParser.process_local_sources(local_datasources, datasources)
        return [ds for ds in datasources if ds]

    def process_local_sources(local_datasources, datasources):
        """Process and validate local data sources."""
        # The reason we use common base_dir and source_path relative to that base
        # is to simplify path management in containerized environments, such as Docker.
        # By using a common base_dir, we can ensure that paths remain consistent
        # when mounting volumes, as only the base_dir needs to be adjusted to point
        # to the mount path inside the container.
        # This way, we only need to adjust the base_dir to point to the mount path.
        source_names, absolute_paths = zip(
            *[
                (source_name, os.path.realpath(params.get("path", None)))
                for source_name, params in local_datasources.items()
            ]
        )
        base_dir = os.path.commonpath(absolute_paths)
        for source_name, data_path in zip(source_names, absolute_paths):
            relative_path = os.path.relpath(data_path, base_dir)
            datasources.append(
                LocalDataSource(
                    name=source_name, source_path=Path(relative_path), base_path=base_dir
                )
            )

    @staticmethod
    def process_s3_source(source_name, params):
        """Process an S3 data source."""
        required_fields = ["uri", "access_key_env_name", "secret_key_env_name", "secret_name"]
        missing_fields = set(required_fields) - set(params.keys())
        if missing_fields:
            raise Exception(
                f"Missing required fields: {', '.join(missing_fields)} "
                f"for S3 data source '{source_name}'"
            )
        return S3DataSource(
            name=source_name,
            uri=params["uri"],
            endpoint=params.get("endpoint") or None,
            access_key_env_name=params["access_key_env_name"],
            secret_key_env_name=params["secret_key_env_name"],
            secret_name=params["secret_name"],
        )

    @staticmethod
    def process_azure_blob_source(source_name, params):
        """Process an Azure Blob data source."""
        required_fields = ["connection_string", "container_name"]
        missing_fields = set(required_fields) - set(params.keys())
        if missing_fields:
            raise Exception(
                f"Missing required fields: {', '.join(missing_fields)} "
                f"for Azure Blob data source '{source_name}'"
            )
        return AzureBlobDataSource(
            name=source_name,
            connection_string=params["connection_string"],
            container_name=params["container_name"],
            folder_prefix=params.get("folder_prefix") or "",
        )
