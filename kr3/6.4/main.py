import secrets
from datetime import datetime, timedelta, timezone
 
import jwt
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too mamy requests"}
    )

SECRET_KEY = "super-puper-secret-key"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()    
fake_users_db: dict[str, str] = {}

class UserCredentials(BaseModel):
    username: str
    password: str
    
#заглушка для проверки работы авторизации
def auth_user(username: str, password: str) -> bool:
    return True

def create_access_token(username: str) -> str:
    payload = {
        "sub": username,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing subject")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
@app.post("/register", status_code=201)
@limiter.limit("1/minute")
def register(credentials: UserCredentials, request: Request):
    if credentials.username in fake_users_db:
        raise HTTPException(status_code=409, detail="User already exists")
    
    hashed_password = pwd_context.hash(credentials.password)
    fake_users_db[credentials.username] = hashed_password
    
    return {"message": "New user registered"}

@app.post("/login")
@limiter.limit("5/minute")
def login(credentials: UserCredentials, request: Request):
    stored_username = next((u for u in fake_users_db if secrets.compare_digest(u, credentials.username)), None,)
    if stored_username is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    hashed_password = fake_users_db[stored_username]
    if not pwd_context.verify(credentials.password, hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    token = create_access_token(stored_username)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/protected_resource")
def protected_resource(username: str = Depends(verify_token)):
    return {"message": f"Доступ пользователю {username} к защищенному ресурсу разрешен."}
