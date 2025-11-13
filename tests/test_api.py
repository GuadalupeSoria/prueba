from datetime import date

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_user_lifecycle_and_matching_flow():
    user_payload = {
        "id": "11111111X",
        "full_name": "María Inquilina",
        "email": "maria@example.com",
        "birthdate": "1993-07-12",
        "preferences": {
            "max_budget": 800,
            "desired_locations": ["Barcelona"],
            "lifestyle": "flexible",
            "allows_pets": True,
            "hobbies": ["yoga", "cocina"],
        },
    }

    property_payload = {
        "id": "prop-bcn-1",
        "title": "Suite en Barcelona",
        "description": "Apartamento céntrico con vecinas fans del yoga yoga y cocina.",
        "city": "Barcelona",
        "monthly_price": 750,
        "available_from": date.today().isoformat(),
        "amenities": {
            "wifi": True,
            "has_workspace": True,
            "allows_pets": True,
            "bedrooms": 2,
            "bathrooms": 1.0,
        },
    }

    created_user = client.post("/users", json=user_payload)
    assert created_user.status_code == 201
    assert created_user.json()["debt_status"] == "clear"

    created_property = client.post("/properties", json=property_payload)
    assert created_property.status_code == 201
    assert created_property.json()["contract_verification"] is None

    verify_user = client.post(
        f"/users/{user_payload['id']}/verify",
        json={"selfie_reference": "selfie-123"},
    )
    assert verify_user.status_code == 200
    assert verify_user.json()["identity_verification"]["verified"] is True

    verify_property = client.post(
        f"/properties/{property_payload['id']}/verify",
        json={"contract_reference": "contract-abc"},
    )
    assert verify_property.status_code == 200
    assert verify_property.json()["contract_verification"]["verified"] is True

    matches = client.get(f"/users/{user_payload['id']}/matches")
    assert matches.status_code == 200
    body = matches.json()
    assert body
    assert body[0]["property_id"] == property_payload["id"]


def test_user_with_debt_cannot_be_matched():
    from app.main import DEBT_REGISTRY, USERS

    DEBT_REGISTRY.add_debtor("99999999D")

    response = client.post(
        "/users",
        json={
            "id": "99999999D",
            "full_name": "Deudor",
            "email": "deudor@example.com",
            "birthdate": "1990-01-01",
            "preferences": {
                "max_budget": 500,
                "desired_locations": ["Madrid"],
                "lifestyle": "early_bird",
                "allows_pets": False,
                "hobbies": [],
            },
        },
    )

    assert response.status_code == 201
    assert response.json()["debt_status"] == "has_debt"

    matches = client.get("/users/99999999D/matches")
    assert matches.status_code == 404

    USERS.pop("99999999D", None)
    DEBT_REGISTRY.remove_debtor("99999999D")
