from fastapi import FastAPI

from database import engine
from routers import auth, users, admin
import models

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(auth.router,)
app.include_router(users.router,)
app.include_router(admin.router,)

