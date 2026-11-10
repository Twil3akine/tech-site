+++
title = "Gitでブランチを切って作業する（branch、switch、mergeなど）"
description = "現在のブランチ確認、ブランチの作成と切り替え、コミット、マージ、競合の直し方、不要なブランチの削除まで。"
date = 2026-11-11

[taxonomies]
tags = ["Git"]
+++

ブランチは変更を別の流れとして分けるための名前である。本体のブランチを直接変更せず、作業用ブランチでコミットを積み、終わったら本体へマージする流れを覚えると、途中の変更を分けて管理できる。

## 現在の状態を確認する

作業を始める前に、現在のブランチと未コミットの変更を確認する。

```console
$ git branch --show-current
main
$ git status --short --branch
## main
```

`git status` の結果にファイル名が表示される場合、そのファイルには未コミットの変更がある。意図しない変更が含まれていないかを確認してからブランチを切る。作業途中の変更はブランチを切り替えても原則として一緒に移動するため、別の作業と混ざりやすい。

## ブランチを作って切り替える

`git switch -c` は、ブランチを作成して、そのまま切り替える。

```console
$ git switch -c feature/login
Switched to a new branch 'feature/login'
```

既にあるブランチへ移る場合は `-c` を付けない。

```console
$ git switch main
$ git switch feature/login
```

ブランチの一覧は `git branch` で確認できる。現在のブランチには `*` が付く。

```console
$ git branch
* feature/login
  main
```

ブランチ名は、作業内容が分かる名前にする。`feature/login` のように種類と対象を組み合わせると、複数の作業を並行しても見分けやすい。

## 変更をコミットする

ファイルを変更したら、状態を確認し、必要なファイルだけをステージしてコミットする。

```console
$ git status --short
 M src/main.rs
$ git add src/main.rs
$ git commit -m "ログイン画面を追加"
```

`git add .` は現在のフォルダ以下の変更をまとめてステージする。関係のないファイルが混ざる可能性があるため、変更量が多いときはファイルごとに確認する方が安全である。

作業ブランチの履歴は `git log --oneline --decorate` で確認できる。

```console
$ git log --oneline --decorate -5
a1b2c3d (HEAD -> feature/login) ログイン画面を追加
e4f5g6h (main) 初期表示を修正
```

コミットIDと表示形式は環境によって異なる。

## mainへマージする

作業が終わったら、取り込み先のブランチへ移動して `git merge` を実行する。

```console
$ git switch main
$ git merge feature/login
```

マージの結果は大きく2つに分かれる。

- `Fast-forward`: main 側に新しいコミットがなく、作業ブランチの先端まで進めるだけの場合
- マージコミットの作成: 両方のブランチに別々のコミットがあり、履歴を合流させる場合

どちらでも、作業ブランチの変更が main へ取り込まれる。マージ後にテストやビルドを実行し、取り込み先の状態で動作を確認する。

## 競合を直す

両方のブランチで同じ箇所を変更すると、Git が自動で決められず競合になる。

```console
$ git merge feature/login
Auto-merging src/main.rs
CONFLICT (content): Merge conflict in src/main.rs
Automatic merge failed; fix conflicts and then commit the result.
```

競合したファイルには、次のような印が入る。

```text
<<<<<<< HEAD
現在のブランチの内容
=======
取り込むブランチの内容
>>>>>>> feature/login
```

`<<<<<<<` から `=======` までが現在のブランチ、`=======` から `>>>>>>>` までが取り込むブランチの内容である。最終的に残す内容へ編集し、印もすべて消す。

編集後は、ファイルをステージしてコミットするとマージが完了する。

```console
$ git add src/main.rs
$ git commit
```

`git commit` を引数なしで実行すると、マージ用のコミットメッセージが用意されたエディタが開く。内容を確認して保存すればよい。途中でマージを取り消したい場合は、コミットする前に `git merge --abort` を使う。

## ブランチを削除する

マージ済みの作業ブランチは `git branch -d` で削除できる。

```console
$ git branch -d feature/login
Deleted branch feature/login (was a1b2c3d).
```

マージされていないブランチを削除しようとすると、Git は変更の消失を避けるために止める。内容を確認せずに強制削除しない。リモートブランチの削除は別の操作になるため、ローカルで `-d` を使っただけではリモートのブランチは消えない。

## 最小の作業手順

通常の作業はこの順序で進める。

1. `git status` で未コミットの変更を確認する
2. `git switch -c 作業名` で作業ブランチを作る
3. 変更し、ファイルを確認してコミットする
4. 取り込み先へ移動し、`git merge 作業名` を実行する
5. テストやビルドで確認する
6. マージ済みの作業ブランチを削除する

ブランチを切る目的は履歴を複雑にすることではなく、作業同士を混ぜずに進めることである。
