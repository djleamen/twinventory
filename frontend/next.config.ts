import type { NextConfig } from "next"

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        // Meshy's file server sends no CORS headers, so the browser can't load its
        // models directly. Requests to /meshy-assets/... are fetched by the Next.js
        // server instead, and the browser sees them as coming from this site.
        source: "/meshy-assets/:path*",
        destination: "https://assets.meshy.ai/:path*",
      },
    ]
  },
}

export default nextConfig
