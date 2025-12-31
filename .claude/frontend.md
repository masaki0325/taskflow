# TaskFlow - Frontend (Next.js) コーディング規約

このファイルは、TaskFlow のフロントエンド開発における詳細なルールとベストプラクティスを定義します。

## 📦 技術スタック

```
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

## 🗂️ ディレクトリ構成

```
frontend/
├── app/                         # Next.js App Router
│   ├── layout.tsx              # ルートレイアウト
│   ├── page.tsx                # ホームページ (/)
│   ├── globals.css             # グローバルスタイル
│   │
│   ├── (auth)/                 # 認証関連ページ（レイアウトグループ）
│   │   ├── layout.tsx          # 認証ページ用レイアウト
│   │   ├── login/
│   │   │   └── page.tsx        # ログインページ
│   │   ├── register/
│   │   │   └── page.tsx        # 登録ページ
│   │   └── reset-password/
│   │       └── page.tsx        # パスワードリセット
│   │
│   └── (dashboard)/            # ダッシュボード（認証必須）
│       ├── layout.tsx          # ダッシュボード用レイアウト
│       ├── page.tsx            # ダッシュボードTOP
│       ├── tasks/
│       │   ├── page.tsx        # タスク一覧
│       │   ├── [id]/
│       │   │   └── page.tsx    # タスク詳細
│       │   └── new/
│       │       └── page.tsx    # タスク新規作成
│       ├── projects/
│       │   ├── page.tsx        # プロジェクト一覧
│       │   └── [id]/
│       │       └── page.tsx    # プロジェクト詳細
│       └── settings/
│           └── page.tsx        # 設定ページ
│
├── components/                  # 再利用可能なコンポーネント
│   ├── ui/                     # shadcn/ui コンポーネント
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   └── dialog.tsx
│   │
│   ├── layouts/                # レイアウトコンポーネント
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── Footer.tsx
│   │
│   ├── tasks/                  # タスク関連コンポーネント
│   │   ├── TaskCard.tsx
│   │   ├── TaskList.tsx
│   │   ├── TaskForm.tsx
│   │   └── TaskFilters.tsx
│   │
│   └── auth/                   # 認証関連コンポーネント
│       ├── LoginForm.tsx
│       └── RegisterForm.tsx
│
├── lib/                         # ユーティリティ、ヘルパー
│   ├── api/                    # APIクライアント
│   │   ├── client.ts          # 共通HTTPクライアント
│   │   ├── auth.ts            # 認証API
│   │   ├── tasks.ts           # タスクAPI
│   │   └── users.ts           # ユーザーAPI
│   │
│   ├── hooks/                  # カスタムフック
│   │   ├── useAuth.ts         # 認証フック
│   │   ├── useTasks.ts        # タスクフック
│   │   └── useLocalStorage.ts # LocalStorageフック
│   │
│   ├── context/                # Reactコンテキスト
│   │   └── AuthContext.tsx    # 認証コンテキスト
│   │
│   └── utils.ts                # ヘルパー関数
│
├── types/                       # 型定義
│   ├── task.ts                 # タスク型
│   ├── user.ts                 # ユーザー型
│   ├── project.ts              # プロジェクト型
│   └── api.ts                  # API型
│
├── __tests__/                   # テスト
│   ├── components/
│   │   └── TaskCard.test.tsx
│   └── lib/
│       └── api/
│           └── tasks.test.ts
│
├── public/                      # 静的ファイル
│   ├── images/
│   └── icons/
│
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.ts
└── jest.config.js
```

---

## 🎯 コーディング規約

### 1. 型定義（types/）

```typescript
// types/task.ts

/**
 * タスクのステータス
 */
export type TaskStatus = "todo" | "in_progress" | "done";

/**
 * タスクの優先度
 */
export type TaskPriority = "low" | "medium" | "high";

/**
 * タスクのベース型
 */
export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  dueDate?: Date;
  projectId?: string;
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
}

/**
 * タスク作成リクエスト型
 */
export interface CreateTaskRequest {
  title: string;
  description?: string;
  priority: TaskPriority;
  dueDate?: string; // ISO 8601形式
  projectId?: string;
  tags?: string[];
}

/**
 * タスク更新リクエスト型
 */
export interface UpdateTaskRequest extends Partial<CreateTaskRequest> {
  status?: TaskStatus;
}
```

### 2. API クライアント（lib/api/）

```typescript
// lib/api/client.ts
import { cookies } from "next/headers";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * APIリクエストの共通設定
 */
