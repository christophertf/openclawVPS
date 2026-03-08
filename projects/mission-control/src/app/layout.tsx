import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Sidebar from "./components/Sidebar";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "CLAW Mission Control",
  description:
    "Real-time operational dashboard for CLAW — projects, agents, memory, automation, and system activity.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <div className="app-layout">
          <Sidebar />
          <div className="main-content">
            <div className="bg-mesh" />
            <div className="scanline-overlay" />
            <main className="page-content">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
