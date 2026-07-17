# ⚾ MLB 終極球探與數據預測系統 (MLB Ultimate Scouting & Prediction System)

這是一個基於 **Python** 與 **Streamlit** 開發的大聯盟棒球綜合數據分析平台。系統整合了傳統數據、Statcast 進階擊球數據，並內建了 **機器學習預測引擎 (Machine Learning)** 與 **非同步爬蟲架構 (Asyncio)**，為球迷、Fantasy Baseball 玩家及數據分析師提供全方位的戰情室。

## ✨ 核心亮點功能 (Key Features)

* **🚀 非同步高速爬蟲架構**：整合 `aiohttp` 與 `asyncio`，併發獲取大聯盟 API 與 10 年歷史守備資料，解決 N+1 查詢瓶頸，實現光速載入。
* **🧠 AI 機器學習勝率預測**：導入 `scikit-learn` 隨機森林 (Random Forest) 模型。綜合兩隊打線 OPS、先發 ERA、牛棚疲勞度與近期動能，產出科學化的賽事勝率預測與特徵重要性 (Feature Importance) 分析。
* **🦄 Fantasy Baseball 深度結算**：內建 Fantasy 積分演算法，支援查看全賽季累積積分，並可精確抓取「近 7 天」的單場進階成就（如完全打擊 CYC、滿貫砲 SLAM、優質先發 QS）。
* **🏥 組織級傷兵名單追蹤**：雙管齊下掃描大聯盟與小聯盟 (MiLB) 的 40 人名單與 Full Roster，結合精準的中文翻譯字典，不漏接任何一位隱藏傷兵的真實病歷。
* **📊 全方位資料視覺化**：結合 `pybaseball` 獲取 Savant 擊球初速 (EV)、Barrel%、wRC+ 等進階數據，並使用 `Plotly` 繪製雷達圖、散佈圖與生涯數據走勢。

## 🛠️ 技術棧 (Tech Stack)

* **前端框架**: Streamlit
* **資料處理**: Pandas, NumPy
* **非同步網路請求**: Requests, aiohttp, asyncio
* **視覺化圖表**: Plotly (Express, Graph Objects)
* **機器學習**: Scikit-Learn (RandomForestClassifier)
* **棒球進階數據**: Pybaseball (Statcast)

## 🚀 如何在本地端運行 (How to Run Locally)

1. **複製此專案 (Clone the repository)**
   ```bash
   git clone [https://github.com/你的GitHub帳號/MLB_Scout_System.git](https://github.com/neil168178-arch/MLB_Scout_System.git)
   cd MLB_Scout_System