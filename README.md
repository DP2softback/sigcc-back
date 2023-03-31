# sigcc-back
Backend from SIGCC system, capstone course in PUCP

# BROADCAST BOT

## Requirements

    1. Docker
    2. Docker compose

## Build

    1. build docker images

        $ docker-compose build

    2. Access to the zappa container

        $ docker-compose run --rm --service-ports bot

    3. Setup virtual environment

        $ python -m venv .venv
        $ source .venv/bin/activate

    4. Install python dependencies

        $ pip install -r requirements.txt

    5. Run migrations

        $ python manage.py migrate

## Run in local

    1. Access to the zappa container

        $ docker-compose run --rm --service-ports bot

    2. Access to the virtual environment

        $ source .venv/bin/activate

    3. Run django server

        $ python manage.py runserver 0:8000