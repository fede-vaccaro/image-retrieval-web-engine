import os
from django.db import models
from taggit.managers import TaggableManager
from django.conf import settings
from django.utils.timezone import now as timezone_now
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import ugettext_lazy as _


def upload_to(instance, filename):
    now = timezone_now()
    filename_base, filename_ext = os.path.splitext(filename)
    return '%s%s' % (
        now.strftime("%Y/%m/%Y%m%d%H%M%S"),
        filename_ext.lower(),
    )


class Image(models.Model):
    title = models.CharField(max_length=80)
    image = models.ImageField(upload_to='img/')
    created = models.DateField(auto_now_add=True)
    quote = models.TextField(null=True)
    signature = ArrayField(base_field=models.FloatField(), null=True)
    tags = TaggableManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")

    def __unicode__(self):
        return self.quote
