# 実装指示: Rust 解説サイト全面リデザイン

作業ディレクトリはこのリポジトリ（Zola サイト）です。
まず design/opus-spec.md（Opus の仕様書）を全文読み、その通りに実装してください。
仕様と異なる判断が必要な箇所は、下の「統合側の決定」が優先します。

## 統合側の決定（仕様への上書き・補足）
1. コードのシンタックスハイライトは現行の giallo（インラインスタイル、night-owl 系）のまま変えない。パネルの外側（角丸12px、余白、言語ラベル、コピーボタン）だけ仕様に合わせる。既存の base.html のコードブロック用スクリプトは、ラベルを右上に置き、コピーボタンを追加する形に拡張してよい。
2. 検索フォームは現行の仕組み（送信時に q へ "site:rust.twil3akine.org " を前置する onsubmit）を維持し、見た目だけ仕様に合わせる。"/" キーでフォーカスする JS を追加する。
3. RSS リンクは今回は入れない（フッター右列は3セクションへのリンクのみ）。
4. 読了管理の localStorage キーは既存の "rk-read" を使い続ける。記事末ボタンの文言は仕様どおり「攻略済みにする」。
5. フォントは Inter に差し替える（Zen Kaku Gothic New の link は外す）。
6. /all/ ページは残すが、トップからはリンクしない（新着が8本以下の間は「もっと見る」なし、という仕様どおり）。

## データ投入（そのまま使うこと）
config.toml の [extra] に追加:
- show_full_title = false
- route = ["std/hashmap.md", "std/iterator.md", "std/file-io.md", "crates/axum-http-server.md"]

各セクションの _index.md の [extra] に planned を追加:
- std: planned = ["Vec の操作", "String と &str", "Option の扱い", "Result と ? 演算子", "所有権と借用", "構造体と impl", "パターンマッチ", "クロージャ", "ジェネリクス", "ライフタイム入門"]
- crates: planned = ["tokio 入門", "serde で JSON", "reqwest で HTTP クライアント", "anyhow と thiserror", "clap で CLI", "tracing でログ"]
- errors: planned = ["E0382 借用後の使用", "E0597 ライフタイム不足", "E0308 型の不一致", "E0277 トレイト境界", "E0502 可変と不変の借用", "E0433 クレート未導入"]

ヒーロー右パネルの中身（静的 HTML、コンパイラ出力の体裁で）:
```
error[E0382]: borrow of moved value: `v`
 --> src/main.rs:4:20
  |
3 |     let v2 = v;
  |              - value moved here
4 |     println!("{v:?}");
  |                    ^ value borrowed here after move
```
パネル下リンク「この直し方 →」は errors セクションへ。

## 触るファイル
- static/css/style.css（全面組み替え。旧ランディング用 .lp-* / .nk-* / .rk-* の CSS は削除する。ただし本番の他ページが使うクラスは壊さないこと）
- templates/base.html（ヘッダー・フッター・フォント・検索・読了記録スクリプト）
- templates/index.html（トップ全面）
- templates/page.html（記事ページ: パンくず、メタ行、目次、記事末の攻略済みボタンと順路の次・関連記事）
- templates/section.html（一覧: 進捗表示と準備中チップ）
- templates/tags/list.html と templates/books 系で base の変更に追随が必要なら最小限直す
- config.toml、各 _index.md（上記データ）

## 制約
- トップページとヘッダー・フッターに書籍レビュー（/books/）へのリンクを置かない。
- `zola build` がエラーなく通ること。終わったら build を実行して結果を確認する。
- 既存の記事本文（content 配下の記事 md）には触らない（_index.md の [extra] 追記のみ可）。
- 完了後、変更ファイル一覧と、仕様から外れた点があればその理由を簡潔に報告する。
