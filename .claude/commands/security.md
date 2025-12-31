# Security Check Command

プロジェクト全体のセキュリティ脆弱性をチェックしてください。

## 実行方法

Task tool を使用して、セキュリティチェック専用の general-purpose エージェントを起動してください。

エージェントへの指示内容:

```
TaskFlowプロジェクト全体のセキュリティ脆弱性を徹底的にチェックしてください。

## チェック手順

1. プロジェクト全体を探索（特にバックエンド、フロントエンド、環境設定）
2. 以下のセキュリティ観点でチェック
3. 脆弱性が見つかった場合は具体的な修正案を提示

## セキュリティチェック項目

### 🔐 認証・認可

**バックエンド（FastAPI）**:
- [ ] パスワードがbcryptでハッシュ化されているか
- [ ] JWTトークンの有効期限が適切か（Access: 15分、Refresh: 7日）
- [ ] Refresh Tokenがデータベース/Redisで管理されているか
- [ ] ログアウト時にRefresh Tokenが無効化されているか
- [ ] 認証が必要なエンドポイントで`Depends(get_current_user)`を使っているか

**フロントエンド（Next.js）**:
- [ ] トークンがHttpOnly Cookieで保存されているか（LocalStorageは脆弱）
- [ ] トークンが期限切れ時に自動でリフレッシュされるか
- [ ] 認証状態がContext/Storeで適切に管理されているか

**チェック対象ファイル**:
- `backend/app/core/security.py`
- `backend/app/api/deps.py`
- `backend/app/api/v1/auth.py`
- `frontend/lib/api/client.ts`
- `frontend/lib/context/AuthContext.tsx`

### 💉 インジェクション攻撃対策

**SQL Injection**:
- [ ] 生SQLを使っていないか（必ずSQLAlchemy ORMを使用）
- [ ] `db.execute(f"SELECT * FROM users WHERE id = {user_id}")`のような危険なコードがないか

**XSS (Cross-Site Scripting)**:
- [ ] `dangerouslySetInnerHTML`を使っていないか
- [ ] ユーザー入力をそのままHTMLに挿入していないか
- [ ] `<div>{userInput}</div>`のようにReactの自動エスケープを使っているか

**コマンドインジェクション**:
- [ ] ユーザー入力を直接シェルコマンドに渡していないか
- [ ] `os.system()`や`subprocess.run(shell=True)`を使っていないか

**チェック対象**:
- `backend/app/crud/*.py`（SQL）
- `frontend/components/**/*.tsx`（XSS）
- `backend/app/**/*.py`（コマンドインジェクション）

### 🔒 データ保護

**環境変数・機密情報**:
- [ ] `.env`ファイルが`.gitignore`に含まれているか
- [ ] `.env.example`に実際の値が含まれていないか
- [ ] `SECRET_KEY`が安全なランダム文字列か（最低32文字）
- [ ] APIキーやパスワードがコードに直書きされていないか

**データベース**:
- [ ] パスワードが平文で保存されていないか
- [ ] センシティブなデータが暗号化されているか

**チェック対象**:
- `.env`、`.env.example`
- `backend/app/core/config.py`
- `backend/app/models/*.py`

### 🌐 CORS設定

- [ ] 本番環境で`allow_origins=["*"]`になっていないか
- [ ] 許可するオリジンが環境変数で管理されているか
- [ ] `allow_credentials=True`の場合、オリジンをワイルドカードにしていないか

**チェック対象**:
- `backend/app/main.py`（CORSMiddleware設定）
- `.env.example`（ALLOWED_ORIGINS）

### 🔐 依存関係の脆弱性

- [ ] `requirements.txt`の依存関係に既知の脆弱性がないか
- [ ] `package.json`の依存関係に既知の脆弱性がないか
- [ ] 古いバージョンのライブラリを使っていないか

**チェック方法**:
- `backend/requirements.txt`を確認
- `frontend/package.json`を確認

### 📝 ログ・エラーメッセージ

- [ ] エラーメッセージに機密情報が含まれていないか
- [ ] スタックトレースが本番環境で表示されていないか
- [ ] ログに個人情報やパスワードが出力されていないか

**チェック対象**:
- `backend/app/api/v1/*.py`（エラーレスポンス）

### 🚪 認可（Authorization）

- [ ] ユーザーが他人のデータにアクセスできないか
- [ ] 管理者権限のチェックが適切か
- [ ] リソースの所有者チェックが実装されているか

**例（悪い例）**:
```python
# ❌ 誰でも他人のタスクを取得できる
@app.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.id == task_id).first()

# ✅ 自分のタスクのみ取得できる
@app.get("/tasks/{task_id}")
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id  # 所有者チェック
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

## 出力形式

以下の形式で報告してください:

### 🔴 Critical（重大な脆弱性 - 即座に修正が必要）
- ファイル名:行番号
- 脆弱性の種類
- 具体的な問題
- 修正案（コード例付き）

### 🟡 Warning（警告 - 改善推奨）
- ファイル名:行番号
- 潜在的なリスク
- 改善案

### 🟢 Secure（セキュアな実装）
- 評価できるセキュリティ対策

### 📊 セキュリティスコア
- チェック項目数 / 合格項目数
- 総合評価（A〜F）

## 注意事項
- OWASP Top 10を意識してチェック
- 具体的なファイル名と行番号を明記
- 必ず修正案を提示
```

上記の指示でTask toolを起動し、セキュリティチェック結果をユーザーに報告してください。
