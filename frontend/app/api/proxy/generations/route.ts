export async function GET() {
  const base = process.env.BACKEND_HTTP_URL || 'http://backend:8000';
  const res = await fetch(`${base}/api/generations`, { cache: 'no-store' });
  const data = await res.json();
  return Response.json(data);
}
