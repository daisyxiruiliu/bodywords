// BodyWords 前端主邏輯
// 人形解剖圖 SVG + 目錄 + 對比 + 多語言

const ORGAN_ZH = {
  head: "頭", face: "臉", eyes: "眼", brows: "眉", mouth: "嘴", forehead: "額",
  ears: "耳", nose: "鼻", neck: "頸", shoulder: "肩", chest: "胸", heart: "心",
  lungs: "肺", liver: "肝", spleen: "脾", kidney: "腎", stomach: "胃",
  intestines: "腸", brain: "腦",
  belly: "腹", back: "背", waist: "腰", arm: "臂", hand: "手", leg: "腿",
  foot: "腳", skin: "膚"
};
const ORGAN_EN = {
  head: "Head", face: "Face", eyes: "Eyes", brows: "Brows", mouth: "Mouth", forehead: "Forehead",
  ears: "Ears", nose: "Nose", neck: "Neck", shoulder: "Shoulder", chest: "Chest", heart: "Heart",
  lungs: "Lungs", liver: "Liver", spleen: "Spleen", kidney: "Kidney", stomach: "Stomach",
  intestines: "Intestines", brain: "Brain",
  belly: "Belly", back: "Back", waist: "Waist", arm: "Arm", hand: "Hand", leg: "Leg",
  foot: "Foot", skin: "Skin"
};
const EMOTION_ZH = { joy: "喜", anger: "怒", sadness: "哀", fear: "懼", surprise: "驚" };
const EMOTION_EN = { joy: "Joy", anger: "Anger", sadness: "Sadness", fear: "Fear", surprise: "Surprise" };
const EMOTION_COLOR = {
  joy: "#f6c445", anger: "#e53935", sadness: "#42a5f5", fear: "#8e44ad", surprise: "#ff9800"
};

const I18N = {
  zh: {
    selectBook: "請選擇或上傳一本書", book: "整本書", chapter: "章節", character: "人物",
    compare: "縱向對比", collapse: "收起", expand: "展開", genCompare: "生成對比",
    compareType: "對比對象", noData: "暫無數據", hits: "相關原文",
    uploading: "上傳與分析中…", uploadDone: "分析完成", uploadFail: "上傳失敗",
    noHits: "此器官暫無對應原文", emotionMix: "情緒"
  },
  en: {
    selectBook: "Select or upload a book", book: "Whole Book", chapter: "Chapters", character: "Characters",
    compare: "Slice Compare", collapse: "Collapse", expand: "Expand", genCompare: "Generate",
    compareType: "Compare by", noData: "No data", hits: "Related Text",
    uploading: "Uploading & analyzing…", uploadDone: "Analysis complete", uploadFail: "Upload failed",
    noHits: "No related text for this organ", emotionMix: "Emotions"
  }
};
let lang = localStorage.getItem("bw_lang") || "zh";
const T = (k) => I18N[lang][k] || k;
const organName = (o) => (lang === "en" ? ORGAN_EN[o] : ORGAN_ZH[o]);
const emoName = (e) => (lang === "en" ? EMOTION_EN[e] : EMOTION_ZH[e]);

// ---------------- 狀態 ----------------
let books = [];
let currentBook = null;      // {book_id, chapters, characters}
let currentScope = "book";   // book | chapter | character
let currentTarget = null;    // null / index / name
let organData = {};          // organ -> {emotion: count}

