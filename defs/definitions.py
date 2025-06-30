from dagster import Definitions
from defs.jobs import pollen_job
from defs.resources import postgres_resource
from defs.resources import telegram_resource

defs = Definitions(
    jobs=[pollen_job],
    resources={
        "postgres": postgres_resource,
        "telegram": telegram_resource,
    },
)
