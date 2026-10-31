# -*- coding: utf-8 -*-
"""用最新詞典重新分析已上傳的書籍。"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyzer

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")

for fn in os.listdir(UPLOAD_DIR):
    if not fn.endswith(".txt"):
        continue
    book_id = fn[:-4]
    path = os.path.join(UPLOAD_DIR, fn)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    print(f"重新分析 {book_id} ({len(text)} 字)...")
    data = analyzer.analyze_book(text, book_id)
    # 書名：優先用舊數據裡的 title，否則用文件名
    old = analyzer.load_analysis(DATA_DIR, book_id)
    data["title"] = (old.get("title") if old else None) or book_id
    analyzer.save_analysis(data, DATA_DIR)
    print(f"  章節: {len(data['chapters'])}, 人物: {len(data['characters'])}: {list(data['characters'])[:12]}")