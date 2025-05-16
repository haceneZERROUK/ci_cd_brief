from datetime import timedelta
from app.utils import create_access_token
from datetime import datetime

film_pref = {"fr_title": "Sachein", "original_title": "Sachein", "released_date": "18/04/2025", "released_year": "2025", "actor_1": "Vijay J", "actor_2": "Genelia D'Souza", "actor_3": "Bipasha Basu", "directors": "John Mahendran", "writer": "John Mahendran", "distribution": " Night ed films ", "country": " Inde", "category": "Comédie", "classification": "Tout public", "duration": "2h 40min", "duration_minutes": 160, "allocine_url": "https://www.allocine.fr/film/fichefilm_gen_cfilm=146874.html", "image_url": "https://fr.web.img6.acsta.net/c_310_420/img/6f/ab/6fab37a7038e573ddf23f4019f37e4f7.jpg"}

def get_token(email, role):
    
    return create_access_token(
        data={"sub": email,
              "role": role},
        expires_delta=timedelta(minutes=30)
    )


def test_get_users_as_admin(client, admin_user):
    token = get_token(admin_user.email, admin_user.role)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/admin/users", headers=headers)
    assert response.status_code == 200

def test_get_users_as_user_forbidden(client, test_user):
    token = get_token(test_user.email, test_user.role)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/admin/users", headers=headers)
    assert response.status_code == 403

def test_create_user_as_admin(client, admin_user):
    token = get_token(admin_user.email, admin_user.role)
    headers = {"Authorization": f"Bearer {token}"}
    user_data = { 
        "cinema_name": "nom_cinema_2",
        "email": "mon_email_2@domaine.com",
        "password": "azerty12"
        }
    response = client.post("/admin/create_users", headers=headers, json=user_data)
    assert response.status_code == 200

def test_create_user_as_user_forbidden(client, test_user):
    token = get_token(test_user.email, test_user.role)
    headers = {"Authorization": f"Bearer {token}"}
    user_data = {
        "cinema_name": "unauthorized",
        "email": "bad@test.com",
        "password": "1235656656"
    }
    response = client.post("/admin/create_users", headers=headers, json=user_data)
    assert response.status_code == 403

def test_post_prediction_as_user(client, test_user, film):
    token = get_token(test_user.email, test_user.role)
    headers = {"Authorization": f"Bearer {token}"}
    prediction_input = [film]
    response = client.post("/predictions", json=prediction_input, headers=headers)
    assert response.status_code == 200
    assert "result" in response.json()

def test_post_prediction_as_user_missing_data(client, test_user, fake_film_missing):
    token = get_token(test_user.email, test_user.role)
    headers = {"Authorization": f"Bearer {token}"}
    prediction_input = [fake_film_missing]
    response = client.post("/predictions", json=prediction_input, headers=headers)
    assert response.status_code == 422
    
def test_post_prediction_as_user_bad_data(client, test_user, fake_film_bad_data):
    token = get_token(test_user.email, test_user.role)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/predictions", json=[fake_film_bad_data], headers=headers)

    # ⚠️ Le schéma n'est pas respecté, on attend une erreur 422
    assert response.status_code == 422

   
def test_post_train_as_admin(client, admin_user):
    token = get_token(admin_user.email,admin_user.role)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/train", headers=headers)
    assert response.status_code == 200

def test_post_train_as_user_forbidden(client, test_user):
    token = get_token(test_user.email, test_user.role)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/train", headers=headers)
    assert response.status_code == 403


