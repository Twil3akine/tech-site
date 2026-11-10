+++
title = "RustでHashMapを作成・操作する（new、get、insert、entryなど）"
description = "HashMap の作成と追加、get による取得、entry による「なければ入れる」、全要素の走査と削除まで。"
date = 2026-11-06

[extra]
rust = "1.99.1"
level = 1

[taxonomies]
tags = ["データ構造"]
+++

キーと値の組を保持するには、標準ライブラリの [HashMap](https://doc.rust-lang.org/std/collections/struct.HashMap.html) を使う。作成と追加、取得、更新、走査、削除の順に、基本操作を確認する。

## 作成・追加・取得

`HashMap::new` で空のマップを作り、`insert` でキーと値の組を追加する。値の取得は `get` で行い、戻り値は `Option<&V>` である。キーが存在しなければ `None` が返る。

```rust
use std::collections::HashMap;

fn main() {
    let mut scores: HashMap<&str, i32> = HashMap::new();
    scores.insert("Alice", 50);
    scores.insert("Bob", 70);

    // get は Option<&V> を返す
    assert_eq!(scores.get("Alice"), Some(&50));
    assert_eq!(scores.get("Carol"), None);

    // 既存のキーへ insert すると値が置き換わり、古い値が返る
    let old = scores.insert("Alice", 55);
    assert_eq!(old, Some(50));
    assert_eq!(scores.get("Alice"), Some(&55));

    // from で配列から作る
    let map = HashMap::from([("a", 1), ("b", 2)]);
    assert_eq!(map.len(), 2);
}
```

`HashMap::from` を使うと、(キー, 値) の配列から直接作れる。要素数は `len` で取得する。

## entryで「なければ入れる」

キーがなければ値を入れ、あれば既存の値への参照を返すのが [entry](https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.entry) である。`or_insert` と組み合わせると、「初回だけ初期値を入れ、あとは既存の値を更新する」という処理が1行で書ける。単語の出現回数を数える例がその典型である。

```rust
use std::collections::HashMap;

fn main() {
    // 単語の出現回数を数える
    let text = "red blue red green blue red";
    let mut counts: HashMap<&str, u32> = HashMap::new();
    for word in text.split_whitespace() {
        *counts.entry(word).or_insert(0) += 1;
    }
    assert_eq!(counts.get("red"), Some(&3));
    assert_eq!(counts.get("blue"), Some(&2));
    assert_eq!(counts.get("green"), Some(&1));

    // and_modify は既存の値があるときだけ呼ばれる
    let mut map: HashMap<&str, i32> = HashMap::new();
    map.entry("a").and_modify(|v| *v += 10).or_insert(1);
    assert_eq!(map.get("a"), Some(&1));
    map.entry("a").and_modify(|v| *v += 10).or_insert(1);
    assert_eq!(map.get("a"), Some(&11));
}
```

`and_modify` は、キーが存在するときに既存の値を書き換える処理を指定する。存在しなければ呼ばれず、後ろの `or_insert` の値が入る。

## 全要素を走査する

`iter` は (&K, &V) の組を順に返す。HashMap の走査順序は不定であり、挿入した順にはならない。順序に依存しない処理に使うか、必要な場合は集めてから並べ替える。

```rust
use std::collections::HashMap;

fn main() {
    let map = HashMap::from([("b", 2), ("a", 1), ("c", 3)]);

    // iter() は (&K, &V) を返す。順序は不定なので、並べ替えてから比べる
    let mut pairs: Vec<(&str, i32)> = map.iter().map(|(k, v)| (*k, *v)).collect();
    pairs.sort();
    assert_eq!(pairs, vec![("a", 1), ("b", 2), ("c", 3)]);

    // keys() と values()
    let mut keys: Vec<&str> = map.keys().copied().collect();
    keys.sort();
    assert_eq!(keys, vec!["a", "b", "c"]);
    assert_eq!(map.values().sum::<i32>(), 6);
}
```

キーだけ、値だけを取り出す `keys` と `values` もある。どちらもイテレータを返すため、`collect` や `sum` などのイテレータのメソッドにつなげられる。

## デフォルト値・存在確認・削除

`get` の戻り値に `copied` と `unwrap_or` をつなげると、キーがない場合のデフォルト値を値そのものとして取り出せる。キーの有無だけを調べるには `contains_key`、削除には `remove` を使う。`remove` は削除した値を `Option` で返す。

```rust
use std::collections::HashMap;

fn main() {
    let mut map = HashMap::from([("a", 1)]);

    // 値がなければデフォルト値を使う
    assert_eq!(map.get("a").copied().unwrap_or(0), 1);
    assert_eq!(map.get("b").copied().unwrap_or(0), 0);

    // キーの有無を調べる
    assert!(map.contains_key("a"));
    assert!(!map.contains_key("b"));

    // remove は削除した値を Option で返す
    assert_eq!(map.remove("a"), Some(1));
    assert_eq!(map.remove("a"), None);
    assert!(map.is_empty());
}
```

## エラーケース

### getの戻り値を値そのものとして使う

`get` の戻り値は `Option` であり、値そのものではない。値の型として受け取ろうとすると、型の不一致でコンパイルエラーになる（E0308）。

```rust
use std::collections::HashMap;

fn main() {
    let map = HashMap::from([("a", 1)]);
    let value: i32 = map.get("a");
    println!("{value}");
}
```

```text
error[E0308]: mismatched types
  = note: expected type `i32`
             found enum `Option<&{integer}>`
```

値を使う前に、`unwrap_or` でデフォルト値を用意するか、`if let Some(...)` で存在を確認する。

### 存在しないキーをインデックスで参照する

`map[キー]` の形でも値を取得できるが、キーが存在しない場合は実行時にパニックする。

```rust
use std::collections::HashMap;

fn main() {
    let map = HashMap::from([("a", 1)]);
    let value = map["missing"];
    println!("{value}");
}
```

```text
no entry found for key
```

キーの存在が確実でない場合は、インデックスではなく `get` を使う。
