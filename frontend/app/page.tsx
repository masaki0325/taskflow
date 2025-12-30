export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <main className="text-center px-4">
        <h1 className="text-6xl font-bold text-gray-900 mb-4">
          TaskFlow
        </h1>
        <p className="text-2xl text-gray-700 mb-8">
          タスク管理SaaS - チーム・個人向け
        </p>

        <div className="bg-white rounded-lg shadow-xl p-8 max-w-2xl">
          <h2 className="text-3xl font-semibold text-gray-800 mb-6">
            🚀 環境構築完了！
          </h2>

          <div className="space-y-4 text-left">
            <div className="flex items-start gap-3">
              <span className="text-2xl">✅</span>
              <div>
                <h3 className="font-semibold text-lg">Next.js 15</h3>
                <p className="text-gray-600">React 19 + TypeScript + App Router</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <span className="text-2xl">✅</span>
              <div>
                <h3 className="font-semibold text-lg">Tailwind CSS</h3>
                <p className="text-gray-600">ユーティリティファーストCSS</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <span className="text-2xl">✅</span>
              <div>
                <h3 className="font-semibold text-lg">Docker環境</h3>
                <p className="text-gray-600">コンテナ化された開発環境</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <span className="text-2xl">✅</span>
              <div>
                <h3 className="font-semibold text-lg">FastAPI Backend</h3>
                <p className="text-gray-600">http://localhost:8000 で稼働中</p>
              </div>
            </div>
          </div>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-gray-600 mb-4">APIドキュメント:</p>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
            >
              Swagger UI を開く →
            </a>
          </div>
        </div>

        <p className="mt-8 text-gray-500">
          Port 3000 で起動中 | Next.js フロントエンド
        </p>
      </main>
    </div>
  );
}
