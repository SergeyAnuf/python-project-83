### Project  Page Analizer
_____________________________________________________________________________________________________
### Hexlet tests and linter status:
[![Actions Status](https://github.com/SergeyAnuf/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/SergeyAnuf/python-project-83/actions)
[![Python CI](https://github.com/SergeyAnuf/python-project-83/actions/workflows/PyCI.yml/badge.svg)](https://github.com/SergeyAnuf/python-project-83/actions/workflows/PyCI.yml)
[
](https://sonarcloud.io/api/project_badges/quality_gate?project=SergeyAnuf_python-project-83)_____________________________________________________________________________________________________

Ссылка на домен сайта: https://python-project-83-h86n.onrender.com
***
## Requirements:

[Python 3.13 +] - (https://www.python.org/downloads/)

[UV 0.7.3 +] - (https://astral.sh)
***

## Installation:

````
git clone git@github.com:SergeyAnuf/python-project-83.git
````

````
cd python-project-83
````

`````
uv build
``````

````````
uv tool install dist/*.whl
````````

***

Local start:

````
uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
````

***

Project run on "render.com"

````
.venv/bin/python -m gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
````
***

Command on "render.com":

build:
````
make build
````
start:
````
make render start
````
