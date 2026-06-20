/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // The frontend talks to the backend via an absolute URL
  // (NEXT_PUBLIC_API_URL), so no rewrites/proxy are needed. This keeps the
  // app cleanly deployable to Netlify, Vercel, or any static/SSR host.
};
module.exports = nextConfig;
