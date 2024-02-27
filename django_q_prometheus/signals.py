import logging
from prometheus_client import Gauge, Summary
from django_q.signals import pre_execute, pre_enqueue
from django_q_prometheus.metrics import Metrics

logger = logging.getLogger('django.server')

TASKS_SUCCESS = Gauge('django_q_tasks_success', 
    'A count of successful tasks.')
TASKS_FAILED = Gauge('django_q_tasks_failed',
    'A count of failed tasks.')
TASKS_QUEUED = Gauge('django_q_tasks_queued',
    'A count of queued tasks.')
SCHEDULES_COUNT = Gauge('django_q_schedules_count', 
    'A count of schedules.')
CLUSTER_COUNT = Gauge('django_q_cluster_count',
    'A count of clsuters.')
WORKER_COUNT = Gauge('django_q_worker_count',
    'A count of workers.')
REINCARNATION_COUNT = Gauge('django_q_reincarnation_count', 
    'A count of processes that have been reincarnated.')
AVERAGE_EXEC_TIME = Summary('django_q_average_execution_seconds',
    'The average execution time in the last 24 hours.')
TASKS_SUCCESS_PER_DAY = Summary('django_q_tasks_per_day',
    'The count of sucessful tasks in the last 24 hours')

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

        exec, tasks = m.average_execution_time
        AVERAGE_EXEC_TIME.observe(exec)
        TASKS_SUCCESS_PER_DAY.observe(tasks)
    except Exception as e:
        # catch any potential exceptions to prevent disruption to the cluster
        logger.error(e)

pre_enqueue.connect(call_hook)
pre_execute.connect(call_hook)