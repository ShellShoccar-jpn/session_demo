#!/bin/sh
#
# シェルスクリプトでHTTPセッションを張るテスト
# ・このシェルスクリプトを動かすには、標準UNIXコマンド以外に下記のものが必要
#   - cgi-name (CGI変数を正規化する。Open usp Tukubaiコマンド)
#   - nameread (正規化されたCGI変数を取り出す。Open usp Tukubaiコマンド)
#   - utconv   (UNIX時間との相互変換をする。拙作独自コマンド)
#   - mkcookie (クライアントに送出するCookie文字列を生成する。拙作独自コマンド)
#

# --- 0)各種定義 -----------------------------------------------------
Dir_MINE="$(d=${0%/*}/; [ "_$d" = "_$0/" ] && d='./'; cd "$d"; pwd)"
Dir_SESSION="$Dir_MINE/SESSIONS" # セッションファイル置き場
Tmp=/tmp/tmp.$$                  # テンポラリーファイルの基本名定義
SESSION_LIFETIME=60              # セッションの有効期限(1分にしてみた)
COOKIE_LIFETIME=120              # Cookieの有効期限(2分にしてみた)
export PATH="$(command -p getconf PATH):${PATH:-}"

# --- 1)CookieからセッションIDを読み取る -----------------------------
session_id=$(printf '%s' "${HTTP_COOKIE:-}"                      |
             sed 's/&/%26/g; s/[;, ]\{1,\}/\&/g; s/^&//; s/&$//' |
             "$Dir_MINE/cgi-name"                                |
             "$Dir_MINE/nameread" session_id                     )

# --- 2)セッションIDの有効性検査 -------------------------------------
session_status='new'                          # デフォルトは「要新規作成」とする
while :; do
  # --- 古いセッションファイルは消しておく
  touch -t $(date '+%Y%m%d%H%M%S'                  |
             "$Dir_MINE/utconv"                    |
             awk "{print \$1-$SESSION_LIFETIME-1}" |
             "$Dir_MINE/utconv" -r                 |
             awk 'sub(/..$/,".&")'                 ) $Tmp-session_expire
  find "$Dir_SESSION" \( \! -newer $Tmp-session_expire \) | xargs rm -f
  # --- セッションID文字列がない or 不正な書式なら「新規作成」判定
  printf '%s' "$session_id" | grep -q '^[A-Za-z0-9]\{16\}$' || break
  # --- セッションID文字列で指定されたファイルが存在しないなら「期限切れ」判定
  [ -f "$Dir_SESSION/$session_id" ] || { session_status='expired'; break; }
  # --- これらの検査に全て合格したら使う
  session_status='exist'
  break
done

# --- 3)セッションファイルの確保(あれば延命、なければ新規作成) -------
case $session_status in
  exist) File_session=$Dir_SESSION/$session_id
         touch "$File_session";;                              # セッションを延命する
  *)     mkdir -p $Dir_SESSION
         File_session=$(mktemp $Dir_SESSION/XXXXXXXXXXXXXXXX)
         [ $? -eq 0 ] || { echo 'cannot create session file' 1>&2; exit; }
         session_id=${File_session##*/};;
esac

# --- 4)-1セッションファイル読み込み ---------------------------------
msg=$(cat "$File_session")
case "${msg}${session_status}" in
  new)     msg="はじめまして! セッションを作りました。(ID=$session_id)";;
  expired) msg="セッションの有効期限が切れたので、作り直しました。(ID=$session_id)";;
esac

# --- 4)-2セッションファイル書き込み ---------------------------------
printf '最終訪問日時は、%04d年%02d月%02d日%02d時%02d分%02d秒です。(ID=%s)' \
       $(date '+%Y %m %d %H %M %S') "$session_id"                            \
       > "$File_session"

# --- 5)Cookieを焼く -------------------------------------------------
cookie_str=$(echo "session_id ${session_id}"                          |
             "$Dir_MINE/mkcookie" -e+${COOKIE_LIFETIME} -p / -s A -h Y)

# --- 6)HTTPレスポンス作成 -------------------------------------------
cat <<-HTTP_RESPONSE
	Content-type: text/html; charset=utf-8$cookie_str

	<html>
	<head>
	  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	  <style type="text/css">
	    <!-- 
	    #shellshoccar_label {float:right; margin:0.5em 0 0 0; padding:0; }
	    -->
	  </style>
	  <title>シェルスクリプトでセッション管理をするサンプル</title>
	</head>
	<body>
	  <div id="shellshoccar_label"><img src="ShellShoccar_logo.gif" alt="ShellShoccar logo"></div>
	  <h1>シェルスクリプトでセッション管理をするサンプル</h1>
	  <p><strong>$msg</strong></p>
	  <ul style="border: 1px #808080 solid; line-height: 1.5em">
	    <li>最終アクセスから1分未満はセッションが有効です。リロードすればあなたのことを覚えています。</li>
	    <li>最終アクセスから2分未満はCookieが有効ですが、セッションは有効期限切れです。リロードすると「セッションを作り直しました」とメッセージを出します。</li>
	    <li>最終アクセスから2分以降はCookieもセッションも有効期限切れです。リロードすると「はじめまして!」とメッセージを出します。</li>
	    <li>ソースコード・解説はこちら→<a href="http://qiita.com/richmikan@github/items/ee77911602afc911858f">シェルスクリプトによるCGIのセッション管理@Qiita</a></li>
	  </ul>
	</body>
	</html>
HTTP_RESPONSE

# --- 7)テンポラリーファイル削除 -------------------------------------
rm -f $Tmp-*
