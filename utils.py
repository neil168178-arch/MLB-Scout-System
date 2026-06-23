# utils.py
import streamlit as st
import pandas as pd
import unicodedata
from config import *

def translate_injury(text):
    if not text:
        return "未公開詳細傷勢"
        
    lower_text = text.lower().strip()
    
    invalid_texts = ['il', 'out', 'day-to-day', '7-day il', '10-day il', '15-day il', '60-day il', 'unknown', 'injured 7-day', 'injured 10-day', 'injured 15-day', 'injured 60-day']
    if lower_text in invalid_texts:
        return "未公開詳細傷勢"
    
    tw_parts = []
    
    if "tommy john" in lower_text: tw_parts.append("手肘韌帶置換手術")
    if "thoracic outlet syndrome" in lower_text: tw_parts.append("胸廓出口症候群")
    if "lumbar degenerative disk disease" in lower_text: tw_parts.append("腰椎間盤退化")
    if "lumbar bulging disc" in lower_text: tw_parts.append("腰椎間盤膨出")
    if "lumbar spine disc herniation" in lower_text: tw_parts.append("腰椎間盤突出")
    if "plantar fasciitis" in lower_text: tw_parts.append("足底筋膜炎")
    if "lateral epicondylitis" in lower_text: tw_parts.append("網球肘(外上髁炎)")
    
    if not tw_parts:
        if "left" in lower_text: tw_parts.append("左")
        elif "right" in lower_text: tw_parts.append("右")
        
        body_parts = ["shoulder", "elbow", "forearm", "wrist", "hand", "finger", "thumb", "lower back", "back", "neck", "oblique", "rib", "hip", "groin", "quad", "hamstring", "knee", "calf", "ankle", "foot", "toe", "achilles", "biceps", "triceps", "lat", "pectoral", "flexor", "tendon", "ligament", "meniscus", "ucl", "acl", "mcl", "labrum", "orbital", "peroneal", "radius", "hamate", "gracilis", "shin bone", "trapezius", "fibula", "metacarpal", "brachialis", "arm", "ac joint", "ulnar nerve", "intercostal", "lumbar", "disc"]
        
        for bp in body_parts:
            if bp in lower_text:
                tw_parts.append(INJURY_DICT.get(bp, ""))
                break
                
        conditions = ["strain", "sprain", "fracture", "contusion", "inflammation", "soreness", "sore", "tightness", "fatigue", "blister", "concussion", "surgery", "impingement", "dislocation", "tear", "bone bruise", "illness", "covid", "viral", "reconstruction", "discomfort", "recovery", "injury", "tendinitis", "arthroscopy", "repair", "fasciitis", "subluxation", "loose bodies", "spasms", "stress reaction", "laceration", "syndrome", "herniation", "non-displaced", "pain", "epicondylitis", "hernia", "rehab"]
        
        for cond in conditions:
            if cond in lower_text:
                tw_parts.append(INJURY_DICT.get(cond, ""))
                break
                
    if tw_parts:
        tw_meaning = "".join([p for p in tw_parts if p])
        return f"{text} ({tw_meaning})"
    
    return text

def format_metric(val, m):
    if pd.isna(val) or val == "": return "-"
    try:
        val_float = float(val)
        fmt = METRIC_FORMATS.get(m, '{:.3f}')
        return fmt.format(val_float)
    except:
        return str(val)

STYLER_FORMATS = {k: lambda x, k=k: format_metric(x, k) for k in METRIC_FORMATS.keys()}

def f_size(target_px, multiplier=1.0):
    target = target_px * multiplier
    min_px = max(10, int(target * 0.8))  
    max_px = int(target * 1.2)
    vw_val = (max_px - min_px) / 8.0     
    base_val = min_px * 0.75
    return f"clamp({min_px}px, {base_val:.1f}px + {vw_val:.2f}vw, {max_px}px)"

def clean_name(name):
    if not isinstance(name, str): return ""
    return unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8').lower().strip()

