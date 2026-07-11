import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timezone, timedelta

# 導入分層模組
from config import *

# 載入所有 utils 工具函數
from utils import (
    format_metric, STYLER_FORMATS, f_size, get_team_color, 
    hex_to_rgba, highlight_elite_stats, style_grade, score_to_grade,
    get_percentile, get_relative_grade, generate_scout_conclusion,
    get_team_logo_url, darken_color, generate_fun_nickname
)

# 載入所有 data_fetcher 的資料抓取函數
from data_fetcher import (
    process_combined_data, fetch_player_gamelog, fetch_player_handedness,
    fetch_savant_platoon_splits, fetch_player_home_away_splits, fetch_player_career,
    fetch_all_teams_stats, fetch_team_recent_matchups, fetch_team_roster,
    fetch_team_injury_list, fetch_recent_form_ranking, fetch_weekly_fantasy_ranking,
    fetch_milb_stats, fetch_daily_schedule, fetch_bullpen_usage, fetch_bvp_data,
    fetch_team_recent_form
)

# 🌟 必須是第一個 Streamlit 指令
st.set_page_config(layout="wide", page_title="MLB 終極球探系統")

# 初始化 session state 字體大小設定（防呆）
if 'font_size' not in st.session_state: st.session_state.font_size = 15
if 'table_font_size' not in st.session_state: st.session_state.table_font_size = 13

# 載入等級色彩設定到 session state
for k, c in zip(grade_keys, grade_defaults):
    if f'color_{k}' not in st.session_state: 
        st.session_state[f'color_{k}'] = c

# --- 側欄功能區 ---
with st.sidebar:
    tw_tz = timezone(timedelta(hours=8))
    year = datetime.now(tw_tz).year 
    p_type = st.radio("球員類型 (切換分頁動態配置)", ["打者", "投手"], key="main_p_type")
    
    data_mode = st.radio("數據分析模式", ["一般賽季分析", "Fantasy 夢幻棒球"], key="main_data_mode")
    min_filter = st.number_input("設定本季 PA (打席) 下限", min_value=0, value=30, step=10, key="main_min_filter_h") if p_type == "打者" else st.number_input("設定本季 IP (投球局數) 下限", min_value=0.0, value=10.0, step=5.0, key="main_min_filter_p")
    
    # 撈取整併大聯盟、Savant 的賽季數據 (原始全資料)
    raw_data = process_combined_data(p_type, year, min_filter).copy()
    target_nickname = None
    
    if not raw_data.empty:
        # 🔥 升級計畫第二步：動態生成全聯盟外號，並加入欄位
        raw_data['Nickname'] = raw_data.apply(lambda row: generate_fun_nickname(row, p_type), axis=1)
        
        all_players = sorted(raw_data['Player'].unique().tolist())
        all_teams = sorted(list(MLB_TEAM_IDS.keys()))
        all_nicknames = sorted(raw_data['Nickname'].unique().tolist())
        
        st.markdown("---")
        target_profile = st.selectbox("🔍 搜尋球員 (進入個人專屬面版)", options=all_players, index=None, placeholder="點選或輸入名字，按右側 ✕ 返回主頁", key="main_search_player")
        target_team = st.selectbox("🏟️ 選擇球隊 (進入球隊專屬面版)", options=all_teams, index=None, placeholder="選擇球隊，按右側 ✕ 返回主頁", key="main_search_team")
        
        # 🔥 升級計畫第二步：外號篩選器
        target_nickname = st.selectbox("🎭 依專屬外號篩選 (同類球員大集合)", options=all_nicknames, index=None, placeholder="選擇外號，列出所有同類型的球員", key="main_search_nickname")
        
        # 判斷當前介面模式與資料流
        if target_profile:
            mode = 'player'
            full_data = raw_data.copy()
            theme_team = full_data[full_data['Player'] == target_profile].iloc[0]['Team']
        elif target_team:
            mode = 'team'
            full_data = raw_data.copy()
            theme_team = target_team
        elif target_nickname:
            mode = 'league'
            # 🚀 篩選全聯盟數據，只保留被判定為該外號的球員！
            full_data = raw_data[raw_data['Nickname'] == target_nickname].copy()
            theme_team = "Los Angeles Dodgers" 
        else:
            mode = 'league'
            full_data = raw_data.copy()
            theme_team = "Los Angeles Dodgers" 
            
        t_colors = get_team_color(theme_team)
        p_prof_color, p_prof_secondary = t_colors[0], t_colors[1]
        
        st.markdown(f"""
            <style>
            [data-testid="stSidebar"] {{ background-color: {p_prof_color} !important; transition: background-color 0.5s ease; }}
            [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] span {{ color: {p_prof_secondary} !important; text-shadow: 0px 1px 3px rgba(0,0,0,0.6), 0px 0px 2px rgba(255,255,255,0.2) !important; font-weight: bold; }}
            [data-testid="stSidebar"] div[data-baseweb="select"] > div {{ background-color: #FFFFFF !important; border: none !important; border-radius: 6px; }}
            [data-testid="stSidebar"] div[data-baseweb="select"] * {{ color: #111111 !important; font-weight: 600 !important; text-shadow: none !important; }}
            [data-testid="stSidebar"] input {{ border: none !important; background-color: #FFFFFF !important; color: #111111 !important; font-weight: bold; text-shadow: none !important; }}
            </style>
        """, unsafe_allow_html=True)
        
    with st.expander("⚙️ 系統外觀設定"):
        st.session_state.font_size = st.slider("📄 全局介面字體大小 (基準值)", min_value=12, max_value=30, value=st.session_state.font_size, step=1, key="setting_font_size")
        st.session_state.table_font_size = st.slider("📊 數據表格專用字體 (基準值)", min_value=10, max_value=24, value=st.session_state.table_font_size, step=1, key="setting_table_font_size")

