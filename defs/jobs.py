from dagster import job
from defs.operations import (
    create_scd2_view_op,
    fetch_data_op,
    store_in_db_op,
    send_telegram_message_op,
    find_new_scd2_events_op,
)


@job
def pollen_job():
    data = fetch_data_op()
    data = store_in_db_op(data)
    data = create_scd2_view_op(data)
    new_events = find_new_scd2_events_op(data)
    send_telegram_message_op(new_events)
