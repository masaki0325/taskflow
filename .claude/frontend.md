# TaskFlow - Frontend (Next.js) コーディング規約

このファイルは、TaskFlowのフロントエンド開発における重要なルールを定義します。

## 技術スタック

```text
Next.js 15 + TypeScript
├── Next.js 15       React Framework (App Router)
├── TypeScript       型安全な開発
├── TailwindCSS      スタイリング
├── shadcn/ui        UIコンポーネントライブラリ
├── React Hook Form  フォーム管理
├── Zod              バリデーション
└── Jest + RTL       テストフレームワーク
```

---

## ディレクトリ構成

```text
frontend/
├── app/                    # Next.js App Router
│   ├── (auth)/            # 認証ページ（login, register）
│   └── (dashboard)/       # ダッシュボード（認証必須）
├── components/
│   ├── ui/                # shadcn/ui コンポーネント
│   └── [feature]/         # 機能別コンポーネント
├── lib/
│   ├── api/               # APIクライアント
│   ├── hooks/             # カスタムフック
│   └── utils.ts           # ヘルパー関数
├── types/                 # 型定義
└── __tests__/             # テスト
```

---

## コーディング規約

### 型定義を必ず使用

```typescript
// ✅ 正しい - 型定義を使用
interface Task {
  id: number;  // バックエンドと一致させる（number）
  title: string;
  status: "todo" | "in_progress" | "done";
}

// ❌ 間違い - any型を使用
const data: any = await fetchAPI('/tasks');
```

### ID型はnumberで統一

```typescript
// ✅ 正しい - バックエンド（int）と一致
export async function getTask(id: number): Promise<Task> {
  return fetchAPI<Task>(`/api/v1/tasks/${id}`);
}

// ❌ 間違い - stringを使用（バックエンドと不一致）
export async function getTask(id: string): Promise<Task> {
  return fetchAPI<Task>(`/api/v1/tasks/${id}`);
}
```

### useEffectの依存配列

```typescript
// ✅ 正しい - useEffect内で非同期処理を定義
useEffect(() => {
  let cancelled = false;

  const loadData = async () => {
    const data = await fetchAPI('/tasks');
    if (!cancelled) {
      setTasks(data);
    }
  };

  loadData();

  return () => {
    cancelled = true;  // クリーンアップ
  };
}, []);

// ❌ 間違い - 外部関数を依存配列に含めない
useEffect(() => {
  fetchTasks();  // fetchTasksが依存配列にない
}, []);
```

---

## セキュリティ要件（重要）

### 絶対に守ること

```typescript
// ❌ dangerouslySetInnerHTML（XSS脆弱性）
<div dangerouslySetInnerHTML={{ __html: userInput }} />

// ✅ テキストをそのまま表示
<div>{userInput}</div>

// ❌ 環境変数をクライアントに露出
const SECRET_KEY = process.env.SECRET_KEY;

// ✅ NEXT_PUBLIC_ プレフィックスをつける
const API_URL = process.env.NEXT_PUBLIC_API_URL;

// ❌ any型の使用
const data: any = await fetchAPI('/tasks');

// ✅ 適切な型定義
const data: Task[] = await fetchAPI<Task[]>('/tasks');
```

---

## Server Component vs Client Component

```typescript
// Server Component（デフォルト）
// - データフェッチに最適
// - SEOに有利
// - useState, useEffect は使えない
export default async function TasksPage() {
  const tasks = await getTasks();
  return <TaskList tasks={tasks} />;
}

// Client Component
// - インタラクティブな操作が必要
// - useState, useEffect が使える
// - ファイルの先頭に 'use client' を追加
"use client";

export default function TaskForm() {
  const [title, setTitle] = useState("");
  return <input value={title} onChange={(e) => setTitle(e.target.value)} />;
}
```

---

## よくある間違い

```typescript
// ❌ useCallbackなしで関数を依存配列に含める（無限ループ）
useEffect(() => {
  fetchTasks();  // 毎レンダーで新しい参照
}, [fetchTasks]);

// ✅ useCallbackでメモ化
const fetchTasks = useCallback(async () => {
  const data = await getTasks();
  setTasks(data);
}, []);

useEffect(() => {
  fetchTasks();
}, [fetchTasks]);

// ❌ ("use client") - 括弧が不要
("use client");

// ✅ "use client" - 正しい構文
"use client";
```

---

## 参考資料

- [Next.js公式ドキュメント](https://nextjs.org/docs)
- [React公式ドキュメント](https://react.dev/)
- [shadcn/ui公式ドキュメント](https://ui.shadcn.com/)

---

**フロントエンド開発時はこのガイドに従ってください！**
