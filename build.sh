#!/usr/bin/env bash

curl -LsSf https://astral.sh/uv/install.sh | sh
. $HOME/.local/bin/env
# Postgres позволяет подключиться к удаленной базе указав ссылку на нее после флага -d
# ссылка подгрузится из переменной окружения, которую нам нужно будет указать на сервисе деплоя
# дальше мы загружаем в поключенную базу наш sql-файл с таблицами
make install && psql -a -d $DATABASE_URL -f database.sql
