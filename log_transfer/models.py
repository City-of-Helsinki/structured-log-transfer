from django.conf import settings
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
        
    def markAsSent(self):
      self.is_sent = True
      self.save()
    
    @staticmethod
    def getUnsentEntries():
      return AuditLogEntry.objects.filter(is_sent=False).order_by("created_at")
