import secrets
from datetime import datetime, timedelta, timezone
from enum import Enum
 
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

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    
ROLE_PERMISSIONS = {
    Role.ADMIN: ["create", "read", "update", "delete"],
    Role.USER: ["read", "update"],
    Role.GUEST: ["read"],}

fake_users_db: dict[str, dict[str, str]] = {}

fake_users_db["admin"] = {
    "hashed_password": pwd_context.hash("adminpass"),
    "role": Role.ADMIN,
}

fake_users_db["user"] = {
    "hashed_password": pwd_context.hash("userpass"),
    "role": Role.USER,
}

fake_users_db["guest"] = {
    "hashed_password": pwd_context.hash("guestpass"),
    "role": Role.GUEST,
}

class UserCredentials(BaseModel):
    username: str
    password: str   
    role: Role = Role.GUEST
    
def create_access_token(username: str, role: Role) -> str:
    payload = {
        "sub": username,
        "role": role.value,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM) 

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing subject or role")
        return {"username": username, "role": Role(role)}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
def require_permission(permission: str):
    def dependency(current_user: dict = Depends(get_current_user)) -> dict:
        role = current_user["role"]
        if permission not in ROLE_PERMISSIONS[role]:
            raise HTTPException(status_code=403, detail=f"Role '{role}' has no '{permission}' permission")
        return current_user
    return dependency

def require_role(*roles: Role):
    def dependency(current_user: dict = Depends(get_current_user)) -> dict:
        role = current_user["role"]
        if role not in roles:
            raise HTTPException(status_code=403, detail=f"Role '{role}' is not allowed to access this resource")
        return current_user
    return dependency

@app.post("/register", status_code=201)
@limiter.limit("1/minute")
def register(request: Request, credentials: UserCredentials):
    if credentials.username in fake_users_db:
        raise HTTPException(status_code=409, detail="User already exists")
 
    fake_users_db[credentials.username] = {
        "hashed_password": pwd_context.hash(credentials.password),
        "role": credentials.role,
    }
    return {"message": "New user created", "role": credentials.role}
 
 
@app.post("/login")
@limiter.limit("5/minute")
def login(request: Request, credentials: UserCredentials):
    stored = next(
        (fake_users_db[u] for u in fake_users_db
         if secrets.compare_digest(u, credentials.username)),
        None,
    )
    if stored is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not pwd_context.verify(credentials.password, stored["hashed_password"]):
        raise HTTPException(status_code=401, detail="Authorization failed")
 
    token = create_access_token(credentials.username, stored["role"])
    return {"access_token": token, "token_type": "bearer", "role": stored["role"]}
 
@app.get("/protected_resource")
def protected_resource(current_user: dict = Depends(require_permission("read"))):
    return {
        "message": f"Welcome, {current_user['username']}!",
        "your_role": current_user["role"],
        "your_permissions": list(ROLE_PERMISSIONS[current_user["role"]]),
    }

@app.put("/resource/{resource_id}")
def update_resource(
    resource_id: int,
    current_user: dict = Depends(require_permission("update")),
):
    return {
        "message": f"Resource {resource_id} updated by {current_user['username']}",
        "role": current_user["role"],
    }
 
@app.post("/resource")
def create_resource(current_user: dict = Depends(require_permission("create"))):
    return {
        "message": f"Resource created by {current_user['username']}",
        "role": current_user["role"],
    }

@app.delete("/resource/{resource_id}")
def delete_resource(
    resource_id: int,
    current_user: dict = Depends(require_permission("delete")),
):
    return {
        "message": f"Resource {resource_id} deleted by {current_user['username']}",
        "role": current_user["role"],
    }

@app.get("/admin/users")
def list_users(current_user: dict = Depends(require_role(Role.ADMIN))):
    return {
        "users": [
            {"username": u, "role": data["role"]}
            for u, data in fake_users_db.items()
        ]
    }