+++
title = "Rustでイテレータを使う（map、filter、collectなど）"
description = "iter と into_iter の違い、map・filter・collect による変換と収集、sum・count による集計、enumerate・zip、クロージャと遅延評価まで。"
date = 2026-11-06

[extra]
rust = "1.99.1"
level = 2

[taxonomies]
tags = ["イテレータ"]
+++

コレクションの要素を順に処理するには、[Iterator](https://doc.rust-lang.org/std/iter/trait.Iterator.html) トレイトのメソッドを使う。変換、抽出、収集、集計をメソッドの連結で書き、クロージャと遅延評価の決まりもあわせて確認する。

## イテレータを作る

コレクションからイテレータを作る方法は主に3つある。`iter` は要素への参照を返し、元の値は残る。`into_iter` は要素そのものを返し、所有権が移る。範囲式 `1..=3` もイテレータである。

```rust
fn main() {
    let values = vec![1, 2, 3];

    // iter() は要素への参照を順に返す
    let mut sum = 0;
    for value in values.iter() {
        sum += value;
    }
    assert_eq!(sum, 6);

    // iter() のあとも values はそのまま使える
    assert_eq!(values.len(), 3);

    // into_iter() は要素そのものを返し、所有権が移る
    let total: i32 = values.into_iter().sum();
    assert_eq!(total, 6);
}
```

`for` で回すだけなら `iter` を明示せず `for value in &values` とも書ける。以後の節では、メソッドを連結するためにイテレータを変数や式の形で扱う。

## 要素を変換・抽出する

### mapとfilter

`map` は各要素に関数を適用して変換し、`filter` は条件を満たす要素だけを残す。どちらもイテレータを返すため、続けて連結できる。終端で `collect` を呼ぶと、結果がコレクションになる。

```rust
fn main() {
    let values = vec![1, 2, 3, 4, 5];

    // 各要素を2倍し、4で割り切れるものだけを集める
    let result: Vec<i32> = values
        .iter()
        .copied()
        .map(|x| x * 2)
        .filter(|x| x % 4 == 0)
        .collect();
    assert_eq!(result, vec![4, 8]);
}
```

`copied` は参照のイテレータを値のイテレータに変える。`iter` が返すのは `&i32` であり、そのままでは数値演算の対象にしにくいため、先に `copied` で値を取り出している。

### collectで集める

`collect` の行き先は、変数の型注釈で決まる。Vec のほか、文字を集めて String にしたり、(キー, 値) の組を集めて HashMap にしたりできる。

```rust
use std::collections::HashMap;

fn main() {
    // collect の行き先は型注釈で決まる
    let chars: String = ['a', 'b', 'c'].iter().collect();
    assert_eq!(chars, "abc");

    // (キー, 値) の組を集めると HashMap になる
    let keys = ["a", "b"];
    let vals = [1, 2];
    let map: HashMap<&str, i32> = keys
        .iter()
        .copied()
        .zip(vals.iter().copied())
        .collect();
    assert_eq!(map.get("b"), Some(&2));
    assert_eq!(map.len(), 2);
}
```

## 集計する

合計、個数、最大値、最小値は終端のメソッドで取得する。これらはイテレータを最後まで消費し、1つの値を返す。

```rust
fn main() {
    let values = vec![3, 1, 4, 1, 5];

    assert_eq!(values.iter().sum::<i32>(), 14);
    assert_eq!(values.iter().count(), 5);
    assert_eq!(values.iter().max(), Some(&5));
    assert_eq!(values.iter().min(), Some(&1));

    // filter と組み合わせると、条件を満たす要素の個数や合計になる
    assert_eq!(values.iter().filter(|&&x| x > 2).count(), 3);
    assert_eq!(values.iter().filter(|&&x| x > 2).sum::<i32>(), 12);
}
```

`sum` は結果の型を推論できない場面があるため、`sum::<i32>()` のように型を明示することが多い。`max` と `min` は、要素が空の場合に備えて `Option` を返す。

## インデックスと組を作る

### enumerate

`enumerate` は (インデックス, 要素) の組を返す。インデックスは 0 から始まる。

```rust
fn main() {
    let names = vec!["a", "b", "c"];

    // enumerate は (インデックス, 要素) を返す
    let with_index: Vec<(usize, &str)> = names
        .iter()
        .enumerate()
        .map(|(i, name)| (i, *name))
        .collect();
    assert_eq!(with_index, vec![(0, "a"), (1, "b"), (2, "c")]);
}
```

### zip

`zip` は2つのイテレータを組にして進める。どちらかが終われば全体も終わるため、長さの違うイテレータ同士では短い方に合わせられる。

```rust
fn main() {
    let names = vec!["a", "b", "c"];
    let scores = vec![10, 20, 30];

    // zip は2つのイテレータを組にして進める
    let pairs: Vec<(&str, i32)> = names
        .iter()
        .copied()
        .zip(scores.iter().copied())
        .collect();
    assert_eq!(pairs, vec![("a", 10), ("b", 20), ("c", 30)]);

    // 長さが違う場合は短い方で終わる
    let short: Vec<(i32, i32)> = (1..=5).zip(1..=2).collect();
    assert_eq!(short, vec![(1, 1), (2, 2)]);
}
```

名前と点数を組にして集めると、対応関係を持ったまま Vec や HashMap にできる。

## クロージャ

`map` や `filter` に渡す関数は、多くの場合クロージャで書く。クロージャは `|引数| 式` の形で、変数に代入して関数のように呼び出すこともできる。通常の関数と違うのは、定義した場所の変数をキャプチャできる点である。

```rust
fn main() {
    // クロージャは変数に代入して、関数のように呼び出せる
    let add_one = |x: i32| x + 1;
    assert_eq!(add_one(1), 2);

    // 周囲の変数をキャプチャする
    let factor = 3;
    let multiply = |x: i32| x * factor;
    assert_eq!(multiply(4), 12);
}
```

引数と戻り値の型は、通常は呼び出し側から推論される。上の `add_one` のように単独で定義する場合は、型注釈を付けると意図が明確になる。

### 遅延評価

`map` などのアダプタは、呼んだ時点では何も処理しない。`collect` や `sum` のような終端のメソッドが呼ばれて初めて、要素が順に処理される。

```rust
use std::cell::Cell;

fn main() {
    let calls = Cell::new(0);

    // map を呼んだだけでは、クロージャはまだ実行されない
    let iter = (1..=3).map(|x| {
        calls.set(calls.get() + 1);
        x * 10
    });
    assert_eq!(calls.get(), 0);

    // collect で初めて要素が順に処理される
    let result: Vec<i32> = iter.collect();
    assert_eq!(result, vec![10, 20, 30]);
    assert_eq!(calls.get(), 3);
}
```

実行回数を数えるために、ここでは `Cell` を使っている。アダプタを連結しただけのイテレータは、消費されなければ破棄されるだけで、副作用も計算も起きない。

## エラーケース

### collectの型注釈を省略する

`collect` は行き先のコレクション型を戻り値の文脈から決める。型がどこからも決まらないと、型推論に失敗してコンパイルエラーになる（E0283）。

```rust
fn main() {
    let values = (1..=3).collect();
    println!("{values:?}");
}
```

```text
error[E0283]: type annotations needed
  = note: the type must implement `FromIterator<i32>`
help: consider giving `values` an explicit type
```

変数に型注釈を付ける（`let values: Vec<_> = ...`）か、関数の引数など型の決まる位置で使う。
