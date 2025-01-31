import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.api.auth_api import auth_api_router
from src.api.user_api import user_api_router

app = FastAPI()

app.include_router(auth_api_router)
app.include_router(user_api_router)



@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_data = await request.body()
    print(f"Request Validation Error: {exc.errors()} \n Body: {request_data}")
    return JSONResponse(
        status_code=422,
        content={"error": exc.errors()},
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        reload=True,
    )
