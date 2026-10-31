# -*- coding: utf-8 -*-
"""BodyWords 身語集 — Flask 後端"""

import os
import json
import uuid
import secrets
import functools
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, make_response

import analyzer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
TOKENS_FILE = os.path.join(DATA_DIR, "tokens.json")

with open(os.path.join(BASE_DIR, "config.json"), encoding="utf-8") as f:
    CONFIG = json.load(f)

app = Flask(__name__)
app.secret_key = CONFIG.get("secret_key", "dev-secret")

os.makedirs(UPLOAD_DIR, exist_ok=True)


# ---------------- 訪問控制 ----------------
def load_tokens():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_tokens(tokens):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(TOKENS_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f, ensure_ascii=False, indent=2)


def check_access():
    """管理員(session)或持有有效鏈接密鑰(cookie token)皆可訪問。"""
    if session.get("admin"):
        return True
    token = request.cookies.get("bw_token")
    if token and token in load_tokens():
        return True
    return False


def require_access(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not check_access():
            # 無權限者看到「空白頁」——不暴露網站存在，也不可搜索
            return render_template("blank.html"), 404
        return f(*args, **kwargs)
    return wrapper


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        pw = request.form.get("password", "")
        if pw == CONFIG.get("admin_password"):
            session["admin"] = True
            return redirect(url_for("index"))
        error = "密碼錯誤 / Wrong password"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------- 管理員：生成分享鏈接 ----------------
@app.route("/admin/tokens", methods=["GET", "POST"])
def admin_tokens():
    if not session.get("admin"):
        return redirect(url_for("login"))
    tokens = load_tokens()
    if request.method == "POST":
        token = secrets.token_urlsafe(8)
        tokens[token] = {"created": str(uuid.uuid1()), "note": request.form.get("note", "")}
        save_tokens(tokens)
    # 分享鏈接直接帶 ?t=，訪客打開即自動兌換
    return render_template("tokens.html", tokens=tokens)


@app.route("/admin/tokens/<token>/revoke", methods=["POST"])
def revoke_token(token):
    if not session.get("admin"):
        return redirect(url_for("login"))
    tokens = load_tokens()
    tokens.pop(token, None)
    save_tokens(tokens)
    return redirect(url_for("admin_tokens"))


# ---------------- 客人：兌換訪問權 ----------------
@app.route("/redeem", methods=["GET", "POST"])
def redeem():
    """訪客用帶密鑰的鏈接兌換訪問權（寫入 Cookie）。
    支持 /redeem?t=xxx 和 /?t=xxx 兩種形式，後者自動兌換後跳轉主頁。
    """
    token = request.args.get("t", "") or request.form.get("token", "")
    # GET 帶有效密鑰 → 直接寫 Cookie 進站（一鍵鏈接）
    if request.method == "GET" and token and token in load_tokens():
        resp = make_response(redirect(url_for("index")))
        resp.set_cookie("bw_token", token, max_age=60 * 60 * 24 * 30, httponly=True)
        return resp
    error = None
    if request.method == "POST" and token:
        if token in load_tokens():
            resp = make_response(redirect(url_for("index")))
            resp.set_cookie("bw_token", token, max_age=60 * 60 * 24 * 30, httponly=True)
            return resp
        error = "密鑰無效 / Invalid key"
    return render_template("redeem.html", error=error, token=token)


# ---------------- 主頁面 ----------------
@app.route("/")
def index():
    # 一鍵鏈接：URL 帶有效 ?t= → 先兌換（寫 Cookie）再進站
    t = request.args.get("t", "")
    if t and t in load_tokens():
        resp = make_response(redirect(url_for("index")))
        resp.set_cookie("bw_token", t, max_age=60 * 60 * 24 * 30, httponly=True)
        return resp
    if not check_access():
        # 無權限者看到「空白頁」——不暴露網站存在
        return render_template("blank.html"), 404
    return render_template("index.html")


# ---------------- API ----------------
@app.route("/api/books")
@require_access
def api_books():
    books = []
    if os.path.isdir(DATA_DIR):
        for fn in os.listdir(DATA_DIR):
            if fn.endswith(".json") and fn != "tokens.json":
                data = analyzer.load_analysis(DATA_DIR, fn[:-5])
                if data:
                    books.append({
                        "book_id": data["book_id"],
                        "title": data.get("title", data["book_id"]),  # 書名，無則用 id
                        "chapters": [c["title"] for c in data["chapters"]],
                        "characters": list(data["characters"].keys()),
                    })
    return jsonify(books)


@app.route("/api/upload", methods=["POST"])
@require_access
def api_upload():
    f = request.files.get("file")
    if not f or not f.filename.endswith(".txt"):
        return jsonify({"error": "請上傳 .txt 文件"}), 400
    # 書名 = 文件名（去擴展名）
    book_name = os.path.splitext(f.filename)[0].strip() or "未命名"
    book_id = uuid.uuid4().hex[:8]
    raw = f.read()
    # 嘗試常見編碼
    text = None
    for enc in ("utf-8", "gb18030", "big5", "utf-16"):
        try:
            text = raw.decode(enc)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    if text is None:
        return jsonify({"error": "無法識別文件編碼"}), 400

    with open(os.path.join(UPLOAD_DIR, f"{book_id}.txt"), "w", encoding="utf-8") as out:
        out.write(text)

    data = analyzer.analyze_book(text, book_id)
    data["title"] = book_name  # 記錄書名
    analyzer.save_analysis(data, DATA_DIR)
    return jsonify({"book_id": book_id, "title": book_name,
                    "chapters": [c["title"] for c in data["chapters"]],
                    "characters": list(data["characters"].keys())})


@app.route("/api/book/<book_id>")
@require_access
def api_book(book_id):
    data = analyzer.load_analysis(DATA_DIR, book_id)
    if not data:
        return jsonify({"error": "not found"}), 404
    # 摘要（不含原文，減少傳輸）
    return jsonify({
        "book_id": book_id,
        "title": data.get("title", book_id),
        "chapters": [{"title": c["title"], "organ_emotion": c["organ_emotion"],
                      "total_hits": c["total_hits"]} for c in data["chapters"]],
        "characters": [{"name": n, "organ_emotion": d["organ_emotion"],
                        "total_hits": d["total_hits"]} for n, d in data["characters"].items()],
    })


@app.route("/api/book/<book_id>/hits")
@require_access
def api_hits(book_id):
    """點擊器官時獲取對應原文。scope: chapter:<idx> / character:<name> / book"""
    data = analyzer.load_analysis(DATA_DIR, book_id)
    if not data:
        return jsonify({"error": "not found"}), 404
    scope = request.args.get("scope", "book")
    organ = request.args.get("organ", "")
    hits = []
    if scope == "book":
        for c in data["chapters"]:
            hits.extend(c["organ_hits"].get(organ, []))
    elif scope.startswith("chapter:"):
        idx = int(scope.split(":")[1])
        if 0 <= idx < len(data["chapters"]):
            hits = data["chapters"][idx]["organ_hits"].get(organ, [])
    elif scope.startswith("character:"):
        name = scope.split(":", 1)[1]
        hits = data["characters"].get(name, {}).get("organ_hits", {}).get(organ, [])
    return jsonify({"organ": organ, "hits": hits})


if __name__ == "__main__":
    app.run(host=CONFIG.get("host", "127.0.0.1"),
            port=CONFIG.get("port", 5000),
            debug=CONFIG.get("debug", False))