import os
import secrets
import random


from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")
print("MODE", os.getenv("MODE"))

MODE = os.getenv("MODE")
DOCS_USERNAME = os.getenv("DOCS_USERNAME")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD")

if MODE not in ["DEV", "PROD"]:
    raise ValueError("Недопустимое значение для MODE. Допустимые: 'DEV' или 'PROD'.")

app = FastAPI(
    title="KR3 API",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

security = HTTPBasic() 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db: dict[str, "UserInDB"] = {}

class UserBase(BaseModel):
    username: str
    
class User(UserBase):
    password: str
    
class UserInDB(UserBase):
    hashed_password: str
    
    
def auth_user(credentials: HTTPBasicCredentials = Depends(security)) -> UserInDB:
    credentials_error = HTTPException( 
        status_code=401,
        detail="Некорректный логин или пароль",
        headers={"WWW-Authenticate": "Basic"},
    )
    
    user = fake_users_db.get(credentials.username)
    if user is None:
        raise credentials_error
    
    username_match = secrets.compare_digest(credentials.username.encode('utf-8'), user.username.encode('utf-8'))
    if not username_match:
        raise credentials_error
    
    password_match = pwd_context.verify(credentials.password, user.hashed_password)
    if not password_match:
        raise credentials_error
    
    return user

def auth_docs(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    username_is_ok = secrets.compare_digest(credentials.username.encode('utf-8'), DOCS_USERNAME.encode('utf-8'))
    password_is_ok = secrets.compare_digest(credentials.password.encode('utf-8'), DOCS_PASSWORD.encode('utf-8'))
    
    if not (username_is_ok and password_is_ok):
        raise HTTPException(
            status_code=401,
            detail="Некорректный логин или пароль для доступа к документации",
            headers={"WWW-Authenticate": "Basic"},
        )

if MODE == "DEV":
    @app.get("/docs", include_in_schema=False)
    def get_docs(username: str = Depends(auth_docs)) -> HTMLResponse:
        return get_swagger_ui_html(openapi_url="/openapi.json", title="KR3 API Docs")

    @app.get("/openapi.json", include_in_schema=False)
    def get_openapi_json(username: str = Depends(auth_docs)) -> JSONResponse:
        return JSONResponse(get_openapi(title=app.title, version="app.version", routes=app.routes))
    
    @app.get("/redoc", include_in_schema=False)
    def get_redoc() -> None:
        raise HTTPException(status_code=404, detail="Redoc недоступен в режиме разработки")
    
elif MODE == "PROD":
        @app.get("/docs", include_in_schema=False)
        def get_docs() -> None:
            raise HTTPException(status_code=404, detail="Документация недоступна в режиме продакшн")
        
        @app.get("/openapi.json", include_in_schema=False)
        def get_openapi_json() -> None:
            raise HTTPException(status_code=404, detail="OpenAPI JSON недоступен в режиме продакшн")
        
        @app.get("/redoc", include_in_schema=False)
        def get_redoc() -> None:
            raise HTTPException(status_code=404, detail="Redoc недоступен в режиме продакшн")
        
@app.post("/register")
def register(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Такой пользователь уже существует")
    hashed_password = pwd_context.hash(user.password)
    user_in_db = UserInDB(username=user.username, hashed_password=hashed_password)
    fake_users_db[user.username] = user_in_db
    
    return {"message" : f"Пользователь {user.username} успешно зарегистрирован"}

@app.get("/login")
def login(user: UserInDB = Depends(auth_user)):
    return {"message": f"Welcome, {user.username}!"}