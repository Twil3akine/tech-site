+++
title = "RustでStringと&strを扱う（push_str、format!、スライスなど）"
description = "String と &str の所有権の違い、生成と追加、+ 演算子、UTF-8 のスライスまで。"
date = 2026-11-10

[extra]
rust = "1.99.1"
level = 1

[taxonomies]
tags = ["String", "文字列"]
+++

`String` は内容を所有して伸縮できる UTF-8 文字列であり、`&str` は文字列データを借用して参照する文字列スライスである。[公式ドキュメント](https://doc.rust-lang.org/std/string/struct.String.html)を参照し、生成、追加、スライスの基本を確認する。

## Stringと&strの違い

`String` は所有者として内容を保持し、変更できる。`&str` は文字列の一部または全体を借用する参照である。関数が読み取りだけを行う場合は `&str` を受け取ると、String と文字列リテラルの両方を渡しやすい。

```rust
fn greet(name: &str) -> String {
    format!("こんにちは、{name}さん")
}

fn main() {
    let owned = String::from("Rust");
    let borrowed: &str = &owned;

    assert_eq!(greet(borrowed), "こんにちは、Rustさん");
    assert_eq!(greet("Ada"), "こんにちは、Adaさん");
    assert_eq!(owned, "Rust");
}
```

`&owned` は String の内容を借用するため、`greet` の呼び出しで所有権は移らない。借用が有効な間は、所有者側で借用と競合する変更はできない。

## Stringを作成する

文字列リテラルから所有する String を作る方法には `to_string` と `String::from` がある。複数の値を埋め込んだ文字列は `format!` で作れる。`format!` は引数の所有権を取らず、新しい String を返す。

```rust
fn main() {
    let first = "hello".to_string();
    let second = String::from("world");
    let message = format!("{first}, {second}!");

    assert_eq!(first, "hello");
    assert_eq!(second, "world");
    assert_eq!(message, "hello, world!");
}
```

どの書き方も所有する String を得る。すでにある String の所有権を保ったまま新しい文字列を組み立てたい場合は、`format!` が扱いやすい。

## 文字列に追加する

`push_str` は `&str` を末尾に追加し、`push` は一つの `char` を追加する。`+` 演算子は左側の String の所有権を受け取り、右側の `&str` を追加して新しい String を返す。

```rust
fn main() {
    let mut text = String::from("Rust");
    text.push_str(" language");
    text.push('!');
    assert_eq!(text, "Rust language!");

    let left = String::from("hello, ");
    let right = String::from("world");
    let joined = left + &right;

    // left は + で所有権が移ったため使えないが、right は借用されたので使える
    assert_eq!(joined, "hello, world");
    assert_eq!(right, "world");
}
```

`+` の左側に置いた String は消費されるため、その後は使えない。両方の元の値を保持したければ `format!("{left}{right}")` を使う方法もある。

## 文字列スライスとUTF-8境界

`&text[start..end]` はバイト位置で範囲を指定する。Rust の文字列は UTF-8 であり、範囲の両端が文字の境界でなければスライス時にパニックする可能性がある。安全に試すには `get` を使うと `None` で確認できる。

```rust
fn main() {
    let text = String::from("猫a");

    // 「猫」は UTF-8 で3バイトなので、0..3 は境界に合う
    assert_eq!(&text[0..3], "猫");
    assert_eq!(text.get(0..3), Some("猫"));

    // 0..1 は文字の途中で終わるため、有効なスライスではない
    assert_eq!(text.get(0..1), None);
    assert_eq!(text.get(3..4), Some("a"));
}
```

範囲をバイト数で決めるときは、文字境界を確認する必要がある。任意の位置で安全に切り出す場合は `get` を使い、`None` の場合を処理する。文字単位の走査には `chars` が使える。
