# シェルスクリプトによるセッション管理デモ

HTTPセッションの管理ごとき、他言語に頼らずPOSIXシェルスクリプトで十分事足りることを実証するためのデモプログラムです。

実際に動作しているものは、[このページ](http://lab-sakura.richlab.org/SESSION_MANAGER/SESSION_DEMO.CGI)で体験できます。

## デモの概要

Webブラウザーで、とにかく[デモページ](http://lab-sakura.richlab.org/SESSION_MANAGER/SESSION_DEMO.CGI)にアクセスしてください。すると次のルールに基づいて表示するメッセージが決まります。

* 最終アクセスから1分未満はセッションが有効です。リロードすればあなたのことを覚えています。
* 最終アクセスから2分未満はCookieが有効ですが、セッションは有効期限切れです。リロードすると「セッションを作り直しました」とメッセージを出します。
* 最終アクセスから2分以降はCookieもセッションも有効期限切れです。リロードすると「はじめまして!」とメッセージを出します。

# 自分でデプロイしてみるには

1. このリポジトリ―をダウンロードしてください。Gitコマンドが使えるなら、下記のように打ち込めばOK。
 * git clone https://github.com/ShellShoccar-jpn/session_demo.git
1. ダウンロードされたファイル中の"README.md"「以外」の全てに対し、下記のようにして実行権限を与えてください。
 * ls -1 | grep -v README.md | xargs chmod +x
1. あとはWebブラウザーで"SESSION_DEMO.CGI"にアクセスするだけ！


# 技術解説

* [シェルスクリプトによるCGIのセッション管理@Qiita](http://qiita.com/richmikan@github/items/ee77911602afc911858f)
