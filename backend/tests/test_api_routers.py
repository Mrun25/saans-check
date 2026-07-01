import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

init_db()
client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

import uuid

def test_create_and_list_sites():
    unique_code = f"TEST02_{uuid.uuid4().hex[:6]}"
    # Test POST /api/sites
    new_site = {
        "site_code": unique_code,
        "district": "Jodhpur",
        "state": "Rajasthan",
        "notes": "Test site"
    }
    response = client.post("/api/sites", json=new_site)
    assert response.status_code == 200
    data = response.json()
    assert data["site_code"] == unique_code
    site_id = data["id"]
    
    # Test GET /api/sites
    response = client.get("/api/sites")
    assert response.status_code == 200
    sites = response.json()
    assert any(s["id"] == site_id for s in sites)

def test_create_submission():
    unique_code = f"TEST03_{uuid.uuid4().hex[:6]}"
    # Make a site first
    new_site = {
        "site_code": unique_code,
        "district": "Nagaur"
    }
    site_res = client.post("/api/sites", json=new_site)
    assert site_res.status_code == 200
    site_code = site_res.json()["site_code"]

    submission = {
        "device_token": "test-device-123",
        "site_code": site_code,
        "language": "hi",
        "years_of_exposure": 15.0,
        "mask_usage_frequency": "never",
        "dust_suppression_at_site": "none"
    }
    response = client.post("/api/submissions", json=submission)
    assert response.status_code == 200
    data = response.json()
    
    assert data["risk_tier"] == "no_audio_submitted"
    assert "message" in data
    # NO_AUDIO_SUBMITTED does not append the exposure reminder by design
    assert "धूल में लंबे समय तक काम करना खतरनाक है" not in data["message"]

def test_dashboard_hotspots():
    response = client.get("/api/dashboard/hotspots")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Check that it doesn't contain forbidden fields
    for row in data:
        assert "device_token" not in row
        assert "raw_model_score" not in row
