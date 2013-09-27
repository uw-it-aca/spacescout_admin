from django.db import models
from django.core.urlresolvers import reverse
from PIL import Image
import hashlib
from functools import wraps


class Space(models.Model):
    """ Spaces are Spots
    """
    spot_id = models.SmallIntegerField(unique=True, null=True)
    is_complete = models.NullBooleanField()
    manager = models.CharField(max_length=50, blank=True)
    modified_by = models.CharField(max_length=50, blank=True)
    modified_date = models.DateTimeField(auto_now=True, auto_now_add=True)
    pending = models.TextField(max_length=8192, null=True)

    def json_data_structure(self):
        return {
            'id': self.id,
            'manager': self.manager,
            'is_complete': self.is_complete,
            'modified_by': self.modified_by,
            'modified_date' : self.modified_date.isoformat()
        }


class SpaceImage(models.Model):
    """ An image of a Space. Multiple images can be associated
    with a Spot, and Spot objects have a 'Spot.spotimage_set'
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
            "creation_date": self.creation_date.isoformat(),
            "modification_date": self.modification_date.isoformat(),
            "upload_user": self.upload_user,
            "upload_application": self.upload_application,
            "thumbnail_root": reverse('spot-image-thumb', kwargs={'spot_id': self.spot.pk, 'image_id': self.pk}).rstrip('/'),
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

        if not img.format in SpotImage.CONTENT_TYPES:
            raise ValidationError('Not an accepted image format')

        self.content_type = SpotImage.CONTENT_TYPES[img.format]
        self.width, self.height = img.size

        super(SpotImage, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.image.delete(save=False)

        super(SpotImage, self).delete(*args, **kwargs)

    def rest_url(self):
        return reverse('spot-image', kwargs={'spot_id': self.spot.pk, 'image_id': self.pk})
