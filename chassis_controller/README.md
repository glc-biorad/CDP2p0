# BRADx Hardwear Interface Server
This is an API webserver using the [FastAPI](https://fastapi.tiangolo.com/) Python library to provide access to the BARDx chassis/bus controller hardware.

Project configuration and dependencies are handled using [Poetry](https://python-poetry.org/). A shell with all dependencies installed can be started by running `poetry shell`. Note: The first time using the application, run `poetry update` to install the dependencies.

To start the application run `uvicorn main:app --reload` in the `app` directory and access the server at http://127.0.0.1:8000. To access the server documentation go to http://127.0.0.1:8000/docs. This will list all the sections and endpoints and allow testing and running commands.

## Testing
Unit testing is setup using [pytest](https://docs.pytest.org/en/7.1.x/) and can be run via `pytest .` in the top level directory.

