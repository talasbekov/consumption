from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from core import get_db
from schemas import LoginForm, RegistrationForm
from services import auth_service

router = APIRouter(prefix="/auth2", tags=["Authorization_V2"])


@router.post("/login", summary="Login")
async def login(
    form: LoginForm, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()
):
    """
    Login to the system.

    - **email**: required and should be a valid email format.
    - **password**: required.
    """
    return auth_service.login(form, db, Authorize)


@router.post("/register", summary="Register")
async def register(form: RegistrationForm, db: Session = Depends(get_db)):

    return auth_service.register(form, db)


# @router.post("/register/user", summary="Register User",
#              dependencies=[Depends(HTTPBearer())])
# async def register_candidate(form: UserRegistrationForm,
#                              Authorize: AuthJWT = Depends(),
#                              db: Session = Depends(get_db)):
#     """
#         Register new candidate to the system.
#
#         - **iin**: str
#     """
#     Authorize.jwt_required()
#     role = Authorize.get_raw_jwt()['role']
#     return auth_service.register_candidate(
#         form=form, db=db, staff_unit_id=role)


@router.get("/refresh", dependencies=[Depends(HTTPBearer())])
def refresh_token(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    try:
        Authorize.jwt_refresh_token_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    return auth_service.refresh_token(db, Authorize)
