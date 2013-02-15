from django.contrib.auth.models import User
from django.db import models


class QueuedSpace(models.Model):
    """ Stores space json for possible further editing before being sent to the server.
        q_etag should update on every save so conflicts can be checked for in queued items.
    """
    space_id = models.IntegerField(blank=True, null=True)
    json = models.TextField()
    q_etag = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=25, blank=True)
    last_modified = models.DateTimeField(auto_now=True, auto_now_add=True)
    modified_by = models.ForeignKey(User, blank=True, null=True)
    approved_by = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return "id: %s (marked %s on %s by %s)" % (self.space_id, self.status, self.last_modified, self.modified_by)

    #TODO: put in an etag generator
