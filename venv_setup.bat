@echo off

REM 仮想環境の作成
python -m venv venv

REM 仮想環境のアクティベート
call venv\Scripts\activate

REM pipのアップグレード
python -m pip install --upgrade pip

REM 必要なライブラリのインストール
pip install -r requirements.txt

REM バッチ処理の終了
@echo finish.
