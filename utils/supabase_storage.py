from storages.backends.s3boto3 import S3Boto3Storage
import uuid
import os


class SupabaseMediaStorage(S3Boto3Storage):
    file_overwrite = False

    def get_available_name(self, name, max_length=None):
        dir_name, file_name = os.path.split(name)
        _, file_ext = os.path.splitext(file_name)

        unique_name = f"{uuid.uuid4().hex}{file_ext}"

        if dir_name:
            return f"{dir_name}/{unique_name}"
        return unique_name

    def exists(self, name):
        return False