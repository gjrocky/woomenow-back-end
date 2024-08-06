from storages.backends.s3boto3 import S3Boto3Storage, S3StaticStorage


class MediaStorage(S3Boto3Storage):
    location = '2023/media'
    file_overwrite = False


class StaticStorage(S3StaticStorage):
    location = '2023/static'
