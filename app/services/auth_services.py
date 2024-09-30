from starlette.requests import Request
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.models.player_models import Player
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, status
from typing import Optional

async def verify_token_in_db(token: str, db: Session):
    # query the db in search for the token
    user = db.query(Player).filter(Player.token == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user

class CustomHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request) -> Optional[Player]:
        # we call the base method to obtain the header
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if credentials:
            scheme = credentials.scheme
            token = credentials.credentials

            # verify that scheme is Bearer
            if scheme.lower() != "bearer":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication scheme")

            # open db session
            db: Session = next(get_db())
            
            user = await verify_token_in_db(token, db)

            return user
        
        # if no token or is it invalid, return None
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authorization")