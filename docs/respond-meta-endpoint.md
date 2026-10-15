# Respondent JSON metadata endpoint — integration notes

This branch adds one small, read-only endpoint to the respondent side of the app
so external clients (for example a React Native front-end) can render a survey
and its gamification features, and submit responses, **without scraping the HTML
pages and without any change to how the existing pages work**.

Nothing else changes: no new dependencies, no database migrations, no model
changes, and the existing pages/endpoints behave exactly as before.

---

## 1. What was added

| Method | Path | Purpose |
| ------ | ---- | ------- |
| `GET` | `/surveys/respond/<uuid>/meta/` | Returns the survey, its `features` (gamification config) and its `questions` as JSON. |

Files touched:

- `surveys/views.py` — new `respond_survey_meta` view (`@require_GET @ensure_csrf_cookie`).
- `surveys/urls.py` — one new route.

The existing submit endpoint is **reused as-is**:

| Method | Path | Purpose |
| ------ | ---- | ------- |
| `POST` | `/surveys/respond/<uuid>/submit/` | Unchanged. Accepts a normal form-encoded body with keys `q_<question id>`. |

### Why `ensure_csrf_cookie`?

`submit_response` is protected by Django's CSRF middleware. A client that is not
a browser (no page with `{% csrf_token %}`) never receives a CSRF token, so its
POST would be rejected with `403`. Decorating the new `meta` endpoint with
`@ensure_csrf_cookie` makes it the single GET a client calls first to receive a
`csrftoken` cookie — which it then echoes back in the `X-CSRFToken` header on
submit. This keeps CSRF protection fully intact; it just hands legitimate clients
a token.

---

## 2. API contract

### `GET /surveys/respond/<uuid>/meta/`

`<uuid>` is the survey's `access_uuid`. Only **active** surveys respond; an
unknown or inactive survey returns `404` (same rule as the respond page).

Response `200` (`application/json`):

```json
{
  "survey": {
    "id": 1,
    "uuid": "ba8ca44c-dc28-481d-9730-4e12c4e281e0",
    "title": "First Hedonic System Adoption Survey",
    "description": "...",
    "is_hmsam": true,
    "access_code": "XIHJLP"
  },
  "features": { "points": { ... }, "mascot": { ... }, "progress": { ... }, "...": "..." },
  "questions": [
    {
      "id": 1,
      "text": "I find the system to be easy to learn how to use the features of this application / software.",
      "code": "PEU1",
      "type": "likert",
      "construct": "peou",
      "required": true,
      "options": [ { "id": 12, "text": "...", "order": 0 } ],
      "ratingMax": 5,
      "ratingStyle": "stars",
      "sectionTitle": "",
      "sectionNum": 1
    }
  ]
}
```

`features` is exactly `Survey.features` (the same JSON the builder writes).
`questions` mirrors the fields the builder already emits, in survey order.

### `POST /surveys/respond/<uuid>/submit/`  (unchanged)

Body: `application/x-www-form-urlencoded`, one entry per answered question keyed
by `q_<question id>`, e.g. `q_1=5&q_2=4&...`. Multi-select answers repeat the key.

Required header when CSRF is enforced: `X-CSRFToken: <token from the meta GET>`.
On success it returns the usual thank-you page (`200`). The server computes
points, records the `Response`/`Answer` rows, updates the respondent's level, and
sends the level-up email exactly as it does for the web flow.

---

## 3. What to do when you receive this PR

**Review**

1. Read the two-file diff (`surveys/views.py`, `surveys/urls.py`). It is additive
   only — nothing existing is modified.

**Before merging**

2. Run the checks:
   ```
   python manage.py check
   ```
   (No migrations to run — `manage.py migrate` is **not** needed.)

**After merging / when you pull it**

3. **Restart the dev server.** The server is normally started with `--noreload`,
   so it will not pick up the new URL until restarted:
   ```
   python manage.py runserver 127.0.0.1:8765
   ```
   (If you run it without `--noreload`, it reloads automatically.)

4. Smoke-test the endpoint against a real, active survey (replace `<uuid>`):
   ```
   curl -i http://127.0.0.1:8765/surveys/respond/<uuid>/meta/
   ```
   Expect `200`, `Content-Type: application/json`, and a `Set-Cookie: csrftoken=...`.

**Optional — only if a browser-based client on another origin will call it**

5. Cross-origin GETs from a *browser* need CORS headers. Native apps (React
   Native / Expo Go) do **not** need this. If you need it, install
   `django-cors-headers`, add it to `MIDDLEWARE`/`INSTALLED_APPS`, and allow the
   client origin in `CORS_ALLOWED_ORIGINS` (with `CORS_ALLOW_CREDENTIALS = True`
   so the CSRF cookie flows). This is **not** required for the current use case.

**No other action is required.** Existing pages, the builder, the dashboard and
the submit endpoint are untouched.

---

## 4. Verifying without touching real data

To exercise the submit path safely, run it inside a transaction that is rolled
back (as was done when developing this change):

```python
# manage.py shell
from django.db import transaction
from django.test import Client
from surveys.models import Survey, Response

s = Survey.objects.filter(is_active=True).first()
c = Client(SERVER_NAME='localhost', enforce_csrf_checks=True)

meta = c.get(f'/surveys/respond/{s.access_uuid}/meta/')
token = meta.cookies['csrftoken'].value

data = {f'q_{q.id}': '4' for q in s.questions.all() if q.question_type == 'likert'}

try:
    with transaction.atomic():
        r = c.post(f'/surveys/respond/{s.access_uuid}/submit/', data,
                   HTTP_X_CSRFTOKEN=token)
        print(r.status_code, Response.objects.filter(survey=s).count())
        transaction.set_rollback(True)
except Exception as e:
    print('error', e)
```

Expected: `200`, and the response count returns to its original value after the
rollback.

---

## 5. Rollback

The change is self-contained. To undo it, revert this commit (or remove the
`respond_survey_meta` view and its URL entry). Because it is additive, reverting
affects nothing else.

---

## 6. Context: who consumes this

This endpoint was added to support a proof-of-concept front-end (the "Feedora
showcase") built on a separate, headless form engine. That app:

- reads survey metadata from this endpoint (`GET …/meta/`);
- renders the survey and its gamification features with its own UI;
- submits responses back through the **existing** `POST …/submit/` endpoint, so
  all of your server-side logic (points, levels, emails, records) continues to be
  the single source of truth.

In other words, this PR deliberately does **not** introduce any new write path or
duplicate your business rules — it only exposes a read-only JSON view and makes
the CSRF token obtainable so a non-browser client can post to the endpoint you
already have.
