# ...existing code...
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .core.database import init_db
from app.routers import bookmark_route,users_router,auth_router,folder_router,tag_router
from app.routers import bookmark_tag_router,bulk_router,search_router #sync_router
# from app.models.models import User,Tag,Bookmark,BookmarkTagLink

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

# print("Creating database and tables...")
# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)
#     print(SQLModel.metadata.tables.keys())
#     print("ENGINE URL:", engine.url.render_as_string(hide_password=False))

app.include_router(users_router.router)
app.include_router(bookmark_route.router)
app.include_router(auth_router.router)
app.include_router(folder_router.router)
app.include_router(tag_router.router)
# app.include_router(sync_router.router)
app.include_router(search_router.router)
app.include_router(bulk_router.router)


@app.get("/")
def root():
    return {"message": "Hello World"}
