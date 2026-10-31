# -*- coding: utf-8 -*-
"""生成獨立的三人對比演示頁（不依賴網站，雙擊即可打開）。"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(BASE, "data", "dc101771.json"), encoding="utf-8"))

names = ["宝玉", "黛玉", "凤姐"]
chars = {}
for n in names:
    # characters 是 dict: {name: {...}}（兼容 list 形式）
    raw = data["characters"]
    if isinstance(raw, dict):
        c = raw.get(n)
    else:
        c = next(x for x in raw if x["name"] == n)
    chars[n] = c["organ_emotion"] if "organ_emotion" in c else c

body_path_js = open(os.path.join(BASE, "static", "body-path.js"), encoding="utf-8").read()

html = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<title>紅樓夢三人情緒人圖對比 — BodyWords</title>
<style>
  body { background:#0e1116; color:#e6e9ef; font-family:"Noto Sans TC","Microsoft JhengHei",sans-serif; margin:0; padding:24px; }
  h1 { font-size:20px; text-align:center; margin-bottom:4px; }
  .sub { text-align:center; color:#8a93a5; font-size:13px; margin-bottom:24px; }
  .row { display:flex; gap:32px; justify-content:center; align-items:flex-start; flex-wrap:wrap; }
  .card { text-align:center; }
  .card h2 { font-size:16px; margin-bottom:6px; }
  .card .stat { font-size:12px; color:#8a93a5; margin-bottom:8px; line-height:1.6; }
  .card svg { height:420px; }
  .legend { display:flex; gap:18px; justify-content:center; margin-top:20px; font-size:13px; }
  .legend span::before { content:""; display:inline-block; width:12px; height:12px; border-radius:3px; margin-right:5px; vertical-align:middle; }
  .l-joy::before { background:#f6c445; } .l-anger::before { background:#e53935; }
  .l-sadness::before { background:#42a5f5; } .l-fear::before { background:#8e44ad; }
  .l-surprise::before { background:#ff9800; }
</style>
</head>
<body>
<h1>《紅樓夢》三人情緒人圖對比</h1>
<div class="sub">基於全文 86 萬字的器官-情緒字面描寫統計 · 顏色=情緒種類 · 深淺=出現強度</div>
<div class="row" id="row"></div>
<div class="legend">
  <span class="l-joy">喜</span><span class="l-anger">怒</span><span class="l-sadness">哀</span>
  <span class="l-fear">懼</span><span class="l-surprise">驚</span>
</div>
<script>
__BODY_PATH__
const CHARS = __CHARS__;
const EMOTION_COLOR = { joy:"#f6c445", anger:"#e53935", sadness:"#42a5f5", fear:"#8e44ad", surprise:"#ff9800" };
const EMOTION_ZH = { joy:"喜", anger:"怒", sadness:"哀", fear:"懼", surprise:"驚" };
const ORGAN_ZH = { head:"頭", face:"臉", eyes:"眼", brows:"眉", mouth:"嘴", forehead:"額", ears:"耳", nose:"鼻",
  neck:"頸", shoulder:"肩", chest:"胸", heart:"心", lungs:"肺", liver:"肝", spleen:"脾", kidney:"腎",
  stomach:"胃", intestines:"腸", brain:"腦", belly:"腹", back:"背", waist:"腰", arm:"臂", hand:"手",
  leg:"腿", foot:"腳", skin:"膚" };

function bodySVG(uid) {
  return `<svg viewBox="0 0 240 460" xmlns="http://www.w3.org/2000/svg" width="240" height="460">
  <defs>
    <linearGradient id="skin${uid}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#20262f"/><stop offset="30%" stop-color="#333d4a"/>
      <stop offset="50%" stop-color="#3b4655"/><stop offset="70%" stop-color="#333d4a"/>
      <stop offset="100%" stop-color="#20262f"/>
    </linearGradient>
    <clipPath id="bodyClip${uid}" transform="translate(${BODY_TX},${BODY_TY}) scale(${BODY_S})">
      <path d="${BODY_PATH}"/>
    </clipPath>
  </defs>
  <g transform="translate(${BODY_TX},${BODY_TY}) scale(${BODY_S})">
    <path d="${BODY_PATH}" fill="url(#skin${uid})" stroke="#5f7086" stroke-width="${(6/BODY_S).toFixed(1)}" stroke-linejoin="round"/>
  </g>
  <g clip-path="url(#bodyClip${uid})" id="organs${uid}">
    <path class="organ" data-organ="head" d="M92 4 Q119 -6 146 4 Q152 30 146 56 Q133 74 119 74 Q105 74 92 56 Q86 30 92 4 Z"/>
    <path class="organ" data-organ="forehead" d="M98 8 Q119 2 140 8 Q142 16 140 24 Q119 18 98 24 Q96 16 98 8 Z"/>
    <path class="organ" data-organ="brows" d="M100 29 Q108 25 116 29 Q108 28 100 31 Z"/>
    <path class="organ" data-organ="brows" d="M122 29 Q130 25 138 29 Q130 28 122 31 Z"/>
    <path class="organ" data-organ="eyes" d="M100 38 Q107 33 116 38 Q107 42 100 38 Z"/>
    <path class="organ" data-organ="eyes" d="M122 38 Q129 33 138 38 Q129 42 122 38 Z"/>
    <path class="organ" data-organ="ears" d="M93 32 Q90 38 92 46 Q94 52 97 50 Q95 42 96 34 Z"/>
    <path class="organ" data-organ="ears" d="M145 32 Q148 38 146 46 Q144 52 141 50 Q143 42 142 34 Z"/>
    <path class="organ" data-organ="nose" d="M117 38 L119 48 Q115 50 116 52 Q119 54 122 52 Q123 50 121 48 L121 38 Z"/>
    <path class="organ" data-organ="mouth" d="M110 56 Q114 53 119 56 Q124 53 128 56 Q124 61 119 61 Q114 61 110 56 Z"/>
    <path class="organ" data-organ="neck" d="M105 64 L105 80 Q119 87 133 80 L133 64 Q119 72 105 64 Z"/>
    <path class="organ" data-organ="shoulder" d="M66 86 Q78 80 91 87 Q93 96 90 105 Q76 107 67 100 Q64 92 66 86 Z"/>
    <path class="organ" data-organ="shoulder" d="M172 86 Q160 80 147 87 Q145 96 148 105 Q162 107 171 100 Q174 92 172 86 Z"/>
    <path class="organ" data-organ="chest" d="M88 94 Q119 84 150 94 Q156 116 152 138 Q119 147 88 138 Q82 116 88 94 Z"/>
    <path class="organ" data-organ="heart" d="M129 106 C 125 102 117 103 117 111 C 117 119 125 126 129 129 C 133 126 141 119 141 111 C 141 103 133 102 129 106 Z"/>
    <path class="organ" data-organ="brain" d="M102 10 Q110 4 119 6 Q128 4 136 10 Q141 16 138 24 Q132 30 119 28 Q106 30 100 24 Q97 16 102 10 Z"/>
    <path class="organ" data-organ="lungs" d="M96 100 Q86 104 84 120 Q83 134 90 141 Q97 144 99 136 L100 110 Q100 102 96 100 Z"/>
    <path class="organ" data-organ="lungs" d="M144 100 Q154 104 156 120 Q157 134 150 141 Q143 144 141 136 L140 110 Q140 102 144 100 Z"/>
    <path class="organ" data-organ="liver" d="M92 144 Q104 142 114 148 Q116 156 108 160 Q96 160 90 154 Q88 148 92 144 Z"/>
    <path class="organ" data-organ="stomach" d="M126 146 Q138 144 142 152 Q144 162 134 164 Q124 164 122 156 Q122 148 126 146 Z"/>
    <path class="organ" data-organ="spleen" d="M144 148 Q152 148 152 156 Q152 164 144 162 Q140 158 142 150 Z"/>
    <path class="organ" data-organ="kidney" d="M96 168 Q92 172 94 180 Q96 186 102 184 Q106 180 104 172 Q102 166 96 168 Z"/>
    <path class="organ" data-organ="kidney" d="M144 168 Q148 172 146 180 Q144 186 138 184 Q134 180 136 172 Q138 166 144 168 Z"/>
    <path class="organ" data-organ="intestines" d="M96 176 Q92 186 98 194 Q104 200 112 196 Q118 192 116 186 Q114 182 108 184 Q104 186 106 190 M112 196 Q120 202 130 198 Q140 194 138 186 Q136 180 130 182 Q126 184 128 190 M130 198 Q136 204 132 210 Q126 214 118 210 Q112 206 116 200" fill="none" stroke-width="4" stroke-linecap="round"/>
    <path class="organ" data-organ="belly" d="M91 141 Q119 149 149 141 Q151 156 149 170 Q119 178 91 170 Q89 156 91 141 Z"/>
    <path class="organ" data-organ="waist" d="M92 171 Q119 179 148 171 Q151 188 149 203 Q119 211 91 203 Q89 188 92 171 Z"/>
    <path class="organ" data-organ="arm" d="M72 102 Q60 118 54 145 Q48 175 45 208 Q43 232 44 246 Q45 254 51 253 Q57 251 58 240 Q62 210 67 180 Q72 150 78 126 Q81 110 72 102 Z"/>
    <path class="organ" data-organ="arm" d="M168 102 Q180 118 186 145 Q192 175 195 208 Q197 232 196 246 Q195 254 189 253 Q183 251 182 240 Q178 210 173 180 Q168 150 162 126 Q159 110 168 102 Z"/>
    <path class="organ" data-organ="hand" d="M30 247 Q26 256 28 264 Q31 272 38 272 Q45 271 47 263 Q49 254 46 248 Q40 243 30 247 Z"/>
    <path class="organ" data-organ="hand" d="M210 247 Q214 256 212 264 Q209 272 202 272 Q195 271 193 263 Q191 254 194 248 Q200 243 210 247 Z"/>
    <path class="organ" data-organ="leg" d="M97 258 Q79 278 80 310 Q82 345 85 380 Q86 410 88 430 Q90 442 97 442 Q104 442 106 430 Q108 395 108 355 Q108 310 110 268 Q110 260 97 258 Z"/>
    <path class="organ" data-organ="leg" d="M143 258 Q161 278 160 310 Q158 345 155 380 Q154 410 152 430 Q150 442 143 442 Q136 442 134 430 Q132 395 132 355 Q132 310 130 268 Q130 260 143 258 Z"/>
    <path class="organ" data-organ="foot" d="M78 432 Q72 440 74 448 Q76 455 84 456 Q92 456 98 452 Q101 446 100 436 Q92 430 78 432 Z"/>
    <path class="organ" data-organ="foot" d="M162 432 Q168 440 166 448 Q164 455 156 456 Q148 456 142 452 Q139 446 140 436 Q148 430 162 432 Z"/>
  </g>
  <g transform="translate(${BODY_TX},${BODY_TY}) scale(${BODY_S})">
    <path d="${BODY_PATH}" fill="none" stroke="#6b7d94" stroke-width="${(6/BODY_S).toFixed(1)}" stroke-linejoin="round"/>
  </g>
</svg>`;
}

function mixHex(a, b, w) {
  const pa = [1,3,5].map(i => parseInt(a.substr(i,2),16));
  const pb = [1,3,5].map(i => parseInt(b.substr(i,2),16));
  return "#" + pa.map((v,i) => Math.round(v*(1-w)+pb[i]*w).toString(16).padStart(2,"0")).join("");
}
function shade(hex, intensity) { return mixHex("#2a323f", hex, intensity); }

function render() {
  const row = document.getElementById("row");
  for (const [name, data] of Object.entries(CHARS)) {
    const total = Object.values(data).flatMap(d => Object.values(d)).reduce((a,b)=>a+b,0);
    const uid = "u" + name;
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `<h2>${name}</h2><div class="stat">描寫總量 ${total} 條</div><div id="w${uid}"></div>`;
    row.appendChild(card);
    document.getElementById("w" + uid).innerHTML = bodySVG(uid);
    const wrap = document.getElementById("w" + uid);
    const maxVal = Math.max(1, ...Object.values(data).flatMap(d => Object.values(d)));
    wrap.querySelectorAll(".organ").forEach(el => {
      const d = data[el.dataset.organ];
      if (!d) { el.style.fill = "transparent"; return; }
      const entries = Object.entries(d).sort((a,b) => b[1]-a[1]);
      const [emo, cnt] = entries[0];
      const intensity = Math.min(1, 0.25 + 0.75 * (cnt / maxVal));
      let color = EMOTION_COLOR[emo];
      if (entries.length > 1) {
        const [e2, c2] = entries[1];
        color = mixHex(color, EMOTION_COLOR[e2], (c2/(cnt+c2))*0.5);
      }
      if (el.tagName === "path" && el.getAttribute("fill") === "none") el.style.stroke = shade(color, intensity);
      else el.style.fill = shade(color, intensity);
      el.dataset.tip = `${ORGAN_ZH[el.dataset.organ]}: ${entries.map(([e,c])=>EMOTION_ZH[e]+"×"+c).join(" ")}`;
      el.addEventListener("mouseenter", () => { document.querySelector(".sub").textContent = el.dataset.tip; });
    });
    // 情緒結構小結
    const emoTotal = {};
    Object.values(data).forEach(d => Object.entries(d).forEach(([e,c]) => emoTotal[e] = (emoTotal[e]||0)+c));
    const top = Object.entries(emoTotal).sort((a,b)=>b[1]-a[1]).slice(0,2)
      .map(([e,c]) => EMOTION_ZH[e] + Math.round(c/total*100) + "%").join(" / ");
    const stat = card.querySelector(".stat");
    stat.innerHTML += `主導：${top}`;
  }
}
render();
</script>
</body>
</html>"""

html = html.replace("__BODY_PATH__", body_path_js)
html = html.replace("__CHARS__", json.dumps(chars, ensure_ascii=False))

out = os.path.join(BASE, "三人對比演示.html")
open(out, "w", encoding="utf-8").write(html)
print("已生成:", out)