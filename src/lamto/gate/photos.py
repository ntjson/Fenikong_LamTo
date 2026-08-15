import uuid

from django.core.files.base import File
from django.core.files.storage import storages

from .models import PhotoDeletion

PREFIX = "gate/pending-enrollment"


class PhotoVersionMissing(RuntimeError):
    pass


def _is_s3(storage):
    return hasattr(storage, "bucket_name") and hasattr(storage, "connection")


def store_pending_photo(file_obj, content_type):
    storage = storages["private"]
    key = f"{PREFIX}/{uuid.uuid4().hex}"
    file_obj.seek(0)
    if _is_s3(storage):
        response = storage.connection.meta.client.put_object(
            Bucket=storage.bucket_name, Key=key, Body=file_obj, ContentType=content_type
        )
        version_id = response.get("VersionId")
        if not version_id:
            response = storage.connection.meta.client.list_object_versions(
                Bucket=storage.bucket_name, Prefix=key
            )
            versions = [
                item
                for group in ("Versions", "DeleteMarkers")
                for item in response.get(group, [])
                if item["Key"] == key
            ]
            for item in versions:
                storage.connection.meta.client.delete_object(
                    Bucket=storage.bucket_name, Key=key, VersionId=item["VersionId"]
                )
            if not versions:
                storage.connection.meta.client.delete_object(Bucket=storage.bucket_name, Key=key)
            raise PhotoVersionMissing("Versioned S3 storage did not return VersionId.")
        return key, version_id
    return storage.save(key, File(file_obj, name=key)), ""


def delete_pending_photo(storage_key, provider_version_id=""):
    if not storage_key:
        return
    storage = storages["private"]
    if _is_s3(storage):
        if not provider_version_id:
            raise PhotoVersionMissing("Refusing an unversioned S3 delete.")
        storage.connection.meta.client.delete_object(Bucket=storage.bucket_name, Key=storage_key, VersionId=provider_version_id)
    else:
        storage.delete(storage_key)


def queue_photo_deletion(photo):
    from django.db import transaction

    deletion = PhotoDeletion.objects.create(
        storage_key=photo.storage_key,
        provider_version_id=photo.provider_version_id,
    )
    photo.delete()
    transaction.on_commit(lambda: process_photo_deletion(deletion.pk))


def process_photo_deletion(deletion_id):
    deletion = PhotoDeletion.objects.filter(pk=deletion_id).first()
    if deletion is None:
        return True
    try:
        delete_pending_photo(deletion.storage_key, deletion.provider_version_id)
    except Exception:
        return False
    deletion.delete()
    return True


def process_photo_deletions():
    return sum(process_photo_deletion(pk) for pk in PhotoDeletion.objects.values_list("pk", flat=True))
