# -*- coding: utf-8 -*-
"""
BodyWords 分析引擎
- 章節切分（第X回/章/卷）
- 人物自動識別（高頻雙字/三字詞 + 常見稱謂過濾）
- 器官-情緒 對應統計（字面描寫，如「羞紅了臉」計入【臉】）
"""

import re
import json
import os
from collections import Counter, defaultdict

# ---------------- 情緒體系（五種基本情緒） ----------------
EMOTIONS = ["joy", "anger", "sadness", "fear", "surprise"]

# 情緒關鍵詞（繁簡兼收）
EMOTION_LEXICON = {
    "joy": ["喜", "樂", "笑", "高興", "開心", "歡", "愉", "甜", "暢", "快活", "喜歡", "興奮", "得意", "笑嘻嘻", "喜滋滋", "歡喜", "暢快", "舒", "樂呵呵"],
    "anger": ["怒", "氣", "惱", "憤", "恨", "嗔", "火", "忿", "急", "暴躁", "惱火", "氣惱", "憤怒", "發作", "咬牙", "怒氣", "生氣", "慍"],
    "sadness": ["悲", "哀", "哭", "淚", "傷心", "愁", "憂", "苦", "淒", "慘", "難過", "傷感", "嗚咽", "泣", "辛酸", "悲傷", "鬱", "悶", "歎", "歎息"],
    "fear": ["怕", "懼", "恐", "驚慌", "慌", "膽", "怯", "畏", "心驚", "毛骨悚然", "戰兢", "發抖", "哆嗦", "惶", "悚", "駭", "害怕", "不安"],
    "surprise": ["驚", "訝", "愕", "愣", "呆", "詫", "奇", "意外", "吃了一驚", "吃驚", "咋舌", "怔", "詫異", "愕然", "駭然", "咋", "咦"],
}

# ---------------- 器官/身體部位 ----------------
# key: 器官id（前端人形圖對應），value: [同義詞/寫法]
ORGAN_LEXICON = {
    "face":    ["臉", "面", "臉龐", "面孔", "面龐", "顏面", "面頰", "腮", "頰", "臉頰", "面皮"],
    "eyes":    ["眼", "目", "眼睛", "眸", "瞳", "目光", "眼神", "眼眶", "眼角", "淚眼", "雙眼"],
    "brows":   ["眉", "眉毛", "眉梢", "眉尖", "黛眉", "蛾眉", "柳眉", "眉頭"],
    "mouth":   ["嘴", "口", "唇", "嘴唇", "櫻唇", "朱唇", "嘴角", "齒", "牙", "舌"],
    "forehead":["額", "額頭", "額角", "天庭"],
    "ears":    ["耳", "耳朵", "耳根", "耳邊", "耳畔"],
    "nose":    ["鼻", "鼻子", "鼻尖", "鼻翼"],
    "neck":    ["頸", "脖", "脖子", "咽喉", "喉", "項"],
    "shoulder":["肩", "肩膀", "肩頭", "肩胛"],
    "chest":   ["胸", "胸口", "胸膛", "胸前", "乳", "心口"],
    "heart":   ["心", "心中", "心頭", "心底", "心裡", "心內", "心窩"],
    "lungs":   ["肺", "肺腑", "心肺"],
    "liver":   ["肝", "肝腸", "肝膽", "心肝"],
    "spleen":  ["脾", "脾胃"],
    "kidney":  ["腎"],
    "stomach": ["胃", "胃口"],
    "intestines": ["腸", "斷腸", "柔腸", "腸肚"],
    "brain":   ["腦", "腦袋", "腦海", "腦筋", "頭腦"],
    "belly":   ["腹", "肚", "肚子", "腹部", "小腹"],
    "back":    ["背", "脊", "脊背", "後背", "背脊"],
    "waist":   ["腰", "腰肢", "細腰", "腰身"],
    "arm":     ["臂", "手臂", "胳膊", "腕", "手腕", "肘"],
    "hand":    ["手", "手掌", "手指", "指尖", "拳", "掌", "指", "纖手", "玉手"],
    "leg":     ["腿", "大腿", "小腿", "膝", "膝蓋", "股"],
    "foot":    ["腳", "足", "足尖", "腳尖", "腳步", "雙足"],
    "skin":    ["膚", "肌膚", "皮膚", "玉肌", "香肌"],
    "head":    ["頭", "頭顱", "頭頂"],
}

