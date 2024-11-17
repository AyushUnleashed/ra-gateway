# Fastapi code for the app
import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import Settings


sentry_sdk.init(
    dsn=Settings.SENTRY_DSN,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    environment=Settings.APP_ENV,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)


app = FastAPI(
    title="ra-gateway",
    description="This is backend gateway for reels ai pro",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# List your frontend domain(s) here
origins = [
    "http://localhost:3000",
    "https://www.reelsai.pro",
    "https://reelsai.pro"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # This allows all methods, including OPTIONS
    allow_headers=["*"],
)

from src.api.routes.main_routes import main_router
from src.api.routes.actor_routes import actors_router
from src.api.routes.products_routes import products_router
from src.api.routes.projects_routes import projects_router
from src.api.routes.scripts_routes import scripts_router
from src.api.routes.users_routes import users_router
from src.api.routes.video_layouts_routes import video_layouts_router
from src.api.routes.webhook_routes import webhook_router

app.include_router(main_router)
app.include_router(actors_router)
app.include_router(products_router)
app.include_router(projects_router)
app.include_router(scripts_router)
app.include_router(users_router)
app.include_router(video_layouts_router)
app.include_router(webhook_router)

@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0
      
if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0", port=5151, workers=2, reload=True)