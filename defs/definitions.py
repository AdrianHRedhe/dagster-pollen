from dagster import Definitions

from defs.jobs import pollen_job
from defs.resources import postgres_resource
from defs.resources import telegram_resource
from defs.schedules import pollen_job_daily_schedule

defs = Definitions(
    jobs=[pollen_job],
    resources={
        "postgres": postgres_resource,
        "telegram": telegram_resource,
    },
    schedules=[pollen_job_daily_schedule],
)
