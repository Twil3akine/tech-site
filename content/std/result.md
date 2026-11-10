+++
title = "RustでResultと?演算子を使う（map_err、unwrap_or_elseなど）"
description = "Result の Ok と Err、? によるエラー伝播、変換メソッド、main でのエラー処理まで。"
date = 2026-11-10

[extra]
rust = "1.99.1"
level = 2

[taxonomies]
tags = ["Result", "エラー処理"]
+++

`Result<T, E>` は成功した値 `Ok(T)` またはエラー `Err(E)` を表す標準ライブラリの型である。[公式ドキュメント](https://doc.rust-lang.org/std/result/enum.Result.html)を参照し、エラーの伝播、変換、`main` での扱いを確認する。

## OkとErr

処理が成功すれば `Ok` に値を入れ、失敗すれば `Err` に理由を入れる。`Result<T, E>` の T は成功時の型、E はエラー型である。

```rust
fn divide(numerator: i32, denominator: i32) -> Result<i32, &'static str> {
    if denominator == 0 {
        Err("0では割れない")
    } else {
        Ok(numerator / denominator)
    }
}

fn main() {
    assert_eq!(divide(12, 3), Ok(4));
    assert_eq!(divide(12, 0), Err("0では割れない"));
}
```

エラーを返すことで、呼び出し側に処理の成功と失敗の両方を伝えられる。`match` や `if let` で分岐するほか、Result のメソッドや `?` で処理をつなげられる。

## ?でエラーを伝播する

`?` は `Ok(value)` なら値を取り出し、`Err(error)` なら現在の関数からエラーを返す。関数の戻り値も Result でなければならず、呼び出し元がエラーを受け取れるようにする。

```rust
fn parse_and_double(input: &str) -> Result<i32, std::num::ParseIntError> {
    let value: i32 = input.parse()?;
    Ok(value * 2)
}

fn main() {
    assert_eq!(parse_and_double("21"), Ok(42));
    assert!(parse_and_double("abc").is_err());
}
```

`parse` のエラー型は `ParseIntError` であり、この例では関数の戻り値のエラー型と一致するため `?` で伝播できる。異なるエラー型を使う場合は、戻り値のエラー型への変換が可能である必要がある。

## map、map_err、and_thenで変換する

`map` は成功値を変換し、`map_err` はエラー値を変換する。`and_then` は成功値を使った次の処理が Result を返す場合に使い、失敗を一つの Result にまとめる。

```rust
fn main() {
    let parsed = "12".parse::<i32>();
    let doubled = parsed.map(|value| value * 2);
    assert_eq!(doubled, Ok(24));

    let named_error = "nope"
        .parse::<i32>()
        .map_err(|error| format!("整数にできない: {error}"));
    assert!(named_error.unwrap_err().starts_with("整数にできない:"));

    let parsed_ok: Result<i32, &str> = Ok(8);
    let positive = parsed_ok.and_then(|value| {
        if value > 0 { Ok(value) } else { Err("正数ではない") }
    });
    assert_eq!(positive, Ok(8));
}
```

成功値を整形するだけなら `map`、エラーを表示向けの型に変えるなら `map_err` を使う。処理を連結して途中の失敗も返したい場合は `and_then` を選ぶ。

## unwrap_or_elseとmain

処理を続けるための代替値があるなら `unwrap_or_else` でエラーから値を作れる。エラーを呼び出し元へ返す場合、`main` の戻り値を `Result<(), Box<dyn std::error::Error>>` にすると、標準ライブラリの多くのエラーを `?` で伝播できる。

```rust
use std::error::Error;

fn parse_count(input: &str) -> Result<usize, Box<dyn Error>> {
    let count: usize = input.parse()?;
    Ok(count)
}

fn main() -> Result<(), Box<dyn Error>> {
    let count = parse_count("3")?;
    assert_eq!(count, 3);

    let fallback = "bad"
        .parse::<i32>()
        .unwrap_or_else(|_error| 0);
    assert_eq!(fallback, 0);
    Ok(())
}
```

`main` が `Ok(())` を返せば正常終了であり、`Err` を返せば実行環境へエラーが報告される。エラーを握りつぶしてよいとは限らないため、代替値を使うのはその動作が妥当な場合に限る。
