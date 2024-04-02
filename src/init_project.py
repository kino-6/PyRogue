import sys
import os

# プロジェクトのルートディレクトリを取得します。この例では、init_project.py がプロジェクトのルートにあると仮定しています。
project_root = os.path.dirname(os.path.abspath(__file__))

# src ディレクトリへのパスを構築します。
src_path = os.path.dirname(os.path.abspath(__file__))

# src ディレクトリが sys.path になければ追加します。
if src_path not in sys.path:
    sys.path.append(src_path)
