from fastapi.testclient import TestClient

from app.main import app
from app.models.user import Role, UserCreate
from app.services.user_service import UserService

client = TestClient(app)

REG_PAYLOAD = {
    "full_name": "Test User",
    "email": "router_test@example.com",
    "phone": "+380991112233",
    "date_of_birth": "1995-03-20",
    "address": "Lviv, Test St 1",
    "password": "Secure456",
}

def _login(email: str, password: str) -> str:
    response = client.post("/api/auth/login", data={"username": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_register_and_login():
    response = client.post("/api/auth/register", json=REG_PAYLOAD)
    assert response.status_code == 201
    assert response.json()["email"] == REG_PAYLOAD["email"]
    assert response.json()["role"] == "User"

    login = client.post("/api/auth/login", data={"username": REG_PAYLOAD["email"], "password": REG_PAYLOAD["password"]})
    assert login.status_code == 200
    assert "access_token" in login.json()


def test_public_register_rejects_role_field():
    payload = REG_PAYLOAD | {"email": "role_try@example.com", "role": "Administrator"}
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422


def test_login_bad_credentials():
    client.post("/api/auth/register", json=REG_PAYLOAD)
    response = client.post("/api/auth/login", data={"username": REG_PAYLOAD["email"], "password": "wrong"})
    assert response.status_code == 401


def test_get_me_requires_auth():
    response = client.get("/api/users/me")
    assert response.status_code == 401


def test_get_me_with_token():
    client.post("/api/auth/register", json=REG_PAYLOAD)
    token = _login(REG_PAYLOAD["email"], REG_PAYLOAD["password"])
    response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == REG_PAYLOAD["email"]


def test_admin_endpoint_blocked_for_user():
    client.post("/api/auth/register", json=REG_PAYLOAD)
    token = _login(REG_PAYLOAD["email"], REG_PAYLOAD["password"])
    response = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_admin_can_create_user_without_exposing_personal_data():
    admin = UserService().register(
        UserCreate(
            full_name="Admin User",
            email="admin@example.com",
            phone="+380991112244",
            date_of_birth="1985-01-01",
            address="Kyiv",
            password="Admin123",
            role=Role.ADMIN,
        ),
        actor_id="system",
        allow_role_selection=True,
    )
    token = _login(admin.email, "Admin123")
    response = client.post(
        "/api/admin/users",
        json={
            "full_name": "Advanced User",
            "email": "advanced@example.com",
            "phone": "+380991112255",
            "date_of_birth": "1991-01-01",
            "address": "Odesa",
            "password": "Advanced123",
            "role": "Advanced user",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["role"] == "Advanced user"
    assert "email" not in body
    assert "full_name" not in body
