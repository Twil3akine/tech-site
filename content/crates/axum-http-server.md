+++
title = "Rustでaxumを使ってHTTPサーバーを立てる（Router、Json、Stateなど）"
description = "Router へのルーティング登録から、JSON の受け渡し、State による状態共有までを、最小構成から順に組み立てる。"
date = 2026-11-06

[extra]
rust = "1.99.1"
crates = ["axum 0.8.9", "tokio 1.54.1", "serde 1.0.229", "serde_json 1.0.154"]

[taxonomies]
tags = ["axum", "tokio", "Web", "HTTP サーバー"]
+++

axum で HTTP サーバーを立てるには、Router にパスとハンドラを登録し、tokio の TcpListener と組み合わせて axum::serve で起動する。最小のサーバーから始め、ルーティング、JSON の受け渡し、状態の共有までを順に組み立てる。axum の全体像は[公式ドキュメント](https://docs.rs/axum/latest/axum/)を参照。

## 依存クレートを追加する

Cargo.toml の `[dependencies]` に次を追加する。tokio は `features = ["full"]` とし、マクロとランタイムを含む一式を有効にする。axum の Json は serde の機能を使うため、serde は derive つきで入れる。

```toml
[dependencies]
axum = "0.8"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

## 最小のサーバーを立てる

ハンドラは async 関数として定義する。戻り値が IntoResponse を実装する型であれば、そのままレスポンスになる。`&'static str` もその1つで、次の root は `"Hello, World!"` を返す。

```rust
use axum::{routing::get, Router};

async fn root() -> &'static str {
    "Hello, World!"
}

#[tokio::main]
async fn main() {
    let app = Router::new().route("/", get(root));

    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000")
        .await
        .unwrap();
    println!("listening on {}", listener.local_addr().unwrap());
    axum::serve(listener, app).await.unwrap();
}
```

[Router](https://docs.rs/axum/latest/axum/struct.Router.html) の route でパスとハンドラを登録する。TcpListener::bind で待ち受けポートを確保し、axum::serve に Router とともに渡すと起動する。main に `#[tokio::main]` を付けると、非同期ランタイム上で main を実行できる。

`cargo run` で起動すると、標準出力に `listening on 127.0.0.1:3000` と表示される。別のターミナルから curl でリクエストを送ると、ハンドラの戻り値がそのまま返る。

```console
$ curl http://127.0.0.1:3000/
Hello, World!
```

## ルーティングを追加する

route をつなげると、パスごとにハンドラを割り当てられる。ここでは `/items` と `/hello/{name}` を追加する。

### HTTPメソッドで振り分ける

同じパスでも、HTTP メソッドごとに別のハンドラを割り当てられる。`get(...)` の戻り値に `.post(...)` をつなげると、GET と POST で処理を分けられる。

```rust
async fn list_items() -> &'static str {
    "list items"
}

async fn create_item() -> &'static str {
    "create item"
}
```

```rust
let app = Router::new()
    .route("/", get(root))
    .route("/items", get(list_items).post(create_item));
```

### パスパラメータを受け取る（Path）

パスの一部を値として受け取るには、パスに `{name}` の形で名前を書き、ハンドラの引数に Path を置く。Path はエクストラクタの一種で、引数に書くだけでパスから値が抽出される。

```rust
async fn hello(Path(name): Path<String>) -> String {
    format!("Hello, {name}!")
}
```

```rust
let app = Router::new()
    .route("/", get(root))
    .route("/hello/{name}", get(hello))
    .route("/items", get(list_items).post(create_item));
```

追加した2つのパスは curl で次のように確認できる。

```console
$ curl http://127.0.0.1:3000/hello/Rust
Hello, Rust!
$ curl http://127.0.0.1:3000/items
list items
$ curl -X POST http://127.0.0.1:3000/items
create item
```

## JSONを扱う

axum の [Json](https://docs.rs/axum/latest/axum/struct.Json.html) を使うと、構造体と JSON を相互に変換できる。例として、次の Item を使う。Serialize は JSON で返す側、Deserialize は JSON を受け取る側に要る。

```rust
#[derive(Serialize, Deserialize)]
struct Item {
    name: String,
    price: u32,
}
```

### 構造体をJSONで返す

戻り値を Json で包むと、内側の値が Serialize を実装していれば JSON として返される。

```rust
async fn sample_item() -> Json<Item> {
    Json(Item {
        name: "sample".to_string(),
        price: 100,
    })
}
```

```rust
.route("/items/sample", get(sample_item))
```

```console
$ curl http://127.0.0.1:3000/items/sample
{"name":"sample","price":100}
```

### JSONのリクエストボディを受け取る

ハンドラの引数に Json を置くと、リクエストボディの JSON がデシリアライズされて渡される。受け取った値をそのまま Json で返すと、受け取りと返却の両方を確認できる。

```rust
async fn create_item(Json(item): Json<Item>) -> Json<Item> {
    Json(item)
}
```

```rust
.route("/items", post(create_item))
```

```console
$ curl -X POST -H 'content-type: application/json' -d '{"name":"book","price":1200}' http://127.0.0.1:3000/items
{"name":"book","price":1200}
```

## 状態を共有する（State）

ハンドラの間で値を共有するには、状態の型を定義し、with_state で Router に渡す。ハンドラは [State](https://docs.rs/axum/latest/axum/extract/struct.State.html) エクストラクタで状態を受け取る。状態の型には Clone が要るため、実体は Arc で包んで共有することが多い。

ここでは `Arc<Mutex<u64>>` のカウンタを状態にし、`/count` へアクセスするたびに値を増やして返す。

```rust
#[derive(Clone, Default)]
struct AppState {
    count: Arc<Mutex<u64>>,
}
```

```rust
#[derive(Serialize)]
struct Count {
    count: u64,
}

async fn get_count(State(state): State<AppState>) -> Json<Count> {
    let mut count = state.count.lock().unwrap();
    *count += 1;
    Json(Count { count: *count })
}
```

```rust
let state = AppState::default();

let app = Router::new()
    .route("/count", get(get_count))
    .with_state(state);
```

```console
$ curl http://127.0.0.1:3000/count
{"count":1}
$ curl http://127.0.0.1:3000/count
{"count":2}
```

状態はプロセスの中にだけあるため、サーバーを再起動するとカウントは1から始まる。

## エラーケース

### 戻り値がIntoResponseを実装していない

独自の構造体をそのまま返すハンドラは登録できない。戻り値が IntoResponse を実装していないため、次のコンパイルエラーになる。

```rust
struct Greeting {
    text: String,
}

async fn bad() -> Greeting {
    Greeting {
        text: "hi".to_string(),
    }
}
```

```text
error[E0277]: the trait bound `fn() -> impl Future<Output = Greeting> {bad}: Handler<_, _>` is not satisfied
```

ハンドラの戻り値には文字列、Json、ステータスコードなど、IntoResponse を実装した型を使う。

### リクエストボディの型が合わない

Json エクストラクタでのデシリアライズに失敗すると、ハンドラは呼ばれず、ステータスコード 422 で理由が返る。name に文字列ではなく数値を渡すと次のようになる。

```console
$ curl -X POST -H 'content-type: application/json' -d '{"name":123,"price":1200}' http://127.0.0.1:3000/items
Failed to deserialize the JSON body into the target type: name: invalid type: integer `123`, expected a string at line 1 column 11
```
