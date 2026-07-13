# Streamlit-in-Snowflake embedding samples

Three minimal, copy-paste-ready Next.js apps that embed a **Streamlit-in-Snowflake**
app in an `<iframe>`. Each folder is identical except for **how it authenticates to
Snowflake** to mint the embed URL:

| Folder                | Auth method                       | Best for                                  |
| --------------------- | --------------------------------- | ----------------------------------------- |
| `examples/pat`        | Programmatic Access Token (PAT)   | Simplest setup, service users             |
| `examples/keypair`    | Key-Pair JWT                      | Rotating RSA keys, no shared secrets      |
| `examples/wif`        | Workload Identity Federation (OIDC) | Cloud workloads with a federated JWT     |
| `examples/plain-node` | PAT, no framework                 | Zero-dependency reference (Node http + static HTML) |

The first three are Next.js (App Router). `plain-node` is the same flow with no
framework — a Node `http` server that mints the URL and serves one static HTML page —
for anyone who wants the bare mechanics without React. It uses PAT; swap the
`createConnection` config in `server.mjs` to use Key-Pair or WIF (see the routes in the
other folders).

## How it works

```
Browser  ──GET /api/embed-url──▶  Next.js server (auth to Snowflake)
                                      │  SELECT SYSTEM$STREAMLIT_GENERATE_EMBED_URL(app, parent_origin)
                                      ▼
                                 { embed_url }
Browser  ◀──{ embedUrl }───────  server
   │
   └──▶  <iframe src={embedUrl} />
```

The embed URL is minted **server-side** and is **single-use** — the client mints one
per load and never caches it (`dynamic = "force-dynamic"`).

Only two files carry the real logic in each app:
- `app/api/embed-url/route.ts` — connects to Snowflake and runs the system function.
- `app/page.tsx` — fetches `/api/embed-url` and drops the result into an `<iframe>`.

## One-time Snowflake setup (all methods)

Run as `ACCOUNTADMIN`. Two things must be true: the minting role holds `USAGE` on the
app, and the parent origin is on the embedding allow-list.

```sql
-- Allow-list the origin your page is served from
ALTER ACCOUNT SET STREAMLIT_EMBEDDING_CONTROLS = $$
allowed_embedding_domains:
  - https://your-domain.com
$$;

-- Minting role needs USAGE on the app + its DB/schema + a warehouse
CREATE ROLE IF NOT EXISTS embed_minter;
GRANT USAGE ON DATABASE  streamlit_apps            TO ROLE embed_minter;
GRANT USAGE ON SCHEMA    streamlit_apps.public     TO ROLE embed_minter;
GRANT USAGE ON STREAMLIT streamlit_apps.public.my_app TO ROLE embed_minter;
GRANT USAGE ON WAREHOUSE embed_wh                  TO ROLE embed_minter;
```

## Per-method credential setup

### PAT (`examples/pat`)

```sql
CREATE USER IF NOT EXISTS embed_svc TYPE = SERVICE;
GRANT ROLE embed_minter TO USER embed_svc;
ALTER USER embed_svc SET DEFAULT_ROLE = embed_minter;

ALTER USER embed_svc ADD PROGRAMMATIC ACCESS TOKEN embed_pat
  ROLE_RESTRICTION = 'EMBED_MINTER' DAYS_TO_EXPIRY = 90;
-- copy the token_secret into SNOWFLAKE_PAT
```

### Key-Pair JWT (`examples/keypair`)

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

### Workload Identity Federation — OIDC (`examples/wif`)

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
cd examples/pat        # or keypair, or wif
npm install
cp .env.example .env.local   # fill in your values
npm run dev                  # http://localhost:3000
```

The `plain-node` variant is the same but framework-free (env is loaded by Node's
built-in `--env-file`, so it needs Node 20.6+):

```bash
cd examples/plain-node
npm install
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
- Minting role has `USAGE` on the app + DB + schema (missing USAGE looks like
  *"object does not exist"*, not a permission error).
- `PARENT_ORIGIN` is in `allowed_embedding_domains` **and** is the exact origin the
  browser loads the page from.
- Don't cache the embed URL — one is minted per load.