def get_team_color(team_name, default_colors=("#EF3E42", "#1E90FF")):
    colors = None
    if not team_name: colors = default_colors
    elif team_name in MLB_TEAM_COLORS: colors = MLB_TEAM_COLORS[team_name]
    else:
        for full_name, c in MLB_TEAM_COLORS.items():
            if full_name.split()[-1] in team_name or team_name in full_name:
                colors = c
                break
    if not colors and team_name and ("Athletics" in team_name or "A's" in team_name): colors = ("#003831", "#EFB21E")
    if not colors: colors = default_colors
    return colors

def darken_color(hex_color, factor=0.7):
    if not hex_color or not isinstance(hex_color, str) or len(hex_color) < 7: return "#000000"
    hex_color = hex_color.lstrip('#')
    try:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"#{max(0, int(r * factor)):02x}{max(0, int(g * factor)):02x}{max(0, int(b * factor)):02x}"
    except: return "#000000"

def get_team_logo_url(team_name):
    if not team_name: return ""
    tid = None
    if team_name in MLB_TEAM_IDS: tid = MLB_TEAM_IDS[team_name]
    else:
        for full_name, i in MLB_TEAM_IDS.items():
            if full_name.split()[-1] in team_name or team_name in full_name:
                tid = i; break
        if not tid and ("Athletics" in team_name or "A's" in team_name): tid = 133
    return f"https://www.mlbstatic.com/team-logos/{tid}.svg" if tid else ""

def hex_to_rgba(hex_color, alpha=0.08):
    if not hex_color or not isinstance(hex_color, str): return "rgba(0,0,0,0)"
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"rgba({r}, {g}, {b}, {alpha})"
    return "rgba(0,0,0,0)"

def score_to_grade(s):
    if pd.isna(s): return 'F'
    if s >= 9.5: return 'S'
    elif s >= 9.0: return 'A++'
    elif s >= 8.0: return 'A+'
    elif s >= 7.0: return 'A'
    elif s >= 6.0: return 'B++'
    elif s >= 5.0: return 'B+'
    elif s >= 4.0: return 'B'
    elif s >= 3.0: return 'C'
    elif s >= 2.0: return 'D'
    elif s >= 1.0: return 'E'
    else: return 'F'

def get_percentile(df, col_name, val, p_type):
    lower_is_better = ['Chase%', 'Whiff%', 'GB%', 'K%'] if p_type == '打者' else ['ERA', 'xERA', 'WHIP', 'FIP', 'BA', 'xBA', 'BB%', 'HardHit%', 'Barrel%', 'Diff']
    series = df[col_name].dropna()
    if len(series) == 0: return 0
    pct = (series >= val).mean() if col_name in lower_is_better else (series <= val).mean()
    return round(pct * 100, 1)

def get_relative_grade(df, col_name, val, p_type):
    lower_is_better = ['Chase%', 'Whiff%', 'GB%', 'K%'] if p_type == '打者' else ['ERA', 'xERA', 'WHIP', 'FIP', 'BA', 'xBA', 'BB%', 'HardHit%', 'Barrel%', 'Diff']
    series = df[col_name].dropna()
    if len(series) == 0: return 'C', 3
    pct = (series >= val).mean() if col_name in lower_is_better else (series <= val).mean()
    grades = {'S': (0.95, 10), 'A++': (0.90, 9), 'A+': (0.80, 8), 'A': (0.70, 7), 'B++': (0.60, 6), 'B+': (0.50, 5), 'B': (0.40, 4), 'C': (0.30, 3), 'D': (0.20, 2), 'E': (0.10, 1), 'F': (0, 0)}
    for g, (p, s) in grades.items():
        if pct >= p: return g, s
    return 'F', 0

# 🔥 防呆安全浮點數轉換
def safe_float(val):
    if pd.isna(val): return 0.0
    try: return float(val)
    except: return 0.0