// ---------------- 人形解剖圖 SVG ----------------
// 底圖：公版醫學剪影（Wikimedia Commons "Human body silhouette.svg", PD, Mikael Häggström)
// v5：顏色以「熱力圖」方式長在身體上——用剪影路徑裁剪，絕無漂浮圓圈
// 器官區域 = 身體輪廓內的解剖分區（頭/頸/胸/腹/四肢），點擊即查原文
function bodySVG(idPrefix = "", small = false) {
  const uid = idPrefix || "m";
  const bodyG = `<g transform="translate(${BODY_TX},${BODY_TY}) scale(${BODY_S})"><path d="${BODY_PATH}" fill="BODY" stroke="STROKE" stroke-width="${(6/BODY_S).toFixed(1)}" stroke-linejoin="round"/></g>`;
  return `
<svg viewBox="0 0 240 460" xmlns="http://www.w3.org/2000/svg" class="body-svg">
  <defs>
    <linearGradient id="skin${uid}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#20262f"/>
      <stop offset="30%" stop-color="#333d4a"/>
      <stop offset="50%" stop-color="#3b4655"/>
      <stop offset="70%" stop-color="#333d4a"/>
      <stop offset="100%" stop-color="#20262f"/>
    </linearGradient>
    <radialGradient id="glow${uid}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#4fc3f7" stop-opacity="0.10"/>
      <stop offset="100%" stop-color="#4fc3f7" stop-opacity="0"/>
    </radialGradient>
    <filter id="organGlow${uid}" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="2.5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <!-- 裁剪：只允許顏色出現在身體輪廓內 -->
    <clipPath id="bodyClip${uid}" transform="translate(${BODY_TX},${BODY_TY}) scale(${BODY_S})">
      <path d="${BODY_PATH}"/>
    </clipPath>
  </defs>
  <ellipse cx="120" cy="230" rx="112" ry="218" fill="url(#glow${uid})"/>

  <!-- 1. 剪影底圖 -->
  ${bodyG.replace('BODY', 'url(#skin' + uid + ')').replace('STROKE', '#5f7086')}

  <!-- 2. 器官熱力層（裁剪在身體內，貼合輪廓的形狀版） -->
  <g clip-path="url(#bodyClip${uid})" id="organs${uid}" filter="url(#organGlow${uid})">
    <!-- 頭區（整個頭部） -->
    <path class="organ" data-organ="head" d="M92 4 Q119 -6 146 4 Q152 30 146 56 Q133 74 119 74 Q105 74 92 56 Q86 30 92 4 Z"/>

    <!-- 額 -->
    <path class="organ" data-organ="forehead" d="M98 8 Q119 2 140 8 Q142 16 140 24 Q119 18 98 24 Q96 16 98 8 Z"/>
    <!-- 眉（彎眉形） -->
    <path class="organ" data-organ="brows" d="M100 29 Q108 25 116 29 Q108 28 100 31 Z"/>
    <path class="organ" data-organ="brows" d="M122 29 Q130 25 138 29 Q130 28 122 31 Z"/>
    <!-- 眼（杏仁形，帶眼頭眼尾） -->
    <path class="organ" data-organ="eyes" d="M100 38 Q107 33 116 38 Q107 42 100 38 Z"/>
    <path class="organ" data-organ="eyes" d="M122 38 Q129 33 138 38 Q129 42 122 38 Z"/>
    <!-- 耳（C形耳廓） -->
    <path class="organ" data-organ="ears" d="M93 32 Q90 38 92 46 Q94 52 97 50 Q95 42 96 34 Z"/>
    <path class="organ" data-organ="ears" d="M145 32 Q148 38 146 46 Q144 52 141 50 Q143 42 142 34 Z"/>
    <!-- 鼻（鼻樑+鼻翼輪廓） -->
    <path class="organ" data-organ="nose" d="M117 38 L119 48 Q115 50 116 52 Q119 54 122 52 Q123 50 121 48 L121 38 Z"/>
    <!-- 嘴（唇形：上唇M字+下唇弧） -->
    <path class="organ" data-organ="mouth" d="M110 56 Q114 53 119 56 Q124 53 128 56 Q124 61 119 61 Q114 61 110 56 Z"/>
    <!-- 臉（透明熱區，覆蓋面部） -->
    <path class="organ" data-organ="face" d="M94 6 Q119 -2 144 6 Q150 32 144 58 Q132 72 119 72 Q106 72 94 58 Q88 32 94 6 Z" fill-opacity="0" style="pointer-events:none"/>
    <!-- 頸（貼合剪影 y64-82，寬 x105-133） -->
    <path class="organ" data-organ="neck" d="M105 64 L105 80 Q119 87 133 80 L133 64 Q119 72 105 64 Z"/>
    <!-- 肩（貼合三角肌：左 x64-92 y84-106，右對稱） -->
    <path class="organ" data-organ="shoulder" d="M66 86 Q78 80 91 87 Q93 96 90 105 Q76 107 67 100 Q64 92 66 86 Z"/>
    <path class="organ" data-organ="shoulder" d="M172 86 Q160 80 147 87 Q145 96 148 105 Q162 107 171 100 Q174 92 172 86 Z"/>
    <!-- 胸（貼合剪影：y94-140，上緣隨鎖骨弧、下緣隨肋弧） -->
    <path class="organ" data-organ="chest" d="M88 94 Q119 84 150 94 Q156 116 152 138 Q119 147 88 138 Q82 116 88 94 Z"/>
    <!-- 心（人體左側=觀者右側，略小） -->
    <path class="organ" data-organ="heart" d="M129 106 C 125 102 117 103 117 111 C 117 119 125 126 129 129 C 133 126 141 119 141 111 C 141 103 133 102 129 106 Z"/>
    <!-- 腦（顱腔內，大腦形） -->
    <path class="organ" data-organ="brain" d="M102 10 Q110 4 119 6 Q128 4 136 10 Q141 16 138 24 Q132 30 119 28 Q106 30 100 24 Q97 16 102 10 Z"/>
    <!-- 肺（真實肺形：上尖下寬，外緣弧形） -->
    <path class="organ" data-organ="lungs" d="M96 100 Q86 104 84 120 Q83 134 90 141 Q97 144 99 136 L100 110 Q100 102 96 100 Z"/>
    <path class="organ" data-organ="lungs" d="M144 100 Q154 104 156 120 Q157 134 150 141 Q143 144 141 136 L140 110 Q140 102 144 100 Z"/>
    <!-- 肝（人體右側=觀者左側，肋下） -->
    <path class="organ" data-organ="liver" d="M92 144 Q104 142 114 148 Q116 156 108 160 Q96 160 90 154 Q88 148 92 144 Z"/>
    <!-- 胃（人體左側=觀者右側） -->
    <path class="organ" data-organ="stomach" d="M126 146 Q138 144 142 152 Q144 162 134 164 Q124 164 122 156 Q122 148 126 146 Z"/>
    <!-- 脾（人體左側=觀者右側，胃外側） -->
    <path class="organ" data-organ="spleen" d="M144 148 Q152 148 152 156 Q152 164 144 162 Q140 158 142 150 Z"/>
    <!-- 腎（腰後兩側，投影在軀幹下部兩旁） -->
    <path class="organ" data-organ="kidney" d="M96 168 Q92 172 94 180 Q96 186 102 184 Q106 180 104 172 Q102 166 96 168 Z"/>
    <path class="organ" data-organ="kidney" d="M144 168 Q148 172 146 180 Q144 186 138 184 Q134 180 136 172 Q138 166 144 168 Z"/>
    <!-- 腸（腹腔下部盤曲） -->
    <path class="organ" data-organ="intestines" d="M96 176 Q92 186 98 194 Q104 200 112 196 Q118 192 116 186 Q114 182 108 184 Q104 186 106 190 M112 196 Q120 202 130 198 Q140 194 138 186 Q136 180 130 182 Q126 184 128 190 M130 198 Q136 204 132 210 Q126 214 118 210 Q112 206 116 200" fill="none" stroke-width="4" stroke-linecap="round"/>
    <!-- 腹（貼合剪影 y141-172，兩側隨腰身內收） -->
    <path class="organ" data-organ="belly" d="M91 141 Q119 149 149 141 Q151 156 149 170 Q119 178 91 170 Q89 156 91 141 Z"/>
    <!-- 腰（貼合剪影 y171-205，隨髖部外擴） -->
    <path class="organ" data-organ="waist" d="M92 171 Q119 179 148 171 Q151 188 149 203 Q119 211 91 203 Q89 188 92 171 Z"/>
    <!-- 背（透明熱區） -->
    <path class="organ" data-organ="back" d="M84 96 L80 180 Q80 212 92 240 L148 240 Q160 212 160 180 L156 96 Z" fill-opacity="0" style="pointer-events:none"/>
    <!-- 臂（貼合剪影臂走向：外緣 58→44，內緣 78→64，y100-245） -->
    <path class="organ" data-organ="arm" d="M72 102 Q60 118 54 145 Q48 175 45 208 Q43 232 44 246 Q45 254 51 253 Q57 251 58 240 Q62 210 67 180 Q72 150 78 126 Q81 110 72 102 Z"/>
    <path class="organ" data-organ="arm" d="M168 102 Q180 118 186 145 Q192 175 195 208 Q197 232 196 246 Q195 254 189 253 Q183 251 182 240 Q178 210 173 180 Q168 150 162 126 Q159 110 168 102 Z"/>
    <!-- 手（貼合剪影：左 x28-52 y245-270） -->
    <path class="organ" data-organ="hand" d="M30 247 Q26 256 28 264 Q31 272 38 272 Q45 271 47 263 Q49 254 46 248 Q40 243 30 247 Z"/>
    <path class="organ" data-organ="hand" d="M210 247 Q214 256 212 264 Q209 272 202 272 Q195 271 193 263 Q191 254 194 248 Q200 243 210 247 Z"/>
    <!-- 腿（貼合剪影：大腿上寬，小腿漸窄至踝） -->
    <path class="organ" data-organ="leg" d="M97 258 Q79 278 80 310 Q82 345 85 380 Q86 410 88 430 Q90 442 97 442 Q104 442 106 430 Q108 395 108 355 Q108 310 110 268 Q110 260 97 258 Z"/>
    <path class="organ" data-organ="leg" d="M143 258 Q161 278 160 310 Q158 345 155 380 Q154 410 152 430 Q150 442 143 442 Q136 442 134 430 Q132 395 132 355 Q132 310 130 268 Q130 260 143 258 Z"/>
    <!-- 腳（貼合剪影：y438-455） -->
    <path class="organ" data-organ="foot" d="M78 432 Q72 440 74 448 Q76 455 84 456 Q92 456 98 452 Q101 446 100 436 Q92 430 78 432 Z"/>
    <path class="organ" data-organ="foot" d="M162 432 Q168 440 166 448 Q164 455 156 456 Q148 456 142 452 Q139 446 140 436 Q148 430 162 432 Z"/>
    <!-- 膚（全身透明熱區） -->
    <g transform="translate(${BODY_TX},${BODY_TY}) scale(${BODY_S})">
      <path class="organ" data-organ="skin" d="${BODY_PATH}" fill-opacity="0" stroke-opacity="0" style="pointer-events:none"/>
    </g>
  </g>

  <!-- 3. 剪影描邊（壓在最上層，勾勒輪廓） -->
  ${bodyG.replace('BODY', 'none').replace('STROKE', '#6b7d94')}
</svg>`;
}

