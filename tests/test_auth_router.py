"""
Integration-style tests for auth and user endpoints using FastAPI TestClient.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

REG_PAYLOAD = {
    "full_name": "Тест Юзер",
    "email": "router_test@example.com",
    "phone": "+380991112233",
    "date_of_birth": "1995-03-20",
    "address": "Lviv, Test St 1",
    "password": "Secure456",
    "role": "User",
}


def test_register_and_login():
    r = client.post("/api/auth/register", json=REG_PAYLOAD)
    assert r.status_code == 201
    assert r.json()["email"] == REG_PAYLOAD["email"]

    r2 = client.post("/api/auth/login", data={"username": REG_PAYLOAD["email"], "password": REG_PAYLOAD["password"]})
    assert r2.status_code == 200
    assert "access_token" in r2.json()


def test_login_bad_credentials():
    client.post("/api/auth/register", json=REG_PAYLOAD)
    r = client.post("/api/auth/login", data={"username": REG_PAYLOAD["email"], "password": "wrong"})
    assert r.status_code == 401


def test_get_me_requires_auth():
    r = client.get("/api/users/me")
    assert r.status_code == 401


def test_get_me_with_token():
    client.post("/api/auth/register", json=REG_PAYLOAD)
    login = client.post("/api/auth/login", data={"username": REG_PAYLOAD["email"], "password": REG_PAYLOAD["password"]})
    token = login.json()["access_token"]
    r = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == REG_PAYLOAD["email"]


def test_admin_endpoint_blocked_for_user():
    client.post("/api/auth/register", json=REG_PAYLOAD)
    login = client.post("/api/auth/login", data={"username": REG_PAYLOAD["email"], "password": REG_PAYLOAD["password"]})
    token = login.json()["access_token"]
    r = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403