# 🌟🌟🌟 上百種詞彙擴充：動態專屬外號引擎 🌟🌟🌟
def generate_fun_nickname(p_prof, p_type):
    try:
        player_name = str(p_prof.get('Player', 'Unknown'))
        idx = abs(hash(player_name)) # 使用球員名稱作為種子，外號固定不亂跳

        if p_type == '投手':
            pos = str(p_prof.get('Position', ''))
            w = safe_float(p_prof.get('W', 0))
            l = safe_float(p_prof.get('L', 0))
            era = safe_float(p_prof.get('ERA', 5.0))
            hr = safe_float(p_prof.get('HR', 0))
            sv = safe_float(p_prof.get('SV', 0))
            whip = safe_float(p_prof.get('WHIP', 1.5))
            k_pct = safe_float(p_prof.get('K%', 0))
            bb_pct = safe_float(p_prof.get('BB%', 0))

            pool = []
            if pos in ['RP', 'CL'] and w >= 4:
                pool = ["勝投怪盜 🥷", "撿勝大師 💰", "運氣爆棚哥 🎰", "先發的心痛 💔", "尾刀專家 🗡️", "勝投小偷 🐁", "不勞而獲王 🏆", "專偷先發勝投 🕵️", "九局神偷 🧀", "勝投收割機 🚜", "先發看著你笑 🙃", "勝投魔法師 🪄"]
            elif era <= 3.5 and w <= 3 and l >= w:
                pool = ["問天組組長 😭", "悲情城市 🌧️", "先發孤兒 🥺", "被隊友背叛的男人 🤦‍♂️", "無語問蒼天 🌌", "化悲憤為力量 😤", "最慘打線受害者 🩸", "真心換絕情 💔", "孤軍奮戰 ⚔️", "老天不公 ☔", "求神拜佛沒人理 🛐", "幫寫個慘字 🩸"]
            elif sv >= 3 and whip >= 1.3:
                pool = ["劇場總監 🍿", "速效胃藥代言人 💊", "心臟病發製造機 🎢", "拆彈兼埋彈專家 💣", "天天開劇場 🎭", "九局大導演 🎬", "收視率保證 📈", "抖抖守護神 🥶", "球迷血壓計 📈", "大怒神 🎢", "滿壘計畫通 ♟️", "放火大隊長 🔥"]
            elif w >= 6 and era >= 4.5:
                pool = ["強運體質 🍀", "打線乾爹 🤝", "勝投精算師 🧮", "命運之子 👶", "被神眷顧的男人 ✨", "隊友罩我 🫂", "自帶八字重 ⚖️", "靠隊友拿勝 ⚾", "護國神山打線 🌋", "爽拿勝投 😎", "躺贏大師 🛌", "玄學投手 ☯️"]
            elif hr >= 12:
                pool = ["煙火大盤商 🎆", "全壘打製造機 🏭", "發球練習機 ⚾", "外野觀眾送禮員 🎁", "球都飛很遠 🚀", "天空守望者 🔭", "被敲全壘打達人 🤦‍♂️", "餵球機 🎾", "長打批發商 🛒", "全壘打牆之友 🧱", "開魯閣廠長 🏭", "發球大師 🎯"]
            elif k_pct >= 28.0:
                pool = ["K博士 👨‍⚕️", "殘酷三振機 ⚔️", "奪三振藝術家 🎨", "打者去旁邊坐 🪑", "風扇修理工 🛠️", "K牌批發商 🎯", "三振大魔王 👿", "揮空終結者 💨", "人體電風扇插座 🔌", "三振提款機 🏧", "空氣切割機 🗡️", "視覺系投手 👁️"]
            elif era <= 2.5 and whip <= 1.0:
                pool = ["無情上鎖機 🔒", "絕望製造者 🚫", "對手噩夢 👻", "九局死神 ☠️", "下班鐘聲 🔔", "外星級壓制 🛸", "絕望之牆 🧱", "不給上壘大師 🛑", "出局如風 🌪️", "打者夢碎機 💥", "安心信賴 💯", "防線天花板 🛡️"]
            elif bb_pct >= 10.0:
                pool = ["四壞保送員 🚶", "控球迷航中 🧭", "自走計程車 🚕", "捕手滿場跑 🏃", "不想投好球 🙅‍♂️", "保送大本營 🎪", "免費送壘包 🎁", "壞球製造機 🚫", "保送發放所 🎫", "堆壘大師 📦", "找不到好球帶 🤷", "保送量販店 🏪"]
            elif era <= 3.3 and whip <= 1.15:
                pool = ["王牌本體 ♠️", "打線絕望者 👻", "主戰神獸 🦁", "豪門最愛 💰", "ACE大物 🃏"]
            else:
                pool = ["打卡公務員 💼", "局數消化機 🍽️", "中規中矩先生 👔", "天天投球機 ⚙️", "平凡的打工仔 👷", "薪水小偷候選 🕵️‍♂️", "默默無名投手 👤", "邊緣人 🌫️", "勞工兄弟 🔧", "佛系投球 🧘", "普通人 🚶"]

            return pool[idx % len(pool)]

        else: # 打者
            hr = safe_float(p_prof.get('HR', 0))
            sb = safe_float(p_prof.get('SB', 0))
            avg = safe_float(p_prof.get('AVG', 0.250))
            k_pct = safe_float(p_prof.get('K%', 0))
            whiff = safe_float(p_prof.get('Whiff%', 0))
            bb_pct = safe_float(p_prof.get('BB%', 0))
            hbp = safe_float(p_prof.get('HBP', 0))

            pool = []
            if hr >= 15 and sb >= 10 and avg >= 0.280:
                pool = ["外星人 👽", "棒球界神獸 🦄", "無死角破壞神 ⚔️", "六邊形戰士 🛡️", "投手的晚安曲 🌙", "棒球之神私生子 👼", "五拍子天選 🌟", "自走外掛 👾", "開掛玩家 🎮", "非人類 🤖", "大谷翔平二世 ⚾", "數據破壞者 📈"]
            elif hr >= 10 and avg <= 0.220:
                pool = ["純粹盲砲 🙈", "不是三振就是全壘打 🎲", "盲劍客 🗡️", "揮空藝術家 🎨", "暴力開盲盒 📦", "球場造風者 🌬️", "大風車 🚁", "力量型盲人 🕶️", "一棒解千愁 🧨", "全壘打或回板凳 🪑", "瞎眼巨砲 🦍", "風扇大廠總裁 🏭"]
            elif (k_pct >= 30.0 or whiff >= 30.0) and hr < 10:
                pool = ["人體電風扇 🌀", "揮空大師 💨", "空調設備 ❄️", "造風機 🎐", "投手之友 🤝", "打不到球 🙈", "三振收集者 🗑️", "空氣斬 🗡️", "風扇大廠CEO 🏭", "涼風徐徐 🧊", "人體造風扇 💨", "三振自助餐 🏧"]
            elif bb_pct >= 12.0 and avg < 0.250:
                pool = ["散步大師 🚶", "選球魔人 👁️", "無極限雷達眼 📡", "一壘是你家 🏠", "不想揮棒症候群 🥱", "保送製造機 🖨️", "看球大師 🧐", "人體計步器 ⏱️", "四壞批發商 🎫", "站著上壘 🧍", "不動如山 ⛰️", "不想拿球棒 🦯"]
            elif hbp >= 5:
                pool = ["萬磁王 🧲", "肉身擋球員 🤕", "人體吸鐵球 🧲", "護具測試員 🛡️", "自帶引力場 🪐", "挨砸大師 🎯", "球找人 ⚾", "痛覺喪失 🥊", "吸球體質 🧲", "靶子打者 🏹", "觸身球批發 🛒", "吸引力法則 🌌"]
            elif sb >= 12:
                pool = ["田徑隊 🏃‍♂️", "音速小子 🐆", "壘間破壞狂 ⚡", "光速蒙面俠 🦸‍♂️", "腳上裝馬達 🛹", "盜壘狂魔 🦹", "捕手噩夢 🏃", "神偷 🥷", "紅綠燈無視 🚥", "飛毛腿 🌪️", "只會跑步 👟", "二壘小偷 🕵️"]
            elif hr <= 3 and avg >= 0.280:
                pool = ["安打碰碰王 🏓", "機關槍打者 🔫", "水槍大師 💧", "只打一壘安打 🎯", "球場牛皮糖 🍬", "德州安打批發商 🤠", "黏人精 🪲", "碰球機器 🤖", "力量封印 🚫", "巧打星人 💫", "鳥安製造機 🐦", "內野安打神 🏃"]
            elif hr >= 15:
                pool = ["無情轟炸機 💣", "重砲手 💥", "巨砲管 🎆", "球場破壞者 🚜", "暴力美學 🥊", "天空守護者 🔭", "無敵破壞王 👑", "投手夢魘 😱", "炸裂專家 🧨", "全壘打狂人 🦍", "一棒擊沉 🚢", "球縫線殺手 ⚾"]
            else:
                pool = ["氣氛大師 🎉", "打卡公務員 💼", "球場路人甲 🚶‍♂️", "隨處可見的打者 🤷‍♂️", "中規中矩先生 👔", "穩定上下班 🕰️", "薪水小偷候選 🕵️‍♂️", "吉祥物 🧸", "休息室DJ 🎵", "普通員工 🧍‍♂️", "無情打卡機 ⏱️"]

            return pool[idx % len(pool)]
    except:
        return "神秘客 ❓"

