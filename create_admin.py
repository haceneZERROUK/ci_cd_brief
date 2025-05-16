from sqlmodel import Session
from app.utils import bcrypt_context
from sqlmodel import SQLModel
from app.database import engine
from app.modeles import Users


def populate_db():

    with Session(engine) as session:
        
        # Ajouter un utilisateur admin
        admin_user = Users(
            cinema_name="admin",
            email="admin",
            hashed_password=bcrypt_context.hash("admin"),
            role="admin",
            is_active=1
            )
        session.add(admin_user)
        session.commit()

    user = Users(cinema_name='test', email='test@test.fr', hashed_password=bcrypt_context.hash('test'))
    session.add(user)
    session.commit()

if __name__ == "__main__" : 
    SQLModel.metadata.create_all(engine)
    populate_db()



