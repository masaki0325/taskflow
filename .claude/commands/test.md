# Test Generation Command

選択されたファイル、または最近変更されたファイルに対して、包括的なテストコードを作成してください。

## 実行方法

Task tool を使用して、テスト生成専用の general-purpose エージェントを起動してください。

エージェントへの指示内容:

```
TaskFlowプロジェクトの指定されたファイル、または最近変更されたファイルに対して、
包括的なテストコードを作成してください。

## テスト作成手順

1. テスト対象のファイルを特定（ユーザーが指定した場合はそれを、未指定の場合はgit diffで最近変更されたファイル）
2. 対象ファイルを読み込み、関数・コンポーネントを解析
3. 適切なテストファイルを作成

## テスト作成方針

### バックエンド（FastAPI）の場合

**使用ツール**: pytest

**テストファイル配置**: `backend/app/tests/test_*.py`

**テストすべき内容**:
- [ ] 正常系: 期待通りの入力で正しい結果が返る
- [ ] 異常系: 不正な入力でエラーハンドリングが動作
- [ ] 認証: 認証が必要なエンドポイントで未認証時に401が返る
- [ ] 境界値: エッジケースのテスト
- [ ] データベース: トランザクションのロールバック

**テンプレート**:
```python
# tests/test_example.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_正常系(client: TestClient, db: Session):
    \"\"\"正常系のテスト\"\"\"
    response = client.post("/api/v1/endpoint", json={...})
    assert response.status_code == 200
    assert response.json()["key"] == "expected_value"

def test_異常系_バリデーションエラー(client: TestClient):
    \"\"\"不正な入力でバリデーションエラーが返る\"\"\"
    response = client.post("/api/v1/endpoint", json={})
    assert response.status_code == 400

def test_認証なしでアクセス(client: TestClient):
    \"\"\"認証なしでアクセスすると401が返る\"\"\"
    response = client.get("/api/v1/protected")
    assert response.status_code == 401
```

### フロントエンド（Next.js）の場合

**使用ツール**: Jest + React Testing Library

**テストファイル配置**: `frontend/__tests__/**/*.test.tsx`

**テストすべき内容**:
- [ ] レンダリング: コンポーネントが正しく表示される
- [ ] インタラクション: ボタンクリック等のイベントが動作
- [ ] 状態管理: stateの変更が正しく反映される
- [ ] エッジケース: 空データ、エラー時の表示

**テンプレート**:
```typescript
// __tests__/components/Example.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Example from '@/components/Example';

describe('Example', () => {
  it('正しくレンダリングされる', () => {
    render(<Example />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });

  it('ボタンクリックで状態が変わる', () => {
    render(<Example />);
    const button = screen.getByRole('button');
    fireEvent.click(button);
    expect(screen.getByText('Changed Text')).toBeInTheDocument();
  });

  it('API呼び出しが成功する', async () => {
    render(<Example />);
    await waitFor(() => {
      expect(screen.getByText('Loaded Data')).toBeInTheDocument();
    });
  });
});
```

## カバレッジ目標
- 主要な機能: 80%以上
- クリティカルな機能（認証、決済等）: 100%

## 出力
- 作成したテストファイルのパス
- テストケース一覧
- カバーできていない部分があれば指摘
```

上記の指示でTask toolを起動し、テストコードを生成してユーザーに報告してください。
