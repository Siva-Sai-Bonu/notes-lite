# notes-lite

Three containers, one app, one pipeline.

```
                 :8080               :5000              :6379
   you  ─────▶  nginx  ── proxy ──▶ notes-api ── redis ──▶  redis
              (Docker Hub)          (this repo)          (Docker Hub)
```

| Container   | Source              | Job                                   |
|-------------|---------------------|----------------------------------------|
| `nginx`     | Docker Hub          | reverse proxy, `/healthz`             |
| `redis`     | Docker Hub          | stores the notes                      |
| `notes-api` | built from `./app`  | Flask REST API, the thing being built |

## Run it locally

```bash
docker compose up --build
curl -X POST localhost:8080/api/notes \
  -H 'Content-Type: application/json' \
  -d '{"title":"first","body":"hello"}'
curl localhost:8080/api/notes
```

## Open in IntelliJ

IntelliJ can open this as a plain project even without the Python plugin,
but for real editing (autocomplete, run configs, debugging):

1. **File → New → Project from Existing Sources** → pick this folder.
2. If the Python plugin is installed: **File → Project Structure → SDK** →
   add a Python 3.12 interpreter (a venv is fine:
   `python3 -m venv .venv && source .venv/bin/activate && pip install -r app/requirements-dev.txt`).
3. To run `app.py` directly against Redis: start only Redis
   (`docker compose up -d redis`) and set `REDIS_HOST=localhost` on the run
   configuration's environment variables.

## Push to Git

```bash
git init -b main
git add .
git commit -m "notes-lite: 3-container app with Jenkins CI/CD"
git remote add origin git@github.com:<you>/notes-lite.git
git push -u origin main
```

## Jenkins

One pipeline (`Jenkinsfile`): test → build image → push to Docker Hub → deploy
(`docker compose up -d`) → smoke test.

1. Add a Docker Hub credential with ID `dockerhub-creds`.
2. Edit `DOCKERHUB_USER` near the top of `Jenkinsfile`.
3. New Item → **Pipeline** → Pipeline script from SCM → point at this repo.
4. The agent needs `docker`, `docker compose`, `python3`, `curl`, `git`.

## API

| Method   | Path              | Body                        |
|----------|-------------------|------------------------------|
| `GET`    | `/api/notes`      | —                            |
| `GET`    | `/api/notes/{id}` | —                            |
| `POST`   | `/api/notes`      | `{"title":"…","body":"…"}`  |
| `DELETE` | `/api/notes/{id}` | —                            |

## Layout

```
.
├── Jenkinsfile
├── docker-compose.yml
├── smoke-test.sh
├── nginx/nginx.conf
└── app/
    ├── app.py
    ├── test_app.py
    ├── requirements.txt
    ├── requirements-dev.txt
    └── Dockerfile
```
