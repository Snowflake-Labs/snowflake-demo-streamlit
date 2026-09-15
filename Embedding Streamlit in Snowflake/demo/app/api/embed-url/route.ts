import { NextResponse } from "next/server"

export const runtime = "nodejs"
export const dynamic = "force-dynamic" // never cache the single-use embed URL

// Mint an embed URL via the Streamlit REST API. No SQL session, so no warehouse.
async function mintEmbedUrl(): Promise<string> {
  const [db, schema, name] = process.env.STREAMLIT_APP!.split(".").map(encodeURIComponent)
  const url =
    `${process.env.SNOWFLAKE_ACCOUNT_URL}/api/v2/databases/${db}/schemas/${schema}` +
    `/streamlits/${name}:generate-embed-url`

  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      Authorization: `Bearer ${process.env.SNOWFLAKE_PAT!}`,
      "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN",
      // Required: the app is resolved under this role. No default-role fallback.
      "X-Snowflake-Role": process.env.SNOWFLAKE_ROLE!,
    },
    body: JSON.stringify({ parent_origin: process.env.PARENT_ORIGIN }),
  })

  // Note: never log the response body — it carries the embed URL, a bearer credential.
  if (res.status === 204) {
    throw new Error(
      "Endpoint returned 204 No Content — this account's build predates the mint " +
        "implementation. See the endpoint-availability notes in the README.",
    )
  }
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`)
  return (await res.json()).embed_url
}

export async function GET() {
  try {
    return NextResponse.json({ embedUrl: await mintEmbedUrl() })
  } catch (e) {
    // Log the detail, return a generic message: upstream error text names objects
    // the caller may not be allowed to know exist. Safe to log here — a failed
    // mint has no embed URL in it.
    console.error("[embed-url] mint failed:", e)
    return NextResponse.json({ error: "Failed to mint embed URL" }, { status: 500 })
  }
}
