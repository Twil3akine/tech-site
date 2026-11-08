# Rust 解説サイト（Twil3akine）

Twil3akine 名義の Rust 解説サイト。公開先は https://rust.twil3akine.org/（2026-11-08 に名義・ドメインを決定。旧 Noptium / noptium.com 表記から移行済み）。静的サイトジェネレータ Zola で構築する。

記事の形式ルールは `../rust-site/format.md`、テーマ候補は `../rust-site/topics.md` を参照。

## ローカルプレビュー

```console
$ zola serve
```

ブラウザで http://127.0.0.1:1111/ を開く。ビルドだけなら `zola build`（出力は `public/`）。

Zola はこの VM では `~/.local/bin/zola`（0.23.6、公式 GitHub リリースの単体バイナリ）に入っている。PATH が通っていない環境では `export PATH="$HOME/.local/bin:$PATH"` を先に実行する。

## 構成

```
zola.toml            サイト設定（タイトル、base_url、ハイライト設定）
content/
  _index.md          トップページ用セクション
  std/               標準ライブラリと基礎（topics.md の (a) + (d)）
  crates/            クレート解説（topics.md の (b)）
  errors/            エラー解決・実務（topics.md の (c)）
templates/           手書きの最小テーマ（外部テーマ依存なし）
  base.html          ヘッダー（アイコン + Twil3akine ブランド + 検索）と共通枠
  index.html         カテゴリ別セクション + 記事カード
  section.html       カテゴリページ
  page.html          記事ページ
static/
  css/style.css      全スタイル（本文幅 約760px、システムフォント、ライト基調）
  img/icon.png       ブランドアイコン（決定済みアイコンから生成）
  favicon.png        64px
  apple-touch-icon.png  180px
```

## 記事の追加方法

1. カテゴリに合うフォルダ（`content/std/`、`content/crates/`、`content/errors/`）に `.md` ファイルを作る。ファイル名は英小文字とハイフンで内容が分かるものにする（例: `axum-http-server.md`）。
2. 先頭にフロントマターを書く。

```toml
+++
title = "Rustで〔対象〕を〔操作〕する（〔主な手段の列挙〕）"
description = "記事の1行要約。トップとカテゴリページのカードに出る。"
date = 2026-11-06

[extra]
rust = "1.99.1"
crates = ["axum 0.8.9", "tokio 1.54.1"]

# 関連リンクを末尾に出す場合のみ（通常は format.md どおり本文中にインラインで置く）
# related = [{ title = "axum 公式ドキュメント", url = "https://docs.rs/axum/latest/axum/" }]
+++
```

フロントマターの項目:

| 項目 | 必須 | 内容 |
|---|---|---|
| `title` | ○ | format.md のタイトル形式どおり |
| `description` | ○ | 1行要約 |
| `date` | ○ | 公開日（`YYYY-MM-DD`）。カテゴリ内の並びは日付降順 |
| `extra.rust` | ○ | 動作確認した Rust のバージョン（例: `"1.99.1"`） |
| `extra.crates` | クレート記事は ○ | `"名前 バージョン"` の配列。std のみの記事では省略可 |
| `extra.related` | 任意 | 末尾の関連リンク領域に出す `{ title, url }` の配列 |

3. 本文は導入の段落から書き始める。次はテンプレートが自動で描くので、**本文には書かない**:
   - 記事タイトル（H1）
   - 冒頭のバージョン明示の文（`extra` から生成）
   - 目次（見出しから自動生成。H2/H3 が対象）
   - 末尾の「この記事で使ったクレート/バージョン」（`extra` から生成。format.md では記事末尾の節だが、このサイトではテンプレート側が出す）

## 既知の割り切り

- 目次は、バージョンメモの直後・本文の前に出る。format.md の指定（導入の直後）とは位置が少し違う。Zola では本文の途中に目次を差し込めないための土台段階の割り切り。
- 検索インデックスは無効（`build_search_index = false`）。記事が増えたら有効化を検討する。
- コードハイライトは `github-light` テーマ（`zola.toml` の `[markdown.highlighting]`）。言語タグ `console` はハイライト対象の文法がないため無地で表示される。

## 未実施のステップ

- [x] Twil3akine 名義への付け替えと `zola build` 確認（2026-11-08、ローカルコミット `3ae3e73`）
- [ ] GitHub へのリポジトリ作成・push（このフォルダはローカルに `git init` 済みなだけ。リモートなし、push 未実施。コミットはローカルのみ）
  - ブロッカー: この VM は `gh auth login` 未完了で、SSH 経由の github.com 接続も egress プロキシで切断される（2026-11-08 確認）。ユーザー側で `gh auth login` を行うか、朝刊サイト（Twil3akine/Morning-Paper）で使っている push 経路を用意する必要がある
- [ ] Cloudflare Pages へのプロジェクト接続（朝刊と同じく GitHub 連携が前提）
- [ ] twil3akine.org 側で `rust` サブドメインを Pages プロジェクトに割り当て（Cloudflare ダッシュボード操作）
