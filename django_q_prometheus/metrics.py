from datetime import timedelta
from django.db import connection
from django.db.models import F, Sum
from django.utils import timezone

from django_q import models
from django_q.brokers import get_broker
from django_q.status import Stat

class Metrics(object):
    def __init__(self, broker=None):
        """ An interface for reporting on performance and statistic
            information in django-q.

        Args:
            broker (Broker, optional): Provide a Broker to query against.
                Defaults to the current configured broker.
        """
        if not broker:
            self._broker = get_broker()
        self._broker.ping()
        self._stat = Stat.get_all(broker=self._broker)
        self.now = timezone.now()

    @property
    def success_count(self) -> int:
        """
        Returns:
            int: A count of successful tasks.
        """
        return models.Success.objects.count()

    @property
    def failure_count(self) -> int:
        """
        Returns:
            int: A count of failed tasks.
        """
        return models.Failure.objects.count()

    @property
    def schedule_count(self) -> int:
        """
        Returns:
            int: A count of schedules.
        """
        return models.Schedule.objects.count()

    @property
    def queue_count(self) -> int:
        """
        Returns:
            int: A count of current tasks in the queue.
        """
        return self._broker.queue_size()

    @property
    def cluster_count(self) -> int:
        """
        Returns:
            int: A count of available clusters.
        """
        return len(self._stat)

    @property
    def worker_count(self) -> int:
        """
        Returns:
            int: A count of all available workers.
        """
        count = 0
        for c in self._stat:
            count += len(c.workers)
        return count

    @property
    def reincarnation_count(self):
        """
        Returns:
            int: A count of processes that have been reincarnated.
        """
        count = 0
        for c in self._stat:
            count += c.reincarnations
        return count

    @property
    def average_execution_time(self) -> tuple[int,int]:
        """ Returns a tuple of the average execution time
            of tasks that have been processed in the last
            24 hours (day).

            Returns:
            (exec_time, tasks_per_day): A tuple containing the average execution time and count of tasks.
        """
        last_tasks = models.Success.objects.filter(
            stopped__gte=self.now - timedelta(hours=24)
        )
        exec_time = 0
        tasks_per_day = last_tasks.count()
        # average execution time over the last 24 hours
        if connection.vendor != "sqlite":
            exec_time = last_tasks.aggregate(
                time_taken=Sum(F("stopped") - F("started"))
            )
            exec_time = exec_time["time_taken"].total_seconds() / tasks_per_day
        else:
            # can't sum timedeltas on sqlite
            for t in last_tasks:
                exec_time += t.time_taken()
            exec_time = exec_time / tasks_per_day
        return (exec_time, tasks_per_day)