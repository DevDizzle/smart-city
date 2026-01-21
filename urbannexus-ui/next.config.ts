import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/fastapi/:path*',
        destination: 'https://urbannexus-backend-550651297425.us-central1.run.app/:path*',
      },
    ];
  },
};

export default nextConfig;