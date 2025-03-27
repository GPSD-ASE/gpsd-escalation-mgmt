from fastapi import FastAPI, Depends
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from middleware.dependencies import verify_api_key
from middleware.limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from contextlib import asynccontextmanager
from middleware.redis import lifespan, log_request_util
from routes.stats import router as stats_router
from routes.analysis import router as analysis_router

app = FastAPI(dependencies=[Depends(verify_api_key)],
              root_path="/gpt", lifespan=lifespan)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.middleware("http")
async def log_request_data(request: Request, call_next):
    return await log_request_util(request, call_next)

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stats_router)
app.include_router(analysis_router)
