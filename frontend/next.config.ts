import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // API URL (バックエンド)
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },

  // Standalone モード: Dockerで最適化されたビルドを生成
  // node_modules を含めずに、必要なファイルだけをバンドル
  output: "standalone",
};

export default nextConfig;