async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_URL}${endpoint}`;

  // アクセストークンを取得（Server Componentの場合）
  const cookieStore = await cookies();
  const token = cookieStore.get("access_token")?.value;

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  // トークンがあれば追加
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(
        error.detail || `HTTP ${response.status}: ${response.statusText}`
      );
    }

    // 204 No Content の場合は null を返す
    if (response.status === 204) {
      return null as T;
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

export default fetchAPI;

// lib/api/tasks.ts
import fetchAPI from "./client";
import type { Task, CreateTaskRequest, UpdateTaskRequest } from "@/types/task";

/**
 * タスク一覧を取得
 */
export async function getTasks(): Promise<Task[]> {
  return fetchAPI<Task[]>("/api/v1/tasks");
}

/**
 * タスク詳細を取得
 */
export async function getTask(id: string): Promise<Task> {
  return fetchAPI<Task>(`/api/v1/tasks/${id}`);
}

/**
 * タスクを作成
 */
export async function createTask(data: CreateTaskRequest): Promise<Task> {
  return fetchAPI<Task>("/api/v1/tasks", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * タスクを更新
 */
export async function updateTask(
  id: string,
  data: UpdateTaskRequest
): Promise<Task> {
  return fetchAPI<Task>(`/api/v1/tasks/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/**
 * タスクを削除
 */
export async function deleteTask(id: string): Promise<void> {
  return fetchAPI<void>(`/api/v1/tasks/${id}`, {
    method: "DELETE",
  });
}
```

### 3. カスタムフック（lib/hooks/）

```typescript
// lib/hooks/useTasks.ts
import { useState, useEffect } from "react";
import { getTasks, createTask, updateTask, deleteTask } from "@/lib/api/tasks";
import type { Task, CreateTaskRequest, UpdateTaskRequest } from "@/types/task";

interface UseTasksReturn {
  tasks: Task[];
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  create: (data: CreateTaskRequest) => Promise<Task>;
  update: (id: string, data: UpdateTaskRequest) => Promise<Task>;
  remove: (id: string) => Promise<void>;
}

/**
 * タスク管理用カスタムフック
 */
export function useTasks(): UseTasksReturn {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getTasks();
      setTasks(data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const create = async (data: CreateTaskRequest): Promise<Task> => {
    const newTask = await createTask(data);
    setTasks((prev) => [newTask, ...prev]);
    return newTask;
  };

  const update = async (id: string, data: UpdateTaskRequest): Promise<Task> => {
    const updatedTask = await updateTask(id, data);
    setTasks((prev) =>
      prev.map((task) => (task.id === id ? updatedTask : task))
    );
    return updatedTask;
  };

  const remove = async (id: string): Promise<void> => {
    await deleteTask(id);
    setTasks((prev) => prev.filter((task) => task.id !== id));
  };

  return {
    tasks,
    loading,
    error,
    refetch: fetchTasks,
    create,
    update,
    remove,
  };
}
```

### 4. コンポーネント（components/）

```typescript
// components/tasks/TaskCard.tsx
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Task } from "@/types/task";

interface TaskCardProps {
  task: Task;
  onClick?: () => void;
}

/**
 * タスクカードコンポーネント
 */
export default function TaskCard({ task, onClick }: TaskCardProps) {
  const priorityColors = {
    low: "bg-blue-100 text-blue-800",
    medium: "bg-yellow-100 text-yellow-800",
    high: "bg-red-100 text-red-800",
  };

  const statusLabels = {
    todo: "未着手",
    in_progress: "進行中",
    done: "完了",
  };

  return (
    <Card
      className="cursor-pointer hover:shadow-lg transition-shadow"
      onClick={onClick}
    >
      <CardHeader>
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg">{task.title}</CardTitle>
          <Badge className={priorityColors[task.priority]}>
            {task.priority}
          </Badge>
        </div>
        {task.description && (
          <CardDescription className="line-clamp-2">
            {task.description}
          </CardDescription>
        )}
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>{statusLabels[task.status]}</span>
          {task.dueDate && (
            <span>期限: {new Date(task.dueDate).toLocaleDateString()}</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
```

### 5. ページコンポーネント（app/）

```typescript
// app/(dashboard)/tasks/page.tsx
"use client";

import { useTasks } from "@/lib/hooks/useTasks";
import TaskCard from "@/components/tasks/TaskCard";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";

/**
 * タスク一覧ページ
 */
export default function TasksPage() {
  const router = useRouter();
  const { tasks, loading, error } = useTasks();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p>読み込み中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-red-500">エラー: {error.message}</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">タスク一覧</h1>
        <Button onClick={() => router.push("/tasks/new")}>
          新規タスク作成
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            onClick={() => router.push(`/tasks/${task.id}`)}
          />
        ))}
      </div>

      {tasks.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">タスクがありません</p>
        </div>
      )}
    </div>
  );
}
```

---

## 🧪 テスト

### コンポーネントテスト

```typescript
// __tests__/components/TaskCard.test.tsx
import { render, screen, fireEvent } from "@testing-library/react";
import TaskCard from "@/components/tasks/TaskCard";
import type { Task } from "@/types/task";

