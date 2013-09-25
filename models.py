from django.db import models

# Create your models here.

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
            'spot_id' : self.spot_id,
            'is_complete': self.is_complete,
            'modified_by': self.modified_by,
            'modified_date' : self.modified_date.isoformat(),
            'pending': self.pending
        }
