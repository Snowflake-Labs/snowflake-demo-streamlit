import { NextResponse } from "next/server"
import crypto from "node:crypto"
import fs from "node:fs"

export const runtime = "nodejs"
export const dynamic = "force-dynamic" // never cache the single-use embed URL

export async function GET() {
  try {
    return NextResponse.json({
      embedUrl: await mintEmbedUrl({
        Authorization: `Bearer ${keypairJwt()}`,
        "X-Snowflake-Authorization-Token-Type": "KEYPAIR_JWT",
      }),
    })
  } catch (e) {
    // Log the detail, return a generic message: upstream error text names objects
    // the caller may not be allowed to know exist, and key-read failures leak the
    // private key's path.
    console.error("[embed-url] mint failed:", e)
    return NextResponse.json({ error: "Failed to mint embed URL" }, { status: 500 })
  }
}

/** RS256 JWT: iss = ACCOUNT.USER.SHA256:<pubkey fingerprint>, sub = ACCOUNT.USER. */
function keypairJwt(): string {
  const passphrase = process.env.SNOWFLAKE_PRIVATE_KEY_PASSPHRASE
  const key = crypto.createPrivateKey({
    key: fs.readFileSync(process.env.SNOWFLAKE_PRIVATE_KEY_PATH!),
    ...(passphrase && { passphrase }),
  })
  const fingerprint = crypto
    .createHash("sha256")
    .update(crypto.createPublicKey(key).export({ type: "spki", format: "der" }))
    .digest("base64")

  // Account and user must be uppercase; periods in the account are invalid in a JWT.
  const account = process.env.SNOWFLAKE_ACCOUNT!.toUpperCase().replace(/\./g, "-")
  const qualifiedUser = `${account}.${process.env.SNOWFLAKE_USER!.toUpperCase()}`
  const now = Math.floor(Date.now() / 1000)

  const b64 = (o: object) => Buffer.from(JSON.stringify(o)).toString("base64url")
  const body = `${b64({ alg: "RS256", typ: "JWT" })}.${b64({
    iss: `${qualifiedUser}.SHA256:${fingerprint}`,
    sub: qualifiedUser,
    iat: now,
    exp: now + 3540, // max lifetime is 1 hour
  })}`
  return `${body}.${crypto.sign("RSA-SHA256", Buffer.from(body), key).toString("base64url")}`
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
