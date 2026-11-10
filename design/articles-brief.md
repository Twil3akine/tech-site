# 実装指示: Rust 解説記事を5本追加する

作業ディレクトリはこのリポジトリ（Zola サイト）です。新規の記事ファイル5本を作成してください。既存ファイルは一切変更しないこと。

## 形式（既存記事 content/std/hashmap.md と完全に揃える）
- front matter:
  +++
  title = "（下記指定）"
  description = "（内容を1文で。最後は「まで。」か「。」で終わる）"
  date = 2026-11-10

  [extra]
  rust = "1.99.1"
  level = （下記指定）

  [taxonomies]
  tags = ["（下記指定）", "（下記指定）"]
  +++
- 本文は「である」調。冒頭段落で対象を1文で定義し、公式ドキュメント（doc.rust-lang.org）へのリンクを1つ入れる。
- 構成は ## 見出し3〜5個。各見出しの下に短い説明文＋ ```rust のコード例。
- コード例はすべて fn main() を含む完結した形で、assert_eq! など検証できる形にする。外部クレート禁止、標準ライブラリのみ。
- コンパイルエラーになる例を載せる場合は、コードブロックの直前に「これはコンパイルエラーになる」と明記し、直後に直し方を示す。
- 嘘のない範囲で書くこと。API の細部が曖昧なら、その項目は書かない。
- 各記事 90〜150 行程度。

## 5本の指定
1. content/errors/e0382.md
   title = "E0382: borrow of moved value の直し方"
   tags = ["E0382", "所有権"], level = 1
   中身: エラー文の読み方（error[E0382] の各行が何を示すか）／なぜ起きるか（ムーブで所有権が移る）／直し方3つ（参照で借りる、clone する、Copy 型になる型では起きない）。最初のコード例はエラーを再現するものにする。

2. content/std/vec.md
   title = "RustでVecを作成・操作する（push、pop、get、iterなど）"
   tags = ["Vec", "コレクション"], level = 1
   中身: 作成（new / vec! マクロ）／追加と削除（push / pop / insert / remove）／取得（インデックスと get の違い、範囲外アクセスのパニック）／走査（iter / iter_mut、for）。

3. content/std/option.md
   title = "RustでOptionを扱う（unwrap、map、and_then、?など）"
   tags = ["Option", "エラー処理"], level = 1
   中身: Option の定義（Some / None）／取り出し方（unwrap の危険性、expect、unwrap_or、unwrap_or_else）／変換（map / and_then / filter）／? 演算子で早期リターン。

4. content/std/result.md
   title = "RustでResultと?演算子を使う（map_err、unwrap_or_elseなど）"
   tags = ["Result", "エラー処理"], level = 2
   中身: Result の定義（Ok / Err）／? 演算子の動作（Ok なら値を取り出し、Err なら早期リターン）／変換（map / map_err / and_then）／main での扱い（Box<dyn Error> を返す main の例）。

5. content/std/string.md
   title = "RustでStringと&strを扱う（push_str、format!、スライスなど）"
   tags = ["String", "文字列"], level = 1
   中身: String と &str の違い（所有権の有無）／作り方（to_string / String::from / format!）／追加（push_str / push、+ 演算子で所有権が移る注意）／文字列スライスと注意点（バイト境界でない位置で切るとパニックする）。

完了後、作成したファイルの一覧だけを報告すること。
