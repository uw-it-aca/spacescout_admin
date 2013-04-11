from django.contrib.auth.models import User
from django.db import models
from django.core.cache import cache
import hashlib
import time
import random


class QueuedSpace(models.Model):
    """ Stores space json for possible further editing before being sent to the server.
        q_etag should update on every save so conflicts can be checked for in queued items.
    """
    space_id = models.IntegerField(blank=True, null=True)
    json = models.TextField()
    errors = models.TextField(blank=True)
    space_etag = models.CharField(max_length=40, blank=True)
    q_etag = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=25, blank=True)
    space_last_modified = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True)
    last_modified = models.DateTimeField(auto_now=True, auto_now_add=True)
    modified_by = models.ForeignKey(User, blank=True, null=True, related_name='modified_by')
    approved_by = models.ForeignKey(User, blank=True, null=True, related_name='approved_by')

    def __unicode__(self):
        return "id: %s (marked %s on %s by %s)" % (self.space_id, self.status, self.last_modified, self.modified_by)

    def save(self, *args, **kwargs):
        if cache.get(self.pk):
            cache.delete(self.pk)
        self.q_etag = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()
        super(QueuedSpace, self).save(*args, **kwargs)
