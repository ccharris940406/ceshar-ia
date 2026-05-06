import uvicorn
from fastapi import FastAPI

from app.api.admin import router as admin_router
from app.api.router import router

app = FastAPI(title="Ceshar IA")
app.include_router(router)
app.include_router(admin_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
