# Django vs FastAPI - URL/ルーティングの違い解説

## 🎯 目的

DjangoとFastAPIで**同じAPI**を作る場合、URL設定がどう違うかを比較します。

---

## 📚 例：ユーザー管理APIを作る

以下のAPIエンドポイントを作ると仮定します：

```
GET  /api/v1/users       ユーザー一覧取得
GET  /api/v1/users/{id}  ユーザー詳細取得
POST /api/v1/users       ユーザー作成
PUT  /api/v1/users/{id}  ユーザー更新
```

---

## 🔴 Django REST Frameworkの場合

### **ファイル構成**

```
myproject/
├── myproject/
│   ├── settings.py       # プロジェクト設定
│   └── urls.py          # ★ メインのURL設定ファイル
├── users/
│   ├── models.py        # Userモデル
│   ├── serializers.py   # Serializer
│   ├── views.py         # ViewSet
│   └── urls.py          # ★ usersアプリのURL設定ファイル
└── manage.py
```

### **ステップ1: `users/views.py` - ViewSet作成**

```python
# users/views.py
from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
```

### **ステップ2: `users/urls.py` - アプリのURL設定**

```python
# users/urls.py （★ このファイルを新規作成する必要がある）
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

# ★ Routerを作成してViewSetを登録
router = DefaultRouter()
router.register('', UserViewSet, basename='user')

# ★ urlpatternsに変換
urlpatterns = [
    path('', include(router.urls)),
]
```

**`urlpatterns` が何をしているか？**
- Djangoは `urlpatterns` というリストに、URLパターンと処理（View）の対応を登録する
- `path('', include(router.urls))` は「このURLにアクセスされたら、routerが管理するURLを使う」という意味

### **ステップ3: `myproject/urls.py` - メインのURL設定**

```python
# myproject/urls.py （★ プロジェクトのメインURLファイル）
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # ★ /api/v1/users にアクセスされたら、users/urls.py にルーティングを委譲
    path('api/v1/users/', include('users.urls')),
]
```

**`include()` が何をしているか？**
- `include('users.urls')` は「users/urls.pyに書かれたURLパターンをここに含める」という意味
- つまり、**URL設定が分散**している

### **結果：最終的なURLマッピング**

```
GET  /api/v1/users/       → UserViewSet.list()
GET  /api/v1/users/{id}/  → UserViewSet.retrieve()
POST /api/v1/users/       → UserViewSet.create()
PUT  /api/v1/users/{id}/  → UserViewSet.update()
```

### **🔥 問題点**

1. **ファイルが分散**：`myproject/urls.py` + `users/urls.py` の2ファイル
2. **`include()` の連鎖**：メインURL → アプリURL → Router → ViewSet
3. **暗黙的な命名**：ViewSetの `.list()`, `.retrieve()` などのメソッド名は自動生成
4. **Router の理解が必要**：`DefaultRouter` が裏でURL生成している

---

## 🟢 FastAPIの場合

### **ファイル構成**

```
myproject/
├── app/
│   ├── main.py          # ★ これだけ！
│   ├── models.py        # Userモデル
│   ├── schemas.py       # Pydanticモデル
│   └── routers/
│       └── users.py     # ★ ユーザーAPIの定義
```

### **ステップ1: `app/routers/users.py` - ルーター作成**

```python
# app/routers/users.py
from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

# ★ 明示的に関数名とHTTPメソッド・URLを定義
@router.get("/", response_model=List[UserResponse])
def get_users():
    """ユーザー一覧取得"""
    return db.query(User).all()

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    """ユーザー詳細取得"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate):
    """ユーザー作成"""
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate):
    """ユーザー更新"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)

    db.commit()
    return db_user
```

### **ステップ2: `app/main.py` - メインファイルで登録**

```python
# app/main.py （★ これだけでOK！）
from fastapi import FastAPI
from app.routers import users

app = FastAPI()

# ★ ルーターを登録（include不要）
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
```

**`app.include_router()` が何をしているか？**
- `users.router` に定義された全てのエンドポイントを `/api/v1/users` 配下に登録
- `tags=["Users"]` はAPI仕様書でグループ化するためのタグ

### **結果：最終的なURLマッピング**

```
GET  /api/v1/users/       → get_users()
GET  /api/v1/users/{id}   → get_user()
POST /api/v1/users/       → create_user()
PUT  /api/v1/users/{id}   → update_user()
```

### **✅ メリット**

1. **1ファイルで完結**：`main.py` だけ見れば全体像が分かる
2. **明示的**：関数名が明確（`get_users`, `create_user` など）
3. **Router不要**：`@router.get("/")` で直接定義
4. **include()の連鎖なし**：シンプルに `app.include_router()` で登録

---

## 🔍 Djangoの `include()` の問題点を図解

### **Djangoの場合（複雑）**

