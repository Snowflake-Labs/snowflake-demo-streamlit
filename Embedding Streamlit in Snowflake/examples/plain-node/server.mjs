import { createServer } from "node:http"
import { readFile } from "node:fs/promises"
import snowflake from "snowflake-sdk"

const PORT = process.env.PORT || 3000

// The embed code is bound to the session that minted it, so reuse one
// long-lived connection rather than opening one per request.
let connPromise = null

function getConnection() {
  if (connPromise) return connPromise
  connPromise = new Promise((resolve, reject) => {
    const conn = snowflake.createConnection({
      account: process.env.SNOWFLAKE_ACCOUNT,
      username: process.env.SNOWFLAKE_USER,
      authenticator: "PROGRAMMATIC_ACCESS_TOKEN",
      token: process.env.SNOWFLAKE_PAT,
      role: process.env.SNOWFLAKE_ROLE,
      warehouse: process.env.SNOWFLAKE_WAREHOUSE,
    })
    conn.connect((err) => (err ? reject(err) : resolve(conn)))
  })
  connPromise.catch(() => (connPromise = null))
  return connPromise
}

function mintEmbedUrl(conn) {
  const app = process.env.STREAMLIT_APP.replace(/'/g, "''")
  const origin = process.env.PARENT_ORIGIN.replace(/'/g, "''")
  return new Promise((resolve, reject) => {
    conn.execute({
      sqlText: `SELECT SYSTEM$STREAMLIT_GENERATE_EMBED_URL('${app}', '${origin}')`,
      complete: (err, _stmt, rows) => {
        if (err) return reject(err)
        resolve(JSON.parse(Object.values(rows[0])[0]).embed_url)
      },
    })
  })
}

createServer(async (req, res) => {
  if (req.url === "/api/embed-url") {
    try {
      const conn = await getConnection()
      const embedUrl = await mintEmbedUrl(conn)
      res.writeHead(200, { "content-type": "application/json" })
      res.end(JSON.stringify({ embedUrl }))
    } catch (e) {
      connPromise = null
      res.writeHead(500, { "content-type": "application/json" })
      res.end(JSON.stringify({ error: e.message }))
    }
    return
  }
  const html = await readFile(new URL("./index.html", import.meta.url))
  res.writeHead(200, { "content-type": "text/html" })
  res.end(html)
}).listen(PORT, () => console.log(`http://localhost:${PORT}`))