// 根據 organData 給器官上色：主情緒決定色系，強度決定深淺
function paintFigure(container, data) {
  const maxVal = Math.max(1, ...Object.values(data).flatMap(d => Object.values(d)));
  container.querySelectorAll(".organ").forEach(el => {
    const organ = el.dataset.organ;
    const d = data[organ];
    if (!d || Object.keys(d).length === 0) {
      // 無數據：完全透明，讓身體底色透出（避免暗色條帶）
      el.style.fill = "transparent";
      if (el.tagName === "path" && el.getAttribute("fill") === "none") el.style.stroke = "transparent";
      el.dataset.tip = "";
      return;
    }
    // 主情緒 = 出現次數最多
    const entries = Object.entries(d).sort((a, b) => b[1] - a[1]);
    const [mainEmo, mainCnt] = entries[0];
    const intensity = Math.min(1, 0.25 + 0.75 * (mainCnt / maxVal));
    // 混合次要情緒顏色（簡單線性混合）
    let color = EMOTION_COLOR[mainEmo];
    if (entries.length > 1) {
      const [emo2, cnt2] = entries[1];
      const w2 = cnt2 / (mainCnt + cnt2);
      color = mixHex(EMOTION_COLOR[mainEmo], EMOTION_COLOR[emo2], w2 * 0.5);
    }
    const c = applyIntensity(color, intensity);
    if (el.tagName === "path" && el.getAttribute("fill") === "none") {
      // 描邊型器官（如腸）：上色到 stroke
      el.style.stroke = c;
      el.style.fill = "none";
    } else {
      el.style.fill = c;
    }
    el.dataset.tip = `${organName(organ)}: ${entries.map(([e, c]) => `${emoName(e)}×${c}`).join(" ")}`;
  });
}

