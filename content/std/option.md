+++
title = "RustでOptionを扱う（unwrap、map、and_then、?など）"
description = "Option の Some と None、取り出しと変換のメソッド、? による早期リターンまで。"
date = 2026-11-10

[extra]
rust = "1.99.1"
level = 1

[taxonomies]
tags = ["エラー処理"]
+++

`Option<T>` は、値がある状態 `Some(T)` と値がない状態 `None` のどちらかを表す標準ライブラリの型である。[公式ドキュメント](https://doc.rust-lang.org/std/option/enum.Option.html)を参照しながら、値の取り出し、変換、早期リターンを確認する。

## SomeとNone

値が存在するときは `Some(value)`、存在しないときは `None` を使う。Option を返すことで、値がない可能性を型で表現できる。

```rust
fn find_first_even(values: &[i32]) -> Option<i32> {
    values.iter().copied().find(|value| value % 2 == 0)
}

fn main() {
    let found = find_first_even(&[1, 3, 8, 10]);
    let missing = find_first_even(&[1, 3, 5]);

    assert_eq!(found, Some(8));
    assert_eq!(missing, None);
}
```

`Option<T>` は `match` や `if let` で分岐できる。`Some` の中身は T 型の値であり、`None` には値が入っていない。

## 値を取り出す

`unwrap` は `Some` なら値を返すが、`None` ではパニックする。`expect` も同様にパニックする一方、失敗時に表示する説明を指定できる。欠損が通常あり得る処理では、デフォルト値を選ぶ `unwrap_or` や `unwrap_or_else` が使える。

```rust
fn main() {
    let present = Some("Rust");
    assert_eq!(present.unwrap(), "Rust");

    let required = Some(42);
    assert_eq!(required.expect("値が必要である"), 42);

    let absent: Option<i32> = None;
    assert_eq!(absent.unwrap_or(0), 0);
    assert_eq!(absent.unwrap_or_else(|| 10 + 5), 15);
}
```

`unwrap` と `expect` は `None` が起きないことを保証できる場合に限って使う。入力や検索結果のように欠損が予想される場合は、デフォルトを与えるか、呼び出し元へ Option を返す方が扱いやすい。

## map、and_then、filterで変換する

`map` は `Some` の中身を変換し、`None` はそのまま保つ。変換先も Option になる処理では `and_then` を使うと Option が入れ子にならない。`filter` は条件に合わない `Some` を `None` にする。

```rust
fn main() {
    let text = Some("42");
    let length = text.map(|value| value.len());
    assert_eq!(length, Some(2));

    // parse は Result を返すため、ok で Option に変換する
    let number = text.and_then(|value| value.parse::<i32>().ok());
    assert_eq!(number, Some(42));

    let positive = number.filter(|value| *value > 0);
    let negative = number.filter(|value| *value < 0);
    assert_eq!(positive, Some(42));
    assert_eq!(negative, None);
}
```

`map` のクロージャは通常の値を返し、`and_then` のクロージャは Option を返す。条件を満たす場合だけ値を残したいときは `filter` が使える。

## ?でNoneを早期リターンする

Option を返す関数の中では `?` を使える。対象が `Some(value)` なら値を取り出し、`None` ならその関数から直ちに `None` を返す。

```rust
fn add_two_numbers(left: Option<i32>, right: Option<i32>) -> Option<i32> {
    let left_value = left?;
    let right_value = right?;
    Some(left_value + right_value)
}

fn main() {
    assert_eq!(add_two_numbers(Some(2), Some(3)), Some(5));
    assert_eq!(add_two_numbers(Some(2), None), None);
}
```

ここではどちらか一方が `None` なら、足し算へ進まず `None` が返る。`?` は呼び出し元へ失敗の可能性を渡す記法であり、`unwrap` のようにパニックするものではない。
