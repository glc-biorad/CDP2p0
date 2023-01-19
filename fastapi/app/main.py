from fastapi import FastAPI

from routers import hardware_interface, chassis_submodule, pipettor_gantry_submodule, prep_deck_submodule, reader_submodule

app = FastAPI()

app.include_router(hardware_interface.router)
app.include_router(chassis_submodule.router)
app.include_router(pipettor_gantry_submodule.router)
app.include_router(prep_deck_submodule.router)
app.include_router(reader_submodule.router)
