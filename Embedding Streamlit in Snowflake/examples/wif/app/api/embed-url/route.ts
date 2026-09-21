import { NextResponse } from "next/server"

export const runtime = "nodejs"
export const dynamic = "force-dynamic" // never cache the single-use embed URL

export async function GET() {
  try {
    return NextResponse.json({
      embedUrl: await mintEmbedUrl({
        // WIF.{AWS|AZURE|GCP|OIDC}.{token} — identity comes from the token, not a username
        Authorization: `Bearer WIF.OIDC.${process.env.SNOWFLAKE_WIF_TOKEN}`,
        "X-Snowflake-Authorization-Token-Type": "WORKLOAD_IDENTITY_FEDERATION",
      }),
    })
  } catch (e) {
    // Log the detail, return a generic message: upstream error text names objects
    // the caller may not be allowed to know exist.
    console.error("[embed-url] mint failed:", e)
    return NextResponse.json({ error: "Failed to mint embed URL" }, { status: 500 })
  }
}

async function mintEmbedUrl(auth: Record<string, string>): Promise<string> {
  const [db, schema, name] = process.env.STREAMLIT_APP!.split(".").map(encodeURIComponent)
  const res = await fetch(
    `${process.env.SNOWFLAKE_ACCOUNT_URL}/api/v2/databases/${db}/schemas/${schema}` +
      `/streamlits/${name}:generate-embed-url`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // Required: the app is resolved under this role. No default-role fallback.
        "X-Snowflake-Role": process.env.SNOWFLAKE_ROLE!,
        ...auth,
      },
      body: JSON.stringify({ parent_origin: process.env.PARENT_ORIGIN }),
    },
  )
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`)
  return (await res.json()).embed_url
}