function mixHex(a, b, w) {
  const pa = [1, 3, 5].map(i => parseInt(a.substr(i, 2), 16));
  const pb = [1, 3, 5].map(i => parseInt(b.substr(i, 2), 16));
  const mix = pa.map((v, i) => Math.round(v * (1 - w) + pb[i] * w));
  return "#" + mix.map(v => v.toString(16).padStart(2, "0")).join("");
}
function applyIntensity(hex, intensity) {
  // 深淺：與深底色混合
  return mixHex("#2a323f", hex, intensity);
}

// ---------------- 圖例 ----------------
function renderLegend() {
  const el = document.getElementById("legend");
  el.innerHTML = Object.keys(EMOTION_COLOR).map(e =>
    `<div><span class="swatch" style="background:${EMOTION_COLOR[e]}"></span>${emoName(e)}</div>`
  ).join("") + `<div class="muted small-text" style="margin-top:6px">${lang === "en" ? "Darker = stronger" : "越深 = 越強烈"}</div>`;
}

// ---------------- 目錄 ----------------
async function loadBooks() {
  const res = await fetch("/api/books");
  books = await res.json();
  renderBookList();
}

function renderBookList() {
  const el = document.getElementById("bookList");
  el.innerHTML = books.map((b, i) => `
    <div class="book-item">
      <div class="book-name ${currentBook && currentBook.book_id === b.book_id ? "active" : ""}" data-idx="${i}">
        📖 ${b.title || b.book_id}
      </div>
      ${currentBook && currentBook.book_id === b.book_id ? `
        <div class="toc-sub">
          <div data-scope="book" class="active">${T("book")}</div>
          <div data-scope="chapter">${T("chapter")} (${b.chapters.length})</div>
          <div data-scope="character">${T("character")} (${b.characters.length})</div>
        </div>` : ""}
    </div>`).join("") || `<p class="muted small-text">${T("noData")}</p>`;

  el.querySelectorAll(".book-name").forEach(n =>
    n.onclick = () => selectBook(books[+n.dataset.idx]));
  el.querySelectorAll(".toc-sub div").forEach(n =>
    n.onclick = () => setScope(n.dataset.scope));
}

