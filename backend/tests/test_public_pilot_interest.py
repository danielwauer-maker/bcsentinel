from app.db import SessionLocal
from app.public_lead_models import PilotInterest


def test_pilot_interest_requires_privacy_consent(client):
    response = client.post(
        "/public/pilot-interest",
        json={
            "contact_name": "Pilot User",
            "contact_email": "pilot@example.com",
            "privacy_consent": False,
        },
    )
    assert response.status_code == 400


def test_pilot_interest_is_persisted_without_email_dependency(client):
    response = client.post(
        "/public/pilot-interest",
        json={
            "contact_name": "Pilot User",
            "contact_email": "pilot@example.com",
            "company_name": "Example GmbH",
            "bc_context": "cloud",
            "message": "Validate assessment and monitoring.",
            "preferred_language": "de",
            "source_page": "controlled-pilot",
            "privacy_consent": True,
            "website": "",
        },
    )
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "accepted"
    assert body["reference"].startswith("PILOT-")

    with SessionLocal() as db:
        row = db.query(PilotInterest).one()
        assert row.contact_email == "pilot@example.com"
        assert row.status == "new"
        assert row.source_page == "controlled-pilot"


def test_pilot_honeypot_is_accepted_without_persistence(client):
    response = client.post(
        "/public/pilot-interest",
        json={
            "contact_name": "Bot User",
            "contact_email": "bot@example.com",
            "privacy_consent": True,
            "website": "https://spam.invalid",
        },
    )
    assert response.status_code == 202
    assert response.json() == {"status": "accepted", "reference": None}

    with SessionLocal() as db:
        assert db.query(PilotInterest).count() == 0
