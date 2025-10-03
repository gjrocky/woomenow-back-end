from storages.backends.s3boto3 import S3Boto3Storage, S3StaticStorage


class MediaStorage(S3StaticStorage):
    location = 'projects/woo_me_now/2025/media'
    file_overwrite = False
    default_acl = "public-read"  # Ensure files are public
    custom_domain = False

    @property
    def querystring_auth(self):
        return False

# class PublicMediaStorage(S3Boto3Storage):
#     location = 'projects/woo_me_now/2025/media/public'
#     file_overwrite = False
#     default_acl = "public-read"
#     custom_domain = False
#
#     @property
#     def querystring_auth(self):
#         return False


class StaticStorage(S3StaticStorage):
    location = 'projects/woo_me_now/2025/static'
    default_acl = "public-read"  # Ensure files are public
