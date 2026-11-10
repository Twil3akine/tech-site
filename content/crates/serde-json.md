+++
title = "Rustでserde_jsonを使ってJSONを読み書きする（Value、構造体、エラー処理など）"
description = "serde_json で JSON を Value として読む方法、構造体へ変換する方法、JSON 文字列を生成する方法まで。"
date = 2026-11-11

[extra]
ogp = "img/ogp/crates-serde-json.png"
rust = "1.99.1"
level = 3
crates = ["serde 1.0.229", "serde_json 1.0.154"]

[taxonomies]
tags = ["JSON"]
+++

[serde_json](https://docs.rs/serde_json/latest/serde_json/) は、Rust の値と JSON を相互に変換するクレートである。JSON の形が決まっていない場合は `Value` として読み、形が決まっている場合は構造体へ変換すると扱いやすい。データモデルの基礎には [serde](https://serde.rs/) を使う。

## 依存クレートを追加する

Cargo.toml の `[dependencies]` に次を追加する。構造体を使う場合は、serde の `derive` 機能も有効にする。

```toml
[dependencies]
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

## ValueとしてJSONを読む

`serde_json::from_str` で JSON 文字列を `Value` に変換する。`Value` は、オブジェクト、配列、文字列、数値、真偽値、null をまとめて表す列挙型である。

```rust
use serde_json::Value;

fn main() {
    let text = r#"{"name":"Rust","tags":["ownership","safety"],"year":2015}"#;
    let value: Value = serde_json::from_str(text).unwrap();

    assert_eq!(value["name"], Value::from("Rust"));
    assert_eq!(value["year"], Value::from(2015));

    let name = value["name"].as_str().unwrap();
    let tags = value["tags"].as_array().unwrap();

    assert_eq!(name, "Rust");
    assert_eq!(tags.len(), 2);
    assert_eq!(tags[0], Value::from("ownership"));
}
```

存在しないキーに対してインデックスでアクセスすると、エラーではなく `Value::Null` が返る。必ず存在するとは限らない値は、`get` で取得し、`Option` として分けて扱う方が安全である。

```rust
use serde_json::Value;

fn main() {
    let value: Value = serde_json::from_str(r#"{"name":"Rust"}"#).unwrap();

    assert_eq!(value.get("name"), Some(&Value::from("Rust")));
    assert_eq!(value.get("website"), None);
    assert_eq!(value["website"], Value::Null);
}
```

## JSONを生成する

`json!` マクロを使うと、Rust の式から `Value` を組み立てられる。`serde_json::to_string` で1行の JSON 文字列にし、`to_string_pretty` でインデント付きにできる。

```rust
use serde_json::json;

fn main() {
    let value = json!({
        "name": "Rust",
        "tags": ["ownership", "safety"],
        "year": 2015
    });

    let compact = serde_json::to_string(&value).unwrap();
    assert!(compact.contains("\"name\":\"Rust\""));
    assert!(compact.contains("\"year\":2015"));

    let pretty = serde_json::to_string_pretty(&value).unwrap();
    assert!(pretty.contains("\n  \"name\": \"Rust\""));
}
```

オブジェクトのキーの順序は利用方法によっては意味を持たない。テストで JSON 全体を文字列として比べると、キーの順序や空白で失敗することがあるため、必要な項目ごとに値を比べる方が安定する。

## 構造体へ変換する

JSON の形が決まっている場合は、`Serialize` と `Deserialize` を付けた構造体を使う。フィールド名と型が合えば、`from_str` で構造体として読み取れる。

```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, PartialEq)]
struct User {
    name: String,
    age: u8,
    admin: bool,
}

fn main() {
    let text = r#"{"name":"rin","age":24,"admin":false}"#;
    let user: User = serde_json::from_str(text).unwrap();

    assert_eq!(user.name, "rin");
    assert_eq!(user.age, 24);
    assert!(!user.admin);

    let output = serde_json::to_string(&user).unwrap();
    let loaded: User = serde_json::from_str(&output).unwrap();
    assert_eq!(loaded, user);
}
```

構造体にないキーが JSON に含まれていても、通常は無視される。逆に、構造体に必須のフィールドが JSON にない場合は変換エラーになる。欠ける可能性があるフィールドは `Option<T>` にし、既定値を使いたい場合は serde の `default` 属性を使う。

## 一部の値だけを構造体にする

外側の形は変わるが、内側の項目だけが安定している場合は、まず `Value` として読み、必要な部分だけを構造体へ変換することもできる。

```rust
use serde::Deserialize;
use serde_json::Value;

#[derive(Debug, Deserialize, PartialEq)]
struct Item {
    id: u64,
    title: String,
}

fn main() {
    let text = r#"{"meta":{"page":1},"item":{"id":7,"title":"note"}}"#;
    let root: Value = serde_json::from_str(text).unwrap();

    let item: Item = serde_json::from_value(root["item"].clone()).unwrap();
    assert_eq!(item, Item { id: 7, title: "note".to_string() });
}
```

`from_value` は `Value` を指定した型へ変換する。API のレスポンス全体を先に受け取り、必要な部分だけを型付きで扱う場合に使う。

## エラー処理

`from_str` は `serde_json::Result<T>` を返す。JSON の文法が壊れている場合だけでなく、構造体の型に合わない場合もエラーになる。

```rust
use serde_json::Value;

fn main() {
    let broken: serde_json::Result<Value> = serde_json::from_str("{");
    assert!(broken.is_err());

    let wrong_type: serde_json::Result<u32> = serde_json::from_str("\"abc\"");
    assert!(wrong_type.is_err());

    let valid: serde_json::Result<Value> = serde_json::from_str("[1, 2, 3]");
    assert!(valid.is_ok());
}
```

外部から受け取る JSON では `unwrap` で止めず、`?` で呼び出し元へ返すか、エラー内容をログに残して入力側の問題として扱う。エラーメッセージには位置や期待された型が含まれるため、原因を調べるときは最初にその内容を確認する。
