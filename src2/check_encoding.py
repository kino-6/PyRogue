# fix_all_encodings.py
import os
import chardet
from pathlib import Path

def check_file_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        print(f"File: {file_path}")
        print(f"Encoding: {result['encoding']}")
        print(f"Confidence: {result['confidence']}")
        print(f"First 10 bytes: {raw_data[:10]}")
        return result['encoding'], raw_data

def fix_file_encoding(file_path):
    try:
        # 現在のエンコーディングを確認
        encoding, content = check_file_encoding(file_path)
        
        # ファイルを現在のエンコーディングで読み込み
        with open(file_path, 'r', encoding=encoding) as f:
            text = f.read()
        
        # UTF-8で書き込み
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
            
        print(f"Fixed encoding for: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                fix_file_encoding(file_path)

if __name__ == "__main__":
    # src2ディレクトリ内のすべてのPythonファイルを処理
    process_directory('.')
    print("Encoding fix completed.")
