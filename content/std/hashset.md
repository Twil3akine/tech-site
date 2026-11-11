+++
title = "RustでHashSetを作成・操作する（insert、contains、union、intersectionなど）"
description = "HashSet の作成と追加、contains による存在確認、和集合・積集合などの集合演算、重複排除への応用まで。"
date = 2026-11-11

[extra]
ogp = "img/ogp/std-hashset.png"
rust = "1.99.1"
level = 1

[taxonomies]
tags = ["データ構造"]
+++

値の集合を保持し、重複を許さずに存在確認を高速に行うには、標準ライブラリの [HashSet](https://doc.rust-lang.org/std/collections/struct.HashSet.html) を使う。作成と追加、削除と走査、集合演算、重複排除への応用の順に確認する。

## 作成・追加・存在確認

`HashSet::new` で空の集合を作り、`insert` で値を追加する。すでにある値を追加しても集合は変わらず、`insert` の戻り値で「新しく入ったかどうか」が分かる。値があるかは `contains` で調べる。

```rust
use std::collections::HashSet;

fn main() {
    let mut set: HashSet<i32> = HashSet::new();

    // insert は新しく入った場合に true を返す
    assert!(set.insert(10));
    assert!(set.insert(20));

    // すでにある値を入れても増えず、false が返る
    assert!(!set.insert(10));
    assert_eq!(set.len(), 2);

    // contains は値の有無を bool で返す
    assert!(set.contains(&10));
    assert!(!set.contains(&30));

    // from で配列から作る。重複はこの時点で取り除かれる
    let fixed: HashSet<i32> = HashSet::from([1, 2, 2, 3]);
    assert_eq!(fixed.len(), 3);
}
```

`contains` の引数は参照である点に注意する。キーを値で保持する `HashMap` と違い、`HashSet` は値そのものだけを保持する。

## 削除と全要素の走査

`remove` は値を削除し、削除できたかどうかを `bool` で返す。`iter` は全要素への参照を返すが、走査順序は不定であり、挿入した順にはならない。

```rust
use std::collections::HashSet;

fn main() {
    let mut set: HashSet<&str> = HashSet::from(["a", "b", "c"]);

    // remove は削除できたら true、なければ false を返す
    assert!(set.remove("b"));
    assert!(!set.remove("b"));
    assert_eq!(set.len(), 2);

    // 順序は不定なので、並べ替えてから比べる
    let mut items: Vec<&str> = set.iter().copied().collect();
    items.sort();
    assert_eq!(items, vec!["a", "c"]);
}
```

順序が意味を持つ処理では、`HashSet` のまま走査せず、集めてから並べ替えるか、次の節のように別の構造と組み合わせる。

## 集合演算

2つの集合に対しては、和集合を返す `union`、積集合を返す `intersection`、差集合を返す `difference`、対称差を返す `symmetric_difference` がある。いずれも結果はイテレータで返る。部分集合かどうかは `is_subset` と `is_superset`、共通要素がないかどうかは `is_disjoint` で調べられる。

```rust
use std::collections::HashSet;

fn main() {
    let a: HashSet<i32> = HashSet::from([1, 2, 3]);
    let b: HashSet<i32> = HashSet::from([3, 4, 5]);

    // 和集合: どちらかにある値
    let mut union: Vec<i32> = a.union(&b).copied().collect();
    union.sort();
    assert_eq!(union, vec![1, 2, 3, 4, 5]);

    // 積集合: 両方にある値
    let mut intersection: Vec<i32> = a.intersection(&b).copied().collect();
    intersection.sort();
    assert_eq!(intersection, vec![3]);

    // 差集合: a にあって b にない値
    let mut difference: Vec<i32> = a.difference(&b).copied().collect();
    difference.sort();
    assert_eq!(difference, vec![1, 2]);

    // 対称差: どちらか一方にだけある値
    let mut symmetric: Vec<i32> = a.symmetric_difference(&b).copied().collect();
    symmetric.sort();
    assert_eq!(symmetric, vec![1, 2, 4, 5]);

    // 部分集合と素集合の判定
    let small: HashSet<i32> = HashSet::from([1, 2]);
    assert!(small.is_subset(&a));
    assert!(a.is_superset(&small));
    assert!(!a.is_disjoint(&b));
}
```

演算結果を `HashSet` として保持したい場合は、`collect` で `HashSet` 型に集める。イテレータのまま `count` や `sum` につなぐこともできる。

## 重複排除に使う

重複を取り除くだけなら、値を `HashSet` に集めるのが最も単純である。重複の有無だけが分かればよい集計にも向く。

```rust
use std::collections::HashSet;

fn main() {
    // 単語の種類数を数える
    let text = "red blue red green blue red";
    let words: HashSet<&str> = text.split_whitespace().collect();
    assert_eq!(words.len(), 3);

    // 数値の重複を取り除く。順序は保持されない
    let values = vec![3, 1, 3, 2, 1];
    let mut unique: Vec<i32> = values.into_iter().collect::<HashSet<_>>().into_iter().collect();
    unique.sort();
    assert_eq!(unique, vec![1, 2, 3]);
}
```

元の順序を保ったまま重複を取り除きたい場合は、「見たかどうか」を記録する集合を別に用意し、`filter` と組み合わせる。`insert` が `true` を返した要素、つまり初めて現れた要素だけを通す形である。

```rust
use std::collections::HashSet;

fn main() {
    let values = vec![3, 1, 3, 2, 1];

    let mut seen: HashSet<i32> = HashSet::new();
    let unique: Vec<i32> = values.into_iter().filter(|v| seen.insert(*v)).collect();

    // 初出の順序がそのまま残る
    assert_eq!(unique, vec![3, 1, 2]);
}
```

「存在するか」だけを大量に調べる処理では、`Vec` を線形に探すより `HashSet` に入れてから `contains` で引く方が速い。要素数に対して何度も検索する場合は、最初に集合へ移しておく。
