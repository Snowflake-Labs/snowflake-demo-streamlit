"use client"

import { useCallback, useEffect, useRef, useState } from "react"

const TOP_NAV = ["Dashboards", "Reports", "Data Catalog", "Admin"]

const SIDEBAR = [
  { group: "Dashboards", items: ["Executive Overview", "Sales Performance", "Inventory", "Aftersales"] },
  { group: "Tools", items: ["Data Explorer", "Reports", "Alerts"] },
]

const ACTIVE = "Sales Performance"

const KPIS = [
  { label: "Units Sold (MTD)", val: "48,210", delta: "+6.4%", up: true },
  { label: "Revenue (MTD)", val: "$2.91B", delta: "+3.1%", up: true },
  { label: "Avg. Selling Price", val: "$60,380", delta: "-1.2%", up: false },
  { label: "Active Dealers", val: "3,742", delta: "+0.8%", up: true },
]

export default function Page() {
  const [embedUrl, setEmbedUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const minted = useRef(false) // embed code is single-use; mint once (StrictMode guard)

  const loadEmbed = useCallback(() => {
    setError(null)
    setEmbedUrl(null)
    fetch("/api/embed-url")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => setEmbedUrl(d.embedUrl))
      .catch(() => setError("Could not reach the analytics service."))
  }, [])

  useEffect(() => {
    if (minted.current) return
    minted.current = true
    loadEmbed()
  }, [loadEmbed])

  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="logo">A</span>
          ACME <span>Analytics</span>
        </div>
        <nav className="topnav">
          {TOP_NAV.map((item) => (
            <a key={item} href="#" className={item === "Dashboards" ? "active" : ""}>
              {item}
            </a>
          ))}
        </nav>
        <div className="user">
          <div className="avatar">MK</div>
          <div className="user-meta">
            <span className="name">Mara Klein</span>
            <span className="role">Sales Analytics</span>
          </div>
        </div>
      </header>

      <div className="body">
        <aside className="sidebar">
          {SIDEBAR.map(({ group, items }) => (
            <div key={group}>
              <div className="nav-label">{group}</div>
              {items.map((name) => (
                <a key={name} href="#" className={`nav-item${name === ACTIVE ? " active" : ""}`}>
                  <span className="dot-icon" />
                  {name}
                </a>
              ))}
            </div>
          ))}
        </aside>

        <main className="content">
          <div className="page-head">
            <div>
              <h1>Sales Performance</h1>
              <div className="sub">Live vehicle sales and revenue analytics across global markets</div>
            </div>
          </div>

          <div className="kpis">
            {KPIS.map((k) => (
              <div className="kpi" key={k.label}>
                <span className="label">{k.label}</span>
                <span className="val">{k.val}</span>
                <span className={`delta ${k.up ? "up" : "down"}`}>{k.delta} vs. last month</span>
              </div>
            ))}
          </div>

          <section className="embed-card">
            <div className="embed-head">
              <span className="embed-title">Sales Intelligence</span>
              <span className="badge">
                <span className="live-dot" />
                Live · Streamlit in Snowflake
              </span>
              <div className="spacer" />
              <button className="link-btn" onClick={loadEmbed}>
                Refresh
              </button>
            </div>
            <div className="embed-body">
              {error ? (
                <div className="embed-state">
                  {error}
                  <button className="btn btn-primary" onClick={loadEmbed}>
                    Try again
                  </button>
                </div>
              ) : embedUrl ? (
                <iframe
                  src={embedUrl}
                  title="Embedded Streamlit App"
                  allow="clipboard-read; clipboard-write; fullscreen"
                />
              ) : (
                <div className="embed-state">Loading…</div>
              )}
            </div>
          </section>
        </main>
      </div>
    </div>
  )
}
