+++
title = "RustでVecを作成・操作する（push、pop、get、iterなど）"
description = "Vec の作成、要素の追加と削除、範囲を考慮した取得、イテレータによる走査まで。"
date = 2026-11-10

[extra]
rust = "1.99.1"
level = 1

[taxonomies]
tags = ["Vec", "コレクション"]
+++

`Vec<T>` は同じ型の値を順番に保持し、実行中に長さを変えられる標準ライブラリのコレクションである。詳しくは[公式ドキュメント](https://doc.rust-lang.org/std/vec/struct.Vec.html)を参照。作成、変更、取得、走査の順に基本操作を確認する。

## Vecを作成する

空の Vec は `Vec::new` で作る。空の場合は要素から型を推論できないため、型注釈を書く。初期値がある場合は `vec!` マクロを使う。

```rust
fn main() {
    let mut values: Vec<i32> = Vec::new();
    values.push(10);
    values.push(20);

    let fixed = vec![1, 2, 3];
    assert_eq!(values, vec![10, 20]);
    assert_eq!(fixed.len(), 3);
    assert_eq!(fixed[0], 1);
}
```

`len` は要素数を返し、`is_empty` は空かどうかを返す。Vec は必要に応じて容量を広げるため、通常は要素数を先に決めなくても追加できる。

## 要素を追加・削除する

末尾への追加は `push`、末尾からの取り出しは `pop` で行う。`pop` は要素がない場合もあるため `Option<T>` を返す。任意の位置には `insert` で挿入し、`remove` で削除する。

```rust
fn main() {
    let mut values = vec![10, 30];
    values.push(40);
    values.insert(1, 20);
    assert_eq!(values, vec![10, 20, 30, 40]);

    let removed = values.remove(2);
    assert_eq!(removed, 30);
    assert_eq!(values.pop(), Some(40));
    assert_eq!(values, vec![10, 20]);

    let empty: Vec<i32> = Vec::new();
    assert_eq!(empty.into_iter().next(), None);
}
```

`insert` と `remove` は指定位置以降の要素をずらす処理を伴う。末尾だけを扱う場合は `push` と `pop` を使うと意図が明確である。

## 要素を取得する

インデックス `values[i]` は要素への参照を返すが、範囲外の位置を指定すると実行時にパニックする。`get(i)` は `Option<&T>` を返すため、位置が範囲内か分からない場合に安全に扱える。

```rust
fn main() {
    let values = vec![10, 20, 30];

    // 範囲内であることが分かっている位置にはインデックスを使える
    assert_eq!(values[1], 20);

    // get は範囲外なら None を返す
    assert_eq!(values.get(2), Some(&30));
    assert_eq!(values.get(3), None);

    let second = values.get(1).copied().unwrap_or(0);
    assert_eq!(second, 20);
}
```

インデックスを使う場合は、長さを確認するか、範囲内であることを別の条件で保証する。`get` なら `match` や `if let` で `Some` と `None` を分けて処理できる。

## iterとforで走査する

`iter` は共有参照を、`iter_mut` は変更可能な参照を順に返す。Vec 自体の所有権を消費してよい場合は `for value in values` の形で所有値を取り出せる。

```rust
fn main() {
    let mut values = vec![1, 2, 3];

    // iter は &i32 を返すため、元の Vec を保持したまま読める
    let sum: i32 = values.iter().sum();
    assert_eq!(sum, 6);

    // iter_mut は &mut i32 を返すため、要素を変更できる
    for value in values.iter_mut() {
        *value *= 2;
    }
    assert_eq!(values, vec![2, 4, 6]);

    // 参照を明示する for も使える
    let mut product = 1;
    for value in &values {
        product *= value;
    }
    assert_eq!(product, 48);
}
```

`for value in &values` は `iter` と同じく借用しながら走査する。要素を変更するなら `&mut values` または `iter_mut`、走査後に元の Vec が不要なら所有値を取り出す形を選ぶ。
