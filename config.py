# config.py
MLB_TEAM_COLORS = {
    "Los Angeles Dodgers": ("#005A9C", "#A5ACAF"), "New York Yankees": ("#0C2340", "#C4CED4"),
    "Boston Red Sox": ("#BD3039", "#0C2340"), "Houston Astros": ("#002D62", "#EB6E1F"),
    "Atlanta Braves": ("#CE1141", "#13274F"), "Philadelphia Phillies": ("#E81828", "#002D72"),
    "New York Mets": ("#002D72", "#FF5910"), "Toronto Blue Jays": ("#134A8E", "#1D2D5C"),
    "Baltimore Orioles": ("#DF4601", "#000000"), "Tampa Bay Rays": ("#092C5C", "#8FBCE6"),
    "Chicago White Sox": ("#27251F", "#C4CED4"), "Cleveland Guardians": ("#0C2340", "#E31937"),
    "Detroit Tigers": ("#0C2340", "#FA4616"), "Kansas City Royals": ("#004687", "#BD9B60"),
    "Minnesota Twins": ("#002B5C", "#D31145"), "Los Angeles Angels": ("#BA0021", "#003263"),
    "Oakland Athletics": ("#003831", "#EFB21E"), "Seattle Mariners": ("#005C5C", "#0C2C56"),
    "Texas Rangers": ("#003278", "#C0111F"), "Chicago Cubs": ("#0E3386", "#CC3433"),
    "Cincinnati Reds": ("#C6011F", "#000000"), "Milwaukee Brewers": ("#12284B", "#FFC52F"),
    "Pittsburgh Pirates": ("#FDB827", "#27251F"), "St. Louis Cardinals": ("#C41E3A", "#0C2340"),
    "Arizona Diamondbacks": ("#A71930", "#E3D4AD"), "Colorado Rockies": ("#333366", "#C4CED4"),
    "San Diego Padres": ("#2F241D", "#FFC425"), "San Francisco Giants": ("#FD5A1E", "#27251F"),
    "Miami Marlins": ("#00A3E0", "#EF3340"), "Washington Nationals": ("#AB0003", "#14225A"),
}

MLB_TEAM_IDS = {
    "Los Angeles Dodgers": 119, "New York Yankees": 147, "Boston Red Sox": 111,
    "Houston Astros": 117, "Atlanta Braves": 144, "Philadelphia Phillies": 143,
    "New York Mets": 121, "Toronto Blue Jays": 141, "Baltimore Orioles": 110,
    "Tampa Bay Rays": 139, "Chicago White Sox": 145, "Cleveland Guardians": 114,
    "Detroit Tigers": 116, "Kansas City Royals": 118, "Minnesota Twins": 142,
    "Los Angeles Angels": 108, "Oakland Athletics": 133, "Seattle Mariners": 136,
    "Texas Rangers": 140, "Chicago Cubs": 112, "Cincinnati Reds": 113,
    "Milwaukee Brewers": 158, "Pittsburgh Pirates": 134, "St. Louis Cardinals": 138,
    "Arizona Diamondbacks": 109, "Colorado Rockies": 115, "San Diego Padres": 135,
    "San Francisco Giants": 137, "Miami Marlins": 146, "Washington Nationals": 120,
}

METRIC_TW = {
    'WAR': '勝場貢獻', 'PA': '打席', 'AB': '打數', 'R': '得分', 'H': '安打', 
    'RBI': '打點', 'AVG': '打擊率', 'OPS': '整體攻擊指數', 'OBP': '上壘率', 
    'wOBA': '加權上壘率', 'HR': '全壘打', 'SB': '盜壘', 'BB': '保送', 'K': '三振', 
    'wRC+': '加權創造得分', 'xwOBA': '預期加權上壘率', 'xBA': '預期打擊率', 
    'HardHit%': '強擊球率', 'Barrel%': '完美擊球率', 'Chase%': '追打壞球率', 
    'Whiff%': '揮空率', 'GB%': '滾地球率',
    'IP': '投球局數', 'ER': '自責分', 'PC': '用球數', 'ERA': '防禦率', 
    'xERA': '預期防禦率', 'WHIP': '每局被上壘率', 'K%': '三振率', 'BB%': '保送率', 
    'FIP': '進階獨立防禦率', 'BA': '被打擊率', 'Diff': '實際預期落差',
    '1B': '一壘安打', '2B': '二壘安打', '3B': '三壘安打', 'HBP': '觸身球', 'E': '失誤',
    'CYC': '完全打擊', 'SLAM': '滿貫砲', 'W': '勝投', 'L': '敗投', 'SHO': '完封',
    'SV': '救援成功', 'OUT': '製造出局數', 'WP': '暴投', 'HLD': '中繼成功', 'QS': '優質先發', 'BSV': '救援失敗'
}

