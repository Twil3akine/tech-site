+++
title = "『プログラミング言語Rust 公式ガイド』は公式ドキュメントを通読するための入門書"
description = "全20章で文法と所有権から並行処理、パターン、高度な機能までを扱い、最終章でマルチスレッドWebサーバーを作る公式ガイドの日本語版。目次と内容、注意点と良い点、ほかのRust書籍との比較を整理する。"
date = 2026-11-11

[extra]
book_name = "プログラミング言語Rust 公式ガイド"
isbn = "978-4-04-893070-3"
ogp = "img/ogp/books-rust-koshiki-guide.png"
+++

Rust コミュニティ公式のガイドブック「The Rust Programming Language」の日本語版である。

全20章、608頁。文法と所有権といった概念の章と、小さなプログラムを作るプロジェクトの章を交互に進め、最終章ではマルチスレッドの Web サーバーを構築する。書誌情報と目次は出版社（KADOKAWA）の[公式ページ](https://www.kadokawa.co.jp/product/301905000150/)で確認した。Steve Klabnik、Carol Nichols・著、尾崎亮太・訳、2019年6月28日発売、定価4,180円（税込）。

<div class="buy-links">
  <a class="buy-link" href="https://www.amazon.co.jp/dp/4048930702?tag=twil3akine-22" rel="sponsored nofollow noopener" target="_blank">Amazonで見る</a>
  <a class="buy-link" href="https://hb.afl.rakuten.co.jp/ichiba/595e2a5d.bb5528a9.595e2a5e.43463c04/?pc=https%3A%2F%2Fitem.rakuten.co.jp%2Fbook%2F15921800%2F&link_type=text&ut=eyJwYWdlIjoiaXRlbSIsInR5cGUiOiJ0ZXh0Iiwic2l6ZSI6IjY0eDY0IiwibmFtIjoxLCJuYW1wIjoicmlnaHQiLCJjb20iOjEsImNvbXAiOiJkb3duIiwicHJpY2UiOjAsImJvciI6MSwiY29sIjoxLCJiYnRuIjoxLCJwcm9kIjowLCJhbXAiOmZhbHNlfQ%3D%3D" rel="sponsored nofollow noopener" target="_blank">楽天ブックスで見る</a>
</div>

- 目次・内容
- 注意点 / こんな人にはオススメできない
- 良い点 / こんな人にオススメしたい
- 類書との比較
- まとめ

## 目次・内容

全20章のうち、主な章は次のとおりである。

1. 事始め
2. 数当てゲームをプログラムする
3. 一般的なプログラミングの概念
4. 所有権を理解する
6. enumとパターンマッチング
8. 一般的なコレクション
9. エラー処理
10. ジェネリック型、トレイト、ライフタイム
12. 入出力プロジェクト: コマンドラインプログラムを構築する
13. 関数型言語の機能: イテレーターとクロージャー
15. スマートポインター
16. 恐れるな! 並行性
18. パターンとマッチング
20. 最後のプロジェクト: マルチスレッドのWebサーバーを構築する

数当てゲーム（2章）、コマンドラインプログラム（12章）、Webサーバー（20章）の3つのプロジェクトが節目に置かれ、その間に概念の章が並ぶ。後半はスマートポインタ、並行性、パターン、unsafe やマクロを含む高度な機能まで進み、入門の範囲で言語の主要な領域を一巡する構成である。

## 注意点 / こんな人にはオススメできない

### 同じ系統の内容が Web で無償公開されている

原著は Rust の公式ドキュメントとして Web で無償公開されており、日本語訳もオンラインで読める。本書を買う意味は、紙で通読しやすさや手元に置いて参照する点に寄る。画面で読むことに抵抗がなければ、Web 版で足りる。

### 2019年の翻訳で、更新は Web 版が先行する

原著と Rust 本体はその後も更新が続いている。新しい文法やツールの変更は Web 版に先に反映されるため、最新の情報を追う用途では Web 版と併用することになる。

## 良い点 / こんな人にオススメしたい

### 公式の説明体系をそのまま通読できる

所有権をはじめとする概念の説明順と用語が公式ドキュメントと一致する。Web 版のドキュメントや他の公式資料と行き来しても、説明の前提がずれない。

### プロジェクトが節目に置かれている

概念だけを読み続ける構成ではなく、数当てゲーム、コマンドラインプログラム、Webサーバーと、段階ごとに動くものを作る。理解の確認を先送りにしにくい。

### 入門の範囲で領域が広い

スマートポインタ、並行性、パターン、高度な機能までを20章に収め、文法の次に何があるかまで見通せる。608頁の分量はあるが、章単位で区切って進められる。

## 類書との比較

### 『プログラミングRust 第2版』

同じく言語を体系的に扱う解説書だが、全23章・688頁と分量が大きく、説明の深さとリファレンス性はあちらが上になる。入門として順に通読する進め方は本書、仕様を掘る用途は『プログラミングRust 第2版』という選び分けである。

- 関連記事: [『プログラミングRust 第2版』はRustを体系的に学ぶための良書](/books/programming-rust-2e/)

### 『実践Rustプログラミング入門 第2版』

2025年刊行で、Webアプリケーション、WebAssembly、Tauri、組み込みと作る題材が広く新しい。本書は概念の説明を順に積み上げる構成で、題材の現代性はあちら、学習の道筋の明確さは本書にある。

- 関連記事: [『実践Rustプログラミング入門 第2版』は作りながら学ぶ実践型の入門書](/books/jissen-rust-2e/)

## まとめ

公式ドキュメントを紙で通読したい人、説明の用語と順序を公式にそろえて基礎を固めたい人に向けた一冊である。Web 版で読むことに抵抗がなければ無理に買う必要はないが、紙の本として手元に置く入門書としては位置づけが明確である。

<div class="buy-links">
  <a class="buy-link" href="https://www.amazon.co.jp/dp/4048930702?tag=twil3akine-22" rel="sponsored nofollow noopener" target="_blank">Amazonで見る</a>
  <a class="buy-link" href="https://hb.afl.rakuten.co.jp/ichiba/595e2a5d.bb5528a9.595e2a5e.43463c04/?pc=https%3A%2F%2Fitem.rakuten.co.jp%2Fbook%2F15921800%2F&link_type=text&ut=eyJwYWdlIjoiaXRlbSIsInR5cGUiOiJ0ZXh0Iiwic2l6ZSI6IjY0eDY0IiwibmFtIjoxLCJuYW1wIjoicmlnaHQiLCJjb20iOjEsImNvbXAiOiJkb3duIiwicHJpY2UiOjAsImJvciI6MSwiY29sIjoxLCJiYnRuIjoxLCJwcm9kIjowLCJhbXAiOmZhbHNlfQ%3D%3D" rel="sponsored nofollow noopener" target="_blank">楽天ブックスで見る</a>
</div>

<!-- 評価の根拠: 版元情報の照合で作成（2026-11-11、nkmk 式の構成）。書籍本文を読んだふりの記述は入れず、構成・対象読者・分量など確認可能な事実から導ける範囲に限っている。マスター本人の総合見解は未記入で、公開前に本人の確認を受ける。星評価は未設定。 -->
