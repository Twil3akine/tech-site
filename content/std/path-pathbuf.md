+++
title = "RustでPathとPathBufを扱う（join、file_name、extensionなど）"
description = "Path と PathBuf の違い、join による結合、ファイル名と拡張子の取得、存在確認、文字列との変換まで。"
date = 2026-11-11

[extra]
ogp = "img/ogp/std-path-pathbuf.png"
rust = "1.99.1"
level = 2

[taxonomies]
tags = ["入出力"]
+++

ファイルやディレクトリのパスは、標準ライブラリの [Path](https://doc.rust-lang.org/std/path/struct.Path.html) と [PathBuf](https://doc.rust-lang.org/std/path/struct.PathBuf.html) で扱う。`&str` と `String` の関係に近く、`Path` は借用したパス、`PathBuf` は所有するパスである。違い、結合、部分の取り出し、存在確認、文字列との変換の順に確認する。

## PathとPathBufの違い

`Path` はパスへの参照を表す型で、それ自体は中身を所有しない。`PathBuf` は中身を所有し、あとから要素を付け足して伸ばせる。文字列における `str` と `String` の関係と同じである。

```rust
use std::path::{Path, PathBuf};

fn main() {
    // Path::new は &str から &Path を作る
    let path: &Path = Path::new("src/main.rs");
    assert_eq!(path, Path::new("src/main.rs"));

    // PathBuf は所有するパス。from で &str や String から作れる
    let owned: PathBuf = PathBuf::from("src/main.rs");
    assert_eq!(owned.as_path(), path);

    // &Path から所有する PathBuf を得るには to_path_buf を使う
    let copied: PathBuf = path.to_path_buf();
    assert_eq!(copied, owned);
}
```

関数の引数でパスを受け取るだけなら `&Path` を使う。パスを組み立てて保持したり返したりする場合は `PathBuf` を使う。

## パスを結合する

`join` は後ろに要素を付けた新しい `PathBuf` を返す。`push` は `PathBuf` 自体を変更して要素を付け足す。どちらも区切り文字は OS に合わせて自動で入るため、`/` を文字列として連結する必要はない。

```rust
use std::path::{Path, PathBuf};

fn main() {
    // join は新しい PathBuf を返す
    let dir = Path::new("src");
    let file = dir.join("main.rs");
    assert_eq!(file, PathBuf::from("src/main.rs"));

    // 複数要素を続けてもよい
    let nested = dir.join("bin").join("app.rs");
    assert_eq!(nested, PathBuf::from("src/bin/app.rs"));

    // push は元の PathBuf を変更する
    let mut buf = PathBuf::from("src");
    buf.push("lib.rs");
    assert_eq!(buf, PathBuf::from("src/lib.rs"));
}
```

`join` や `push` に絶対パスを渡すと、元のパスは捨てられ、渡した絶対パスに置き換わる。相対パスをつなぐつもりで絶対パスを混ぜると意図しない結果になるため、結合する要素が絶対パスになり得る場合は事前に確認する。

## ファイル名と拡張子を取り出す

`file_name` は末尾の要素、`file_stem` は拡張子を除いたファイル名、`extension` は拡張子、`parent` は親ディレクトリを返す。いずれも「存在しない」場合があり得るため、戻り値は `Option` である。ファイル名まわりの戻り値は文字列とは限らないため `&str` ではなく `&OsStr` で返る。

```rust
use std::ffi::OsStr;
use std::path::Path;

fn main() {
    let path = Path::new("docs/report.v2.md");

    // 末尾の要素は OsStr として返る
    assert_eq!(path.file_name(), Some(OsStr::new("report.v2.md")));

    // file_stem は最後の拡張子を除いた部分
    assert_eq!(path.file_stem(), Some(OsStr::new("report.v2")));
    assert_eq!(path.extension(), Some(OsStr::new("md")));

    // 親ディレクトリは &Path で返る
    assert_eq!(path.parent(), Some(Path::new("docs")));

    // 要素の数は components で数えられる
    assert_eq!(path.components().count(), 2);

    // ルートにはファイル名がない
    assert_eq!(Path::new("/").file_name(), None);
}
```

拡張子がないファイルでは `extension` が `None` を返し、`.gitignore` のようなドットで始まる名前は全体が `file_stem` 側になる。値を文字列として使う場合は、次の節の変換を組み合わせる。

## 存在するか確認する

`exists` はパスが存在すれば `true` を返す。ファイルかどうかは `is_file`、ディレクトリかどうかは `is_dir` で判別できる。

```rust
use std::path::Path;

fn main() {
    let path = Path::new("path-note.txt");
    std::fs::write(path, "hello").unwrap();

    // 書いた直後なので存在し、ファイルとして判定される
    assert!(path.exists());
    assert!(path.is_file());
    assert!(!path.is_dir());

    // カレントディレクトリはディレクトリとして判定される
    let dir = Path::new(".");
    assert!(dir.exists());
    assert!(dir.is_dir());

    std::fs::remove_file(path).unwrap();
    assert!(!path.exists());
}
```

`exists` は、権限不足などで確認自体に失敗した場合も `false` を返す。「存在しない」と「確認できなかった」を区別したい場合は、結果を `io::Result<bool>` で返す `try_exists` を使う。

## 文字列との変換

パスは OS の文字列であり、UTF-8 であるとは限らない。そのため `&str` への変換は `to_str` で行い、変換できない場合は `None` が返る。表示やログへの出力が目的なら、変換できない部分を代替文字に置き換える `to_string_lossy` が使える。OS の文字列としてそのまま扱う場合は `as_os_str` で `&OsStr` を得る。

```rust
use std::path::Path;

fn main() {
    let path = Path::new("src/main.rs");

    // UTF-8 として解釈できれば Some(&str) が返る
    assert_eq!(path.to_str(), Some("src/main.rs"));

    // lossy 変換は常に文字列を返す
    assert_eq!(path.to_string_lossy(), "src/main.rs");

    // パスを受け取る関数は &Path で受けると &str からも渡せる
    fn count_components(path: &Path) -> usize {
        path.components().count()
    }
    assert_eq!(count_components(Path::new("a/b/c")), 3);
    assert_eq!(count_components(path), 2);
}
```

ファイル名を `file_name` などで取り出した `&OsStr` も、同じ考え方で `to_str` や `to_string_lossy` を使って文字列に変える。パスの結合や比較は `Path` のまま行い、文字列に変えるのは表示や他 API との受け渡しに必要な場面に限ると、変換できないケースを最小限にできる。
