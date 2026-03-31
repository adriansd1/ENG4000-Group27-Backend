import type { Metadata, Viewport } from "next";
import "./globals.css";
import ClientBody from "./ClientBody";

export const metadata: Metadata = {
  title: "ENG4000 Group 27 Energy Expert",
  description:
    "A local frontend for the Group 27 energy analytics backend. Ask natural-language questions, inspect generated SQL, and review returned rows.",
  icons: {
    icon: "https://ext.same-assets.com/2088670124/2347147756.png",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased">
        <ClientBody>{children}</ClientBody>
      </body>
    </html>
  );
}
