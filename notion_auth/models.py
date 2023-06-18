from django.db import models
from django.urls import reverse


# Create your models here.


class LineUser(models.Model):
    line_user_id = models.CharField(max_length=255, unique=True)
    notion_token = models.TextField(null=True, blank=True)
    eeclass_username = models.CharField(max_length=255)
    eeclass_password = models.CharField(max_length=255)

    class Meta:
        ordering = ['-line_user_id']

    # Methods
    def get_absolute_url(self):
        """Returns the url to access a particular instance of MyModelName."""
        return reverse('model-detail-view', args=[str(self.id)])

    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return self.line_user_id
