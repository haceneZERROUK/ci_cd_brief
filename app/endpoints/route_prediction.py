# GET /predictions : Pour récupérer les prédictions de films à projeter.
# POST /predictions : Pour soumettre un film et obtenir une prédiction de fréquentation.
# GET /predictions/{film_id} : Pour récupérer les détails d'une prédiction spécifique.
# GET /predictions/top : Pour obtenir les films avec les meilleures prédictions pour la semaine.

from fastapi import APIRouter, Depends,HTTPException, status
from typing import Annotated
from ..use_model import use_model
from ..train_model import train_model
from app.utils import get_current_user

router = APIRouter()


@router.post("/predictions")
def get_predictions(data: list[dict],current_user: Annotated[str, Depends(get_current_user)]):
    result = use_model(data)
    if result == 'Error 1':
                raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="FOrmat de données invalide (donnée manquante)."
        )
    if result == 'Error 2':
                raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="FOrmat de données invalide (type invalide)."
        )
    return {"result" : result}

@router.post("/train")
def get_predictions(current_user: Annotated[str, Depends(get_current_user)]):
    
    if current_user.role == "admin" : 
        result = train_model()
        return {"result" : result}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas l'autorisation d'accéder à cette ressource."
        )
