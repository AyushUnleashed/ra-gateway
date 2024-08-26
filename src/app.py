# Fastapi code for the app
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # This allows all methods, including OPTIONS
    allow_headers=["*"],
)

from api.basic_routes import basic_router

app.include_router(basic_router)
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5151)