"""
Notes API - Flask + Redis.

Redis stores each note as a hash (HSET) under key "note:<id>", and keeps
every id in a set called "notes" so we can list them.
"""
import os
import uuid
from datetime import datetime, timezone

import redis
from flask import Flask, jsonify, request

app = Flask(__name__)

r = redis.Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=int(os.environ.get("REDIS_PORT", 6379)),
    decode_responses=True,  # get back str, not bytes
)


@app.get("/health")
def health():
    r.ping()  # raises if redis is unreachable -> Compose healthcheck fails loudly
    return {"status": "ok"}


@app.get("/api/notes")
def list_notes():
    ids = r.smembers("notes")
    notes = [r.hgetall(f"note:{i}") for i in ids]
    notes.sort(key=lambda n: n.get("created_at", ""))
    return jsonify(notes)


@app.get("/api/notes/<note_id>")
def get_note(note_id):
    note = r.hgetall(f"note:{note_id}")
    if not note:
        return {"error": "not found"}, 404
    return jsonify(note)


@app.post("/api/notes")
def create_note():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return {"error": "title is required"}, 400

    note_id = str(uuid.uuid4())
    note = {
        "id": note_id,
        "title": title,
        "body": data.get("body", ""),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    r.hset(f"note:{note_id}", mapping=note)
    r.sadd("notes", note_id)
    return jsonify(note), 201


@app.delete("/api/notes/<note_id>")
def delete_note(note_id):
    r.delete(f"note:{note_id}")
    r.srem("notes", note_id)
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
