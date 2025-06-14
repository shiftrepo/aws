import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'GitPlayground - 楽しく学ぶGit操作',
  description: 'チーム開発でのGit操作を楽しく学べるインタラクティブサイト',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <body className={inter.className}>
        <main className="container">
          {children}
        </main>
      </body>
    </html>
  );
}