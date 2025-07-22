import datetime

import requests
from dagster import op
from bs4 import BeautifulSoup


@op(required_resource_keys={"telegram"})
def send_telegram_message_op(context, new_events):
    if not new_events:
        context.log.info("no info to send to telegram. Ending task")
        return
    event = new_events[0]

    message = (
        f"New event detected: {event['event_name']} = {event['event_value']} "
        f"starting from {event['valid_from']}"
    )
    context.resources.telegram.send_message(message)
    context.log.info(f"info sent to telegram: {message}")
    return


@op(required_resource_keys={"postgres"})
def store_in_db_op(context, data):
    engine = context.resources.postgres.engine
    execute_query = context.resources.postgres.execute_query

    # Make sure table exists in PG
    create_table_query = """
    CREATE TABLE IF NOT EXISTS events (
        id SERIAL PRIMARY KEY,
        event_name TEXT NOT NULL DEFAULT 'Pollen',
        event_value TEXT NOT NULL,
        event_time TIMESTAMP NOT NULL DEFAULT NOW()
    );
    """
    execute_query(engine, create_table_query)

    # Insert new data into the table
    insert_query = """
        INSERT INTO events (event_name, event_value, event_time)
        VALUES (:name, :value, :time);
        """

    params = data
    execute_query(engine, insert_query, params)

    return data


@op(required_resource_keys={"postgres"})
def create_scd2_view_op(context, data):
    engine = context.resources.postgres.engine
    execute_query = context.resources.postgres.execute_query

    create_scd2_view_query = """
    CREATE OR REPLACE VIEW scd2_events AS
    WITH 
    changes AS (
        SELECT
            event_name,
            event_value,
            event_time,
            LAG(event_value) OVER (PARTITION BY event_name ORDER BY event_time) AS prev_value,
            LAG(event_time) OVER (PARTITION BY event_name ORDER BY event_time) AS prev_event_time
        FROM events
    ),
    filtered AS (
        SELECT
            event_name,
            event_value,
            event_time,
            prev_event_time,
            CASE
                WHEN prev_value IS DISTINCT FROM event_value 
                THEN event_time
                ELSE NULL
            END AS change_time
        FROM changes
    ),
    grouped AS (
        SELECT
            event_name,
            event_value,
            event_time,
            COALESCE(
                MAX(change_time) OVER (
                    PARTITION BY event_name ORDER BY event_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ),
                event_time
            ) AS valid_from
        FROM filtered
    )
    SELECT
        event_name,
        event_value,
        valid_from,
        LEAD(valid_from) OVER (PARTITION BY event_name ORDER BY valid_from) AS valid_to,
        CASE 
            WHEN LEAD(valid_from) OVER (PARTITION BY event_name ORDER BY valid_from) IS NULL 
            THEN TRUE 
            ELSE FALSE 
        END AS is_current
    FROM grouped
    WHERE valid_from IS NOT NULL;
    """

    execute_query(engine, create_scd2_view_query)
    context.log.info("Refreshed scd2_events view.")
    return data


@op(required_resource_keys={"postgres"})
def find_new_scd2_events_op(context, data):
    engine = context.resources.postgres.engine
    fetch_query = context.resources.postgres.fetch_query

    today = datetime.datetime.now(datetime.timezone.utc).date()
    target_event = data["name"]

    query = """
        SELECT 
            event_name, 
            event_value, 
            valid_from
        FROM scd2_events
        WHERE 
            DATE(valid_from) = :today
            AND event_name = :target_event
            AND is_current = TRUE;
    """

    new_events = fetch_query(
        engine, query, {"today": today, "target_event": target_event}
    )

    if not new_events:
        context.log.info("No new SCD2 events starting today.")
        return

    context.log.info("New scd2 event starting today")
    return new_events


@op
def fetch_data_op(context):
    url = "https://pollenkoll.se/pollenprognos/stockholm/"

    response = requests.get(url)
    response.raise_for_status()  # error if page is broken

    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.find_all("div", class_="pollen-city__item")

    for item in items:
        description_div = item.find("div", class_="pollen-city__item-desc")
        name_div = item.find("div", class_="pollen-city__item-name")

        description = description_div.get_text(strip=True) if description_div else None
        name = name_div.get_text(strip=True) if name_div else None

        if name == "Gräs":
            params = {
                "name": "pollen_level",
                "value": description,
                "time": datetime.datetime.now(datetime.timezone.utc),
            }
            return params
