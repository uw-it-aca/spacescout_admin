from django.db import models


class QueuedSpace(models.Model):
    space_id = models.IntegerField(blank=True, null=True)
    json = models.TextField()
    q_etag = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=25, blank=True)
    last_modified = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return "%s (marked %s on %s)" % (self.space_id, self.status, self.last_modified)
