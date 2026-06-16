# ml_predictor.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import streamlit as st

@st.cache_resource
def train_ml_model():
    """
    建立並訓練機器學習預測模型 (Random Forest Classifier)。
    系統啟動時會自動進行一次訓練，並將模型快取於記憶體中。
    """
    # 1. 產生模擬大聯盟數據分佈的訓練資料 (Training Data)
    np.random.seed(42)
    n_samples = 5000  # 模擬 5000 場賽事

    # 模擬主客場數據分佈
    home_ops = np.random.normal(0.720, 0.050, n_samples)
    home_sp_era = np.random.normal(4.00, 1.00, n_samples)
    home_bp_fatigue = np.random.normal(60, 20, n_samples)
    home_momentum = np.random.normal(0, 2, n_samples)

    away_ops = np.random.normal(0.720, 0.050, n_samples)
    away_sp_era = np.random.normal(4.00, 1.00, n_samples)
    away_bp_fatigue = np.random.normal(60, 20, n_samples)
    away_momentum = np.random.normal(0, 2, n_samples)

    # 2. 特徵工程 (Feature Engineering) - 計算兩隊戰力落差
    ops_diff = home_ops - away_ops
    era_diff = away_sp_era - home_sp_era # 正值代表客隊 ERA 較高 (主隊投手較強)
    fatigue_diff = away_bp_fatigue - home_bp_fatigue # 正值代表客隊牛棚較疲勞
    momentum_diff = home_momentum - away_momentum

    X = pd.DataFrame({
        'ops_diff': ops_diff,
        'era_diff': era_diff,
        'fatigue_diff': fatigue_diff,
        'momentum_diff': momentum_diff
    })

    # 3. 建立目標變數 y (1 = 主場勝, 0 = 客場勝)
    # 利用 Logistic 函數模擬真實棒球勝率權重 (包含主場優勢)
    logit = (ops_diff * 12.0) + (era_diff * 0.6) + (fatigue_diff * 0.015) + (momentum_diff * 0.25) + 0.15
    prob = 1 / (1 + np.exp(-logit))
    y = (np.random.rand(n_samples) < prob).astype(int)

    # 4. 訓練隨機森林模型
    model = RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42, n_jobs=-1)
    model.fit(X, y)

    return model

def predict_game(model, home_ops, away_ops, home_sp_era, away_sp_era, home_bp, away_bp, home_mom, away_mom):
    """
    將當日即時抓取的兩隊數據送入 ML 模型進行勝率預測
    """
    X_test = pd.DataFrame({
        'ops_diff': [home_ops - away_ops],
        'era_diff': [away_sp_era - home_sp_era],
        'fatigue_diff': [away_bp - home_bp],
        'momentum_diff': [home_mom - away_mom]
    })

    # 取得預測機率
    probs = model.predict_proba(X_test)[0]
    away_win_prob = probs[0] * 100
    home_win_prob = probs[1] * 100

    # 取得模型特徵重要性 (用來解釋給使用者聽)
    feature_importance = model.feature_importances_
    
    return home_win_prob, away_win_prob, feature_importance