# 器官中文名（繁中）
ORGAN_ZH = {
    "face": "臉", "eyes": "眼", "brows": "眉", "mouth": "嘴", "forehead": "額",
    "ears": "耳", "nose": "鼻", "neck": "頸", "shoulder": "肩", "chest": "胸",
    "heart": "心", "lungs": "肺", "liver": "肝", "spleen": "脾", "kidney": "腎",
    "stomach": "胃", "intestines": "腸", "brain": "腦",
    "belly": "腹", "back": "背", "waist": "腰", "arm": "臂",
    "hand": "手", "leg": "腿", "foot": "腳", "skin": "膚", "head": "頭",
}
ORGAN_EN = {
    "face": "Face", "eyes": "Eyes", "brows": "Brows", "mouth": "Mouth", "forehead": "Forehead",
    "ears": "Ears", "nose": "Nose", "neck": "Neck", "shoulder": "Shoulder", "chest": "Chest",
    "heart": "Heart", "lungs": "Lungs", "liver": "Liver", "spleen": "Spleen", "kidney": "Kidney",
    "stomach": "Stomach", "intestines": "Intestines", "brain": "Brain",
    "belly": "Belly", "back": "Back", "waist": "Waist", "arm": "Arm",
    "hand": "Hand", "leg": "Leg", "foot": "Foot", "skin": "Skin", "head": "Head",
}

EMOTION_ZH = {"joy": "喜", "anger": "怒", "sadness": "哀", "fear": "懼", "surprise": "驚"}
EMOTION_EN = {"joy": "Joy", "anger": "Anger", "sadness": "Sadness", "fear": "Fear", "surprise": "Surprise"}

# 排除的停用詞/非人名高頻詞
STOPWORDS = {
    "什麼", "怎麼", "這裡", "那裡", "自己", "我們", "你們", "他們", "她們", "知道", "說道",
    "出來", "起來", "過來", "時候", "如今", "所以", "但是", "只是", "一面", "一個", "兩個",
    "太太", "姑娘", "丫頭", "婆子", "老爺", "小子", "夫人", "奶奶", "姐姐", "妹妹", "哥哥",
    "弟弟", "兄弟", "姊妹", "老老", "媽媽", "女兒", "兒子", "東西", "今日", "明日", "昨日",
    "笑道", "說著", "說道", "聽了", "來了", "去了", "見了", "罷了", "罷了", "只得", "不知",
    "只見", "一個", "了一", "說著", "怎麼", "什麼", "那裡", "這裡", "眾人", "咱們", "你們",
    "他們", "起來", "出來", "說話", "答應", "回來", "過去", "一面", "忽然", "登時", "半日",
    "老太", "王夫", "賈政", "賈璉", "平兒", "襲人", "寶釵", "黛玉", "寶玉", "鳳姐", "賈母",
    # 上面最後一行是誤放——這些其實是人名，從 STOPWORDS 移除
}
# 修正：把誤放的人名移除
for _name in ["老太", "王夫", "賈政", "賈璉", "平兒", "襲人", "寶釵", "黛玉", "寶玉", "鳳姐", "賈母"]:
    STOPWORDS.discard(_name)
# 稱謂前綴，用於合併（如 王夫人/賈母 保留為人物）
TITLES = ["夫人", "太太", "老爺", "奶奶", "姑娘", "丫頭", "小子", "姐姐", "妹妹", "哥哥", "弟弟", "女兒", "兒子", "婆婆", "公公"]

CHAPTER_RE = re.compile(
    r"^\s*(第[一二三四五六七八九十百千零〇\d]+[回章节卷部][^\n]{0,40})\s*$",
    re.M,
)

SENT_SPLIT_RE = re.compile(r"[。！？；\n!?;\n]")


def split_chapters(text):
    """按「第X回/章」切分章節，返回 [(title, body)]；無章節標題則整篇為一章。"""
    matches = list(CHAPTER_RE.finditer(text))
    if not matches:
        return [("全書", text)]
    chapters = []
    # 第一個標題之前的內容
    if matches[0].start() > 0:
        pre = text[: matches[0].start()].strip()
        if len(pre) > 50:
            chapters.append(("卷首", pre))
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chapters.append((title, text[start:end]))
    return chapters


