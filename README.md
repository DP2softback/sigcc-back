# sigcc-back
Backend from SIGCC system, capstone course in PUCP

# Configuration steps

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


## Crear superuser for Django Admin:

    python manage.py createsuperuser

    username:demoadmin
    email:demoadmin@demoadmin.com
    password: demopassword


## resetear migraciones

    1. Eliminar los archivos de migraciones, excepto el init:
        __init__.py         //este no        

    2. En un terminal del sistema (no el de zappa) buscar el id del contenedor de la base de datos
        $ docker ps   (y ubican el id)

    3. Entrar a la base de datos

        $ docker exec -it e0ccbadd2699 psql -U user -W postgres

    4. Dentro de la bd, lanzar los comandos:

        postgres=# DROP DATABASE db;
        DROP DATABASE
        postgres=# CREATE DATABASE db;
        CREATE DATABASE

    5. Regresando al terminal de zappa, lanzar migrate

        $ python manage.py migrate

## Api documentation (temporal):
        https://documenter.getpostman.com/view/19467606/2s93m4Y3bm
