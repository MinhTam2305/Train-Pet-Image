Quick deploy notes

1) Prepare local repo

   - Create venv, install deps, run smoke test (see README.md)

2) Commit & push

   - Use `init_repo.ps1` to create initial commit, then add remote and push.

3) Render (Docker)

   - Connect your GitHub repo to Render and pick the repository.
   - Choose "Docker" as the service type (Render will use the included Dockerfile).
   - Set Environment variables:
       - LIGHT_MODE = 1
       - FEATURES_FILE = features_light.pkl
   - If you need `/train`, upload `serviceAccountKey.json` as a secure file or set creds via Render secrets — do NOT commit it.

4) Railway / Heroku

   - Use Procfile; start command: `gunicorn app:app -b 0.0.0.0:$PORT`
   - Set env vars as above.

Security notes

- Do not commit `serviceAccountKey.json` or cert/key files. Use host secrets.
- Limit `/train` access or remove it from production if you don't want remote downloads.
