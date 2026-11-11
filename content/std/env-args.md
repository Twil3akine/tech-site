+++
title = "Rustで環境変数とコマンドライン引数を扱う（args、var、current_dirなど）"
description = "std::env の args と args_os による引数の受け取り、var と var_os による環境変数の取得と設定、カレントディレクトリの取得まで。"
date = 2026-11-11

[extra]
ogp = "img/ogp/std-env-args.png"
rust = "1.99.1"
level = 2

[taxonomies]
tags = ["入出力"]
+++

コマンドライン引数と環境変数は、標準ライブラリの [std::env](https://doc.rust-lang.org/std/env/) で扱う。引数の受け取り、環境変数の取得と設定、カレントディレクトリの順に確認する。

## コマンドライン引数を受け取る（args）

`env::args` は引数を `String` のイテレータで返す。先頭の要素はプログラム自体のパスで、実際の引数は2番目から並ぶ。引数の個数は実行時まで決まらないため、イテレータとして処理するか、`collect` で `Vec<String>` に集める。

```rust
use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();

    // 先頭はプログラム自体のパスなので、要素は必ず1つ以上ある
    assert!(!args.is_empty());
    assert!(!args[0].is_empty());

    // 2番目以降が実際の引数。なければ None になる
    let first = env::args().nth(1);
    assert_eq!(first, None);
}
```

上の例は引数なしで実行したときの結果である。`program file.txt` のように実行すれば、`nth(1)` は `Some("file.txt")` を返す。引数の解釈を自前で行う場合は、個数が足りないケースを `Option` の分岐で処理する。引数の数が多いツールでは、解釈を専門のクレートに任せることも多い。

## args_osとの違い

`args` は引数が UTF-8 として解釈できない場合にパニックする。OS の引数は UTF-8 とは限らないため、ファイル名などを引数で受ける場合は、パニックしない `env::args_os` を使う。こちらは `OsString` のイテレータを返す。

```rust
use std::env;

fn main() {
    let args: Vec<std::ffi::OsString> = env::args_os().collect();
    assert!(!args.is_empty());

    // OsString は to_string_lossy で表示用の文字列に変えられる
    let program = args[0].to_string_lossy();
    assert!(!program.is_empty());
}
```

通常の引数は `args` で十分であり、パスとして受け取る引数や、壊れた文字列が来ても落としたくない場合に `args_os` を選ぶ。`OsString` は `PathBuf` へ変換できるため、引数をパスとして扱う処理と相性がよい。

## 環境変数を取得する（var と var_os）

`env::var` は環境変数を `String` として取得し、`Result<String, VarError>` を返す。変数がなければ `Err(VarError::NotPresent)`、値が UTF-8 でなければ `Err(VarError::NotUnicode)` になる。`env::var_os` は `Option<OsString>` を返し、UTF-8 でない値もそのまま受け取れる。

```rust
use std::env;

fn main() {
    // 存在しない変数は NotPresent になる
    match env::var("RUST_SITE_EXAMPLE_MISSING") {
        Err(env::VarError::NotPresent) => {}
        other => panic!("unexpected: {other:?}"),
    }

    // var_os は Option で返る
    assert_eq!(env::var_os("RUST_SITE_EXAMPLE_MISSING"), None);

    // PATH は通常の環境なら設定されている
    let path = env::var_os("PATH");
    assert!(path.is_some());
}
```

値の存在だけを分岐に使うなら `var_os` の `Option` で十分で、値の文字列としての解釈まで含めて扱うなら `var` の `Result` で失敗の理由を分けられる。

## 環境変数を設定する（set_var）

`env::set_var` は自プロセスの環境変数を設定し、`env::remove_var` は削除する。設定した値は同じプロセスからの取得に反映され、起動する子プロセスにも引き継がれる。

```rust
use std::env;

fn main() {
    env::set_var("RUST_SITE_EXAMPLE_MODE", "test");
    assert_eq!(env::var("RUST_SITE_EXAMPLE_MODE"), Ok("test".to_string()));

    env::remove_var("RUST_SITE_EXAMPLE_MODE");
    assert_eq!(env::var_os("RUST_SITE_EXAMPLE_MODE"), None);
}
```

環境変数はプロセス全体で共有されるため、並行に動く他のスレッドが読み書きと競合し得る。このため Rust 2024 エディションでは `set_var` と `remove_var` は `unsafe` 関数になっている。設定は起動直後の初期化に寄せ、実行中に頻繁に書き換える設計は避ける。

## カレントディレクトリを取得・変更する

`env::current_dir` はカレントディレクトリを `io::Result<PathBuf>` で返す。失敗する可能性のある操作なので、戻り値は `Result` である。変更は `env::set_current_dir` で行う。

```rust
use std::env;

fn main() {
    let dir = env::current_dir().unwrap();

    // カレントディレクトリは絶対パスで返り、実在する
    assert!(dir.is_absolute());
    assert!(dir.exists());

    // 親ディレクトリへ移動すると、取得結果も変わる
    let parent = dir.parent().unwrap().to_path_buf();
    env::set_current_dir(&parent).unwrap();
    assert_eq!(env::current_dir().unwrap(), parent);

    // 元に戻す
    env::set_current_dir(&dir).unwrap();
    assert_eq!(env::current_dir().unwrap(), dir);
}
```

カレントディレクトリもプロセス全体で共有される状態である。ライブラリの内部で変更すると、呼び出し側の相対パスの解釈まで変わってしまうため、変更はプログラムの入口付近に寄せ、処理中のパスは `PathBuf` として明示的に受け渡す形が扱いやすい。
