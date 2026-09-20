import type { Metadata } from "next"
import { Fraunces, Instrument_Sans } from "next/font/google"
import { Providers } from "@/components/providers"
import "./globals.css"

const display = Fraunces({ variable: "--font-display", subsets: ["latin"], axes: ["opsz"] })
const body = Instrument_Sans({ variable: "--font-body", subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Twinventory",
  description: "See clothes on you before you buy them.",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col">
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
