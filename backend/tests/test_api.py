from fastapi.testclient import TestClient


def create_reel(client: TestClient, external_id: str = "test-reel-1") -> dict:
    response = client.post(
        "/api/v1/reels",
        json={
            "external_id": external_id,
            "scope": "mine",
            "title": "Mein Test Reel",
            "description": "Erste Fassung",
            "status": "draft",
            "source_handle": "@interreels",
            "duration_seconds": 28,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_health_endpoints(client: TestClient) -> None:
    live = client.get("/api/v1/health/live")
    ready = client.get("/api/v1/health/ready")
    assert live.status_code == 200
    assert live.json() == {"status": "ok", "database": None}
    assert ready.status_code == 200
    assert ready.json() == {"status": "ok", "database": "ok"}


def test_reel_crud_and_optimistic_lock(client: TestClient) -> None:
    created = create_reel(client)
    reel_id = created["id"]

    listed = client.get("/api/v1/reels", params={"scope": "mine", "limit": 20})
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["id"] == reel_id

    updated = client.patch(
        f"/api/v1/reels/{reel_id}",
        json={"title": "Neue Fassung", "version": created["version"]},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Neue Fassung"
    assert updated.json()["version"] == created["version"] + 1

    conflict = client.patch(
        f"/api/v1/reels/{reel_id}",
        json={"title": "Veraltete Fassung", "version": created["version"]},
    )
    assert conflict.status_code == 409


def test_script_is_saved_and_versioned(client: TestClient) -> None:
    reel = create_reel(client, "script-reel")
    created = client.put(
        f"/api/v1/reels/{reel['id']}/script",
        json={"hook": "Starker Hook", "body": "Der Hauptteil", "call_to_action": "Jetzt speichern"},
    )
    assert created.status_code == 200
    assert created.json()["version"] == 1

    updated = client.put(
        f"/api/v1/reels/{reel['id']}/script",
        json={"hook": "Noch stärker", "version": 1},
    )
    assert updated.status_code == 200
    assert updated.json()["hook"] == "Noch stärker"
    assert updated.json()["version"] == 2

    detail = client.get(f"/api/v1/reels/{reel['id']}")
    assert detail.json()["script"]["body"] == "Der Hauptteil"


def test_competitors_and_settings(client: TestClient) -> None:
    competitor = client.post(
        "/api/v1/competitors",
        json={"handle": "@creatorlab", "display_name": "Creator Lab", "followers_count": 284000},
    )
    assert competitor.status_code == 201
    assert competitor.json()["handle"] == "creatorlab"
    assert client.get("/api/v1/competitors").json()["total"] == 1

    settings = client.patch(
        "/api/v1/settings",
        json={"display_name": "Leo Rosen", "locale": "de", "autosave": False},
    )
    assert settings.status_code == 200
    assert settings.json()["autosave"] is False


def test_apify_endpoint_is_safe_without_token(client: TestClient) -> None:
    config = client.get("/api/v1/imports/apify/config")
    assert config.status_code == 200
    assert config.json()["configured"] is False

    response = client.post(
        "/api/v1/imports/apify",
        json={"source_url": "https://www.instagram.com/creatorlab/", "limit": 20},
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "APIFY_NOT_CONFIGURED"

