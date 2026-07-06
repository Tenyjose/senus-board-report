from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import periods, metrics, insights


app = FastAPI(title="Senus Board Report API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(periods.router)
app.include_router(metrics.router)
app.include_router(insights.router)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Senus Board Report API"}