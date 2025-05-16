from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os
from .modeles import *
import urllib.parse

"""
Module de configuration et de gestion de la connexion à la base de données.
"""

load_dotenv()

# Chemin absolu de la base de données
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Répertoire où se trouve ce fichier
DATABASE_PATH = os.path.join(BASE_DIR, '..', 'bdd_clients.db')  # Cela remonte d'un niveau et pointe vers ta bdd

# URI pour SQLite avec chemin absolu
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Configuration de SQLAlchemy
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

try:
    # Création du moteur avec logging SQL
    engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=True)
    print(engine)

    # Test de connexion
    with engine.connect() as conn:
        print("Connexion à la base de données réussie!")

    # Création des tables
    SQLModel.metadata.create_all(engine)
    print("Tables créées avec succès!")

except Exception as e:
    print(f"Erreur lors de la connexion à la base de données: {str(e)}")
    raise

def db_connection():
    """
    Générateur de session de base de données pour FastAPI.
    """
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
