import { NextResponse } from "next/server"
import snowflake from "snowflake-sdk"

export const runtime = "nodejs"
export const dynamic = "force-dynamic"

// The embed code is bound to the session that minted it, so reuse one
// long-lived connection rather than opening one per request.
let connPromise: Promise<snowflake.Connection> | null = null

function getConnection(): Promise<snowflake.Connection> {
  if (connPromise) return connPromise
  connPromise = new Promise((resolve, reject) => {
    const conn = snowflake.createConnection({
      account: process.env.SNOWFLAKE_ACCOUNT!,
      authenticator: "WORKLOAD_IDENTITY",
      workloadIdentityProvider: "OIDC",
      token: process.env.SNOWFLAKE_WIF_TOKEN!,
      role: process.env.SNOWFLAKE_ROLE,
      warehouse: process.env.SNOWFLAKE_WAREHOUSE,
    })
    conn.connect((err) => (err ? reject(err) : resolve(conn)))
  })
  connPromise.catch(() => (connPromise = null))
  return connPromise
}

export async function GET() {
  try {
    const conn = await getConnection()
    return NextResponse.json({ embedUrl: await mintEmbedUrl(conn) })
  } catch (e) {
    connPromise = null
    return NextResponse.json({ error: (e as Error).message }, { status: 500 })
  }
}

function mintEmbedUrl(conn: snowflake.Connection): Promise<string> {
  const app = process.env.STREAMLIT_APP!.replace(/'/g, "''")
  const origin = process.env.PARENT_ORIGIN!.replace(/'/g, "''")
  return new Promise((resolve, reject) => {
    conn.execute({
      sqlText: `SELECT SYSTEM$STREAMLIT_GENERATE_EMBED_URL('${app}', '${origin}')`,
      complete: (err, _stmt, rows) => {
        if (err) return reject(err)
        resolve(JSON.parse(Object.values(rows![0])[0] as string).embed_url)
      },
    })
  })
}
