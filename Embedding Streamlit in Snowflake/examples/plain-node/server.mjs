import { createServer } from "node:http"
import { readFile } from "node:fs/promises"

const PORT = process.env.PORT || 3000

async function mintEmbedUrl() {
  const [db, schema, name] = process.env.STREAMLIT_APP.split(".").map(encodeURIComponent)
  const res = await fetch(
    `${process.env.SNOWFLAKE_ACCOUNT_URL}/api/v2/databases/${db}/schemas/${schema}` +
      `/streamlits/${name}:generate-embed-url`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${process.env.SNOWFLAKE_PAT}`,
        "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN",
        // Required: the app is resolved under this role. No default-role fallback.
        "X-Snowflake-Role": process.env.SNOWFLAKE_ROLE,
      },
      body: JSON.stringify({ parent_origin: process.env.PARENT_ORIGIN }),
    },
  )
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`)
  return (await res.json()).embed_url
}

createServer(async (req, res) => {
  if (req.url === "/api/embed-url") {
    try {
      const embedUrl = await mintEmbedUrl()
      // Never cache: the embed code is single-use.
      res.writeHead(200, { "content-type": "application/json", "cache-control": "no-store" })
      res.end(JSON.stringify({ embedUrl }))
    } catch (e) {
      // Log the detail, return a generic message: upstream error text names objects
      // the caller may not be allowed to know exist.
      console.error("[embed-url] mint failed:", e)
      res.writeHead(500, { "content-type": "application/json" })
      res.end(JSON.stringify({ error: "Failed to mint embed URL" }))
    }
    return
  }
  const html = await readFile(new URL("./index.html", import.meta.url))
  res.writeHead(200, { "content-type": "text/html" })
  res.end(html)
}).listen(PORT, () => console.log(`http://localhost:${PORT}`))
