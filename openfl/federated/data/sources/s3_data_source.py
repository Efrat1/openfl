# Copyright 2020-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from typing import Generator
from urllib.parse import urlparse

import boto3

from openfl.federated.data.sources.data_source import DataSource, DataSourceType


class S3DataSource(DataSource):
    """Class for S3 data"""

    def __init__(
        self,
        uri: str,
        endpoint=None,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        hash_func=None,
    ):
        super().__init__(DataSourceType.S3)
        self.uri = uri
        self.endpoint = endpoint
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.hash_func = hash_func

    def enumerate_files(self) -> Generator[str, None, None]:
        """Enumerate all files in the data source"""
        parsed = urlparse(self.uri)
        bucket_name = parsed.netloc
        prefix = parsed.path.lstrip("/")  # Remove leading slash

        s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )

        paginator = s3_client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            if "Contents" in page:
                for obj in page["Contents"]:
                    full_s3_path = f"s3://{bucket_name}/{obj['Key']}"
                    yield full_s3_path

        # parsed = urlparse(self.uri)
        # bucket_name = parsed.netloc
        # prefix = parsed.path.lstrip('/')  # Remove leading slash

        # s3_client = boto3.client("s3", endpoint_url=self.endpoint)

        # continuation_token = None
        # while True:
        #     list_kwargs = {"Bucket": bucket_name, "Prefix": prefix}
        #     if continuation_token:
        #         list_kwargs["ContinuationToken"] = continuation_token

        #     response = s3_client.list_objects_v2(**list_kwargs)

        #     if "Contents" in response:
        #         for obj in response["Contents"]:
        #             yield f"s3://{bucket_name}/{obj['Key']}"

        #     if not response.get("IsTruncated"):  # No more files to list
        #         break

        #     continuation_token = response.get("NextContinuationToken")

    def _get_s3_etag(self, obj_path: str):
        parsed = urlparse(obj_path)
        bucket_name = parsed.netloc
        object_key = parsed.path.lstrip("/")

        s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )

        response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
        return response["ETag"]

    def _read_s3_object(self, obj_path: str):
        parsed = urlparse(obj_path)
        bucket_name = parsed.netloc
        object_key = parsed.path.lstrip("/")

        s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )

        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        return response["Body"].read()

    def compute_file_hash(self, path: str) -> str:
        if not self.hash_func:
            return self._get_s3_etag(path)
        else:
            data = self._read_s3_object(path)
            return self.hash_func(data).hexdigest()

    @classmethod
    def from_dict(cls, ds_dict: dict):
        return cls(uri=ds_dict["uri"], endpoint=ds_dict.get("endpoint", None))
