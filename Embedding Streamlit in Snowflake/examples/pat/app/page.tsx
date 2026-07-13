"use client"

import { useEffect, useRef, useState } from "react"

export default function Page() {
  const [url, setUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const requested = useRef(false)

  useEffect(() => {
    if (requested.current) return // embed URL is single-use; mint once
    requested.current = true
    fetch("/api/embed-url")
      .then((r) => r.json())
      .then((d) => (d.embedUrl ? setUrl(d.embedUrl) : setError(d.error)))
      .catch((e) => setError(String(e)))
  }, [])

  if (error) return <p style={{ padding: 24, fontFamily: "system-ui" }}>Error: {error}</p>
  if (!url) return <p style={{ padding: 24, fontFamily: "system-ui" }}>Loading…</p>
  return (
    <iframe
      src={url}
      title="Streamlit in Snowflake"
      allow="clipboard-read; clipboard-write; fullscreen"
      style={{ border: 0, width: "100vw", height: "100vh" }}
    />
  )
}