def detect_characters(text, max_chars=30):
    """簡易人名識別（繁簡通用）：
    核心策略——人名後常跟「道/說/笑/哭/道」等動詞（X道、X說），或前面有稱謂。
    用「上下文驗證」而非純詞頻，大幅減少噪音。
    """
    # 繁簡停用詞（合併）
    stop = set(STOPWORDS) | {
        # 簡體
        "什么", "怎么", "这里", "那里", "我们", "你们", "他们", "她们", "自己", "知道",
        "出来", "起来", "过来", "时候", "如今", "所以", "但是", "只是", "一面", "一个",
        "两个", "东西", "今日", "明日", "昨日", "只得", "不知", "只见", "众人", "说着",
        "说道", "笑道", "听了", "来了", "去了", "见了", "罢了", "说话", "答应", "回来",
        "过去", "咱们", "大家", "这个", "那个", "这样", "那样", "一时", "半日", "登时",
        "忽然", "两个", "三个", "几个", "太太", "姑娘", "丫头", "婆子", "老爷", "小子",
        "夫人", "奶奶", "姐姐", "妹妹", "哥哥", "兄弟", "女儿", "儿子", "妈妈", "老老",
        "了一", "的是", "也是", "又是", "不是", "就是", "都是", "还有", "没有", "不能",
        # 繁體
        "什麼", "怎麼", "這裡", "那裡", "我們", "你們", "他們", "她們", "聽了", "來了",
        "去了", "見了", "罷了", "說著", "說道", "笑道", "答應", "回來", "過去", "眾人",
        "這個", "那個", "這樣", "那樣", "一時", "半日", "登時", "忽然", "幾個", "還有",
        "沒有", "不能", "都是", "就是", "不是", "也是", "了的", "著呢",
        "听见", "聽見", "人家", "如此", "这么", "這麼", "只管", "只顧", "谁知",
        "誰知", "原来", "原來", "于是", "於是", "可是", "因为", "因為", "如果",
        "宝玉笑", "笑道", "说着", "只见", "这里", "那里", "两个", "三个",
        "也没", "这会子", "這會子", "到底", "不用", "不了", "不曾", "未必",
        "只得", "只好", "正是", "才是", "便是", "竟是", "却是", "可是", "倒是",
        "越发", "越發", "更加", "更兼", "偏生", "偏偏", "可巧", "方才", "刚才",
        "剛才", "且说", "且說", "话说", "話說", "却说", "卻說",
        "叫我", "有人", "没人", "沒人", "无人", "無人", "何人", "谁人", "誰人",
    }
    # 動詞/虛詞結尾（繁簡）
    verb_end = "的了是在有和就都也又把被向從说听说聽看走去來不沒著话话過过道说云言问问答笑哭叹嘆忙便"
    # 稱謂詞（人名後綴，用於驗證上下文）
    name_verbs = {"道", "說", "说", "笑", "哭", "嘆", "叹", "問", "问", "叫", "喚", "唤", "拉", "推", "見", "见", "聽", "听"}

    tri = Counter(re.findall(r"[\u4e00-\u9fff]{3}", text))
    bi = Counter(re.findall(r"[\u4e00-\u9fff]{2}", text))

    # 上下文驗證：統計「X道」「X說」等模式次數（人名強信號）
    ctx = Counter()
    for m in re.finditer(r"([\u4e00-\u9fff]{2,3})(道|說|说|笑道|說道|说道|叹道|嘆道)", text):
        ctx[m.group(1)] += 1

    candidates = {}
    # 3字詞：需詞頻>=5 且 上下文信號>=2
    for w, c in tri.items():
        if c >= 5 and w not in stop and w[-1] not in verb_end:
            if ctx.get(w, 0) >= 2 or c >= 50:
                candidates[w] = c
    # 2字詞：需詞頻>=8 且 上下文信號>=3
    for w, c in bi.items():
        if c >= 8 and w not in stop and w not in candidates and w[-1] not in verb_end:
            if ctx.get(w, 0) >= 3:
                candidates[w] = c

    # 合併：若「王夫人」在，「王夫」去掉；若「老太太」在，「老太」去掉
    final = {}
    for w, c in candidates.items():
        if any(w + s in candidates for s in ("夫人", "太太", "老太太", "小子", "丫頭", "丫头")):
            continue
        final[w] = c

    # 別名合併：同一人的不同稱呼歸到主名（主名=詞頻最高者）
    # 明確別名表：這些稱呼視為同一人（歸到右邊的主名）
    ALIAS_MAP = {
        "老太太": "贾母", "賈母": "贾母", "老祖宗": "贾母",
        "林黛玉": "黛玉", "黛玉儿": "黛玉",
        "凤姐儿": "凤姐", "鳳姐兒": "凤姐", "王熙凤": "凤姐", "王熙鳳": "凤姐",
        "宝二爷": "宝玉", "寶二爺": "宝玉", "宝玉儿": "宝玉",
        "宝钗儿": "宝钗", "寶釵": "宝钗",
        "袭人儿": "袭人", "襲人": "袭人",
        "紫鹃儿": "紫鹃", "紫鵑": "紫鹃",
        "晴雯儿": "晴雯",
        "香菱儿": "香菱",
        "平儿儿": "平儿", "平兒": "平儿",
        "鸳鸯儿": "鸳鸯", "鴛鴦": "鸳鸯",
        "探春儿": "探春",
        "惜春儿": "惜春",
        "迎春儿": "迎春",
        "李纨儿": "李纨", "李紈": "李纨",
        "薛姨妈": "薛姨妈", "薛姨媽": "薛姨妈",
        "刘姥姥": "刘姥姥", "劉姥姥": "刘姥姥",
        "麝月儿": "麝月",
        "贾蓉儿": "贾蓉", "賈蓉": "贾蓉",
        "贾芸儿": "贾芸", "賈芸": "贾芸",
        "贾赦儿": "贾赦", "賈赦": "贾赦",
        "贾政儿": "贾政", "賈政": "贾政",
        "贾琏儿": "贾琏", "賈璉": "贾琏",
        "贾珍儿": "贾珍", "賈珍": "贾珍",
        "邢夫人": "邢夫人",
        "王夫人": "王夫人",
        "尤氏儿": "尤氏",
    }
    merged = {}
    # 按詞頻降序處理，高頻者為主名
    for w in sorted(final, key=lambda x: -final[x]):
        c = final[w]
        w = ALIAS_MAP.get(w, w)
        target = None
        for main in merged:
            # w 是 main 的別名：w+兒 == main，或 w 是 main 的子串且長度>=2
            if (w + "儿" == main or w + "兒" == main
                    or (len(w) >= 2 and (main.startswith(w) or main.endswith(w)) and main != w)):
                target = main
                break
        if target:
            merged[target] += c
        else:
            merged[w] = c
    ranked = sorted(merged.items(), key=lambda x: -x[1])[:max_chars]
    return [w for w, _ in ranked]