def generate_scout_conclusion(prs, p_prof, p_type):
    idx = abs(hash(str(p_prof.get('Player', 'Unknown')))) 
    overall = prs.get('WAR', 50)
    
    if p_type == '打者':
        if overall >= 85:
            p_pool = ["聯盟頂級且、", "MVP大熱門級別的", "具備統治全場實力的", "技術近乎無懈可擊的", "全明星先發等級的", "教科書般精湛的", "令對方投手聞風喪膽的", "具備史詩級破壞力的", "球隊絕對基石型的", "無可取代的頂尖"]
            c_pool = ["全能型超級巨星", "打擊線核心靈魂", "純粹的安打製造機器", "現代棒球終極進攻核武", "五拍子天選大物", "王牌殺手", "王牌粉碎機", "超級六角星全才打者"]
            s_pool = ["，正以現象級的演出主宰著整個賽季。", "，是任何先發輪值都不想面對的終極噩夢。", "，完美展現了豪門身價與令人驚嘆的破壞力。", "，其強悍火網能徹底摧毀對手的任何防守戰術部署。"]
        elif overall >= 60:
            p_pool = ["實力強勁的", "技術高超的", "中流砥柱級的", "破壞力十足的", "戰術價值極高的", "表現極具侵略性的", "不可忽視的優質"]
            c_pool = ["核心進攻發動機", "一線主戰打者", "中長程火砲專家", "前段棒次開路先鋒", "高產出打擊手", "關鍵時刻的冷酷殺手"]
            s_pool = ["，在中心棒次提供極其穩定的火力支援。", "，能有效串聯攻勢並徹底帶動球隊進攻氣勢。", "，擁有隨時用一發長打徹底改變比賽局勢的優異能力。", "，是教練團調兵遣將時最安心的進攻核心。"]
        elif overall >= 35:
            p_pool = ["四平八穩的", "稱職可靠的", "功能性明確的", "中規中矩的", "穩健發揮的", "潛力優質的"]
            c_pool = ["主力輪替成員", "體系型實用打者", "稱職的戰術綠葉", "攻守均衡的基底球員", "不可或缺的拼圖型戰力"]
            s_pool = ["，在打線中默默貢獻，提供穩定的基本盤。", "，特定戰術安排下能發揮出極佳的奇效。", "，表現四平八穩，是穩定球隊深度的中堅力量。", "，持續提供穩定的上場產出與打擊掩護。"]
        else:
            p_pool = ["尚在磨練的", "力求突破的", "手感調整中的", "尋求穩定度的", "充滿成長空間的潛力"]
            c_pool = ["拼圖型替補成員", "新秀學習期打者", "戰術功能型工兵", "處於發展階段的角色球員"]
            s_pool = ["，需要提升擊球品質以爭取更多先發發揮空間。", "，正在積極適應大聯盟層級的球風與配球強度。", "，仍需累積經驗，未來成長性值得持續追蹤觀察。"]
            
    else: # 投手
        if overall >= 85:
            p_pool = ["賽揚獎頂級大熱門、", "具備王牌壓制型的", "擁有絕對統治力的", "展現支配全場氣勢的", "聯盟無解級的", "神獸級傲人表現的", "防線堅不可摧的"]
            c_pool = ["終極頭號王牌(Ace)", "防線至高神柱", "奪三振藝術家", "球隊不敗制勝保證", "令對手絕望的球場主宰者"]
            s_pool = ["，每次登板都是一場近乎完美的視覺饗宴。", "，徹底鎖死對手打線，是球隊最引以為傲的制勝王牌。", "，正用極具侵略性的投球風格統治著最高殿堂。", "，擁有以一己之力徹底封鎖任何豪門打線的絕對實力。"]
        elif overall >= 60:
            p_pool = ["極具實力的", "高壓制力的", "發揮穩健的", "技術精湛的", "主戰輪值級別的", "威風凜凜的優質"]
            c_pool = ["優質前段先發投手", "中流砥柱型主力王牌", "極具破壞力的後援核心", "防線重要救火隊", "高效率的投球大師"]
            s_pool = ["，能夠穩定吃下大量局數並為球隊鎖定勝局。", "，在關鍵時刻總是能用穩健的控球化解失分危機。", "，是投手陣容中極其倚重的核心主戰戰力。", "，其優異的投球型態能完美執行各種局數封鎖任務。"]
        elif overall >= 35:
            p_pool = ["稱職合格的", "功能型明確的", "穩打穩紮的", "中規中矩的", "四平八穩的"]
            c_pool = ["中段輪值投手", "穩健的長中繼戰力", "任務型後援投手", "實用性高的大眾臉投手"]
            s_pool = ["，默默提供穩定的局數消化與局勢控制。", "，在特定的局數安排下能發揮極佳的拆彈效果。", "，表現穩定，是維繫整個投手群深度的重要基石。", "，能精準完成教練團交辦的基本投球工作。"]
        else:
            p_pool = ["力求突破的", "手感調整中的", "尚在磨練的", "尋求控球穩定度的", "極具改造潛力的"]
            c_pool = ["邊緣輪替投手", "成長期新秀投手", "待開發的長線戰力", "力求轉型的角色型投手"]
            s_pool = ["，需要大幅提升進壘點的精準度與球威壓制力。", "，正處於適應最高殿堂打者強度的關鍵學期。", "，未來仍需透過更多實戰修正投球機制與配球策略。"]

    pref = p_pool[idx % len(p_pool)]
    core = c_pool[(idx + 1) % len(c_pool)]
    suff = s_pool[(idx + 2) % len(s_pool)]
    
    return f"綜合評估為一位【{pref}{core}】{suff}"

