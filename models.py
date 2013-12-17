from django.db import models
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from PIL import Image
import hashlib
from functools import wraps


class Space(models.Model):
    """ Spaces are Spots
    """
    spot_id = models.SmallIntegerField(unique=True, null=True)
    is_complete = models.NullBooleanField()
    is_pending_publication = models.NullBooleanField()
    manager = models.CharField(max_length=50, blank=True)
    modified_by = models.CharField(max_length=50, blank=True)
    modified_date = models.DateTimeField(auto_now=True, auto_now_add=True)
    pending = models.TextField(max_length=8192, null=True)

    def __unicode__(self):
        return u"id {0}".format(self.spot_id)

    def json_data_structure(self):
        return {
            'id': self.id,
            'manager': self.manager,
            'is_complete': self.is_complete,
            'is_published': self.pending and len(self.pending) != 0,
            'is_pending_publication': self.is_pending_publication,
            'modified_by': self.modified_by,
            'modified_date' : self.modified_date.isoformat()
        }


class SpotImageLink(models.Model):
    """ Images associated with a space or spot
    """
    space = models.ForeignKey(Space)
    spot_id = models.SmallIntegerField()
    image_id = models.SmallIntegerField(unique=True)
    is_deleted = models.NullBooleanField()
    display_index = models.PositiveIntegerField(null=True)


class SpaceImage(models.Model):
    """ An image of a Space. Multiple images can be associated
    with a Space, and Space objects have a 'Space.spotimage_set'
    method that will return all SpotImage objects for the Spot.
    """
    CONTENT_TYPES = {
        "JPEG": "image/jpeg",
        "GIF": "image/gif",
        "PNG": "image/png",
    }

    description = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to="space_images")
    space = models.ForeignKey(Space)
    content_type = models.CharField(max_length=40)
    width = models.IntegerField()
    height = models.IntegerField()
    display_index = models.SmallIntegerField()
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
    upload_user = models.CharField(max_length=40)
    upload_application = models.CharField(max_length=100)

    def __unicode__(self):
        if self.description:
            return "%s" % self.description
        else:
            return "%s" % self.image.name

    def json_data_structure(self):
        return {
            "id": self.pk,
            "url": self.rest_url(),
            "content-type": self.content_type,
            "width": self.width,
            "height": self.height,
            "display_index": self.display_index,
            "creation_date": self.creation_date.isoformat(),
            "modification_date": self.modification_date.isoformat(),
            "upload_user": self.upload_user,
            "upload_application": self.upload_application,
            "description": self.description
        }

    def save(self, *args, **kwargs):
        try:
            if isinstance(self.image, UploadedFile) and self.image.file.multiple_chunks():
                img = Image.open(self.image.file.temporary_file_path())
            else:
                img = Image.open(self.image)
        except:
            raise ValidationError('Not a valid image format')

        if not img.format in SpaceImage.CONTENT_TYPES:
            raise ValidationError('Not an accepted image format')

        self.content_type = SpaceImage.CONTENT_TYPES[img.format]
        self.width, self.height = img.size

        super(SpaceImage, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.image.delete(save=False)

        super(SpaceImage, self).delete(*args, **kwargs)

    def rest_url(self):
        return reverse('space-image', kwargs={'space_id': self.space.pk, 'image_id': self.pk})
