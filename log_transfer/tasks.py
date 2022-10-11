import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from elasticsearch import Elasticsearch

from log_transfer.models import AuditLogEntry

ES_STATUS_CREATED = "created"
LOGGER = logging.getLogger(__name__)

def send_audit_log_to_elastic_search():
    if not (
        settings.ELASTICSEARCH_HOST
        and settings.ELASTICSEARCH_PORT
        and settings.ELASTICSEARCH_APP_AUDIT_LOG_INDEX
       # and settings.ELASTICSEARCH_USERNAME
       # and settings.ELASTICSEARCH_PASSWORD
    ):
        LOGGER.warning(
            "Trying to send audit log to Elasticsearch without proper configuration, process skipped"
        )
        return
    es = Elasticsearch(
        [
            {
                "host": settings.ELASTICSEARCH_HOST,
                "port": settings.ELASTICSEARCH_PORT,
                "scheme": settings.ELASTICSEARCH_SCHEME
            }
        ],
        basic_auth=(settings.ELASTICSEARCH_USERNAME, settings.ELASTICSEARCH_PASSWORD),
    )
    print(es)
    entries = AuditLogEntry.objects.filter(is_sent=False).order_by("created_at")
    resultids=[]
    
    for entry in entries:
        message_body = entry.message.copy()
        message_body["@timestamp"] = entry.message["audit_event"][
            "date_time"
        ]  # required by ES
        rs = es.index(
            index=settings.ELASTICSEARCH_APP_AUDIT_LOG_INDEX,
            id=entry.id,
            document=message_body,
            op_type="create",
        )
        print("Sending status: ", rs)
        
        if rs.get("result") == ES_STATUS_CREATED:
            entry.is_sent = True
            entry.save()
            resultids.append(rs.get("_id"))
    return resultids

# Used for tests only
def search_entries_from_elastic_search():
    if not (
        settings.ELASTICSEARCH_HOST
        and settings.ELASTICSEARCH_PORT
        and settings.ELASTICSEARCH_APP_AUDIT_LOG_INDEX
      #  and settings.ELASTICSEARCH_USERNAME
      #  and settings.ELASTICSEARCH_PASSWORD
    ):
        LOGGER.warning(
            "Trying to send audit log to Elasticsearch without proper configuration, process skipped"
        )
        return
    es = Elasticsearch(
        [
            {
                "host": settings.ELASTICSEARCH_HOST,
                "port": settings.ELASTICSEARCH_PORT,
                "scheme": settings.ELASTICSEARCH_SCHEME
            }
        ],
        basic_auth=(settings.ELASTICSEARCH_USERNAME, settings.ELASTICSEARCH_PASSWORD),
    )
  
    print("Search: ", settings.ELASTICSEARCH_APP_AUDIT_LOG_INDEX)
    
    # Index needs a refresh for the search to work this quickly
    es.indices.refresh(index=settings.ELASTICSEARCH_APP_AUDIT_LOG_INDEX)

    rs = es.search(index=settings.ELASTICSEARCH_APP_AUDIT_LOG_INDEX, query={"match_all": {}})
    print("Search result: ", rs)
    return rs    
    
# Used for tests only
def get_entries_from_elastic_search(idlist):
    if not (
        settings.ELASTICSEARCH_HOST
        and settings.ELASTICSEARCH_PORT
        and settings.ELASTICSEARCH_APP_AUDIT_LOG_INDEX
      #  and settings.ELASTICSEARCH_USERNAME
      #  and settings.ELASTICSEARCH_PASSWORD
    ):
        LOGGER.warning(
            "Trying to send audit log to Elasticsearch without proper configuration, process skipped"
        )
        return
    es = Elasticsearch(
        [
            {
                "host": settings.ELASTICSEARCH_HOST,
                "port": settings.ELASTICSEARCH_PORT,
                "scheme": settings.ELASTICSEARCH_SCHEME
            }
        ],
        basic_auth=(settings.ELASTICSEARCH_USERNAME, settings.ELASTICSEARCH_PASSWORD),
    )
  
    print("Getting from : ", settings.ELASTICSEARCH_APP_AUDIT_LOG_INDEX)
    rs = es.mget(index=settings.ELASTICSEARCH_APP_AUDIT_LOG_INDEX, ids=idlist)
    print("Result: ", rs)
    return rs
    


def clear_audit_log_entries(days_to_keep=30):
    # Only remove entries older than `X` days
    sent_entries = AuditLogEntry.objects.filter(
        is_sent=True, created_at__lte=(timezone.now() - timedelta(days=days_to_keep))
    )
    sent_entries.delete()