def highlight_elite_stats(val, col_name, p_type):
    style = ''
    if pd.isna(val) or not isinstance(val, (int, float)): return style
    if col_name == 'WAR' and val >= 5.0: return 'color: #EF3E42; font-weight: bold;'
    if p_type == '打者':
        if col_name == 'Barrel%' and val >= 12.0: style = 'color: #EF3E42; font-weight: bold;'
        elif col_name in ['xwOBA'] and val >= 0.380: style = 'color: #EF3E42; font-weight: bold;'
        elif col_name in ['wRC+'] and val >= 130: style = 'color: #EF3E42; font-weight: bold;'
        elif col_name == 'Whiff%' and val <= 20.0: style = 'color: #EF3E42; font-weight: bold;'
    else:
        if col_name == 'xERA' and val <= 3.30: style = 'color: #EF3E42; font-weight: bold;'
        elif col_name in ['Whiff%', 'K%'] and val >= 28.0: style = 'color: #EF3E42; font-weight: bold;'
        elif col_name == 'HardHit%' and val <= 33.0: style = 'color: #EF3E42; font-weight: bold;'
    return style

def style_grade(val):
    if not isinstance(val, str): return ''
    for grade, key in grade_to_key.items():
        if val == grade:
            bg_col = st.session_state.get(f"color_{key}", "#000")
            txt_col = "black" if grade in ['S', 'A++'] else "white"
            return f'background-color: {bg_col}; color: {txt_col}; font-weight: bold;'
    return ''