async function selectBook(b) {
  const res = await fetch(`/api/book/${b.book_id}`);
  currentBook = await res.json();
  currentScope = "book";
  currentTarget = null;
  renderBookList();
  renderComparePick();
  document.getElementById("viewTitle").textContent = `📖 ${currentBook.title || b.book_id}`;
  showFigure();
  // 展開目錄子項
  const sub = document.querySelector(".toc-sub");
  if (sub) sub.querySelectorAll("div")[0].classList.add("active");
}

function setScope(scope) {
  currentScope = scope;
  currentTarget = null;
  renderBookList();
  renderScopeSelector();
  // 視圖切換：compare 顯示對比視圖，其他顯示單圖
  const isCompare = scope === "compare";
  document.getElementById("singleView").classList.toggle("hidden", isCompare);
  document.getElementById("compareView").classList.toggle("hidden", !isCompare);
  document.getElementById("backBtn").classList.toggle("hidden", !isCompare);
  document.querySelectorAll(".tab").forEach(t =>
    t.classList.toggle("active", t.dataset.scope === scope));
  if (isCompare) {
    renderComparePick();
    document.getElementById("viewTitle").textContent = `🩻 ${T("compare")}`;
  } else {
    showFigure();
  }
}

function renderScopeSelector() {
  const el = document.getElementById("scopeSelector");
  if (currentScope === "book" || !currentBook) { el.classList.add("hidden"); return; }
  el.classList.remove("hidden");
  const items = currentScope === "chapter"
    ? currentBook.chapters.map((c, i) => ({ label: c.title, value: i }))
    : currentBook.characters.map(c => ({ label: c.name, value: c.name }));
  // 下拉式選擇（省空間，不擋人形圖）
  const label = document.createElement("span");
  label.className = "scope-label";
  label.textContent = currentScope === "chapter" ? "章節：" : "人物：";
  const sel = document.createElement("select");
  sel.className = "scope-select";
  sel.innerHTML = `<option value="">— 請選擇 —</option>` +
    items.map(it => `<option value="${it.value}">${it.label}</option>`).join("");
  sel.onchange = () => {
    if (sel.value === "") { currentTarget = null; showFigure(); return; }
    currentTarget = currentScope === "chapter" ? +sel.value : sel.value;
    showFigure();
  };
  el.innerHTML = "";
  el.appendChild(label);
  el.appendChild(sel);
}