# 🌟 全域主畫面樣式與頂部標題
if not full_data.empty:
    global_metrics = [c for c in full_data.columns if c not in exclude_cols and c != 'Nickname']
    
    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"], .stApp {{ background-color: {hex_to_rgba(p_prof_color, 0.05)} !important; transition: background-color 0.5s ease; }}
        [data-testid="stHeader"] {{ background-color: transparent !important; }}
        [data-testid="stMetricValue"] {{ color: {p_prof_color} !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); }}
        [data-testid="stMetricDelta"] > div {{ font-size: 1.15rem !important; font-weight: 900 !important; }}
        .block-container {{ max-width: 1400px !important; margin: 0 auto !important; padding-top: 1rem !important; padding-bottom: 2rem !important; }}
        .table-scroll-container {{ width: 100%; max-height: 65vh; overflow: auto; border: 1px solid #e0e0e0; border-radius: 8px; background-color: white; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
        table.dataframe {{ width: 100%; border-collapse: collapse; margin: 0; background-color: white; }}
        table.dataframe th, table.dataframe td {{ padding: 6px 12px; border: 1px solid #e0e0e0; text-align: center !important; white-space: nowrap; font-size: {f_size(st.session_state.table_font_size)} !important; }}
        table.dataframe thead th {{ background-color: {p_prof_color}; color: white !important; font-size: {f_size(st.session_state.table_font_size, 0.9)} !important; position: sticky; top: 0; z-index: 10; box-shadow: 0 2px 2px -1px rgba(0,0,0,0.4); }}
        button[data-baseweb="tab"] p {{ font-size: {f_size(st.session_state.font_size, 0.9)} !important; font-weight: bold; }}
        @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} 100% {{ opacity: 1; }} }}
        </style>
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: {p_prof_color}; text-shadow: 1px 1px 3px rgba(0,0,0,0.15); font-weight: 900; margin: 0; padding: 0;">⚾ MLB 球探數據系統 ⚾</h1>
            <div style="width: 120px; height: 5px; background-color: {p_prof_secondary}; margin: 10px auto; border-radius: 3px; box-shadow: 0px 1px 2px rgba(0,0,0,0.2);"></div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 📌 模式 A：球員個人專屬分析面板
# ==========================================
if not full_data.empty:
    if mode == 'player':
        p_prof = full_data[full_data['Player'] == target_profile].iloc[0]
        logo_url = get_team_logo_url(p_prof['Team'])
        hand_info = fetch_player_handedness(p_prof['Player_ID'])
        
        # 由於已在 full_data 運算，直接提取外號
        fun_nickname = p_prof['Nickname']
        
        logo_html = f"<img src='{logo_url}' width='45' style='vertical-align: middle; margin-right: 12px;'>" if logo_url else ""
        
        st.markdown(f"<h2 style='color:{p_prof_color}; border-bottom: 3px solid {p_prof_color}; padding-bottom: 10px; display: flex; align-items: center;'>{logo_html} <span> {target_profile} <span style='font-size:0.55em; background-color:{p_prof_color}; color:#FFFFFF; border: 1.5px solid {p_prof_secondary}; padding:4px 10px; border-radius:20px; margin-left:10px; vertical-align:middle; text-shadow:none;'>{fun_nickname}</span> <span style='font-size:0.6em; color:{p_prof_secondary}; margin-left:10px;'>({hand_info})</span> | {p_prof['Team']} - {p_prof['Position']}</span></h2>", unsafe_allow_html=True)
        
        st.markdown("### 📊 本賽季核心數據與最新動態 (Season Stats & Trends)")
        gamelog_df = fetch_player_gamelog(int(p_prof['Player_ID']), p_type, year)
        last_game = gamelog_df.iloc[0] if not gamelog_df.empty else None
        prev_game = gamelog_df.iloc[1] if len(gamelog_df) > 1 else None
        
        if p_type == '打者':
            m_cols = st.columns(9)
            m_cols[0].metric("AB", format_metric(p_prof['AB'], 'AB'), delta=f"+{int(last_game['AB'])}" if last_game is not None and last_game['AB']>0 else None)
            m_cols[1].metric("R", format_metric(p_prof['R'], 'R'), delta=f"+{int(last_game['R'])}" if last_game is not None and last_game['R']>0 else None)
            m_cols[2].metric("H", format_metric(p_prof['H'], 'H'), delta=f"+{int(last_game['H'])}" if last_game is not None and last_game['H']>0 else None)
            m_cols[3].metric("RBI", format_metric(p_prof['RBI'], 'RBI'), delta=f"+{int(last_game['RBI'])}" if last_game is not None and last_game['RBI']>0 else None)
            m_cols[4].metric("HR", format_metric(p_prof['HR'], 'HR'), delta=f"+{int(last_game['HR'])}" if last_game is not None and last_game['HR']>0 else None)
            m_cols[5].metric("SB", format_metric(p_prof['SB'], 'SB'), delta=f"+{int(last_game['SB'])}" if last_game is not None and last_game['SB']>0 else None)
            m_cols[6].metric("BB", format_metric(p_prof['BB'], 'BB'), delta=f"+{int(last_game['BB'])}" if last_game is not None and last_game['BB']>0 else None)
            m_cols[7].metric("K", format_metric(p_prof['K'], 'K'), delta=f"+{int(last_game['K'])}" if last_game is not None and last_game['K']>0 else None, delta_color="inverse")
            d_avg = round(last_game['AVG (賽季打擊率走勢)'] - prev_game['AVG (賽季打擊率走勢)'], 3) if prev_game is not None else 0.0
            m_cols[8].metric("AVG", format_metric(p_prof['AVG'], 'AVG'), delta=f"{d_avg:.3f}" if d_avg != 0 else None)
        else:
            m_cols = st.columns(10)
            m_cols[0].metric("IP", format_metric(p_prof['IP'], 'IP'), delta=f"+{last_game['IP']}" if last_game is not None and last_game['IP_calc']>0 else None)
            m_cols[1].metric("H", format_metric(p_prof['H'], 'H'), delta=f"+{int(last_game['H'])}" if last_game is not None and last_game['H']>0 else None, delta_color="inverse")
            m_cols[2].metric("R", format_metric(p_prof['R'], 'R'), delta=f"+{int(last_game['R'])}" if last_game is not None and last_game['R']>0 else None, delta_color="inverse")
            m_cols[3].metric("ER", format_metric(p_prof['ER'], 'ER'), delta=f"+{int(last_game['ER'])}" if last_game is not None and last_game['ER']>0 else None, delta_color="inverse")
            m_cols[4].metric("BB", format_metric(p_prof['BB'], 'BB'), delta=f"+{int(last_game['BB'])}" if last_game is not None and last_game['BB']>0 else None, delta_color="inverse")
            m_cols[5].metric("K", format_metric(p_prof['K'], 'K'), delta=f"+{int(last_game['K'])}" if last_game is not None and last_game['K']>0 else None)
            m_cols[6].metric("PC", format_metric(p_prof['PC'], 'PC'), delta=f"+{int(last_game['PC'])}" if last_game is not None and last_game['PC']>0 else None, delta_color="off")
            m_cols[7].metric("HR", format_metric(p_prof['HR'], 'HR'), delta=f"+{int(last_game['HR'])}" if last_game is not None and last_game['HR']>0 else None, delta_color="inverse")
            d_whip = round(last_game['WHIP (賽季WHIP走勢)'] - prev_game['WHIP (賽季WHIP走勢)'], 3) if prev_game is not None else 0.0
            m_cols[8].metric("WHIP", format_metric(p_prof['WHIP'], 'WHIP'), delta=f"{d_whip:.2f}" if d_whip != 0 else None, delta_color="inverse")
            d_era = round(last_game['ERA (賽季防禦率走勢)'] - prev_game['ERA (賽季防禦率走勢)'], 2) if prev_game is not None else 0.0
            m_cols[9].metric("ERA", format_metric(p_prof['ERA'], 'ERA'), delta=f"{d_era:.2f}" if d_era != 0 else None, delta_color="inverse")

        st.markdown("### 📅 近 5 場傳統賽事表現 (Last 5 Games Log)")
        if not gamelog_df.empty:
            recent_5 = gamelog_df.head(5).copy()
            if p_type == '打者':
                recent_5 = recent_5.rename(columns={'AVG (賽季打擊率走勢)': 'AVG'})
                show_cols = ['Date', 'Opponent', '主/客', 'AB', 'R', 'H', 'RBI', 'HR', 'SB', 'BB', 'K', 'AVG']
            else:
                recent_5 = recent_5.rename(columns={'WHIP (賽季WHIP走勢)': 'WHIP', 'ERA (賽季防禦率走勢)': 'ERA'})
                show_cols = ['Date', 'Opponent', '主/客', 'IP', 'H', 'R', 'ER', 'BB', 'K', 'PC', 'HR', 'WHIP', 'ERA']
            
            def color_gamelog_rows(row):
                is_home = "主場" in str(row['主/客'])
                bg = hex_to_rgba(p_prof_color, 0.18) if is_home else hex_to_rgba(get_team_color(row['Opponent'])[0], 0.18)
                return [f'background-color: {bg}; color: black; font-weight: 500;' for _ in row.index]
                
            styled_recent_5 = recent_5[show_cols].style.apply(color_gamelog_rows, axis=1).format(STYLER_FORMATS).hide(axis='index')
            st.markdown(f"<div class='table-scroll-container'>{styled_recent_5.to_html()}</div>", unsafe_allow_html=True)
        else:
            st.info("⚠️ 目前查無本賽季出賽紀錄。")

        st.markdown("---")
        st.markdown("### 🦄 本週 Fantasy 逐場分數結算 (近 7 天)")
        start_str = (datetime.now(tw_tz) - timedelta(days=7)).strftime("%Y-%m-%d")
        recent_7d = gamelog_df[gamelog_df['Date'] >= start_str].copy() if not gamelog_df.empty else pd.DataFrame()
        weekly_score = recent_7d['Fantasy_Pts'].sum() if not recent_7d.empty else 0
        
        st.markdown(f'''
        <div style="background: linear-gradient(135deg, {p_prof_color} 0%, {darken_color(p_prof_color, 0.6)} 100%); padding: 20px 30px; border-radius: 12px; color: white; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 15px rgba(0,0,0,0.15);">
            <div>
                <h4 style="margin: 0 0 5px 0; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 1.1em;">本週 (近7天) Fantasy 總積分</h4>
                <div style="font-size: {f_size(st.session_state.font_size, 3.0)}; font-weight: 900; line-height: 1; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">{weekly_score:,.0f} <span style="font-size: 0.4em; opacity: 0.8; font-weight: normal; text-shadow: none;">pts</span></div>
            </div>
            <div style="text-align: right; opacity: 0.85; font-size: {f_size(st.session_state.font_size, 0.95)}; line-height: 1.6; font-weight: bold;">
                ✓ 包含近 7 天的所有出賽紀錄<br>✓ 精確結算單場 CYC / SLAM / QS 等進階成就
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        if not recent_7d.empty:
            if p_type == '打者':
                show_cols_f = ['Date', 'Opponent', '主/客', 'Fantasy_Pts', 'AB', 'R', 'H', 'RBI', 'HR', 'SB', 'BB', 'K']
            else:
                show_cols_f = ['Date', 'Opponent', '主/客', 'Fantasy_Pts', 'IP', 'H', 'R', 'ER', 'BB', 'K', 'PC', 'HR']
                
            def color_recent_7d(row):
                is_home = "主場" in str(row['主/客'])
                bg = hex_to_rgba(p_prof_color, 0.18) if is_home else hex_to_rgba(get_team_color(row['Opponent'])[0], 0.18)
                return [f'background-color: {bg}; color: black !important; font-weight: 900 !important; font-size: 1.15em;' if col == 'Fantasy_Pts' else f'background-color: {bg}; color: black; font-weight: 500;' for col in row.index]
                
            styled_7d = recent_7d[show_cols_f].style.apply(color_recent_7d, axis=1).format(STYLER_FORMATS).hide(axis='index')
            st.markdown(f"<div class='table-scroll-container'>{styled_7d.to_html()}</div>", unsafe_allow_html=True)
        else:
            st.info(f"⚠️ {target_profile} 在近 7 天內沒有出賽紀錄。")

        st.markdown("---")
        scout_metrics = [m for m in global_metrics if m not in ['CYC', 'SLAM', 'E']]
        prs = {m: get_percentile(full_data, m, p_prof[m], p_type) for m in scout_metrics}
        sorted_prs = sorted(prs.items(), key=lambda x: x[1], reverse=True)
        strengths = [item for item in sorted_prs if item[1] >= 75][:4]
        weaknesses = sorted([item for item in sorted_prs if item[1] <= 35][-4:], key=lambda x: x[1])
        conclusion = generate_scout_conclusion(prs, p_prof, p_type) 
        
        st.markdown("### 🤖 深度球探報告")
        st.markdown("#### 🟢 優勢 (Strengths)")
        if strengths:
            for m, pr in strengths: st.markdown(f"<div style='font-size:{f_size(st.session_state.font_size)};'>• **{m}** 聯盟前 {max(1, 100-pr):.0f}%</div>", unsafe_allow_html=True)
        else: st.markdown(f"<div style='font-size:{f_size(st.session_state.font_size)};'>• 無明顯頂尖數據</div>", unsafe_allow_html=True)
        
        st.markdown("#### 🔴 弱點 (Weaknesses)")
        if weaknesses:
            for m, pr in weaknesses: st.markdown(f"<div style='font-size:{f_size(st.session_state.font_size)};'>• **{m}** { '偏高' if pr > 15 else '極差' } (倒數 {max(1, pr):.0f}%)</div>", unsafe_allow_html=True)
        else: st.markdown(f"<div style='font-size:{f_size(st.session_state.font_size)};'>• 無明顯數據短板</div>", unsafe_allow_html=True)
        
        st.markdown("#### 📝 總結定位")
        st.info(f"**{conclusion}** | 評級請點擊左側欄搜尋框右側 ✕ 回到全聯盟綜合排名查看")

        st.markdown("---")
        st.markdown("### 📊 本季單人完整進階數據表")
        single_df = full_data[full_data['Player'] == target_profile].drop(columns=['Player_ID', 'Nickname'], errors='ignore')
        styled_single = single_df.style.apply(lambda x: [highlight_elite_stats(v, x.name, p_type) for v in x], axis=0).format(STYLER_FORMATS).hide(axis='index')
        st.markdown(f"<div class='table-scroll-container' style='max-height: none;'>{styled_single.to_html()}</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### ⚔️ 對決左右手數據 (Savant Platoon Splits)")
        with st.spinner("載入 Savant 進階對戰數據..."):
            platoon_df = fetch_savant_platoon_splits(p_prof['Player_ID'], p_type, year)
            if not platoon_df.empty:
                styled_platoon = platoon_df.style.format(STYLER_FORMATS).hide(axis='index')
                st.markdown(f"<div class='table-scroll-container' style='max-height: none;'>{styled_platoon.to_html()}</div>", unsafe_allow_html=True)
            else: st.info("⚠️ 查無本季 Savant 進階對戰左右手數據。")
        
        st.markdown("---")
        st.markdown("### 🏟️ 主客場表現差異 (Home/Away)")
        with st.spinner("載入主客場數據..."):
            ha_df = fetch_player_home_away_splits(p_prof['Player_ID'], p_type, year)
            if not ha_df.empty:
                styled_ha = ha_df.style.format(STYLER_FORMATS).hide(axis='index')
                st.markdown(f"<div class='table-scroll-container' style='max-height: none;'>{styled_ha.to_html()}</div>", unsafe_allow_html=True)
            else: st.info("⚠️ 查無本季主客場數據。")
                
        st.markdown("---")
        st.markdown("### 📜 生涯逐年數據走勢 (Career Trend)")
        with st.spinner("載入生涯數據..."):
            career_df = fetch_player_career(p_prof['Player_ID'], p_type)
            if not career_df.empty:
                col_c_sel, _ = st.columns([1, 2])
                career_metrics = [c for c in career_df.columns if c not in ['Season', 'Team']]
                def_c_idx = career_metrics.index('OPS') if p_type == '打者' and 'OPS' in career_metrics else (career_metrics.index('ERA') if p_type == '投手' and 'ERA' in career_metrics else 0)
                sel_career_metric = col_c_sel.selectbox("選擇生涯指標", career_metrics, index=def_c_idx, key='career_metric_player')
                
                fig_career = px.line(career_df, x='Season', y=sel_career_metric, hover_data=['Team'], markers=True, color_discrete_sequence=[p_prof_color])
                fig_career.update_traces(marker=dict(size=10, line=dict(color='white', width=2)), line=dict(width=3))
                fig_career.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=450, xaxis_title="賽季 (Season)", yaxis_title=sel_career_metric, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_career, width="stretch", config={'scrollZoom': True})
            else: st.info("⚠️ 查無生涯逐年數據。")

# ==========================================
# 📌 模式 B：球隊分析戰情室
# ==========================================
    elif mode == 'team':
        logo_url = get_team_logo_url(theme_team)
        logo_html = f"<img src='{logo_url}' width='55' style='vertical-align: middle; margin-right: 15px; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.2));'>" if logo_url else ""
        
        st.markdown(f"<h2 style='color:{p_prof_color}; border-bottom: 3px solid {p_prof_color}; padding-bottom: 10px; display: flex; align-items: center;'>{logo_html} <span>{theme_team} 專屬分析戰情室</span></h2>", unsafe_allow_html=True)
        
        st.markdown("### 📊 本季球隊核心數據與大聯盟排名 (Team Stats & MLB Ranks)")
        with st.spinner("載入 30 隊排行榜數據中..."):
            ts_df = fetch_all_teams_stats(year)
            if not ts_df.empty and theme_team in ts_df['Team'].values:
                ts = ts_df[ts_df['Team'] == theme_team].iloc[0]
                
                def team_metric_card(label, val_str, rank):
                    rank_color = "#00E676" if rank <= 15 else "#A9A9A9"
                    return f'''
                    <div style="background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 15px; border: 1px solid #e0e0e0; text-align: center;">
                        <div style="font-size: {f_size(st.session_state.font_size, 0.9)}; color: #555; margin-bottom: 5px; font-weight: bold;">{label}</div>
                        <div style="font-size: {f_size(st.session_state.font_size, 1.8)}; font-weight: 900; color: {p_prof_color};">{val_str}</div>
                        <div style="font-size: {f_size(st.session_state.font_size, 0.85)}; color: {rank_color}; font-weight: bold; margin-top: 5px;">聯盟第 {int(rank)} 名</div>
                    </div>
                    '''
                
                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(team_metric_card("打擊率 (AVG)", f"{ts['H_AVG']:.3f}", ts['H_AVG_Rank']), unsafe_allow_html=True)
                c2.markdown(team_metric_card("攻擊指數 (OPS)", f"{ts['H_OPS']:.3f}", ts['H_OPS_Rank']), unsafe_allow_html=True)
                c3.markdown(team_metric_card("全壘打 (HR)", f"{int(ts['H_HR'])}", ts['H_HR_Rank']), unsafe_allow_html=True)
                c4.markdown(team_metric_card("總得分 (Runs)", f"{int(ts['H_R'])}", ts['H_R_Rank']), unsafe_allow_html=True)
                
                c5, c6, c7, c8 = st.columns(4)
                c5.markdown(team_metric_card("團隊防禦率 (ERA)", f"{ts['P_ERA']:.2f}", ts['P_ERA_Rank']), unsafe_allow_html=True)
                c6.markdown(team_metric_card("每局被上壘率 (WHIP)", f"{ts['P_WHIP']:.2f}", ts['P_WHIP_Rank']), unsafe_allow_html=True)
                c7.markdown(team_metric_card("團隊三振數 (K)", f"{int(ts['P_K'])}", ts['P_K_Rank']), unsafe_allow_html=True)
                c8.markdown(team_metric_card("團隊保送數 (BB)", f"{int(ts['P_BB'])}", ts['P_BB_Rank']), unsafe_allow_html=True)
            else:
                st.info("⚠️ 尚無本賽季團隊數據。")
                
        st.markdown("---")
        st.markdown("### 📅 近 5 場對戰近況 (Last 5 Matchups)")
        with st.spinner("載入近期戰況..."):
            recent_games_df = fetch_team_recent_matchups(MLB_TEAM_IDS.get(theme_team), datetime.now(tw_tz).strftime("%Y-%m-%d"))
            if not recent_games_df.empty:
                styled_recent = recent_games_df.style.map(lambda x: 'color: white; background-color: #4CAF50; font-weight: bold; text-align: center;' if x == 'W' else 'color: white; background-color: #F44336; font-weight: bold; text-align: center;', subset=['勝負 (Result)'])\
                                                     .map(lambda val: f'color: {get_team_color(val)[0]} !important; font-weight: 900 !important;', subset=['對手 (Opponent)'])\
                                                     .hide(axis='index')
                st.markdown(f"<div class='table-scroll-container'>{styled_recent.to_html()}</div>", unsafe_allow_html=True)
            else: st.info("⚠️ 尚無近況賽事資料。")
                
        st.markdown("---")
        st.markdown("### 📋 目前完整球員名單與守備位置 (Active Roster & Positions)")
        with st.spinner("載入大聯盟名單與本季精確守位..."):
            roster_df = fetch_team_roster(MLB_TEAM_IDS.get(theme_team), year)
            if not roster_df.empty:
                styled_roster = roster_df.style.map(lambda _: f'color: {p_prof_color} !important; font-weight: 700 !important;').hide(axis='index')
                st.markdown(f"<div class='table-scroll-container' style='max-height: 800px;'>{styled_roster.to_html()}</div>", unsafe_allow_html=True)
            else: st.warning("⚠️ 無法載入球員名單。")
                
        st.markdown("---")
        st.markdown("### 🏥 目前球隊傷兵名單 (Injured List)")
        with st.spinner("掃描全組織醫療與傷兵報告中 (包含小聯盟與 60天 IL)..."):
            il_df = fetch_team_injury_list(MLB_TEAM_IDS.get(theme_team))
            if not il_df.empty:
                styled_il = il_df.style.apply(lambda row: ['color: #D32F2F !important; font-weight: 900 !important;' if col == '名單狀態 (Status)' else f'color: {p_prof_color} !important; font-weight: 700 !important;' for col in row.index], axis=1).hide(axis='index')
                st.markdown(f"<div class='table-scroll-container' style='max-height: 400px;'>{styled_il.to_html()}</div>", unsafe_allow_html=True)
            else:
                st.success(f"✅ {theme_team} 目前非常健康，查無全組織傷兵紀錄！")

# ==========================================
# 📌 模式 C：全聯盟綜合分析主頁
# ==========================================
    else:
        # data 現在已經是經過「外號過濾器」篩選過後的版本了！
        data = full_data.copy()
        
        scout_metrics_l = [m for m in global_metrics if m not in ['CYC', 'SLAM', 'E']]
        data['綜合分數'] = [round(sum(get_relative_grade(data, m, row[m], p_type)[1] for m in scout_metrics_l)/len(scout_metrics_l), 3) for _, row in data.iterrows()]
        data = data.sort_values(by='綜合分數', ascending=False).reset_index(drop=True)
        data.insert(0, '同池排名', data.index + 1)
        data.insert(1, '綜合評級', data['綜合分數'].apply(score_to_grade))
        data = data.drop(columns=['綜合分數'])
            
        if data_mode == "一般賽季分析":
            if p_type == "打者":
                tab_rank, tab_recent, tab_radar, tab_scatter, tab_h2h, tab_predict, tab_mvp, tab_milb = st.tabs(["📊 排名", "🔥 近況", "📈 雷達", "🌌 散佈", "⚖️ 對決", "🔮 預測", "👑 MVP", "🌱 MiLB"])
                tab_cy = None
            else:
                tab_rank, tab_recent, tab_radar, tab_scatter, tab_h2h, tab_predict, tab_mvp, tab_cy, tab_milb = st.tabs(["📊 排名", "🔥 近況", "📈 雷達", "🌌 散佈", "⚖️ 對決", "🔮 預測", "👑 MVP", "🏆 賽揚", "🌱 MiLB"])

            with tab_rank:
                st.markdown("### 🏆 全聯盟大數據洗牌與排名")
                
                # 提示目前的外號過濾狀態
                if target_nickname:
                    st.success(f"🎭 **外號同好會啟動**：目前列表只顯示被 AI 判定為【{target_nickname}】的同類球員！")
                    
                col_sort1, col_sort2 = st.columns([1, 2])
                sortable_cols = [c for c in data.columns if c not in ['Player', 'Player_ID', 'Team', 'Position', 'Nickname', '同池排名', '綜合評級']]
                sort_metric = col_sort1.selectbox("🔍 選擇重新排序指標", sortable_cols, index=sortable_cols.index('WAR') if 'WAR' in sortable_cols else 0, key="league_rank_metric")
                
                lower_is_better_metrics = ['Chase%', 'Whiff%', 'GB%', 'K%'] if p_type == '打者' else ['ERA', 'xERA', 'WHIP', 'FIP', 'BA', 'xBA', 'BB%', 'HardHit%', 'Barrel%', 'Diff']
                sort_order = col_sort2.radio("排序方式", ["由高到低", "由低到高"], index=1 if sort_metric in lower_is_better_metrics else 0, horizontal=True, key="league_rank_order")
                
                sorted_data = data.sort_values(by=sort_metric, ascending=(sort_order == "由低到高")).reset_index(drop=True)
                sorted_data['同池排名'] = sorted_data.index + 1
                
                # 🚀 把 Nickname 欄位插入到 Position 後面顯示
                cols_order = list(sorted_data.columns)
                if 'Nickname' in cols_order:
                    cols_order.remove('Nickname')
                    pos_idx = cols_order.index('Position') if 'Position' in cols_order else 2
                    cols_order.insert(pos_idx + 1, 'Nickname')
                    sorted_data = sorted_data[cols_order]
                
                def color_rank_rows(row):
                    team_color = get_team_color(row['Team'])[0]
                    return [f'color: {team_color} !important; font-weight: 900 !important;' if col in ['Player', 'Team', 'Position', 'Nickname'] else '' for col in row.index]

                styled_df = sorted_data.drop(columns=['Player_ID'], errors='ignore').style\
                    .apply(lambda x: [highlight_elite_stats(v, x.name, p_type) for v in x], axis=0)\
                    .apply(color_rank_rows, axis=1)\
                    .map(style_grade, subset=['綜合評級']).format(STYLER_FORMATS).hide(axis='index')
                st.markdown(f"<div class='table-scroll-container'>{styled_df.to_html()}</div>", unsafe_allow_html=True)
                
            with tab_recent:
                st.markdown(f"### 🔥 {p_type}近況火熱排行榜")
                col_filt1, col_filt2 = st.columns([1, 2])
                recent_min_filter = col_filt1.slider("設定近況最少打席 (PA) 門檻", min_value=1, max_value=50, value=10, step=1, key="league_recent_filter_h") if p_type == '打者' else col_filt1.slider("設定近況最少投球局數 (IP) 門檻", min_value=1.0, max_value=30.0, value=3.0, step=0.5, key="league_recent_filter_p")
                col_filt2.caption(f"<br>以大數據掃描近期 14 天賽事，當前篩選門檻：至少 **{recent_min_filter}** {'打席' if p_type == '打者' else '局(若看牛棚RP/CL建議調低)'}。", unsafe_allow_html=True)
                    
                with st.spinner("全網大範圍撈取最新戰報中..."):
                    recent_df = fetch_recent_form_ranking(p_type)
                    if not recent_df.empty:
                        if p_type == '打者': recent_df = recent_df[recent_df['PA'] >= recent_min_filter].copy()
                        else: recent_df = recent_df[recent_df['IP_calc'] >= recent_min_filter].copy().drop(columns=['IP_calc'])
                            
                    if not recent_df.empty:
                        # 🔥 完美連動：如果選擇了外號，近況榜也會自動過濾只留下該外號的球員
                        if target_nickname:
                            recent_df = recent_df[recent_df['Player'].isin(full_data['Player'])].reset_index(drop=True)
                            
                        if not recent_df.empty:
                            recent_df['Position'] = recent_df['Player'].map(raw_data.set_index('Player')['Position'].to_dict()).fillna(recent_df['Position']).replace('Unknown', 'DH/PH')
                            cols_r = list(recent_df.columns); cols_r.remove('Position'); cols_r.insert(2, 'Position'); recent_df = recent_df[cols_r]
                            
                            c_rm, c_rp = st.columns(2)
                            sel_recent_m = c_rm.selectbox("📊 選擇近況排序指標", ['OPS', 'AVG', 'OBP', 'SLG', 'HR', 'RBI', 'PA'] if p_type == '打者' else ['ERA', 'WHIP', 'K', 'BB', 'SV', 'IP'], index=0, key="league_recent_m")
                            sel_recent_pos = c_rp.selectbox("🛡️ 篩選守備位置", ["全部 (ALL)", "DH", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF"] if p_type == '打者' else ["全部 (ALL)", "SP", "RP", "CL"], index=0, key="league_recent_pos")
                            
                            if sel_recent_pos != "全部 (ALL)": 
                                recent_df = recent_df[recent_df['Position'].astype(str).apply(lambda x: sel_recent_pos in [p.strip() for p in x.split(',')])]
                            
                            if not recent_df.empty:
                                recent_df = recent_df.sort_values(by=sel_recent_m, ascending=False if p_type == '打者' else (True if sel_recent_m in ['ERA', 'WHIP', 'BB'] else False)).reset_index(drop=True)
                                recent_df.index += 1
                                cmap = 'Reds' if p_type == '打者' else ('Blues_r' if sel_recent_m in ['ERA', 'WHIP', 'BB'] else 'Blues')
                                
                                styled_recent = recent_df.style.apply(lambda row: [f'color: {get_team_color(row["Team"])[0]} !important; font-weight: 900 !important;' if col in ['Player', 'Team', 'Position'] else '' for col in row.index], axis=1).format(STYLER_FORMATS).background_gradient(subset=[sel_recent_m], cmap=cmap).hide(axis='index')
                                st.markdown(f"<div class='table-scroll-container'>{styled_recent.to_html()}</div>", unsafe_allow_html=True)
                            else: st.warning("⚠️ 目前抓取不到符合此【守備位置】的近況數據。")
                        else: st.warning("⚠️ 這個外號的球員們在近期並沒有符合打席/局數門檻的賽事表現。")
                    else: st.warning("⚠️ 目前抓取不到符合此【局數/打席門檻】的近況數據，請嘗試往左調低拉條！")

            with tab_radar:
                st.markdown("### 🎯 選擇雷達圖比較目標")
                col_t1, col_t2 = st.columns(2)
                players_list = data['Player'].unique()
                idx2 = 1 if len(players_list) > 1 else 0
                
                target1_rad = col_t1.selectbox("雷達圖主要目標", players_list, index=0, key='league_radar_t1')
                target2_rad = col_t2.selectbox("雷達圖比較對象", players_list, index=idx2, key='league_radar_t2')
                
                p1_rad, p2_rad = data[data['Player'] == target1_rad].iloc[0], data[data['Player'] == target2_rad].iloc[0]
                t1_colors_rad, t2_colors_rad = get_team_color(p1_rad['Team']), get_team_color(p2_rad['Team'])
                p1_color_rad, p2_color_rad = t1_colors_rad[0], (t2_colors_rad[0] if t2_colors_rad[0] != t1_colors_rad[0] else t2_colors_rad[1])
                
                st.markdown("---\n### 📊 選擇顯示指標 (勾選即可動態更新)")
                default_rad_metrics = global_metrics[:5]
                if 'WAR' in global_metrics and 'WAR' not in default_rad_metrics: default_rad_metrics[-1] = 'WAR'
                
                selected_metrics = []
                cb_cols = st.columns(6)
                for i, m in enumerate(global_metrics):
                    if cb_cols[i % 6].checkbox(m, value=m in default_rad_metrics, key=f"cb_rad_{m}"): selected_metrics.append(m)
                        
                if selected_metrics:
                    res1, res2 = [get_percentile(data, m, p1_rad[m], p_type) for m in selected_metrics], [get_percentile(data, m, p2_rad[m], p_type) for m in selected_metrics]
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(r=res1, theta=selected_metrics, fill='toself', line_color=p1_color_rad, name=target1_rad))
                    if target1_rad != target2_rad: fig.add_trace(go.Scatterpolar(r=res2, theta=selected_metrics, fill='toself', line_color=p2_color_rad, name=target2_rad))
                    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 100])), showlegend=True, height=600, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, width="stretch", config={'scrollZoom': True})
                    
                    st.markdown("### 📊 指標詳細 PR 值對比")
                    stat_cols = st.columns(4)
                    for i, m in enumerate(selected_metrics):
                        pr1 = get_percentile(data, m, p1_rad[m], p_type)
                        if target1_rad != target2_rad:
                            pr2 = get_percentile(data, m, p2_rad[m], p_type)
                            stat_cols[i % 4].markdown(f"<div style='font-size:{f_size(st.session_state.font_size, 1.1)}; margin-bottom:12px; padding: 10px; background-color: white; border-radius: 8px; border: 1px solid #ddd;'><b>{m}</b><br><span style='color:{p1_color_rad}; font-weight:bold;'>■ {target1_rad}</span>: {format_metric(p1_rad[m], m)} (PR: {pr1})<br><span style='color:{p2_color_rad}; font-weight:bold;'>■ {target2_rad}</span>: {format_metric(p2_rad[m], m)} (PR: {pr2})</div>", unsafe_allow_html=True)
                        else: stat_cols[i % 4].markdown(f"<div style='font-size:{f_size(st.session_state.font_size, 1.1)}; margin-bottom:12px; padding: 10px; background-color: white; border-radius: 8px; border: 1px solid #ddd;'><b>{m}</b><br><span style='color:{p1_color_rad}; font-weight:bold;'>■ {target1_rad}</span>: {format_metric(p1_rad[m], m)} (PR: {pr1})</div>", unsafe_allow_html=True)
                else: st.warning("⚠️ 請至少勾選一項指標以顯示雷達圖！")

            with tab_scatter:
                st.markdown("### 🌌 進階數據散佈圖落點")
                plot_metrics = [c for c in data.columns if c not in ['同池排名', '綜合評級', 'Player', 'Player_ID', 'Team', 'Position', 'Nickname']]
                col_sx, col_sy = st.columns(2)
                x_col = col_sx.selectbox("X 軸", plot_metrics, index=plot_metrics.index('WAR') if 'WAR' in plot_metrics else 0, key="league_scatter_x")
                y_col = col_sy.selectbox("Y 軸", plot_metrics, index=plot_metrics.index('wRC+') if 'wRC+' in plot_metrics else (plot_metrics.index('Barrel%') if 'Barrel%' in plot_metrics else 1), key="league_scatter_y")
                
                # 🚀 散佈圖彩蛋：滑鼠停留在星星上時顯示專屬外號！
                fig = px.scatter(data, x=x_col, y=y_col, color="Team", hover_name="Player", hover_data=["Nickname"], color_discrete_map={t: get_team_color(t)[0] for t in data['Team'].unique()})
                for trace in fig.data: trace.showlegend = False
                
                fig.add_scatter(x=[p1_rad[x_col]], y=[p1_rad[y_col]], mode='markers', marker=dict(size=22, color=p1_color_rad, symbol='star', line=dict(color='white', width=2)), name=target1_rad, showlegend=True)
                if target1_rad != target2_rad: fig.add_scatter(x=[p2_rad[x_col]], y=[p2_rad[y_col]], mode='markers', marker=dict(size=18, color=p2_color_rad, symbol='star', line=dict(color='white', width=1.5)), name=target2_rad, showlegend=True)
                    
                fig.update_layout(height=650, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, width="stretch", config={'scrollZoom': True})

            with tab_h2h:
                st.markdown("### ⚔️ 選擇對決比較目標")
                col_h1, col_h2 = st.columns(2)
                h2h_t1 = col_h1.selectbox("對決主要目標", players_list, index=0, key='league_h2h_t1')
                h2h_t2 = col_h2.selectbox("對決比較對象", players_list, index=idx2, key='league_h2h_t2')
                
                p1_h2h, p2_h2h = data[data['Player'] == h2h_t1].iloc[0], data[data['Player'] == h2h_t2].iloc[0]
                st.subheader(f"⚖️ {h2h_t1} VS {h2h_t2} (全指標生死鬥)")
                for m in global_metrics:
                    col_m1, col_m2 = st.columns(2)
                    v1, v2 = p1_h2h[m], p2_h2h[m]
                    is_lower_better = m in (['Chase%', 'Whiff%', 'GB%', 'K%'] if p_type == '打者' else ['ERA', 'xERA', 'WHIP', 'FIP', 'BA', 'xBA', 'BB%', 'HardHit%', 'Barrel%', 'Diff'])
                    c1, c2 = "#00E676" if (v1 < v2 if is_lower_better else v1 > v2) else "#A9A9A9", "#00E676" if (v2 < v1 if is_lower_better else v2 > v1) else "#A9A9A9"
                    
                    col_m1.markdown(f"<div style='font-size:{f_size(st.session_state.font_size, 1.3)};'><b>{h2h_t1} - {m} ({METRIC_TW.get(m, m)})</b><br><span style='font-size:{f_size(st.session_state.font_size, 2.2)}; color:{c1}; font-weight:bold;'>{format_metric(v1, m)}</span> (評級: {get_relative_grade(data, m, v1, p_type)[0]})</div>", unsafe_allow_html=True)
                    if h2h_t1 != h2h_t2: col_m2.markdown(f"<div style='font-size:{f_size(st.session_state.font_size, 1.3)};'><b>{h2h_t2} - {m} ({METRIC_TW.get(m, m)})</b><br><span style='font-size:{f_size(st.session_state.font_size, 2.2)}; color:{c2}; font-weight:bold;'>{format_metric(v2, m)}</span> (評級: {get_relative_grade(data, m, v2, p_type)[0]})</div>", unsafe_allow_html=True)
                    st.divider()

            with tab_predict:
                st.markdown("### 📅 賽程預測中心與勝率推算")
                col_d, col_g = st.columns([1, 2])
                target_date = col_d.date_input("選擇比賽日期", datetime.now(timezone(timedelta(hours=8))).date(), key="league_predict_date")
                schedule = fetch_daily_schedule(target_date.strftime("%Y-%m-%d"))
                
                selected_game = None
                if schedule:
                    selected_matchup = col_g.selectbox("選擇預測賽事", [g['matchup'] for g in schedule], key="league_predict_game")
                    selected_game = next((g for g in schedule if g['matchup'] == selected_matchup), None)
                else:
                    col_g.warning("該日無賽事或尚未公佈")
                
                st.markdown("---")
                if selected_game:
                    away_t, home_t = selected_game['away_team'], selected_game['home_team']
                    away_p, home_p = selected_game['away_pitcher'], selected_game['home_pitcher']
                    home_t_color, away_t_color = get_team_color(home_t)[0], get_team_color(away_t)[0]
                    if home_t_color == away_t_color: away_t_color = get_team_color(away_t)[1]
                    
                    with st.spinner("加載預測引擎數據、球隊近況與近期火力..."):
                        pred_hitters, pred_pitchers = process_combined_data("打者", year, 0), process_combined_data("投手", year, 0)
                        hp_stats, ap_stats = pred_pitchers[pred_pitchers['Player'] == home_p], pred_pitchers[pred_pitchers['Player'] == away_p]
                        hh_stats, ah_stats = pred_hitters[pred_hitters['Team'] == home_t], pred_hitters[pred_hitters['Team'] == away_t]
                        
                        home_bp_era = float(pred_pitchers[(pred_pitchers['Team'] == home_t) & (pred_pitchers['Position'].isin(['RP', 'CL']))]['ERA'].replace(0, pd.NA).mean() or 4.00)
                        away_bp_era = float(pred_pitchers[(pred_pitchers['Team'] == away_t) & (pred_pitchers['Position'].isin(['RP', 'CL']))]['ERA'].replace(0, pd.NA).mean() or 4.00)
                        
                        home_bp_pitches, away_bp_pitches = fetch_bullpen_usage(home_t, target_date.strftime("%Y-%m-%d")), fetch_bullpen_usage(away_t, target_date.strftime("%Y-%m-%d"))
                        away_form, home_form = fetch_team_recent_form(MLB_TEAM_IDS.get(away_t), target_date.strftime("%Y-%m-%d")), fetch_team_recent_form(MLB_TEAM_IDS.get(home_t), target_date.strftime("%Y-%m-%d"))
                        
                        away_ops, home_ops = ah_stats['OPS'].mean() if not ah_stats.empty else 0.700, hh_stats['OPS'].mean() if not hh_stats.empty else 0.700
                        away_p_era = float(ap_stats['ERA'].replace(0, pd.NA).mean() or 4.00) if not ap_stats.empty else 4.00
                        home_p_era = float(hp_stats['ERA'].replace(0, pd.NA).mean() or 4.00) if not hp_stats.empty else 4.00
                        
                        def get_recent_pitcher_era(p_id):
                            if not p_id: return None
                            try:
                                df = fetch_player_gamelog(int(p_id), "投手", year)
                                if df is None or df.empty: return None
                                r5 = df.head(5)
                                if 'IP_calc' not in r5.columns or 'ER' not in r5.columns: return None
                                ip = r5['IP_calc'].sum()
                                er = r5['ER'].sum()
                                return float(er * 9 / ip) if ip > 0 else None
                            except Exception:
                                return None
                        
                        home_p_recent_era_val = get_recent_pitcher_era(selected_game.get('home_pitcher_id'))
                        away_p_recent_era_val = get_recent_pitcher_era(selected_game.get('away_pitcher_id'))
                        home_p_recent_era = home_p_recent_era_val if home_p_recent_era_val is not None else home_p_era
                        away_p_recent_era = away_p_recent_era_val if away_p_recent_era_val is not None else away_p_era

                        recent_hitters_df = fetch_recent_form_ranking("打者")
                        if recent_hitters_df is not None and not recent_hitters_df.empty and 'OPS' in recent_hitters_df.columns:
                            home_recent_ops_val = recent_hitters_df[recent_hitters_df['Team'] == home_t]['OPS'].mean()
                            away_recent_ops_val = recent_hitters_df[recent_hitters_df['Team'] == away_t]['OPS'].mean()
                            home_recent_ops = float(home_recent_ops_val) if pd.notna(home_recent_ops_val) else home_ops
                            away_recent_ops = float(away_recent_ops_val) if pd.notna(away_recent_ops_val) else away_ops
                        else:
                            home_recent_ops, away_recent_ops = home_ops, away_ops

                        away_win_rate = (away_form.count('W') / len(away_form)) * 100 if away_form else 50.0
                        home_win_rate = (home_form.count('W') / len(home_form)) * 100 if home_form else 50.0

                        away_strength = (away_ops * 50 + away_recent_ops * 50) + (max(0, 5 - away_p_era) * 5 + max(0, 5 - away_p_recent_era) * 5 + (ap_stats['WAR'].sum() if not ap_stats.empty else 0.0) * 5) + (sum([1 if f=='W' else -1 for f in away_form]) * 1.5)
                        home_strength = (home_ops * 50 + home_recent_ops * 50) + (max(0, 5 - home_p_era) * 5 + max(0, 5 - home_p_recent_era) * 5 + (hp_stats['WAR'].sum() if not hp_stats.empty else 0.0) * 5) + 3.0 + (sum([1 if f=='W' else -1 for f in home_form]) * 1.5)
                        total_strength = away_strength + home_strength
                        home_win_prob, away_win_prob = (50.0, 50.0) if total_strength == 0 else ((home_strength / total_strength) * 100, (away_strength / total_strength) * 100)
                        
                        st.subheader(f"🔮 {selected_game['matchup']} 戰力與勝率預測")
                        st.markdown(f'<div style="display: flex; justify-content: space-between; font-size: {f_size(st.session_state.font_size, 0.9)}; font-weight: bold; margin-bottom: 10px;"><div>客隊近況 (近5場): {" ".join(["<span style=\'background-color:#4CAF50; color:white; padding:2px 6px; border-radius:4px; font-size:0.85em; font-weight:bold;\'>W</span>" if f == "W" else "<span style=\'background-color:#F44336; color:white; padding:2px 6px; border-radius:4px; font-size:0.85em; font-weight:bold;\'>L</span>" for f in away_form]) if away_form else "無資料"}</div><div>主隊近況 (近5場): {" ".join(["<span style=\'background-color:#4CAF50; color:white; padding:2px 6px; border-radius:4px; font-size:0.85em; font-weight:bold;\'>W</span>" if f == "W" else "<span style=\'background-color:#F44336; color:white; padding:2px 6px; border-radius:4px; font-size:0.85em; font-weight:bold;\'>L</span>" for f in home_form]) if home_form else "無資料"}</div></div><div style="display: flex; height: 40px; border-radius: 8px; overflow: hidden; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"><div style="width: {away_win_prob}%; background-color: {away_t_color}; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: {f_size(st.session_state.font_size, 1.6)};">{away_t} {away_win_prob:.1f}%</div><div style="width: {home_win_prob}%; background-color: {home_t_color}; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: {f_size(st.session_state.font_size, 1.6)};">{home_t} {home_win_prob:.1f}%</div></div>', unsafe_allow_html=True)
                        
                        def draw_comparison_bar(label, away_val, home_val, is_int=False, lower_is_better=False, is_pct=False):
                            if away_val is None or pd.isna(away_val): away_val = 0
                            if home_val is None or pd.isna(home_val): home_val = 0
                            
                            away_val, home_val = float(away_val), float(home_val)
                            
                            if away_val == home_val:
                                away_adv, home_adv = False, False
                            elif lower_is_better:
                                away_adv, home_adv = away_val < home_val, home_val < away_val
                            else:
                                away_adv, home_adv = away_val > home_val, home_val > away_val
                                
                            muted_color = "#E0E0E0"
                            a_bar_color = away_t_color if away_adv else (muted_color if home_adv else away_t_color)
                            h_bar_color = home_t_color if home_adv else (muted_color if away_adv else home_t_color)
                            
                            a_text_color = away_t_color if away_adv else ("#B0BEC5" if home_adv else "#555")
                            h_text_color = home_t_color if home_adv else ("#B0BEC5" if away_adv else "#555")
                            
                            a_weight = "900" if away_adv else "500"
                            h_weight = "900" if home_adv else "500"
                            a_size = f_size(st.session_state.font_size, 1.25) if away_adv else f_size(st.session_state.font_size, 0.95)
                            h_size = f_size(st.session_state.font_size, 1.25) if home_adv else f_size(st.session_state.font_size, 0.95)
                            
                            if is_pct: fmt = "{:.0f}%"
                            elif is_int: fmt = "{:.0f}"
                            else: fmt = "{:.3f}" if "OPS" in label else "{:.2f}"
                                
                            a_str, h_str = fmt.format(away_val), fmt.format(home_val)
                            
                            sum_val = away_val + home_val
                            if sum_val == 0:
                                a_pct, h_pct = 50, 50
                            else:
                                if lower_is_better:
                                    a_pct = (home_val / sum_val) * 100
                                    h_pct = (away_val / sum_val) * 100
                                else:
                                    a_pct = (away_val / sum_val) * 100
                                    h_pct = (home_val / sum_val) * 100
                                    
                            if lower_is_better and sum_val > 0:
                                if away_val == 0: a_pct, h_pct = 95, 5
                                if home_val == 0: a_pct, h_pct = 5, 95
                                
                            a_icon = "🔥 " if away_adv else ""
                            h_icon = " 🔥" if home_adv else ""
                                
                            return f'''
                            <div style="margin-bottom: 16px; padding: 12px 15px; background-color: white; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border: 1px solid #f0f0f0;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 8px; align-items: center;">
                                    <span style="color: {a_text_color}; font-weight: {a_weight}; font-size: {a_size}; transition: all 0.3s;">{a_icon}{a_str}</span>
                                    <span style="color: #333; font-weight: bold; font-size: {f_size(st.session_state.font_size, 0.95)}; text-align: center; flex: 1;">{label}</span>
                                    <span style="color: {h_text_color}; font-weight: {h_weight}; font-size: {h_size}; transition: all 0.3s;">{h_str}{h_icon}</span>
                                </div>
                                <div style="display: flex; height: 14px; border-radius: 7px; overflow: hidden; background-color: #f5f5f5;">
                                    <div style="width: {a_pct}%; background-color: {a_bar_color}; transition: all 0.5s;"></div>
                                    <div style="width: {h_pct}%; background-color: {h_bar_color}; transition: all 0.5s;"></div>
                                </div>
                            </div>
                            '''

                        st.markdown(f"<div style='font-size:{f_size(st.session_state.font_size, 1.2)}; font-weight:bold; margin-bottom: 15px; text-align:center;'>⚖️ 核心戰力對比拔河 (優勢方點亮專屬隊色)</div>", unsafe_allow_html=True)
                        
                        bars_html = (
                            draw_comparison_bar(f"先發投手本季指標 (ERA)", away_p_era, home_p_era, lower_is_better=True) +
                            draw_comparison_bar(f"先發投手近況 (近 5 場 ERA)", away_p_recent_era, home_p_recent_era, lower_is_better=True) +
                            draw_comparison_bar(f"打線本季破壞力 (OPS)", away_ops, home_ops) +
                            draw_comparison_bar(f"打線近況火燙度 (近期 OPS)", away_recent_ops, home_recent_ops) +
                            draw_comparison_bar("球隊近況氣勢 (近 5 場勝率)", away_win_rate, home_win_rate, is_pct=True) +
                            draw_comparison_bar("牛棚疲勞度 (近 2 日消耗球數)", away_bp_pitches, home_bp_pitches, is_int=True, lower_is_better=True)
                        )
                        st.markdown(bars_html, unsafe_allow_html=True)
                        
                        h_span = f"<span style='color:{home_t_color}; font-weight:900;'>{home_t}</span>"
                        a_span = f"<span style='color:{away_t_color}; font-weight:900;'>{away_t}</span>"
                        
                        adv_str = "<span style='color:#00E676; font-weight:900; background-color:rgba(0,230,118,0.1); padding:2px 6px; border-radius:4px;'>佔優</span>"
                        dis_str = "<span style='color:#FF5252; font-weight:900; background-color:rgba(255,82,82,0.1); padding:2px 6px; border-radius:4px;'>劣勢</span>"
                        warn_str = "<span style='color:#FF5252; font-weight:900; animation: blink 1s infinite;'>疲勞警告</span>"

                        p_adv = f"➔ {h_span} {adv_str}" if home_p_era < away_p_era else (f"➔ {a_span} {adv_str}" if away_p_era < home_p_era else "➔ 平分秋色")
                        pr_adv = f"➔ {h_span} {adv_str}" if home_p_recent_era < away_p_recent_era else (f"➔ {a_span} {adv_str}" if away_p_recent_era < home_p_recent_era else "➔ 平分秋色")
                        h_adv = f"➔ {h_span} {adv_str}" if home_ops > away_ops else (f"➔ {a_span} {adv_str}" if away_ops > home_ops else "➔ 平分秋色")
                        hr_adv = f"➔ {h_span} {adv_str}" if home_recent_ops > away_recent_ops else (f"➔ {a_span} {adv_str}" if away_recent_ops > home_recent_ops else "➔ 平分秋色")
                        f_adv = f"➔ {h_span} {adv_str}" if home_win_rate > away_win_rate else (f"➔ {a_span} {adv_str}" if away_win_rate > home_win_rate else "➔ 平分秋色")

                        reasoning = [f"⚾ **先發投手本季戰力**：{h_span} (ERA {home_p_era:.2f}) vs {a_span} (ERA {away_p_era:.2f}) {p_adv}"]
                        reasoning.append(f"🎯 **先發投手近況 (近5場)**：{h_span} (ERA {home_p_recent_era:.2f}) vs {a_span} (ERA {away_p_recent_era:.2f}) {pr_adv}")
                        reasoning.append(f"🏏 **打線本季破壞力**：{h_span} (OPS {home_ops:.3f}) vs {a_span} (OPS {away_ops:.3f}) {h_adv}")
                        reasoning.append(f"🔥 **打線近況火燙度 (近期)**：{h_span} (OPS {home_recent_ops:.3f}) vs {a_span} (OPS {away_recent_ops:.3f}) {hr_adv}")
                        reasoning.append(f"📈 **球隊近況氣勢 (近5場)**：{h_span} (勝率 {home_win_rate:.0f}%) vs {a_span} (勝率 {away_win_rate:.0f}%) {f_adv}")
                        reasoning.append(f"🛡️ **牛棚狀況評估 (近2日)**：{h_span} 消耗 {home_bp_pitches} 球 vs {a_span} 消耗 {away_bp_pitches} 球。")
                        
                        if home_bp_pitches > 80: reasoning.append(f"⚠️ **{warn_str}**：{h_span} 牛棚負荷過大，後援戰局處於 {dis_str}！")
                        if away_bp_pitches > 80: reasoning.append(f"⚠️ **{warn_str}**：{a_span} 牛棚負荷過大，後援戰局處於 {dis_str}！")
                        
                        with st.expander("🧠 點擊查看詳細勝率預測邏輯與戰力解析", expanded=True):
                            for r in reasoning: st.markdown(f"<div style='font-size:{f_size(st.session_state.font_size, 1.1)}; margin-bottom:12px; line-height: 1.5;'>{r}</div>", unsafe_allow_html=True)
                        
                        st.markdown("---")
                        for title, t_color, hit_stats, pit_stats, pitcher, pitcher_id in [(f"⚔️ 上半局：{away_t} (客隊打線) VS {home_p} (主隊先發)", home_t_color, ah_stats, hp_stats, home_p, selected_game['home_pitcher_id']), (f"⚔️ 下半局：{home_t} (主隊打線) VS {away_p} (客隊先發)", away_t_color, hh_stats, ap_stats, away_p, selected_game['away_pitcher_id'])]:
                            st.markdown(f"<h3 style='color:{t_color}'>{title}</h3>", unsafe_allow_html=True)
                            if not pit_stats.empty: st.markdown(f"<div class='table-scroll-container'>{pit_stats.drop(columns=['Player_ID']).style.format(STYLER_FORMATS).hide(axis='index').to_html()}</div>", unsafe_allow_html=True)
                            else: st.warning(f"查無先發 {pitcher} 的本季數據")
                            
                            hit_stats = hit_stats.sort_values(by='OPS', ascending=False)
                            if pitcher_id and not hit_stats.empty:
                                bvp_df = fetch_bvp_data(pitcher_id, hit_stats['Player_ID'].tolist())
                                if not bvp_df.empty: st.markdown(f"<div style='font-size:{f_size(st.session_state.font_size, 1.5)}; font-weight:bold; margin-top:10px; margin-bottom:10px;'>🔥 生涯對戰紀錄 (BvP)</div><div class='table-scroll-container'>{bvp_df.style.format(STYLER_FORMATS).hide(axis='index').to_html()}</div>", unsafe_allow_html=True)
                            if not hit_stats.empty: st.markdown(f"<div style='font-size:{f_size(st.session_state.font_size, 1.5)}; font-weight:bold; margin-top:10px; margin-bottom:10px;'>**打線本季表現**</div><div class='table-scroll-container'>{hit_stats.drop(columns=['Player_ID']).style.format(STYLER_FORMATS).hide(axis='index').to_html()}</div>", unsafe_allow_html=True)
                            if title.startswith("⚔️ 上半局"): st.divider()

            with tab_mvp:
                st.subheader(f"👑 {year} 賽季 MVP 預測排行榜")
                with st.spinner("運算 MVP 積分中..."):
                    mvp_df = data.copy()
                    if not mvp_df.empty:
                        if p_type == '打者':
                            mvp_df['MVP_Index'] = (mvp_df['WAR'] * 20 + mvp_df['OPS'] * 50 + mvp_df['wRC+'] * 0.5).round(1)
                            keep_cols = ['Player', 'Team', 'Position', 'Nickname', 'WAR', 'OPS', 'wRC+', 'HR', 'MVP_Index']
                        else:
                            mvp_df['MVP_Index'] = (mvp_df['WAR'] * 25 + mvp_df['K%'] * 1.5 - mvp_df['ERA'] * 10).round(1)
                            keep_cols = ['Player', 'Team', 'Position', 'Nickname', 'WAR', 'ERA', 'WHIP', 'K%', 'MVP_Index']
                        mvp_top = mvp_df.sort_values('MVP_Index', ascending=False).head(15).reset_index(drop=True)
                        mvp_top.index += 1
                        st.markdown(f"<div class='table-scroll-container'>{mvp_top[keep_cols].style.format(STYLER_FORMATS).background_gradient(subset=['MVP_Index'], cmap='YlOrRd').to_html()}</div>", unsafe_allow_html=True)
            
            if p_type == "投手" and tab_cy is not None:
                with tab_cy:
                    st.subheader(f"🏆 {year} 賽季 賽揚獎 (Cy Young) 預測排行榜")
                    with st.spinner("運算賽揚積分中..."):
                        cy_df = data.copy()
                        if not cy_df.empty:
                            cy_df['Cy_Index'] = (cy_df['WAR'] * 15 + cy_df['K%'] * 1.2 - cy_df['ERA'] * 8 - cy_df['WHIP'] * 10).round(1)
                            cy_top = cy_df.sort_values('Cy_Index', ascending=False).head(15).reset_index(drop=True)
                            cy_top.index += 1
                            st.markdown(f"<div class='table-scroll-container'>{cy_top[['Player', 'Team', 'Position', 'Nickname', 'WAR', 'ERA', 'WHIP', 'K%', 'IP', 'Cy_Index']].style.format(STYLER_FORMATS).background_gradient(subset=['Cy_Index'], cmap='Blues').to_html()}</div>", unsafe_allow_html=True)

            with tab_milb:
                st.subheader(f"🌱 小聯盟潛力 {p_type} 農場新秀報告 (MiLB Top Prospects)")
                lvl_map = {"AAA (3A)": 11, "AA (2A)": 12, "High-A": 13, "Single-A": 14}
                milb_level = st.selectbox("選擇小聯盟層級", list(lvl_map.keys()), key="league_milb_level")
                
                with st.spinner(f"撈取 {milb_level} {p_type} 數據中..."):
                    milb_df = fetch_milb_stats(year, lvl_map[milb_level], p_type)
                    if not milb_df.empty:
                        col_t, col_s, col_o = st.columns([1, 1, 1])
                        sel_team = col_t.selectbox("選擇大聯盟母隊", ["全聯盟"] + sorted(milb_df['大聯盟母隊 (MLB Team)'].unique()), key="league_milb_team")
                        sort_cols = [c for c in milb_df.columns if c not in ['球員 (Player)', '大聯盟母隊 (MLB Team)']]
                        sel_sort = col_s.selectbox("自訂排序指標", sort_cols, index=sort_cols.index('OPS') if p_type == '打者' and 'OPS' in sort_cols else (sort_cols.index('ERA') if p_type == '投手' and 'ERA' in sort_cols else 0), key="league_milb_sort")
                        lower_is_better_milb = ['ERA', 'WHIP', 'L'] if p_type == '投手' else []
                        sel_order = col_o.radio("排序方式 ", ["由高到低", "由低到高"], index=1 if sel_sort in lower_is_better_milb else 0, horizontal=True, key="league_milb_order")
                        
                        if sel_team != "全聯盟": milb_df = milb_df[milb_df['大聯盟母隊 (MLB Team)'] == sel_team]
                        milb_df = milb_df.sort_values(by=sel_sort, ascending=(sel_order == "由低到高")).head(20).reset_index(drop=True)
                        milb_df.index += 1
                        
                        cmap = 'Greens' if p_type == '打者' else 'Blues'
                        if sel_sort in lower_is_better_milb: cmap = 'Blues_r' if p_type == '投手' else 'Greens_r'
                        st.markdown(f"<div class='table-scroll-container'>{milb_df.style.format(STYLER_FORMATS).background_gradient(subset=[sel_sort], cmap=cmap).to_html()}</div>", unsafe_allow_html=True)
                    else:
                        st.warning(f"⚠️ 目前查無 {year} 賽季 {milb_level} 的 {p_type} 數據。")

        # 🔮 分流 B：Fantasy 夢幻棒球獨立大戰情室
        else:
            tab_weekly, tab_season = st.tabs(["🔥 近七日狀態結算排行 (包含 SLAM/QS進階成就)", "📊 本季累積數據篩選 (Season)"])
            
            with tab_weekly:
                st.caption("透過官方 API 直接抓取近七日累積數據，支援判定「滿貫砲 (SLAM)」與「優質先發 (QS)」等進階成就！")
                with st.spinner("掃描近七日全聯盟逐場日誌，精算 Fantasy 積分中..."):
                    weekly_df = fetch_weekly_fantasy_ranking(p_type)
                    if not weekly_df.empty:
                        # 🔥 完美連動：在 Fantasy 近七日戰情室中，依然支援外號篩選！
                        if target_nickname:
                            weekly_df = weekly_df[weekly_df['Player'].isin(full_data['Player'])].reset_index(drop=True)
                            
                        if not weekly_df.empty:
                            weekly_df['Position'] = weekly_df['Player'].map(raw_data.set_index('Player')['Position'].to_dict()).fillna(weekly_df['Position'])
                            weekly_df['Nickname'] = weekly_df['Player'].map(raw_data.set_index('Player')['Nickname'].to_dict()).fillna("")
                            
                            col_w1, col_w2, col_w3 = st.columns([1, 1, 1])
                            sel_week_pos = col_w1.selectbox("🛡️ 篩選本週守備位置", ["全部 (ALL)", "DH", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF"] if p_type == '打者' else ["全部 (ALL)", "SP", "RP", "CL"], index=0, key="league_fan_week_pos")
                            sort_week_metric = col_w2.selectbox("📊 選擇排序指標", ["Fan_Pts", "Avg_Pts"], index=0, key="league_fan_week_sort")
                            sort_week_order = col_w3.radio("排序方式", ["由高到低", "由低到高"], index=0, horizontal=True, key="league_fan_week_order")
                            
                            if sel_week_pos != "全部 (ALL)": 
                                weekly_df = weekly_df[weekly_df['Position'].astype(str).apply(lambda x: sel_week_pos in [p.strip() for p in x.split(',')])]
                            
                            weekly_df = weekly_df.sort_values(by=sort_week_metric, ascending=(sort_week_order == "由低到高")).reset_index(drop=True)
                            weekly_df.index += 1
                            
                            # 插入 Nickname 欄位
                            cols_w = list(weekly_df.columns); cols_w.remove('Nickname'); pos_idx_w = cols_w.index('Position') if 'Position' in cols_w else 2
                            cols_w.insert(pos_idx_w + 1, 'Nickname')
                            weekly_df = weekly_df[cols_w]
                            
                            styled_weekly = weekly_df.style.apply(lambda row: [f'color: black !important; font-weight: 900 !important; font-size: 1.15em;' if col in ['Fan_Pts', 'Avg_Pts'] else (f'color: {get_team_color(row["Team"])[0]} !important; font-weight: 900 !important;' if col in ['Player', 'Team', 'Position', 'Nickname'] else '') for col in row.index], axis=1).format(STYLER_FORMATS).hide(axis='index')
                            st.markdown(f"<div class='table-scroll-container'>{styled_weekly.to_html()}</div>", unsafe_allow_html=True)
                        else: st.warning("⚠️ 這個外號的球員們在近七日沒有可結算的 Fantasy 分數。")
                    else: st.warning("⚠️ 查無近七日比賽資料。")
                    
            with tab_season:
                st.caption("完整提取夢幻棒球常用的累積計分項目！")
                fantasy_cols = ['Player', 'Team', 'Position', 'Nickname', 'Fantasy_Score', 'R', 'H', '1B', '2B', '3B', 'HR', 'RBI', 'SB', 'BB', 'HBP', 'K', 'E', 'CYC', 'SLAM'] if p_type == '打者' else ['Player', 'Team', 'Position', 'Nickname', 'Fantasy_Score', 'W', 'L', 'SHO', 'SV', 'OUT', 'H', 'ER', 'HR', 'BB', 'HBP', 'K', 'WP', 'HLD', 'QS', 'BSV']
                fantasy_df = data[fantasy_cols].copy()
                
                col_f1, col_f2 = st.columns([1, 1])
                sort_f_metric = col_f1.selectbox("📊 選擇排序指標 (Season Fantasy)", fantasy_cols[4:], index=0, key='league_fan_season_metric')
                sel_fantasy_pos = col_f2.selectbox("🛡️ 篩選守備位置 (Season Fantasy)", ["全部 (ALL)", "DH", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF"] if p_type == '打者' else ["全部 (ALL)", "SP", "RP", "CL"], index=0, key='league_fan_season_pos')
                
                if sel_fantasy_pos != "全部 (ALL)": 
                    fantasy_df = fantasy_df[fantasy_df['Position'].astype(str).apply(lambda x: sel_fantasy_pos in [p.strip() for p in x.split(',')])]
                if sort_f_metric not in ['CYC', 'SLAM']: 
                    fantasy_df = fantasy_df.sort_values(by=sort_f_metric, ascending=True if sort_f_metric in ['L', 'E', 'ER', 'H', 'BB', 'BSV', 'WP'] else False).reset_index(drop=True)
                    
                if not fantasy_df.empty:
                    fantasy_df.index += 1
                    styled_fan = fantasy_df.style.apply(lambda row: [f'color: black !important; font-weight: 900 !important; font-size: 1.1em;' if col == 'Fantasy_Score' else (f'color: {get_team_color(row["Team"])[0]} !important; font-weight: 900 !important;' if col in ['Player', 'Team', 'Position', 'Nickname'] else '') for col in row.index], axis=1).format(STYLER_FORMATS).hide(axis='index')
                    st.markdown(f"<div class='table-scroll-container'>{styled_fan.to_html()}</div>", unsafe_allow_html=True)
                else: st.warning("⚠️ 目前抓取不到符合此【外號/守備位置】的 Fantasy 數據。")