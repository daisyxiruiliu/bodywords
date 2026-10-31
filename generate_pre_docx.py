# -*- coding: utf-8 -*-
"""生成 pre補充.docx：繁體中文版 + 英文版（完整圖文，四、五節精簡連貫）。"""
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn

OUT = r"D:\qh·china\pre補充.docx"

doc = Document()
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(11)
style.element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft JhengHei")


def set_font(run, size=None, bold=False, color=None, east="Microsoft JhengHei"):
    run.font.name = "Calibri"
    if size:
        run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)
    run._element.rPr.rFonts.set(qn("w:eastAsia"), east)


def heading(text, level=1):
    p = doc.add_heading("", level=level)
    set_font(p.add_run(text), size={1: 20, 2: 15, 3: 12.5}.get(level, 12), bold=True)


def para(text, bold=False, color=None):
    p = doc.add_paragraph()
    set_font(p.add_run(text), bold=bold, color=color)


def bullet(text):
    p = doc.add_paragraph(style="List Bullet")
    set_font(p.add_run(text))


def quote(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Pt(24)
    set_font(p.add_run(text), color=(0x80, 0x80, 0x80))


def table(headers, rows):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Light Grid Accent 1"
    for i, h in enumerate(headers):
        set_font(t.rows[0].cells[i].paragraphs[0].add_run(h), bold=True)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            set_font(cells[i].paragraphs[0].add_run(v))
    doc.add_paragraph()


# ===================== 繁體中文版 =====================
heading("🫀 BodyWords 身語集", 1)

heading("一、這是什麼", 2)
para("我做了一個網站 BodyWords 身語集：把小說裡「器官 ↔ 情緒」的字面描寫（例如「羞紅了臉」「心中歡喜」）統計出來，畫在一張科學的解剖人形圖上。")
bullet("顏色種類 = 情緒種類（喜／怒／哀／懼／驚）")
bullet("深淺 = 出現的強度")
bullet("點擊任何一個器官，就能看到對應的原文出處")
para("網站用 Flask 在本機跑，再用 cloudflared 開一條加密隧道接到公網，最後以 token 密鑰當門禁，只有拿到帶密鑰連結的人才進得來。")

heading("二、我發給 AI 的 prompt（原文）", 2)
para("這是我當時發給 GLM-5.3-flash 的完整 prompt，共 10 條要求：")
quote("我需要你幫我寫一個人圖網站，接下來為你介紹：")
quote("1. 所有內容煩請你寫進 D:\\qh·china\\bodywords，編程語言是 python")
quote("2. 這個程序的主要功能是分析文本中情感與器官的對應，視覺上需要用人形圖（科學的解剖圖）展示不同器官的情緒狀態（用顔色種類、深淺、明暗程度來表現）")
quote("3. 我不知道前後端有什麼區別？不過我希望保密性稍微好一點，比如只有我給出鏈接的人才可以訪問這種")
quote("4. 語言我希望有英語、繁中兩種切換")
quote("5. 文章應當是可以隨時上傳的，目前先支持 txt")
quote("6. 請先按照字面描寫，比如【羞紅了臉】這種描寫就算【臉】的")
quote("7. 我希望每個器官點擊都可以展示出對應的文本")
quote("8. 每一本書、每一個章節、每一個人物都要有自己的人圖，所以也許你需要做一個可供點擊的目錄")
quote("9. 我希望人物和章節能有個人圖的縱向動態對比，就有點像醫學切片一樣，這樣可以清晰看出變化")
quote("10. 有不懂的直接問我，不要擅自理解，如果你覺得準備好了請開始")
para("重點標紅第 10 條：我一開始就寫了「不要擅自理解」。這說明我其實早有預感——細節愈多，我愈怕它會自己猜我的意思。", color=(0xC0, 0x39, 0x2B))

heading("三、第一版：10 條都做出來了，但埋了雷", 2)
para("這 10 條因為明確、可驗證（有路徑、有功能清單），AI 基本上都做到了——txt 上傳、章節目錄、點器官看原文、中英切換、訪客連結控制都通了；但「人形圖」第一版做得不像人、很難看，我返工了好幾版，它才換成專業的醫學剪影。真正的失敗不是這 10 條，而是我後來追加的一條短指令。")

heading("四、追加的那一條 → 它如何誤解", 2)
para("網站能跑之後，我發現人物列表裡，「黛玉」和「林黛玉」被當成了兩個人。於是我追加了一句話：「把不同名字但指同一個人的人物名，和它們的數據，整合成同一個人」——就這一句，我既沒說誰跟誰是同一人，也沒說怎麼判斷。")
para("它確實照做了，但交回來的列表還留著「鳳姐」和「鳳姐兒」兩筆、留著「林黛玉」和「黛玉」兩筆，甚至冒出「賈母笑」「寶玉忙」「寶玉便」這種根本不存在的名字，還有「叫我」「有人」這類根本不是人名的詞。")
para("回頭看，它的錯很有規律：方向搞反、沒把帶姓氏的稱呼當別名、把「笑道／忙道」的動詞黏進名字、連代詞也當成人物。所以嚴格說，它不是亂做，而是忠實地執行了我沒講清楚的那部分——「誰和誰是同一人」這種知識，它無法自己從文本裡推出來。")

heading("五、我接手後怎麼改", 2)
para("我不再指望它自動理解，而是把領域知識直接寫進程式碼：手工別名對照表（林黛玉→黛玉、鳳姐兒→鳳姐、王熙鳳→鳳姐、老太太→賈母）、動詞結尾黑名單（笑、哭、嘆、忙、便）、代詞停用詞（叫我、有人），並讓合併不只作用在名字上，也把「含林黛玉」的句子數據一起併進黛玉。")
para("改完之後，三十位人物，零重複、零噪音。", bold=True)

heading("六、我學到了什麼", 2)
bullet("模糊的指令 = 被擅自理解的結果；「有不懂就問」要靠我更主動，AI 很少真的回頭問，它更可能默默猜。")
bullet("AI 是執行者，不是判斷者——「誰和誰是同一人」這條規則，必須由人來給。")
bullet("驗證比生成重要——「賈母笑」這種錯，人一眼就看出來，但 AI 自己不會發現。")

heading("七、《紅樓夢》器官 × 情緒 範例對照表（配圖用）", 2)
table(["#", "器官", "情緒", "原文（節選）"], [
    ["1", "臉", "😊 害臊→尷", "黛玉…說了兩句，不覺紅了臉…寶釵見他羞得滿臉飛紅，滿口央告"],
    ["2", "心", "😢 哀（急轉悲）", "接不下去，心中一急…因而轉急為悲，早已滾下淚來"],
    ["3", "眼／眉", "😲 驚", "黛玉一見，便吃一大驚…眉如墨畫，目若秋波"],
    ["4", "心", "😢 哀（驚痛）", "只覺心中似戳了一刀，哇的一聲，直奔出一口血來"],
    ["5", "心", "😊 喜", "賈母見秦鍾…心中十分歡喜"],
    ["6", "臉", "😨 懼（嚇）", "那傻大姐…反嚇得黃了臉，說：「再不敢了。」"],
])
para("建議「一組三圖」：臉 + 羞（例1）、心 + 喜（例5）、心 + 哀（例2）——同一器官「心」不同情緒，正好展示深淺／顏色的變化。")

doc.add_page_break()

# ===================== English =====================
heading("🫀 BodyWords", 1)

heading("1. What It Is", 2)
para("I built a website called BodyWords: it tallies literal \"organ ↔ emotion\" descriptions in novels (e.g. \"her face blushed with shame,\" \"joy in the heart\") and renders them on a scientific anatomical human figure.")
bullet("Color = emotion type (joy / anger / sadness / fear / surprise)")
bullet("Shading = strength of occurrence")
bullet("Click any organ to see the original source text")
para("The site runs locally with Flask, opens an encrypted tunnel to the internet via cloudflared, and uses a token key as a gate so only people with the keyed link can get in.")

heading("2. The Prompt I Sent (verbatim)", 2)
para("This is the complete 10-point prompt I originally sent to GLM-5.3-flash:")
quote("I need you to help me build a human-figure website. Here are the requirements:")
quote("1. Write everything into D:\\qh·china\\bodywords, using Python")
quote("2. The main function is to analyze the correspondence between emotions and organs in text, visually using a human figure (scientific anatomical drawing) to show the emotional states of different organs (using color type, shade, and brightness)")
quote("3. I don't know the difference between front-end and back-end — but I'd like decent privacy, e.g. only people I give the link to can access it")
quote("4. I want both English and Traditional Chinese language switching")
quote("5. Articles should be uploadable anytime; for now, support txt")
quote("6. For now, go by literal descriptions — e.g. \"羞紅了臉 (face blushed with shame)\" should count as 【face】")
quote("7. I want every organ to be clickable to show its corresponding text")
quote("8. Every book, every chapter, and every character should have their own human figure, so you may need a clickable table of contents")
quote("9. I want people and chapters to have a vertical dynamic comparison of the human figure, a bit like medical cross-sections, to clearly see changes over time")
quote("10. If you don't understand something, ask me directly — don't interpret it on your own. Begin when you feel ready.")
para("Highlight point 10: I wrote \"don't interpret it on your own\" from the very start — I actually had a premonition: the more details there are, the more I was afraid it would guess my meaning.", color=(0xC0, 0x39, 0x2B))

heading("3. First Version: All 10 Points Done, but a Landmine Was Buried", 2)
para("Because those points were explicit and verifiable, the AI mostly delivered — txt upload, chapter TOC, click-to-see-source-text, EN/中 switching, invite-link access all worked; but the figure was ugly at first and I had it redo it several times. The real failure wasn't these 10 points — it was one short follow-up instruction I added later.")

heading("4. The Follow-up → How It Misunderstood", 2)
para("After the site ran, I saw \"黛玉\" and \"林黛玉\" treated as two people, so I added one line: \"merge the character names that refer to the same person, along with their data, into one person\" — that one sentence said neither who is the same person, nor how to tell.")
para("It complied, but the list still kept \"凤姐\" and \"凤姐儿\" as two, kept \"林黛玉\" and \"黛玉\" as two, and even produced names that don't exist like \"贾母笑,\" \"宝玉忙,\" \"宝玉便,\" plus pronouns like \"叫我\" and \"有人.\"")
para("Looking back, the errors followed a pattern: reversed direction, missed surname aliases, verbs glued onto names, pronouns taken as people. It wasn't doing it randomly — it was faithfully executing the part I hadn't specified, because \"who is the same person\" is knowledge it cannot infer from text on its own.")

heading("5. How I Fixed It", 2)
para("I stopped expecting it to understand on its own and wrote my domain knowledge directly into the code: a hand-built alias map (林黛玉→黛玉, 凤姐儿→凤姐, 王熙凤→凤姐, 老太太→贾母), a verb-ending blacklist (笑、哭、叹、忙、便), and pronoun stopwords (叫我、有人), plus making the merge also fold the data from sentences containing \"林黛玉\" into \"黛玉.\"")
para("After that, thirty characters, zero duplicates, zero noise.", bold=True)

heading("6. What I Learned", 2)
bullet("A vague instruction = a result that got interpreted on its own; \"ask if you don't understand\" requires me to be proactive, since an AI rarely asks back.")
bullet("An AI is an executor, not a judge — \"who is the same person\" must be supplied by a human.")
bullet("Verifying matters more than generating — a mistake like 贾母笑 is obvious to a human but the AI will never spot it itself.")

heading("7. Dream of the Red Chamber Organ × Emotion Example Table (for slides)", 2)
table(["#", "Organ", "Emotion", "Original text (excerpt)"], [
    ["1", "Face", "😊 shy → awkward", "黛玉…說了兩句，不覺紅了臉…寶釵見他羞得滿臉飛紅，滿口央告"],
    ["2", "Heart", "😢 sadness (turns to grief)", "接不下去，心中一急…因而轉急為悲，早已滾下淚來"],
    ["3", "Eyes / Brows", "😲 surprise", "黛玉一見，便吃一大驚…眉如墨畫，目若秋波"],
    ["4", "Heart", "😢 grief (shock-pain)", "只覺心中似戳了一刀，哇的一聲，直奔出一口血來"],
    ["5", "Heart", "😊 joy", "賈母見秦鍾…心中十分歡喜"],
    ["6", "Face", "😨 fear (frightened)", "那傻大姐…反嚇得黃了臉，說：「再不敢了。」"],
])
para("Suggested \"one set of three\": face + shyness (1), heart + joy (5), heart + sadness (2) — same organ \"heart,\" different emotion, showing the shift in shade / color.")

doc.save(OUT)
print(f"已生成：{OUT}")