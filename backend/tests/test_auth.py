"""Authentication endpoint tests."""

SIGNUP = {"name": "Asha", "email": "asha@example.com", "password": "secret123"}


def test_signup_creates_user(client):
    response = client.post("/api/auth/signup", json=SIGNUP)

    assert response.status_code == 201
    body = response.get_json()
    assert body["user"]["email"] == "asha@example.com"
    assert body["user"]["name"] == "Asha"
    # The password must never be returned or stored in plain text.
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]


def test_signup_duplicate_email_rejected(client):
    client.post("/api/auth/signup", json=SIGNUP)

    response = client.post("/api/auth/signup", json=SIGNUP)

    assert response.status_code == 409
    assert response.get_json()["error"]["code"] == "EMAIL_IN_USE"


def test_signup_validation_error(client):
    response = client.post(
        "/api/auth/signup", json={"name": "", "email": "not-an-email", "password": "1"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"


def test_login_success(client):
    client.post("/api/auth/signup", json=SIGNUP)
    client.post("/api/auth/logout")

    response = client.post(
        "/api/auth/login",
        json={"email": SIGNUP["email"], "password": SIGNUP["password"]},
    )

    assert response.status_code == 200
    assert response.get_json()["user"]["email"] == "asha@example.com"


def test_login_invalid_credentials(client):
    client.post("/api/auth/signup", json=SIGNUP)

    response = client.post(
        "/api/auth/login",
        json={"email": SIGNUP["email"], "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_me_requires_auth(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "UNAUTHORIZED"


def test_me_returns_current_user(client):
    client.post("/api/auth/signup", json=SIGNUP)

    response = client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.get_json()["user"]["email"] == "asha@example.com"


def test_logout_clears_session(client):
    client.post("/api/auth/signup", json=SIGNUP)
    assert client.get("/api/auth/me").status_code == 200

    logout = client.post("/api/auth/logout")

    assert logout.status_code == 200
    assert logout.get_json() == {"success": True}
    assert client.get("/api/auth/me").status_code == 401
