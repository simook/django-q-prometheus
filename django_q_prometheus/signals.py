import time
import logging
from prometheus_client import Gauge, Summary
from django_q.signals import pre_execute, pre_enqueue
from django_q_prometheus.metrics import Metrics

logger = logging.getLogger('django.server')

MODE='mostrecent'
LABELS = []

TASKS_SUCCESS = Gauge('django_q_tasks_success', 
    'A count of successful tasks.', LABELS, multiprocess_mode=MODE)
TASKS_FAILED = Gauge('django_q_tasks_failed',
    'A count of failed tasks.', LABELS, multiprocess_mode=MODE)
TASKS_QUEUED = Gauge('django_q_tasks_queued',
    'A count of queued tasks.', LABELS, multiprocess_mode=MODE)
SCHEDULES_COUNT = Gauge('django_q_schedules_count', 
    'A count of schedules.', LABELS, multiprocess_mode=MODE)
CLUSTER_COUNT = Gauge('django_q_cluster_count',
    'A count of clsuters.', LABELS, multiprocess_mode=MODE)
WORKER_COUNT = Gauge('django_q_worker_count',
    'A count of workers.', LABELS, multiprocess_mode=MODE)
REINCARNATION_COUNT = Gauge('django_q_reincarnation_count', 
    'A count of processes that have been reincarnated.', LABELS, multiprocess_mode=MODE)
AVERAGE_EXEC_TIME = Gauge('django_q_average_execution_seconds',
    'The average execution time in the last 24 hours.', LABELS, multiprocess_mode=MODE)
TASKS_SUCCESS_PER_DAY = Gauge('django_q_tasks_per_day',
    'The count of sucessful tasks in the last 24 hours', LABELS, multiprocess_mode=MODE)

def call_hook(sender, **kwargs):
    try:
        m = Metrics()
        TASKS_SUCCESS.set(m.success_count)
        TASKS_FAILED.set(m.failure_count)
        TASKS_QUEUED.set(m.queue_count)
        SCHEDULES_COUNT.set(m.schedule_count)
        CLUSTER_COUNT.set(m.cluster_count)
        WORKER_COUNT.set(m.worker_count)
        REINCARNATION_COUNT.set(m.reincarnation_count)

        e, tasks = m.average_execution_time
        AVERAGE_EXEC_TIME.set(e)
        TASKS_SUCCESS_PER_DAY.set(tasks)
    except Exception as e:
        # catch any potential exceptions to prevent disruption to the cluster
        logger.error(e)

pre_enqueue.connect(call_hook)
pre_execute.connect(call_hook)