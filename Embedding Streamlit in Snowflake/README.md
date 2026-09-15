# Streamlit-in-Snowflake embedding samples

Minimal, copy-paste-ready examples that embed a **Streamlit-in-Snowflake**
app in an `<iframe>`. Each `examples/` folder is identical except for **how it
authenticates to Snowflake** to mint the embed URL:

| Folder                | Auth method                       | Best for                                  |
| --------------------- | --------------------------------- | ----------------------------------------- |
| `examples/pat`        | Programmatic Access Token (PAT)   | Simplest setup, service users             |
| `examples/keypair`    | Key-Pair JWT                      | Rotating RSA keys, no shared secrets      |
| `examples/wif`        | Workload Identity Federation (OIDC) | Cloud workloads with a federated JWT     |
| `examples/plain-node` | PAT, no framework                 | Zero-dependency reference (Node http + static HTML) |

`pat`, `keypair`, and `wif` are Next.js (App Router). `plain-node` is the same
flow with no framework — a Node `http` server that mints the URL and serves one
static HTML page — for anyone who wants the bare mechanics without React. It uses
PAT; swap the two auth headers in `server.mjs` to use Key-Pair or WIF (see the
routes in the other folders).

The `demo/` folder is a fuller example: a styled analytics portal (Next.js) that
embeds the Streamlit app as a live panel, using the same PAT flow. Start with an
`examples/` folder to learn the mechanics; look at `demo/` to see it in a
realistic UI.

All of them use the **Streamlit REST API** to mint the URL, so there is **no SQL
session and no Snowflake driver** — the only dependency is Next.js (`plain-node`
has none at all).

## How it works

```
Browser  ──GET /api/embed-url──▶  your server
                                      │  POST /api/v2/databases/{db}/schemas/{schema}
                                      │       /streamlits/{name}:generate-embed-url
                                      │  Authorization: Bearer <PAT | JWT | WIF.OIDC.…>
                                      │  { "parent_origin": "https://…" }
                                      ▼
                                 { "embed_url": "https://…" }
Browser  ◀──{ embedUrl }───────  your server
   │
   └──▶  <iframe src={embedUrl} />
```

The embed URL is minted **server-side** and is **single-use** — treat it as a bearer
credential. Its authorization code is valid for 10 minutes, is invalidated on first
redemption, and must not be logged or cached. Both sides of the fetch opt out of
caching: the route sets `dynamic = "force-dynamic"`, and the browser fetches with
`cache: "no-store"` so a reload always mints a fresh code instead of replaying a
spent one.

Only two files carry the real logic in each app:
- `app/api/embed-url/route.ts` — POSTs to the endpoint with the right auth header.
- `app/page.tsx` — fetches `/api/embed-url` and drops the result into an `<iframe>`.

## Authentication

Each method is just a different `Authorization` header on the same request:

| Method | `Authorization` | `X-Snowflake-Authorization-Token-Type` |
| ------ | --------------- | -------------------------------------- |
| PAT | `Bearer <pat_secret>` | `PROGRAMMATIC_ACCESS_TOKEN` |
| Key-Pair | `Bearer <RS256 JWT>` | `KEYPAIR_JWT` |
| WIF | `Bearer WIF.OIDC.<token>` | `WORKLOAD_IDENTITY_FEDERATION` |

The app is resolved under the role in the **required** `X-Snowflake-Role` header —
there is no `DEFAULT_ROLE` or `PUBLIC` fallback, and a missing header is rejected. That
role must hold `USAGE` and `EMBED` on the app. A missing app and a role without `USAGE`
both return the same **`403 FORBIDDEN`** ("Streamlit does not exist or you do not have
access to it"), so app existence isn't leaked. Holding `USAGE` but not `EMBED` is a
distinct `403` ("Role does not have the EMBED privilege on this Streamlit").

The Key-Pair sample builds its JWT with Node's built-in `crypto` (no `jsonwebtoken`
dependency): SHA-256 fingerprint of the DER public key, `iss = ACCOUNT.USER.SHA256:<fp>`,
`sub = ACCOUNT.USER`, RS256-signed, max 1-hour lifetime.

## Snowflake setup

