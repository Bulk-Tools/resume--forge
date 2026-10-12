# ResumeForge API

Backend API for the ResumeForge project (100 resume templates). Serves the
template registry, renders standalone A4 HTML resumes via `engine/renderer.py`,
exposes sample datasets, and validates resume payloads.

## Prerequisites

- Python 3.11+
- `pip install -r requirements.txt`

The API imports the engine via `sys.path` pointing at
`~/workspace/resume-forge/engine` and reads the template registry from
`~/workspace/resume-forge/templates/registry.json` when it exists (it starts
with an empty list and logs a warning if the file is missing).

## Run locally

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then open http://localhost:8000/health

### Docker

```bash
cd ~/workspace/resume-forge
docker build -f api/Dockerfile -t resumeforge-api .
docker run -p 8000:8000 resumeforge-api
```

## Endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| GET | `/health` | Health check -> `{"ok": true}` |
| GET | `/api/templates` | List templates (slug, name, persona, tags, layout, sample) |
| GET | `/api/templates/{slug}` | Full template config JSON (404 if unknown) |
| GET | `/api/templates/{slug}/html` | Rendered standalone HTML; `?sample=engineer\|designer\|executive\|general` overrides the template's dataset |
| GET | `/api/samples` | List sample dataset keys |
| GET | `/api/samples/{key}` | One sample dataset |
| POST | `/api/render` | Render any config with any data -> `{"html": "..."}` |
| POST | `/api/validate` | Validate a resume payload -> `{"ok": bool, "errors": [...]}` |

## Example

```bash
curl -s http://localhost:8000/health
# {"ok": true}

curl -s http://localhost:8000/api/templates | head -c 300

curl -s -X POST http://localhost:8000/api/render \
  -H 'Content-Type: application/json' \
  -d @payload.json

curl -s -X POST http://localhost:8000/api/validate \
  -H 'Content-Type: application/json' \
  -d '{"data":{"name":"Jane"}}'
# {"ok": false, "errors": ["missing or empty required field: title", ...]}
```
