"""
Unit tests. fakeredis stands in for real Redis, so these run with no Docker
and no network - fast enough to run on every commit.
"""
import fakeredis
import pytest

import app as app_module


@pytest.fixture
def client():
    app_module.r = fakeredis.FakeRedis(decode_responses=True)
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as client:
        yield client


def test_health(client):
    assert client.get("/health").status_code == 200


def test_create_and_list_note(client):
    resp = client.post("/api/notes", json={"title": "first", "body": "hello"})
    assert resp.status_code == 201
    note_id = resp.get_json()["id"]

    listed = client.get("/api/notes").get_json()
    assert len(listed) == 1
    assert listed[0]["title"] == "first"

    fetched = client.get(f"/api/notes/{note_id}").get_json()
    assert fetched["body"] == "hello"


def test_create_note_without_title_fails(client):
    resp = client.post("/api/notes", json={"title": "  "})
    assert resp.status_code == 400


def test_delete_note(client):
    note_id = client.post("/api/notes", json={"title": "temp"}).get_json()["id"]
    assert client.delete(f"/api/notes/{note_id}").status_code == 204
    assert client.get(f"/api/notes/{note_id}").status_code == 404
