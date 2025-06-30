import os
import requests
from types import SimpleNamespace

from dotenv import load_dotenv
from dagster import resource
from sqlalchemy import create_engine, text


@resource
def telegram_resource():
    load_dotenv()
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in your .env file"
        )

    def send_message(text: str):
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        r = requests.post(url, data=payload)
        r.raise_for_status()
        return r.json()

    # this lets our function be called as
    # telegram_resource.send_message, and it also works for
    # using several functions in the future without need for
    # a class
    return SimpleNamespace(send_message=send_message)


@resource
def postgres_resource():
    # Load connection params from env
    url = (
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/"
        f"{os.getenv('POSTGRES_DB')}"
    )

    engine = create_engine(url, pool_pre_ping=True)

    def execute_query(engine, query, params=None):
        with engine.connect() as conn:
            conn.execute(text(query), params or {})
            conn.commit()

    def fetch_query(engine, query, params=None):
        with engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    return SimpleNamespace(
        fetch_query=fetch_query, execute_query=execute_query, engine=engine
    )
