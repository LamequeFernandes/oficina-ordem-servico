from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.usuario.application.use_cases import LoginUseCase
from app.modules.usuario.application.dto import LoginOutputDTO
from app.modules.usuario.infrastructure.repositories import AuthRepository


router = APIRouter()


@router.post('/login', response_model=LoginOutputDTO)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    try:
        repo = AuthRepository(db)
        use_case = LoginUseCase(repo)
        return use_case.execute(
            form_data.username, form_data.password
        )   # type: ignore
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
