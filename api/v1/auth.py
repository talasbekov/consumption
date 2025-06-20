from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core import get_db, configs
from services import (
    authenticate_user,
    create_access_token,
    get_current_user
)
from schemas import (
    RegistrationForm,
    Token,
    UserRead,
    TokenData # Added TokenData import for the new function
)
from models import User, Employee
from sqlalchemy import select
from typing import Optional # Added Optional for type hints
from jose import JWTError, jwt # Added for new function

router = APIRouter(prefix="/auth", tags=["Authorization"])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post(
    "/login",
    response_model=Token,
    summary="Login (получение JWT-токена)"
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    - Принимает form-data с полями username (email) и password.
    - Если аутентификация успешна, возвращает {"access_token": <JWT>, "token_type": "bearer"}.
    - Если нет — 401.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Attempt to fetch the associated Employee record
    employee = None
    if user.employee_id:
        employee_result = await db.execute(select(Employee).filter(Employee.id == user.employee_id))
        employee = employee_result.scalars().first()

    employee_division_id = employee.division_id if employee else None
    # Default to Role 4 for now, this is a temporary default
    user_role = user.role if user.role is not None else 4

    token_data_payload = {
        "sub": user.email,  # Standard subject claim
        "user_id": user.id,
        "role": user_role,
        "division_id": employee_division_id,
    }

    expires = timedelta(minutes=configs.ACCESS_TOKEN_EXPIRES_IN)
    access_token = create_access_token(
        data=token_data_payload, # Pass the new payload
        expires_delta=expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register (создание нового пользователя)"
)
async def register_user(
    form: RegistrationForm,
    db: AsyncSession = Depends(get_db),
):
    """
    1. Проверяет, что email ещё не занят.
    2. Хэширует пароль.
    3. Сохраняет нового пользователя в БД.
    4. Возвращает сериализованный UserRead (id + email).
    """
    # Проверяем, есть ли уже юзер с таким email
    existing = await authenticate_user(db, form.email, form.password)
    # Обратите внимание: здесь лучше сначала проверить get_user_by_email отдельно,
    # чтобы не проверять пароль для существующего, но для простоты достаточно:
    if existing or (await db.execute(
            select(User).where(User.email == form.email)
        )).scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )

    # Хэшируем пароль и создаём модель
    from services import get_password_hash  # можно импортировать вверху
    hashed_pwd = get_password_hash(form.password)

    new_user = User(
        email=form.email,
        password=hashed_pwd,
    )
    db.add(new_user)
    await db.flush()  # чтобы получить new_user.id

    # Коммит произойдёт автоматически, потому что get_db() делает await session.commit()
    return new_user


@router.get(
    "/me",
    response_model=UserRead,
    summary="Получить текущего пользователя"
)
async def read_users_me(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    1. Взять token из заголовка Authorization: Bearer <token>.
    2. Раскодировать и найти пользователя через get_current_user.
    3. Вернуть его данные (UserRead).
    """
    user = await get_current_user(token, db)
    return user


async def get_current_token_data(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, configs.SECRET_KEY, algorithms=[configs.ALGORITHM])
        email: Optional[str] = payload.get("sub")
        user_id: Optional[int] = payload.get("user_id")
        role: Optional[int] = payload.get("role")

        # Role should ideally always be present in new tokens.
        # Role is crucial for authorization. If missing, token is considered invalid.
        if role is None:
            # Log this event: "Role missing in token for user_id: {user_id}"
            raise credentials_exception # Role must be present

        user_division_id: Optional[int] = payload.get("division_id")

        if email is None or user_id is None: # Role is now checked for None above
            raise credentials_exception

        return TokenData(email=email, user_id=user_id, role=role, division_id=user_division_id)
    except JWTError:
        raise credentials_exception
