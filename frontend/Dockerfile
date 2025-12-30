# ============================================================
# Dockerイメージのベース指定 - Next.js フロントエンド
# ============================================================
# Node.js 20 の Alpine Linux版（軽量）
FROM node:20-alpine AS base

# ============================================================
# 依存関係のインストール
# ============================================================
FROM base AS deps

# 作業ディレクトリ
WORKDIR /app

# package.json と package-lock.json をコピー
# キャッシュ最適化のため先にコピー
COPY package*.json ./

# 依存関係をインストール
# --frozen-lockfile: package-lock.jsonを厳密に守る
RUN npm ci

# ============================================================
# ビルダー - Next.jsアプリケーションをビルド
# ============================================================
FROM base AS builder

WORKDIR /app

# node_modules をコピー
COPY --from=deps /app/node_modules ./node_modules

# アプリケーションコードをコピー
COPY . .

# Next.jsのテレメトリを無効化（オプション）
ENV NEXT_TELEMETRY_DISABLED=1

# Next.jsアプリケーションをビルド
# 本番用の最適化されたビルドを作成
RUN npm run build

# ============================================================
# ランナー - 本番環境で実行
# ============================================================
FROM base AS runner

WORKDIR /app

# 本番環境モード
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# セキュリティのため非rootユーザーを作成
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# 必要なファイルだけをコピー
COPY --from=builder /app/public ./public

# Next.jsの出力ファイルをコピー
# standalone モードを使用する場合は server.js も含める
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# 非rootユーザーに切り替え
USER nextjs

# ポート公開
EXPOSE 3000

# 環境変数
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Next.jsサーバーを起動
CMD ["node", "server.js"]

# ============================================================
# 開発環境用（docker-compose.ymlで使用）
# ============================================================
FROM base AS dev

WORKDIR /app

# 開発環境モード
ENV NODE_ENV=development

# package.json をコピー
COPY package*.json ./

# 依存関係をインストール（devDependencies含む）
RUN npm install

# アプリケーションコードはボリュームマウントで注入

# ポート公開
EXPOSE 3000

# 開発サーバーを起動（ホットリロード有効）
CMD ["npm", "run", "dev"]
