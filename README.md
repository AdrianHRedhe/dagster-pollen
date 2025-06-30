# Dagster pollen project
This project is a showcase of how dagster can be used to
orchestrate a simple ingestion of data into postgres. And
then to notify a user via telegram on certain events.

Specifically it will fetch data on pollen () levels in
Stockholm. It will save the data each day and construct an
SCD2 table containing the valid from and valid to dates of
each status.

If there is a change in the pollen status, a message will be
sent out to the user via telegram, using a bot and a token +
chat id.

The project runs in docker, since my goal was to a) run this
on my raspberry pi b) make it simple to run on other
computers in general and c) to make it into a nice scaffold
for future automations that i might want to run. An added
bonus is that it is very simple to setup a postgres instance
which can have persistent data in between runs.

I use uv to manage the packages. But you don't need it
installed as you are only using docker. You will need to
have docker on your machine though to be running this
project. Docker engine should suffice which is open source.

## How to run
In the root of the project first fill in a .env file since
that will not be part of the repo. You need to fill in
certain values for PG and others for Telegram:

### Postgres .env values
As long as you dont make any changes to the compose file,
these values should work for postgres:
`
POSTGRES_DB=mydb
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypass
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
`

### Telegram .env values
For telegram you need to create an account and message
@BotFather to create a new bot. This will give you a token.
Then you can message your bot to start the conversation, you
need to write the first message before a bot can contact
you. You can then save the message id of your conversation
with your bot. Once you have done this you can fill in the 
following values in the .env file
`
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
`

### Running docker compose
Once the .env file is filled in with those values in the
root of the project, it is as simple as running the
following command in the terminal
`docker compose build && docker compose up`

### Checking in on runs
The program will automatically be running at 9 in the
morning every day. You can go to localhost:3000 to check out
dagster, upcoming runs, and also trigger runs manually if
you want to.