describe("TaskCard", () => {
  const mockTask: Task = {
    id: "1",
    title: "テストタスク",
    description: "これはテスト用のタスクです",
    status: "todo",
    priority: "high",
    tags: [],
    createdAt: new Date("2024-01-01"),
    updatedAt: new Date("2024-01-01"),
  };

  it("タスクのタイトルと説明が表示される", () => {
    render(<TaskCard task={mockTask} />);

    expect(screen.getByText("テストタスク")).toBeInTheDocument();
    expect(screen.getByText("これはテスト用のタスクです")).toBeInTheDocument();
  });

  it("優先度バッジが正しく表示される", () => {
    render(<TaskCard task={mockTask} />);

    expect(screen.getByText("high")).toBeInTheDocument();
  });

  it("クリック時にonClickが呼ばれる", () => {
    const handleClick = jest.fn();
    render(<TaskCard task={mockTask} onClick={handleClick} />);

    fireEvent.click(screen.getByText("テストタスク"));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

---

## ⚠️ 注意事項

### やってはいけないこと

```typescript
// ❌ dangerouslySetInnerHTML の使用（XSS脆弱性）
<div dangerouslySetInnerHTML={{ __html: userInput }} />

// ✅ テキストをそのまま表示
<div>{userInput}</div>

// ❌ any型の使用
const data: any = await fetchAPI('/tasks');

// ✅ 適切な型定義
const data: Task[] = await fetchAPI<Task[]>('/tasks');

// ❌ useEffectの依存配列を空にする（ESLint警告）
useEffect(() => {
  fetchTasks();
}, []); // fetchTasks が依存配列に含まれていない

// ❌ メモ化されていないfetchTasksを依存配列に含めると無限ループが発生
useEffect(() => {
  fetchTasks(); // fetchTasksが毎レンダーで新しい参照になるため無限ループ
}, [fetchTasks]);

// ✅ パターン1: useCallbackでfetchTasksをメモ化し、依存配列に含める
const fetchTasks = useCallback(async () => {
  setLoading(true);
  try {
    const data = await api.getTasks();
    setTasks(data);
  } catch (error) {
    setError(error);
  } finally {
    setLoading(false);
  }
}, []); // fetchTasksの依存関係（この例ではなし）

useEffect(() => {
  fetchTasks();
}, [fetchTasks]); // メモ化されているため安全

// ✅ パターン2: マウント時のみ実行したい場合は、非同期ロジックをuseEffect内に移動
useEffect(() => {
  let cancelled = false;

  const loadTasks = async () => {
    setLoading(true);
    try {
      const data = await api.getTasks();
      if (!cancelled) {
        setTasks(data);
      }
    } catch (error) {
      if (!cancelled) {
        setError(error);
      }
    } finally {
      if (!cancelled) {
        setLoading(false);
      }
    }
  };

  loadTasks();

  return () => {
    cancelled = true; // クリーンアップでキャンセルフラグを設定
  };
}, []); // マウント時のみ実行

// ❌ 環境変数をクライアントに露出
const SECRET_KEY = process.env.SECRET_KEY; // NEXT_PUBLIC_がないとクライアントで使えない

// ✅ クライアント側で必要な環境変数には NEXT_PUBLIC_ をつける
const API_URL = process.env.NEXT_PUBLIC_API_URL;
```

### Server Component vs Client Component

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
("use client");

export default function TaskForm() {
  const [title, setTitle] = useState("");

  return <input value={title} onChange={(e) => setTitle(e.target.value)} />;
}
```

---

**フロントエンド開発時はこのガイドに従ってください！** 🚀
