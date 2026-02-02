# ...existing code...
from fastapi import FastAPI
from app.middleware.ip_guard import IPGuardMiddleware
from contextlib import asynccontextmanager
from .core.database import init_db
from fastapi.middleware.cors import CORSMiddleware
from app.routers import bookmark_route,users_router,auth_router,folder_router,tag_router
from app.routers import bookmark_tag_router,bulk_router,search_router ,sync_router
# from app.models.models import User,Tag,Bookmark,BookmarkTagLink
from fastapi import Request,Response

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield



app = FastAPI(lifespan=lifespan)


@app.options("/{path:path}", include_in_schema=False)
async def global_options_handler(request: Request, path: str):
    return Response(status_code=200)

origins = [
    
    "http://localhost:5173",
    "http://localhost:5174"
]

#1️⃣ CORS FIRST
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2️⃣ chrome-extension dynamic CORS
@app.middleware("http")
async def allow_chrome_extension_cors(request: Request, call_next):
    response = await call_next(request)
    origin = request.headers.get("origin")

    if origin and origin.startswith("chrome-extension://"):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"

    return response

# 3️⃣ IP guard LAST
app.add_middleware(IPGuardMiddleware)

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

