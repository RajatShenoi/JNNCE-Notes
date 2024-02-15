from io import BytesIO
import uuid
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobClient
from django.conf import settings

from notes.exceptions import NotAllowedExtenstionError, UploadBlobError

from .models import File

ALLOWED_EXTENTIONS = ['.pdf']

def create_blob_client(file_name):

    default_credential = DefaultAzureCredential()

    secret_client = SecretClient(
        vault_url=settings.AZURE_VAULT_ACCOUNT, credential=default_credential
    )

    storage_credentials = secret_client.get_secret(name=settings.AZURE_STORAGE_KEY_NAME)

    return BlobClient(
        account_url=settings.AZURE_STORAGE_ACCOUNT,
        container_name=settings.AZURE_APP_BLOB_NAME,
        blob_name=file_name,
        credential=storage_credentials.value,
    )

def check_file_ext(path):
    ext = Path(path).suffix
    return ext in ALLOWED_EXTENTIONS

def download_blob(file):
    blob_client = create_blob_client(file)
    if not blob_client.exists():
        return
    blob_content = blob_client.download_blob()
    return blob_content

def delete_blob(file):
    blob_client = create_blob_client(file)
    if not blob_client.exists():
        return
    blob_client.delete_blob()

def save_file_url_to_db(file_url, display_name, ext, user, course_module):
    new_file = File.objects.create(
        user=user,
        file_url=file_url,
        file_name=display_name,
        file_extension=ext,
        course_module=course_module,
    )
    new_file.save()
    return new_file

def upload_file_to_blob(file, display_name, user, course_module):

    if not check_file_ext(file.name):
        raise NotAllowedExtenstionError

    file_prefix = uuid.uuid4().hex
    ext = Path(file.name).suffix
    file_name = f"{file_prefix}{ext}"
    file_content = file.read()
    file_io = BytesIO(file_content)
    blob_client = create_blob_client(file_name=file_name)
    d = blob_client.upload_blob(data=file_io)
    try:
        _ = d['etag']
    except KeyError:
        raise UploadBlobError
    file_object = save_file_url_to_db(blob_client.url, display_name, ext, user, course_module)
    return file_object