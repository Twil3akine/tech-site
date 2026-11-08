+++
title = "Rustでファイルを読み書きする（read_to_string、File、BufReaderなど）"
description = "fs::write と read_to_string による全体の読み書き、BufReader による行ごとの読み取り、OpenOptions による追記、? によるエラー伝播まで。"
date = 2026-11-06

[extra]
rust = "1.99.1"

[taxonomies]
tags = ["ファイル", "入出力"]
+++

ファイルの読み書きには、標準ライブラリの [std::fs](https://doc.rust-lang.org/std/fs/) と [std::io](https://doc.rust-lang.org/std/io/) を使う。全体をまとめて扱う方法から始め、行ごとの読み取り、追記、エラーの伝播の順に確認する。以下のコードで使うファイルは、いずれも実行時のカレントディレクトリに作られる。

## ファイル全体を読み書きする

ファイル全体を一度に書くには `fs::write`、全体を文字列として読むには `fs::read_to_string` を使う。どちらもファイルを開く、処理する、閉じる、までを内部で行う。

```rust
use std::fs;

fn main() {
    let path = "note.txt";

    // write はファイルがなければ作り、あれば中身を丸ごと置き換える
    fs::write(path, "hello\n").unwrap();

    // read_to_string はファイル全体を String で返す
    let content = fs::read_to_string(path).unwrap();
    assert_eq!(content, "hello\n");
}
```

`fs::write` は既存のファイルに対しては追記ではなく置き換えになる。バイナリを読み取る場合は `fs::read` を使う。中身を `Vec<u8>` で返す。

## 行ごとに読む（BufReader）

大きなファイルを行単位で処理する場合は、`File::open` でファイルを開き、`BufReader` で包んでから `lines` を使う。`lines` は行ごとのイテレータで、各要素は改行を含まない `io::Result<String>` である。

```rust
use std::fs::File;
use std::io::{BufRead, BufReader};

fn main() {
    std::fs::write("lines.txt", "one\ntwo\nthree\n").unwrap();

    let file = File::open("lines.txt").unwrap();
    let reader = BufReader::new(file);

    // lines() は行ごとのイテレータ。行末の改行は含まれない
    let lines: Vec<String> = reader.lines().collect::<Result<_, _>>().unwrap();
    assert_eq!(
        lines,
        vec!["one".to_string(), "two".to_string(), "three".to_string()]
    );
}
```

`BufReader` は読み取りをまとめて行い、システムコールの回数を減らす。`lines` の要素が `Result` なのは、読み取りの途中で I/O エラーが起こり得るためである。上のコードでは `collect::<Result<_, _>>()` で、最初のエラーで全体をエラーとして返す形にしている。

## 追記する（OpenOptions）

末尾への追記は `OpenOptions` で行う。`append(true)` を指定して開いたファイルへの書き込みは、常に末尾へ追加される。

```rust
use std::fs::OpenOptions;
use std::io::Write;

fn main() {
    let path = "log.txt";
    std::fs::write(path, "first\n").unwrap();

    // append(true) で末尾への追記になる
    let mut file = OpenOptions::new().append(true).open(path).unwrap();
    writeln!(file, "second").unwrap();
    drop(file);

    let content = std::fs::read_to_string(path).unwrap();
    assert_eq!(content, "first\nsecond\n");

    // create(true) を付けると、ファイルがなければ作る
    std::fs::remove_file(path).unwrap();
    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(path)
        .unwrap();
    writeln!(file, "new").unwrap();
    drop(file);
    assert_eq!(std::fs::read_to_string(path).unwrap(), "new\n");
}
```

`OpenOptions` は既定では「ファイルがなければエラー」であり、作成は `create(true)` を明示した場合だけ行われる。書き込みには [Write](https://doc.rust-lang.org/std/io/trait.Write.html) トレイトの `write_all` や `writeln!` を使う。ファイルはスコープを抜けると閉じられるが、上のコードでは読み直しの前に `drop` で明示的に閉じている。

## エラーを?で伝播させる

ファイル操作はすべて `io::Result` を返すため、`?` で呼び出し元へエラーを伝播させるのが基本形である。関数の戻り値を `io::Result<...>` にし、`main` 自体も `io::Result<()>` を返す形にできる。

```rust
use std::fs;
use std::io;

fn read_first_line(path: &str) -> io::Result<String> {
    let content = fs::read_to_string(path)?;
    // lines().next() は先頭行。空ファイルなら None になる
    Ok(content.lines().next().unwrap_or("").to_string())
}

fn main() -> io::Result<()> {
    fs::write("greeting.txt", "hello\nworld\n")?;
    let first = read_first_line("greeting.txt")?;
    assert_eq!(first, "hello");
    Ok(())
}
```

`?` を付けた式は、成功すれば中の値を取り出し、失敗すればその場で関数から `Err` を返す。`unwrap` と違い、失敗の扱いを呼び出し側に委ねられる。

## エラーケース

### 存在しないファイルをunwrapで読む

存在しないファイルを読むと `Err` が返る。これを `unwrap` すると、その場でパニックする。

```rust
fn main() {
    let _content = std::fs::read_to_string("does-not-exist.txt").unwrap();
}
```

```text
called `Result::unwrap()` on an `Err` value: Os { code: 2, kind: NotFound, message: "No such file or directory" }
```

エラーの種別は `kind` で判別できる。この例では `std::io::ErrorKind::NotFound` である。ファイルの有無が事前に分からない場合は `unwrap` せず、`?` で伝播させるか、`match` で `kind` ごとに分岐する。