def analyze_segment(text):
    """
    分析一段文本，返回:
    {
      "organ_emotion": {organ: {emotion: count}},
      "organ_hits": {organ: [{"quote":..., "emotion":...}]},
      "total_hits": int
    }
    句子級匹配：一句話中同時出現情緒詞與器官詞，則記一次對應。
    """
    organ_emotion = defaultdict(lambda: defaultdict(int))
    organ_hits = defaultdict(list)
    total = 0
    for sent in SENT_SPLIT_RE.split(text):
        sent = sent.strip()
        if not sent or len(sent) > 200:
            continue
        emotions_in = set()
        for emo, words in EMOTION_LEXICON.items():
            if any(w in sent for w in words):
                emotions_in.add(emo)
        if not emotions_in:
            continue
        for organ, words in ORGAN_LEXICON.items():
            organ_word = next((w for w in words if w in sent), None)
            if organ_word is None:
                continue
            for emo in emotions_in:
                organ_emotion[organ][emo] += 1
                total += 1
            if len(organ_hits[organ]) < 200:
                organ_hits[organ].append({"quote": sent, "emotion": sorted(emotions_in)})
    return {
        "organ_emotion": {o: dict(d) for o, d in organ_emotion.items()},
        "organ_hits": dict(organ_hits),
        "total_hits": total,
    }


def analyze_book(text, book_id):
    """分析整本書：章節切分 + 人物識別 + 各章/各人物分析。"""
    chapters = split_chapters(text)
    characters = detect_characters(text)

    chapter_results = []
    for title, body in chapters:
        res = analyze_segment(body)
        chapter_results.append({
            "title": title,
            "organ_emotion": res["organ_emotion"],
            "organ_hits": res["organ_hits"],
            "total_hits": res["total_hits"],
        })

    # 人物級：粗略按出現密度歸屬句子
    # 別名映射：句子含「林黛玉」也應算入「黛玉」；「凤姐儿」算入「凤姐」
    def name_variants(name):
        vs = {name}
        if len(name) >= 2:
            vs.add(name + "儿")
            vs.add(name + "兒")
            # 姓氏前綴：黛玉 → 林黛玉
            for s in ("林", "賈", "贾", "王", "薛", "史", "秦", "尤"):
                vs.add(s + name)
        # 明確別名：贾母/老太太/老祖宗 同一人
        if name == "贾母":
            vs |= {"老太太", "老祖宗"}
        return vs

    character_results = {}
    for name in characters:
        variants = name_variants(name)
        char_organ = defaultdict(lambda: defaultdict(int))
        char_hits = defaultdict(list)
        for sent in SENT_SPLIT_RE.split(text):
            if not any(v in sent for v in variants):
                continue
            emotions_in = set()
            for emo, words in EMOTION_LEXICON.items():
                if any(w in sent for w in words):
                    emotions_in.add(emo)
            if not emotions_in:
                continue
            for organ, words in ORGAN_LEXICON.items():
                if any(w in sent for w in words):
                    for emo in emotions_in:
                        char_organ[organ][emo] += 1
                    if len(char_hits[organ]) < 100:
                        char_hits[organ].append({"quote": sent.strip(), "emotion": sorted(emotions_in)})
        character_results[name] = {
            "organ_emotion": {o: dict(d) for o, d in char_organ.items()},
            "organ_hits": dict(char_hits),
            "total_hits": sum(sum(d.values()) for d in char_organ.values()),
        }

    return {
        "book_id": book_id,
        "chapters": chapter_results,
        "characters": character_results,
    }


def save_analysis(data, data_dir):
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, f"{data['book_id']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    return path


def load_analysis(data_dir, book_id):
    path = os.path.join(data_dir, f"{book_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)