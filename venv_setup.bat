@echo off

REM Pythonのバージョンを指定して仮想環境を作成
py -3.11 -m venv venv

REM 仮想環境のアクティベート
call venv\Scripts\activate

REM pipのアップグレード
python -m pip install --upgrade pip

REM 必要なライブラリのインストール
pip install -r requirements.txt

REM バッチ処理の終了
@echo finish.

REM 仮想環境がアクティベートされた状態の新しいコマンドプロンプトを開く
cmd /k
