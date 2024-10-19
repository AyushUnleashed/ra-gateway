# Fastapi code for the app
import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import Config


sentry_sdk.init(
    dsn=Config.SENTRY_DSN,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    environment=Config.APP_ENV,
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

from src.api.main_routes import main_router
from src.api.webhook_routes import webhook_router

app.include_router(main_router)
app.include_router(webhook_router)

@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0
      
if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0", port=5151, workers=2, reload=True)