```
リクエスト: GET /api/v1/users/
    ↓
myproject/urls.py
    urlpatterns = [
        path('api/v1/users/', include('users.urls')),  # ★ users.urls に委譲
    ]
    ↓
users/urls.py
    urlpatterns = [
        path('', include(router.urls)),  # ★ router.urls に委譲
    ]
    ↓
router (DefaultRouter)
    router.register('', UserViewSet)  # ★ ViewSetに委譲
    ↓
UserViewSet.list()  # ★ 最終的にここが呼ばれる
```

**問題：3段階の委譲が発生**

### **FastAPIの場合（シンプル）**

```
リクエスト: GET /api/v1/users/
    ↓
main.py
    app.include_router(users.router, prefix="/api/v1/users")
    ↓
users.router
    @router.get("/")
    def get_users():  # ★ 直接ここが呼ばれる
```

**シンプル：1段階で完了**

---

## 🎯 あなたのDjangoプロジェクトの具体例

### **あなたのコード（atma/urls.py:14-41）**

```python
# ★ メインのURLファイル
urlpatterns = [
    path("api-admin/", admin.site.urls),
    path("accounts/", include(atma.infrastructure.accounts.urls)),  # ★ 委譲1
    path("db_info/", include("atma.infrastructure.db_info.urls")),   # ★ 委譲2
    # ... 省略 ...
]

# OnsiteUser向け
urlpatterns += [
    path("corporations/", include("atma.services.corporations.interfaces.rest")),  # ★ 委譲3
    path("mvps/", include("atma.services.mvps.interfaces.rest")),                 # ★ 委譲4
    # ... さらに10個以上 ...
]

# 企業管理者/マネジャー評価者向け
urlpatterns += [
    path("tenant/my/users/auth/", include("atma.services.users_auth.interfaces.rest.tenant")),  # ★ 委譲5
    # ... さらに多数 ...
]
```

**何が起きているか？**

1. `urlpatterns` リストに、URLパターンを登録している
2. `include()` で、各サービスの `urls.py` に処理を委譲している
3. **18個以上のサービス × 各URL設定ファイル = 管理が大変**

### **FastAPIで書くと**

```python
# main.py （★ これだけ！）
from fastapi import FastAPI
from app.routers import (
    accounts,
    db_info,
    corporations,
    mvps,
    users_auth,
    # ... 他のルーター ...
)

app = FastAPI()

# ★ シンプルに登録するだけ
app.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
app.include_router(db_info.router, prefix="/db_info", tags=["DB Info"])

# OnsiteUser向け
app.include_router(corporations.router, prefix="/corporations", tags=["Corporations"])
app.include_router(mvps.router, prefix="/mvps", tags=["MVPs"])

# 企業管理者/マネジャー評価者向け
app.include_router(users_auth.router, prefix="/tenant/my/users/auth", tags=["Tenant Auth"])

# ... 全てmain.pyで一元管理 ...
```

**違い：**

| Django | FastAPI |
|--------|---------|
| `urlpatterns` リストに `include()` で委譲 | `app.include_router()` で直接登録 |
| 各サービスに `urls.py` ファイルが必要 | `router` オブジェクトだけでOK |
| 3段階の委譲（main urls → app urls → router → view） | 1段階で完了（main → router → 関数） |
| URL設定が分散（メイン + 各サービス） | main.py で一元管理 |

---

## 📊 コード量の比較

### **Django: 3ファイル必要**

```python
# 1. myproject/urls.py
urlpatterns = [
    path('api/v1/users/', include('users.urls')),
]

# 2. users/urls.py （★ 新規作成必要）
router = DefaultRouter()
router.register('', UserViewSet)
urlpatterns = [path('', include(router.urls))]

# 3. users/views.py
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
```

**合計：約15行**

### **FastAPI: 2ファイル**

```python
# 1. main.py
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])

# 2. routers/users.py
@router.get("/")
def get_users():
    return db.query(User).all()

@router.post("/")
def create_user(user: UserCreate):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    return db_user
```

**合計：約10行（30%減）**

---

## 🎯 結論

### **Django の `urlpatterns` + `include()`**
- URLパターンをリストに登録する仕組み
- `include()` で他のファイルに処理を委譲できる
- **問題**：URL設定が複数ファイルに分散 → 全体像が見えにくい

### **FastAPI の `app.include_router()`**
- ルーターを直接登録する仕組み
- **メリット**：main.py だけで全体像が分かる
- **メリット**：ファイル分散なし → シンプル

---

**あなたの疑問への答え：**

> `urlpatterns` は何をしているの？

→ **DjangoでURLと処理（View）を紐付けるリスト**。`path()` や `include()` で定義したパターンを登録している。

> FastAPIで書くとどうなるの？

→ **`app.include_router()` で1行で完結**。`urlpatterns` も `include()` も不要。

---

**実際のコード比較：**

| Django（あなたのコード） | FastAPI |
|------------------------|---------|
| `path("corporations/", include("atma.services.corporations.interfaces.rest"))` | `app.include_router(corporations.router, prefix="/corporations", tags=["Corporations"])` |

**同じことをしているが、FastAPIの方が:**
- ファイル分散なし（include不要）
- tagsでAPI仕様書が自動グループ化
- main.pyで全体像が見える
