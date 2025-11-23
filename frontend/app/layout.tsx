import type { Metadata } from "next";
import "./globals.css";
import { LocaleProvider } from "@/hooks/useLocale";
import { ThemeProvider } from "@/hooks/useTheme";
import ClientLayout from "@/components/ClientLayout";

export const metadata: Metadata = {
  title: "Top-TieR Global HUB AI",
  description: "OSINT platform with bilingual support and dark theme",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html suppressHydrationWarning>
      <body className="antialiased">
        <ThemeProvider>
          <LocaleProvider>
            <ClientLayout>
              {children}
            </ClientLayout>
          </LocaleProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
