from fastapi.testclient import TestClient

from app.main import app


def test_chat_query_role_and_location() -> None:
    with TestClient(app) as client:
        role_response = client.post("/api/chat/query", json={"query": "Who is the Vice Chancellor?"})
        location_response = client.post("/api/chat/query", json={"query": "Where is Geomatic Engineering?"})

    assert role_response.status_code == 200
    assert role_response.json()["matches"][0]["id"] == "richard-k-amankwah"

    assert location_response.status_code == 200
    assert location_response.json()["matches"][0]["id"] == "department-of-geomatic-engineering"


def test_admin_login_and_rbac() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/auth/login",
            json={"email": "editor@umat.edu.gh", "password": "Editor123!"},
        )
        users_response = client.get("/api/admin/users")

    assert login_response.status_code == 200
    assert users_response.status_code == 403
