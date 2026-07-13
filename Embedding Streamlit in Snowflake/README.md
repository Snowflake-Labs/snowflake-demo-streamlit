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
PAT; swap the `createConnection` config in `server.mjs` to use Key-Pair or WIF
(see the routes in the other folders).

The `demo/` folder is a fuller example: a styled analytics portal (Next.js) that
embeds the Streamlit app as a live panel, using the same PAT flow. Start with an
`examples/` folder to learn the mechanics; look at `demo/` to see it in a
realistic UI.

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

Each app reuses **one long-lived Snowflake connection** across requests (see
`getConnection` in the route). The embed code is bound to the session that minted
it, so that session must stay alive until the browser redeems the code — opening
and closing a connection per request causes the embed to fail with a `401`.

Only two files carry the real logic in each app:
- `app/api/embed-url/route.ts` — connects to Snowflake and runs the system function.
- `app/page.tsx` — fetches `/api/embed-url` and drops the result into an `<iframe>`.

## Snowflake setup

Before running a sample, complete the one-time account setup — enabling the
embedding feature, allow-listing your parent origin, and creating the minting
role and per-method credentials (PAT, key-pair JWT, or WIF). See the docs:

[Embed a Streamlit in Snowflake app](https://docs.snowflake.com/en/LIMITEDACCESS/streamlit/embed-streamlit-app)

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
