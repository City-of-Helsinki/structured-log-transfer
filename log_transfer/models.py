from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class AuditLogEntry(models.Model):
    is_sent = models.BooleanField(default=False, verbose_name=_("is sent"))
    message = models.JSONField(verbose_name=_("message"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))

    class Meta:
        db_table = settings.AUDIT_TABLE_NAME

    def __str__(self):
        return ", ".join(
            [
                "Is sent: " + str(self.is_sent),
                "Message: " + str(self.message),
                "Created at: " + str(self.created_at)
            ]
        )
