# Schémas Pydantic pour les formulaires de l'API
from pydantic import BaseModel, Field, EmailStr
from typing import Union


class CreateUserRequest(BaseModel):

    cinema_name: str = Field(..., description="Nom de la banque")
    email: EmailStr
    password: str = Field(..., min_length=8, description="longueur minimale de 8 caractères")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cinema_name": "nom_cinema",
                "email": "mon_email@domaine.com",
                "password": "azerty12",
            }
        }        
        

