import os
import multiprocessing
from fastapi import FastAPI
from uvicorn import Config, Server, run

class Server(multiprocessing.Process):
    """ Class for working with a local uvicorn server """
    def __init__(self) -> None:
        super().__init__()

    def stop(self) -> None:
        self.terminate()

    def run(self, *args, **kwargs) -> None:
        # Get the current working path 
        path = os.path.abspath(os.getcwd()).split('\\')
        app_dir = "\\".join(path + ['fastapi','app'])
        run('main:app', app_dir=app_dir, reload=True)