function getOrganData() {
  if (!currentBook) return {};
  if (currentScope === "book") return mergeChapterData(currentBook.chapters);
  if (currentScope === "chapter" && currentTarget !== null)
    return currentBook.chapters[currentTarget]?.organ_emotion || {};
  if (currentScope === "character" && currentTarget !== null) {
    const c = currentBook.characters.find(x => x.name === currentTarget);
    return c ? c.organ_emotion : {};
  }
  return {};
}

function mergeChapterData(chapters) {
  const merged = {};
  chapters.forEach(c => {
    Object.entries(c.organ_emotion || {}).forEach(([organ, emos]) => {
      merged[organ] = merged[organ] || {};
      Object.entries(emos).forEach(([e, cnt]) => merged[organ][e] = (merged[organ][e] || 0) + cnt);
    });
  });
  return merged;
}

function showFigure() {
  const wrap = document.getElementById("figureWrap");
  wrap.innerHTML = bodySVG("main");
  organData = getOrganData();
  paintFigure(wrap, organData);
  bindOrganClicks(wrap, "main");
  renderLegend();
}

// ---------------- 器官點擊 → 原文 ----------------
function bindOrganClicks(wrap, prefix) {
  wrap.querySelectorAll(".organ").forEach(el => {
    el.onclick = () => openOrganModal(el.dataset.organ);
    el.onmouseenter = () => { if (el.dataset.tip) showToast(el.dataset.tip); };
  });
}

async function openOrganModal(organ) {
  if (!currentBook) return;
  let scopeParam = "book";
  if (currentScope === "chapter" && currentTarget !== null) scopeParam = `chapter:${currentTarget}`;
  if (currentScope === "character" && currentTarget !== null) scopeParam = `character:${currentTarget}`;
  const res = await fetch(`/api/book/${currentBook.book_id}/hits?scope=${encodeURIComponent(scopeParam)}&organ=${organ}`);
  const data = await res.json();
  document.getElementById("modalTitle").textContent =
    `${organName(organ)} — ${T("hits")}`;
  const body = document.getElementById("modalBody");
  body.innerHTML = (data.hits || []).map(h => `
    <div class="hit-item">
      ${highlightQuote(h.quote, organ)}
      <div class="hit-emo">${T("emotionMix")}: ${h.emotion.map(emoName).join("、")}</div>
    </div>`).join("") || `<p class="muted">${T("noHits")}</p>`;
  document.getElementById("organModal").classList.remove("hidden");
}

function highlightQuote(q, organ) {
  // 高亮器官詞（簡化：高亮器官中文名）
  const zh = ORGAN_ZH[organ];
  if (lang !== "en" && zh && q.includes(zh))
    return q.replace(new RegExp(zh, "g"), `<mark>${zh}</mark>`);
  return q;
}

// ---------------- 對比視圖（橫向切片 + 正態放大） ----------------
function initCompare() {
  document.getElementById("compareBtn").onclick = renderCompare;
  document.getElementById("compareType").onchange = renderComparePick;
  document.getElementById("backBtn").onclick = () => setScope("book");
  // 正態放大：鼠標在切片上移動時，以鼠標 x 為中心高斯放大
  const strip = document.getElementById("compareStrip");
  strip.addEventListener("mousemove", e => gaussianZoom(e));
  strip.addEventListener("mouseleave", () => resetZoom());
}

