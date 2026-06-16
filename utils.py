# utils.py
import streamlit as st
import pandas as pd
import unicodedata
from config import *

def translate_injury(text):
    if not text:
        return "未公開詳細傷勢"
        
    lower_text = text.lower().strip()
    
    # 完美使用你的防呆邏輯
    invalid_texts = ['il', 'out', 'day-to-day', '7-day il', '10-day il', '15-day il', '60-day il', 'unknown', 'injured 7-day', 'injured 10-day', 'injured 15-day', 'injured 60-day']
    if lower_text in invalid_texts:
        return "未公開詳細傷勢"
    
    tw_parts = []
    
    if "tommy john" in lower_text:
        tw_parts.append("手肘韌帶置換手術")
    else:
        if "left" in lower_text: tw_parts.append("左")
        elif "right" in lower_text: tw_parts.append("右")
        
        body_parts = ["shoulder", "elbow", "forearm", "wrist", "hand", "finger", "thumb", "lower back", "back", "neck", "oblique", "rib", "hip", "groin", "quad", "hamstring", "knee", "calf", "ankle", "foot", "toe", "achilles", "biceps", "triceps", "lat", "pectoral", "flexor", "tendon", "ligament", "meniscus", "ucl", "acl", "mcl", "labrum"]
        for bp in body_parts:
            if bp in lower_text:
                tw_parts.append(INJURY_DICT[bp])
                break
                
        conditions = ["strain", "sprain", "fracture", "contusion", "inflammation", "soreness", "sore", "tightness", "fatigue", "blister", "concussion", "surgery", "impingement", "dislocation", "tear", "bone bruise", "illness", "covid", "viral"]
        for cond in conditions:
            if cond in lower_text:
                tw_parts.append(INJURY_DICT[cond])
                break
                
    if tw_parts:
        tw_meaning = "".join(tw_parts)
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

def safe_float(val):
    try: return float(val)
    except: return 0.0

def generate_scout_conclusion(prs, p_prof, p_type):
    pr_barrel, pr_hardhit, pr_whiff, pr_chase = prs.get('Barrel%', 50), prs.get('HardHit%', 50), prs.get('Whiff%', 50), prs.get('Chase%', 50)
    pr_gb, pr_xba, pr_k, pr_bb = prs.get('GB%', 50), prs.get('xBA', 50), prs.get('K%', 50), prs.get('BB%', 50)
    if p_type == '打者':
        val = p_prof.get('AVG', 0.0)
        if val >= 0.320: tier = "歷史級"
        elif val >= 0.300: tier = "MVP級"
        elif val >= 0.280: tier = "全明星級"
        elif val >= 0.250: tier = "先發主力"
        elif val >= 0.220: tier = "板凳待命"
        else: tier = "掙扎中"
        
        if pr_whiff >= 80 and pr_chase >= 80: adj = "選球精湛的"
        elif pr_whiff >= 65: adj = "黏球纏鬥的"
        elif pr_whiff <= 20: adj = "電風扇式的"
        elif pr_gb <= 20: adj = "強力滾地的" 
        elif pr_gb >= 80: adj = "極端飛球的"
        elif pr_xba >= 80: adj = "高打擊率的"
        else: adj = "風格均衡的"
        
        if pr_barrel >= 95: noun = "核彈巨砲"
        elif pr_barrel >= 80: noun = "恐怖重砲"
        elif pr_hardhit >= 75: noun = "強擊球製造機"
        elif pr_barrel <= 20: noun = "碰碰槍"
        else: noun = "實用打者"
        return f"{tier}{adj}{noun}"
    else:
        val = p_prof.get('ERA', 9.99)
        if val <= 2.50: tier = "神獸級"
        elif val <= 3.00: tier = "賽揚級"
        elif val <= 3.50: tier = "全明星級"
        elif val <= 4.00: tier = "主力輪值/穩健牛棚"
        elif val <= 4.50: tier = "工作馬"
        else: tier = "掙扎中"
        
        if pr_bb >= 85: adj = "雷達導航般的"
        elif pr_bb >= 65: adj = "控球穩健的"
        elif pr_bb <= 20: adj = "狂野亂放的"
        elif pr_gb >= 80: adj = "製造滾地的" 
        elif pr_gb <= 20: adj = "飛球派的"
        else: adj = "表現均衡的"
        
        if pr_k >= 95: noun = "三振魔人"
        elif pr_k >= 80: noun = "K博士"
        elif pr_whiff >= 80: noun = "揮空引誘大師"
        elif pr_hardhit >= 80: noun = "軟投派大師"
        elif pr_k <= 20: noun = "發球機"
        else: noun = "實力派投手"
        return f"{tier}{adj}{noun}"

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