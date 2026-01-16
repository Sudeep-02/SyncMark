# ...existing code...
from fastapi import FastAPI
from app.core.rate_limit import RateLimitMiddleware
from contextlib import asynccontextmanager
from .core.database import init_db
from fastapi.middleware.cors import CORSMiddleware
from app.routers import bookmark_route,users_router,auth_router,folder_router,tag_router
from app.routers import bookmark_tag_router,bulk_router,search_router ,sync_router
# from app.models.models import User,Tag,Bookmark,BookmarkTagLink

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield



app = FastAPI(lifespan=lifespan)


origins = [
    
    "http://localhost:5173",
    "http://localhost:5174"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,   # required if using cookies
    allow_methods=["GET","POST","PATCH","DELETE","OPTIONS"],
    allow_headers=["*"],
    
)

app.add_middleware(RateLimitMiddleware)

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
app.include_router(sync_router.router)
app.include_router(search_router.router)
app.include_router(bulk_router.router)