function gaussianZoom(e) {
  const strip = document.getElementById("compareStrip");
  const items = [...strip.querySelectorAll(".compare-item")];
  if (items.length < 2) return;
  const stripRect = strip.getBoundingClientRect();
  const mx = e.clientX - stripRect.left;  // 鼠標在 strip 內的 x
  const sigma = 180;                       // 高斯寬度（px）
  const maxScale = 1.55;
  items.forEach(it => {
    const r = it.getBoundingClientRect();
    const cx = r.left + r.width / 2 - stripRect.left;
    const d = cx - mx;
    const g = Math.exp(-(d * d) / (2 * sigma * sigma));  // 0~1
    const scale = 1 + (maxScale - 1) * g;
    it.style.transform = `scale(${scale.toFixed(3)})`;
    it.classList.toggle("dim", g < 0.25);
  });
}

// ---------------- 單圖科技感縮放：整張人圖跟隨鼠標平滑放大，方便查看 ----------------
function initFigureZoom() {
  const wrap = document.getElementById("figureWrap");
  const svgEl = () => wrap.querySelector("svg");
  let raf = null;

  wrap.addEventListener("mousemove", e => {
    const svg = svgEl();
    if (!svg) return;
    const rect = svg.getBoundingClientRect();
    // 鼠標在圖內的相對位置（0~1）
    const rx = (e.clientX - rect.left) / rect.width;
    const ry = (e.clientY - rect.top) / rect.height;
    if (raf) cancelAnimationFrame(raf);
    raf = requestAnimationFrame(() => {
      const scale = 1.8;  // 放大倍數
      svg.style.transformOrigin = `${(rx * 100).toFixed(1)}% ${(ry * 100).toFixed(1)}%`;
      svg.style.transform = `scale(${scale})`;
      svg.style.zIndex = 5;
      wrap.classList.add("zooming");
    });
  });
  wrap.addEventListener("mouseleave", () => {
    if (raf) cancelAnimationFrame(raf);
    const svg = svgEl();
    if (svg) { svg.style.transform = ""; svg.style.zIndex = ""; }
    wrap.classList.remove("zooming");
  });
}

function resetZoom() {
  document.querySelectorAll("#compareStrip .compare-item").forEach(it => {
    it.style.transform = "";
    it.classList.remove("dim");
  });
}

function renderComparePick() {
  const type = document.getElementById("compareType").value;
  const el = document.getElementById("comparePick");
  if (!currentBook) { el.innerHTML = `<span class="muted small-text">${T("noData")}</span>`; return; }
  const items = type === "chapter"
    ? currentBook.chapters.map((c, i) => ({ label: c.title, value: i }))
    : currentBook.characters.map(c => ({ label: c.name, value: c.name }));
  // 快速選擇按鈕
  const quick = `
    <div class="quick-pick">
      <button data-act="all">☑ 全部</button>
      <button data-act="none">☐ 清空</button>
      ${type === "chapter" ? `
        <button data-act="first10">前10章</button>
        <button data-act="first20">前20章</button>
        <button data-act="range">自訂範圍</button>` : `
        <button data-act="top10">前10人物</button>`}
    </div>`;
  el.innerHTML = quick + items.map((it, idx) =>
    `<label><input type="checkbox" value="${it.value}" data-idx="${idx}"> ${it.label}</label>`).join("");
  el.dataset.items = JSON.stringify(items);

  // 章節/人物列表摺疊切換（按鈕放在列表容器外面，收起後仍可點）
  const toggle = document.createElement("button");
  toggle.className = "compare-pick-toggle";
  toggle.textContent = "▾ 收起列表";
  toggle.onclick = () => {
    const pick = document.getElementById("comparePick");
    const collapsed = pick.classList.toggle("collapsed");
    toggle.textContent = collapsed ? "▸ 展開列表" : "▾ 收起列表";
  };
  el.insertAdjacentElement("afterend", toggle);  // 插在 comparePick 之後（同層）

  // 快速選擇事件
  el.querySelectorAll(".quick-pick button").forEach(btn => {
    btn.onclick = () => {
      const act = btn.dataset.act;
      const boxes = [...el.querySelectorAll("input[type=checkbox]")];
      if (act === "all") boxes.forEach(b => b.checked = true);
      else if (act === "none") boxes.forEach(b => b.checked = false);
      else if (act === "first10") boxes.forEach((b, i) => b.checked = i < 10);
      else if (act === "first20") boxes.forEach((b, i) => b.checked = i < 20);
      else if (act === "top10") boxes.forEach((b, i) => b.checked = i < 10);
      else if (act === "range") {
        const a = prompt(`輸入起始序號 (1-${items.length})`, "1");
        if (a === null) return;
        const b2 = prompt(`輸入結束序號 (1-${items.length})`, String(Math.min(10, items.length)));
        if (b2 === null) return;
        const s = parseInt(a) - 1, e = parseInt(b2);
        boxes.forEach((b, i) => b.checked = i >= s && i < e);
      }
    };
  });
}

