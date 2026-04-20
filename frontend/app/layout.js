import "./globals.css";

export const metadata = {
  title: "Project Management MVP",
  description: "Kanban project workspace"
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}