from dagster import ScheduleDefinition

from defs.jobs import pollen_job

pollen_job_daily_schedule = ScheduleDefinition(
    job=pollen_job,
    cron_schedule="0 9 * * *",
)
