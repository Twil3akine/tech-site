+++
title = "Rustでスライスを使う（範囲、chunks、windows、splitなど）"
description = "配列や Vec の一部を参照するスライスの基本。範囲指定、分割、chunks、windows、split まで。"
date = 2026-11-11

[extra]
rust = "1.99.1"
level = 2

[taxonomies]
tags = ["データ構造"]
+++

スライスは配列や Vec の中にある連続した要素を参照する型である。要素のコピーを作らずに一部分だけを渡せるため、範囲を扱う関数や、一定の大きさごとに区切る処理でよく使う。型は `[T]`、その参照は `&[T]` と書く。詳しくは[公式ドキュメント](https://doc.rust-lang.org/std/primitive.slice.html)を参照。

## 範囲を指定して取り出す

配列や Vec に対して `1..3` のような範囲を指定すると、その範囲のスライスが得られる。範囲の終端は含まないため、`1..3` はインデックス 1 と 2 を指す。

```rust
fn main() {
    let values = [10, 20, 30, 40];

    let middle = &values[1..3];
    assert_eq!(middle, [20, 30]);
    assert_eq!(middle.len(), 2);

    // 範囲指定でも get を使うと、範囲外のときに None を受け取れる
    assert_eq!(values.get(1..3), Some([20, 30].as_slice()));
    assert_eq!(values.get(3..10), None);
}
```

文字列のスライスである `&str` も同じ考え方だが、UTF-8 の文字境界でない位置では分割できない。バイト位置だけを見て文字列を切る場合は、その位置が文字境界であることを確認する必要がある。

## 先頭と末尾を取り出す

先頭の要素と残りを分けるには `split_first` を使う。空のスライスでは `None` を返すため、要素があるかどうかを分けて処理できる。末尾側は `split_last` で同じように扱える。

```rust
fn main() {
    let values = [10, 20, 30];

    let (first, rest) = values.split_first().unwrap();
    assert_eq!(*first, 10);
    assert_eq!(rest, [20, 30]);

    let (last, head) = values.split_last().unwrap();
    assert_eq!(*last, 30);
    assert_eq!(head, [10, 20]);

    let empty: [i32; 0] = [];
    assert_eq!(empty.split_first(), None);
}
```

最初の要素だけを読みたい場合は `first`、最後の要素だけを読みたい場合は `last` も使える。どちらも要素がなければ `None` を返す。

## chunksで一定の個数に分ける

`chunks(n)` は、スライスを最大で n 個ずつの塊に分ける。最後の塊だけ要素数が少なくなる。似たメソッドの `chunks_exact(n)` は余りを別に分けるため、すべての塊を同じ大きさとして扱いたい場合に向く。

```rust
fn main() {
    let values = [1, 2, 3, 4, 5];

    let groups: Vec<&[i32]> = values.chunks(2).collect();
    assert_eq!(groups.len(), 3);
    assert_eq!(groups[0], [1, 2]);
    assert_eq!(groups[1], [3, 4]);
    assert_eq!(groups[2], [5]);

    let exact: Vec<&[i32]> = values.chunks_exact(2).collect();
    assert_eq!(exact.len(), 2);
    assert_eq!(exact[0], [1, 2]);
    assert_eq!(exact[1], [3, 4]);

    let remainder = values.chunks_exact(2).remainder();
    assert_eq!(remainder, [5]);
}
```

`chunks(0)` のように 0 を渡すとパニックする。個数が外部から決まる場合は、0 でないことを先に確認する。

## windowsで重なる範囲を取る

`windows(n)` は、n 個の要素を1つずつずらしながら取り出す。連続する要素同士の差や、直前と直後の値を比べる処理で使う。

```rust
fn main() {
    let values = [3, 5, 9, 10];

    let differences: Vec<i32> = values
        .windows(2)
        .map(|pair| pair[1] - pair[0])
        .collect();
    assert_eq!(differences, vec![2, 4, 1]);

    let sums: Vec<i32> = values.windows(3).map(|group| group.iter().sum()).collect();
    assert_eq!(sums, vec![17, 24]);
}
```

`chunks` と違い、`windows` の各範囲は重なる。要素数が n より少ない場合は何も返らない。

## splitで区切る

`split` は、条件を満たす要素を区切りとしてスライスを分ける。区切りに使った要素自体は結果に含まれない。

```rust
fn main() {
    let values = [1, 2, 0, 3, 0, 4, 5];

    let groups: Vec<&[i32]> = values.split(|value| *value == 0).collect();
    assert_eq!(groups.len(), 3);
    assert_eq!(groups[0], [1, 2]);
    assert_eq!(groups[1], [3]);
    assert_eq!(groups[2], [4, 5]);

    // 先頭や末尾が区切りだと、空のスライスも結果に含まれる
    let padded = [0, 1, 0];
    let parts: Vec<&[i32]> = padded.split(|value| *value == 0).collect();
    assert_eq!(parts.len(), 3);
    assert!(parts[0].is_empty());
    assert_eq!(parts[1], [1]);
    assert!(parts[2].is_empty());
}
```

空の部分も意味を持つデータでは `split` を使い、空の部分を省きたい場合は `split(|value| *value == 0).filter(|group| !group.is_empty())` のように条件を加える。

## 関数の引数にはスライスを使う

配列と Vec の両方を受け取る関数では、引数を `&[T]` にすると呼び出し側の形をそろえられる。所有権は移らず、長さもスライス自身が持つ。

```rust
fn total(values: &[i32]) -> i32 {
    values.iter().sum()
}

fn main() {
    let array = [1, 2, 3];
    let vector = vec![4, 5, 6];

    assert_eq!(total(&array), 6);
    assert_eq!(total(&vector), 15);
    assert_eq!(total(&vector[1..]), 11);
}
```

要素を変更する関数では `&mut [T]` を使う。スライスに切り分けてから渡せば、元の配列や Vec の一部だけを変更対象にできる。