For the full account setup — enabling the embedding feature, allow-listing your
parent origin, and creating the minting role and credentials — see
[Embed a Streamlit in Snowflake app](https://docs.snowflake.com/en/LIMITEDACCESS/streamlit/embed-streamlit-app).
The short version follows.

### One-time setup (all methods)

Run as `ACCOUNTADMIN`. Two things must be true: the minting role holds `USAGE` and
`EMBED` on the app, and the parent origin is on the embedding allow-list.

```sql
-- Allow-list the origin your page is served from
ALTER ACCOUNT SET STREAMLIT_EMBEDDING_CONTROLS = $$
allowed_embedding_domains:
  - https://your-domain.com
$$;

-- Minting role needs USAGE on the app + its DB/schema (no warehouse: the REST
-- endpoint requires no SQL session)
CREATE ROLE IF NOT EXISTS embed_minter;
GRANT USAGE ON DATABASE  streamlit_apps            TO ROLE embed_minter;
GRANT USAGE ON SCHEMA    streamlit_apps.public     TO ROLE embed_minter;
GRANT USAGE ON STREAMLIT streamlit_apps.public.my_app TO ROLE embed_minter;

-- EMBED authorizes the role to mint embed URLs for the app; USAGE alone only
-- allows viewing it in Snowflake, and minting returns 403
GRANT EMBED ON STREAMLIT streamlit_apps.public.my_app TO ROLE embed_minter;
```

### Per-method credential setup

#### PAT (`examples/pat`, `examples/plain-node`, `demo`)

```sql
CREATE USER IF NOT EXISTS embed_svc TYPE = SERVICE;
GRANT ROLE embed_minter TO USER embed_svc;
ALTER USER embed_svc SET DEFAULT_ROLE = embed_minter;

ALTER USER embed_svc ADD PROGRAMMATIC ACCESS TOKEN embed_pat
  ROLE_RESTRICTION = 'EMBED_MINTER' DAYS_TO_EXPIRY = 90;
-- copy the token_secret into SNOWFLAKE_PAT
```

#### Key-Pair JWT (`examples/keypair`)

```bash
# Generate an encrypted RSA key pair
openssl genrsa 2048 | openssl pkcs8 -topk8 -v2 aes-256-cbc -inform PEM -out rsa_key.p8
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
```

```sql
CREATE USER IF NOT EXISTS embed_svc TYPE = SERVICE;
GRANT ROLE embed_minter TO USER embed_svc;
ALTER USER embed_svc SET DEFAULT_ROLE = embed_minter;
ALTER USER embed_svc SET RSA_PUBLIC_KEY = 'MIIB... (contents of rsa_key.pub)';
-- point SNOWFLAKE_PRIVATE_KEY_PATH at rsa_key.p8
```

#### Workload Identity Federation — OIDC (`examples/wif`)

The workload's identity is the OIDC JWT you place in `SNOWFLAKE_WIF_TOKEN`; there is
no client-side username. Map the token's issuer/subject to a Snowflake user:

```sql
CREATE USER IF NOT EXISTS embed_svc TYPE = SERVICE
  WORKLOAD_IDENTITY = (
    TYPE = OIDC
    ISSUER = 'https://your-idp.example.com'
    SUBJECT = 'your-workload-subject'
  );
GRANT ROLE embed_minter TO USER embed_svc;
ALTER USER embed_svc SET DEFAULT_ROLE = embed_minter;
```

> WIF authenticates using a live federated token, so it runs in the cloud environment
> that issues it (or wherever you can supply a valid OIDC JWT) — not from a static
> local secret.

## Run any sample

```bash
cd examples/pat        # or keypair, or wif, or ../demo
npm install
cp .env.example .env.local   # fill in your values
npm run dev                  # http://localhost:3000
```

The `plain-node` variant has **no dependencies at all** — no `npm install` needed. Env
is loaded by Node's built-in `--env-file`, so it needs Node 20.6+:

```bash
cd examples/plain-node
cp .env.example .env.local   # fill in your values
npm start                    # http://localhost:3000
```

### Serving from the allow-listed origin (required for the iframe to load)

The iframe's `postMessage` lifecycle uses `PARENT_ORIGIN` as its target, so the page
must be served from **exactly** that origin. For local HTTPS testing:

```bash
brew install mkcert && mkcert -install
mkcert your-domain.com localhost 127.0.0.1
echo "127.0.0.1 your-domain.com" | sudo tee -a /etc/hosts

sudo $(which npx) next dev --port 443 --hostname your-domain.com \
  --experimental-https \
  --experimental-https-key ./your-domain.com+2-key.pem \
  --experimental-https-cert ./your-domain.com+2.pem
```

## Checklist / gotchas

- `ENABLE_STREAMLIT_EMBEDDING_FEATURE = true` on the account.
- `X-Snowflake-Role` is **required**, and that role needs `USAGE` and `EMBED` on the
  app. A missing app and a missing `USAGE` return the same **`403`** (existence isn't
  leaked); a missing `EMBED` is its own `403`.
- `PARENT_ORIGIN` is in `allowed_embedding_domains` **and** is the exact origin the
  browser loads the page from. A non-matching origin is rejected with `403` at mint
  time and again at render.
- Don't log, cache, or persist the embed URL — it is a bearer credential; mint one per
  embed session. The code it carries expires in 10 minutes and is single-use.
- The routes return a generic `500` and log the real error server-side. Don't echo
  upstream error text to the client: Snowflake's messages name the database, schema,
  app, and role, and confirm whether an app exists once the role can see it, while
  key-read failures disclose the private key's path. Read the server log when debugging.
- Add authentication to `/api/embed-url` before deploying. The samples leave it open
  for brevity; an unauthenticated mint endpoint lets anyone who can reach your page
  obtain a working embed URL for the app.
- `SNOWFLAKE_ACCOUNT_URL` must be the full account URL
  (`https://<account>.snowflakecomputing.com`, or your PrivateLink hostname).

### Endpoint availability

These samples target the resource-nested endpoint:

```
POST /api/v2/databases/{database}/schemas/{schema}/streamlits/{name}:generate-embed-url
```

It is recent, so verify it against your target account before demoing:

```bash
curl -s -o /dev/null -w '%{http_code} %{size_download}\n' -X POST \
  "$SNOWFLAKE_ACCOUNT_URL/api/v2/databases/DB/schemas/SCHEMA/streamlits/APP:generate-embed-url" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $SNOWFLAKE_PAT" \
  -H "X-Snowflake-Role: $SNOWFLAKE_ROLE" \
  -d '{"parent_origin":"https://your-domain.com"}'
# 200 <bytes>  -> implemented
# 204 0        -> build predates the implementation
# 404          -> route not present on this build
```

On an account where the endpoint isn't available yet, the SQL function
`SYSTEM$STREAMLIT_GENERATE_EMBED_URL('<app>', '<origin>')` is the working fallback —
run over the SQL API or a driver. Note it requires **literal constant arguments**;
bind parameters are rejected.
