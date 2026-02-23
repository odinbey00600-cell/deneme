export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body style={{ background: '#0b0e11', color: '#f0f0f0', fontFamily: 'Arial', margin: 20 }}>{children}</body>
    </html>
  );
}