function renderCompare() {
  const type = document.getElementById("compareType").value;
  const picked = [...document.querySelectorAll("#comparePick input:checked")].map(i => i.value);
  const strip = document.getElementById("compareStrip");
  if (!currentBook || picked.length === 0) { strip.innerHTML = `<p class="muted small-text">${T("noData")}</p>`; return; }
  strip.innerHTML = picked.map(v => {
    const label = type === "chapter" ? currentBook.chapters[+v].title : v;
    const id = "cmp" + Math.random().toString(36).slice(2, 7);
    return `<div class="compare-item">
      <div class="cmp-label" title="${label}">${label}</div>
      <div id="${id}">${bodySVG(id, true)}</div>
    </div>`;
  }).join("");
  picked.forEach(v => {
    const data = type === "chapter"
      ? currentBook.chapters[+v]?.organ_emotion || {}
      : currentBook.characters.find(c => c.name === v)?.organ_emotion || {};
    const label = type === "chapter" ? currentBook.chapters[+v].title : v;
    const item = [...strip.querySelectorAll(".compare-item")].find(d => d.querySelector(".cmp-label").textContent === label);
    if (item) paintFigure(item, data);
  });
}

// ---------------- 上傳 ----------------
function initUpload() {
  const input = document.getElementById("fileInput");
  const status = document.getElementById("uploadStatus");
  input.onchange = async () => {
    const file = input.files[0];
    if (!file) return;
    status.textContent = T("uploading");
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch("/api/upload", { method: "POST", body: fd });
    const data = await res.json();
    if (data.error) { status.textContent = T("uploadFail") + ": " + data.error; return; }
    status.textContent = T("uploadDone");
    await loadBooks();
    await selectBook({ book_id: data.book_id });
  };
}

// ---------------- 語言切換 ----------------
function initLang() {
  document.getElementById("langToggle").onclick = () => {
    lang = lang === "zh" ? "en" : "zh";
    localStorage.setItem("bw_lang", lang);
    location.reload();
  };
}

// ---------------- toast ----------------
let toastTimer;
function showToast(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove("show"), 1800);
}

// ---------------- init ----------------
const modalEl = document.getElementById("organModal");
if (modalEl) {
  document.getElementById("modalClose").onclick = () => modalEl.classList.add("hidden");
  modalEl.onclick = (e) => { if (e.target.id === "organModal") modalEl.classList.add("hidden"); };
}
initLang();
if (document.getElementById("fileInput")) initUpload();
if (document.getElementById("compareView")) initCompare();
if (document.getElementById("figureWrap")) initFigureZoom();
// 頂部 scope 標籤頁綁定
document.querySelectorAll(".tab").forEach(t =>
  t.onclick = () => setScope(t.dataset.scope));
if (document.getElementById("bookList")) {
  loadBooks().then(() => {
    document.getElementById("viewTitle").textContent = T("selectBook");
    document.getElementById("figureWrap").innerHTML = bodySVG("main");
    renderLegend();
  });
}