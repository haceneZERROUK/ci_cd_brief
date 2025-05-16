import pytest
from sqlmodel import SQLModel, create_engine, Session,select
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.database import db_connection
from app.modeles import Users  # Assure-toi que le modèle est bien importé
from app.main import app  # Ton application FastAPI si tu en as une

# --- Création de la base de données de test (SQLite en mémoire) ---
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Fixture pour la base de données ---
@pytest.fixture(scope="session")
def create_test_db():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)

# --- Fixture pour la session de test ---
@pytest.fixture(scope="function")
def db_session(create_test_db):
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

# --- Fixture pour insérer un utilisateur de test ---
@pytest.fixture
def test_user(db_session):
    stmt = select(Users).where(Users.email == "test@cinema.com")
    result = db_session.execute(stmt).scalars().first()

    if result :
        return result
    
    user = Users(
        cinema_name="Cinema Test",
        email="test@cinema.com",
        hashed_password="hashedpwd123",
        role="cinema"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def admin_user(db_session):
    stmt = select(Users).where(Users.email == 'admin@admin.com')
    result = db_session.execute(stmt).scalars().first()
    
    
    if result :
        return result

    user = Users(
        cinema_name="admin",
        email="admin@admin.com",
        hashed_password="hashedpwd123",
        role="admin"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

# --- Optionnel : client API FastAPI avec session override ---
@pytest.fixture
def client(db_session):
    def override_get_session():
        yield db_session

    app.dependency_overrides[db_connection] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def film():
    return {"fr_title": "Sachein", "original_title": "Sachein", "released_date": "18/04/2025", "released_year": "2025", "actor_1": "Vijay J", "actor_2": "Genelia D'Souza", "actor_3": "Bipasha Basu", "directors": "John Mahendran", "writer": "John Mahendran", "distribution": " Night ed films ", "country": " Inde", "category": "Comédie", "classification": "Tout public", "duration": "2h 40min", "duration_minutes": 160, "allocine_url": "https://www.allocine.fr/film/fichefilm_gen_cfilm=146874.html", "image_url": "https://fr.web.img6.acsta.net/c_310_420/img/6f/ab/6fab37a7038e573ddf23f4019f37e4f7.jpg"}

@pytest.fixture
def fake_film_missing():
    return {"fr_title": "Sachein", "original_title": "Sachein", "released_date": "18/04/2025", "released_year": "2025", "actor_1": "Vijay J", "actor_2": "Genelia D'Souza", "actor_3": "Bipasha Basu","writer": "John Mahendran", "distribution": " Night ed films ", "country": " Inde", "category": "Comédie", "classification": "Tout public", "duration": "2h 40min", "duration_minutes": 160, "allocine_url": "https://www.allocine.fr/film/fichefilm_gen_cfilm=146874.html", "image_url": "https://fr.web.img6.acsta.net/c_310_420/img/6f/ab/6fab37a7038e573ddf23f4019f37e4f7.jpg"}

@pytest.fixture
def fake_film_bad_data():
    return {"fr_title": "Sachein", "original_title": "Sachein", "released_date": "hacene", "released_year": 2025, "actor_1": "Vijay J", "actor_2": "Genelia D'Souza", "actor_3": "Bipasha Basu", "directors": "John Mahendran", "writer": "John Mahendran", "distribution": " Night ed films ", "country": " Inde", "category": "Comédie", "classification": "Tout public", "duration": "2h 40min", "duration_minutes": 160, "allocine_url": "https://www.allocine.fr/film/fichefilm_gen_cfilm=146874.html", "image_url": "https://fr.web.img6.acsta.net/c_310_420/img/6f/ab/6fab37a7038e573ddf23f4019f37e4f7.jpg"}