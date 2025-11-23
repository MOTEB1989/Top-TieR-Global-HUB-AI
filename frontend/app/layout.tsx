import type { Metadata } from "next";
import "./globals.css";
import { LocaleProvider } from "@/hooks/useLocale";
import { ThemeProvider } from "@/hooks/useTheme";
import Navigation from "@/components/Navigation";

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
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased">
        <ThemeProvider>
          <LocaleProvider>
            <Navigation />
            <main className="min-h-screen bg-white dark:bg-gray-900">
              {children}
            </main>
          </LocaleProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
