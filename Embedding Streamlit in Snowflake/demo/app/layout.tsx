import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "ACME Analytics — Sales Performance",
  description: "Analytics portal with a Streamlit-in-Snowflake dashboard embedded as a live panel.",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