INJURY_DICT = {
    "shoulder": "肩膀", "elbow": "手肘", "forearm": "前臂", "wrist": "手腕", "hand": "手部", 
    "finger": "手指", "thumb": "拇指", "lower back": "下背部", "back": "背部", "neck": "頸部", 
    "oblique": "腹斜肌", "rib": "肋骨", "hip": "髖部", "groin": "腹股溝", 
    "quad": "大腿前側", "hamstring": "大腿後側", "knee": "膝蓋", "calf": "小腿", 
    "ankle": "腳踝", "foot": "腳部", "toe": "腳趾", "achilles": "阿基里斯腱",
    "biceps": "二頭肌", "triceps": "三頭肌", "lat": "背闊肌", "pectoral": "胸肌",
    "flexor": "屈肌", "tendon": "肌腱", "ligament": "韌帶", "meniscus": "半月板",
    "ucl": "尺骨附屬韌帶", "acl": "前十字韌帶", "mcl": "內側副韌帶", "labrum": "關節唇",
    "strain": "拉傷", "sprain": "扭傷", "fracture": "骨折", "contusion": "挫傷", 
    "inflammation": "發炎", "soreness": "痠痛", "sore": "痠痛", "tightness": "緊繃", 
    "fatigue": "疲勞", "blister": "水泡", "concussion": "腦震盪", "surgery": "手術",
    "impingement": "夾擠症", "dislocation": "脫臼", "tear": "撕裂", "bone bruise": "骨挫傷",
    "illness": "生病", "covid": "新冠肺炎", "viral": "病毒感染"
}

METRIC_FORMATS = {
    'Fantasy_Score': '{:.0f}', 'Fantasy_Pts': '{:.0f}', 'Fan_Pts': '{:.0f}', 'Avg_Pts': '{:.1f}',
    'PA': '{:.0f}', 'AB': '{:.0f}', 'R': '{:.0f}', 'H': '{:.0f}', 'RBI': '{:.0f}', 
    'HR': '{:.0f}', 'SB': '{:.0f}', 'BB': '{:.0f}', 'K': '{:.0f}', 'wRC+': '{:.0f}', 
    'PC': '{:.0f}', 'SV': '{:.0f}', 'W': '{:.0f}', 'L': '{:.0f}', 'ER': '{:.0f}',
    '1B': '{:.0f}', '2B': '{:.0f}', '3B': '{:.0f}', 'HBP': '{:.0f}', 'E': '{:.0f}',
    'SHO': '{:.0f}', 'OUT': '{:.0f}', 'WP': '{:.0f}', 'HLD': '{:.0f}', 'QS': '{:.0f}', 'BSV': '{:.0f}',
    '打數 (AB)': '{:.0f}', '安打 (H)': '{:.0f}', '全壘打 (HR)': '{:.0f}', '三振 (K)': '{:.0f}', '保送 (BB)': '{:.0f}',
    'IP': '{:.1f}', 'K%': '{:.1f}', 'BB%': '{:.1f}', 'HardHit%': '{:.1f}', 'Barrel%': '{:.1f}', 
    'Whiff%': '{:.1f}', 'Chase%': '{:.1f}', 'GB%': '{:.1f}', 'WAR': '{:.1f}', 'Avg EV': '{:.1f}',
    'MVP_Index': '{:.1f}', 'Cy_Index': '{:.1f}',
    'ERA': '{:.2f}', 'xERA': '{:.2f}', 'WHIP': '{:.2f}', 'FIP': '{:.2f}', 'Diff': '{:.2f}',
    'ERA (賽季防禦率走勢)': '{:.2f}', 'WHIP (賽季WHIP走勢)': '{:.2f}',
    'AVG': '{:.3f}', 'OPS': '{:.3f}', 'OBP': '{:.3f}', 'SLG': '{:.3f}', 'wOBA': '{:.3f}', 
    'xwOBA': '{:.3f}', 'xBA': '{:.3f}', 'BA': '{:.3f}', 'BAA': '{:.3f}',
    'AVG (賽季打擊率走勢)': '{:.3f}', 'OBP (賽季上壘率走勢)': '{:.3f}', 
    'SLG (賽季長打率走勢)': '{:.3f}', 'OPS (賽季OPS走勢)': '{:.3f}'
}

grade_keys = ['S', 'A_plus_plus', 'A_plus', 'A', 'B_plus_plus', 'B_plus', 'B', 'C', 'D', 'E', 'F']
grade_defaults = ['#FFD700', '#FF3300', '#FF6600', '#FF9900', '#0033CC', '#0066FF', '#3399FF', '#2E8B57', '#808080', '#A9A9A9', '#555555']
grade_to_key = {'S': 'S', 'A++': 'A_plus_plus', 'A+': 'A_plus', 'A': 'A', 'B++': 'B_plus_plus', 'B+': 'B_plus', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F'}

exclude_cols = ['Player', 'Player_ID', 'Team', 'Position', 'PA', 'AB', 'R', 'ER', 'PC', 'IP', 'H', 'HR', 'SB', 'Diff', 'IP_calc']