import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# ==========================================
# 0. 完美兼容：安全支持 VS Code 运行按钮
# ==========================================
if __name__ == '__main__':
    from streamlit import runtime
    from streamlit.web import cli as stcli
    if not runtime.exists():
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())

# ==========================================
# 1. 页面全局配置
# ==========================================
st.set_page_config(
    page_title="TK Quant Terminal", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. 国际化与双模词典 (i18n & Dual Mode)
# ==========================================
LANG_DICT = {
    "CN": {
        "PRO": {
            "sb_title": "### 📊 TK Quant Terminal",
            "sb_caption": "机构级量化与精算风控引擎 | **By Kai Teng**",
            "sb_settings": "⚙️ 引擎参数设置",
            "sb_pool": "自选监控池 (逗号分隔):",
            "sb_bm": "大盘风控锚点 (Benchmark):",
            "sb_actuarial": "#### 💰 精算与资金管理",
            "sb_capital": "模拟账户本金 ($):",
            "sb_winrate": "系统预期胜率 (Win Rate):",
            "sb_wlratio": "盈亏赔率 (W/L Ratio):",
            "sb_btn": "🚀 启动 TK 云端量化引擎",
            "m_title": "📊 宏微观双周期量化决策矩阵",
            "m_subtitle": "Powered by **TK's Actuarial & Quant Architecture**",
            "m_fetching": "TK 引擎正在调动全球网络节点拉取数据...",
            "m_bm_bull": "**宏观风控阀**: 🟢 {0} 大盘处于多头结构，系统风险敞口正常开启。",
            "m_bm_bear": "**宏观风控阀**: 🔴 {0} 大盘跌破 20 日均线生命线，全局风控拦截开启！",
            "m_calc": "正在进行多维矩阵与量价测算: {0}...",
            "m_nodata": "无法获取 {0} 的有效数据。",
            "m_report": "🏷️ {0} 深度研报切片",
            "m_price": "最新成交价",
            "m_vwap": "机构成本 (VWAP)",
            "m_zscore": "统计动量 (Z-Score)",
            "m_kelly": "Kelly 目标仓位",
            "m_var": "95% 单日 VaR",
            "m_chart_title": "{0} 最近 60 周期微观结构",
            "m_ai_decision": "#### 🤖 算法决断",
            "m_logic": "逻辑",
            "m_risk_params": "#### 🛡️ 精算风控参数",
            "m_stop_loss": "防守止损位",
            "m_kelly_ratio": "Kelly 比例",
            "m_var_exp": "VaR 尾部敞口",
            "m_waiting": "👈 请 in 左侧侧边栏设置风控参数，并点击 **启动 TK 云端量化引擎**。",
            "a_hold": "HOLD (震荡观望)",
            "a_hold_r": "动能交织，方向未明",
            "a_buy": "STRONG BUY (量价突破)",
            "a_buy_r": "大盘安全，突破机构 VWAP 成本线",
            "a_block": "RISK BLOCKED (大盘拦截)",
            "a_block_r": "触发被动风控",
            "a_rev": "REVERSION BUY (极值回归)",
            "a_rev_r": "价格严重超跌，均值回归需求强烈",
            "a_sell": "PANIC SELL (破位抛售)",
            "a_sell_r": "技术面崩塌，共振下杀逃顶"
        },
        "BASIC": {
            "sb_title": "### 📊 TK 智能投资助手",
            "sb_caption": "简单易懂的 AI 炒股辅助工具 | **By Kai Teng**",
            "sb_settings": "⚙️ 投资偏好设置",
            "sb_pool": "关注的股票 (输入代码，逗号隔开):",
            "sb_bm": "参考的大盘 (如 SPY 代表美股):",
            "sb_actuarial": "#### 💰 资金与安全保护",
            "sb_capital": "准备投资的总金额 ($):",
            "sb_winrate": "你觉得这套方法的准头 (胜率):",
            "sb_wlratio": "赚一次和亏一次的比例 (盈亏比):",
            "sb_btn": "🚀 开始 AI 智能分析",
            "m_title": "📊 智能股票体检报告",
            "m_subtitle": "利用大数据帮你把脉股票走势",
            "m_fetching": "正在从网上拉取最新的股票行情...",
            "m_bm_bull": "**大盘环境**: 🟢 现在 {0} 大盘整体趋势向上，是个可以考虑入场的好时机。",
            "m_bm_bear": "**大盘环境**: 🔴 现在 {0} 大盘整体在跌，系统建议暂时管住手，不买股票！",
            "m_calc": "正在诊断股票: {0}...",
            "m_nodata": "找不到 {0} 的数据，请检查代码拼写。",
            "m_report": "🏷️ {0} 智能诊断结果",
            "m_price": "当前价格",
            "m_vwap": "主力平均成本",
            "m_zscore": "短期爆发力",
            "m_kelly": "建议买入金额",
            "m_var": "最坏可能亏损 (每天)",
            "m_chart_title": "{0} 最近几小时的走势图",
            "m_ai_decision": "#### 🤖 AI 给你的建议",
            "m_logic": "原因",
            "m_risk_params": "#### 🛡️ 安全保护建议",
            "m_stop_loss": "建议止损价 (跌破就跑)",
            "m_kelly_ratio": "建议投入资金占比",
            "m_var_exp": "若买入，每天最多可能亏掉",
            "m_waiting": "👈 请在左边设置好你的偏好，然后点击 **开始 AI 智能分析**。",
            "a_hold": "保持观望 (什么都不做)",
            "a_hold_r": "现在涨跌看不清，不要瞎折腾。",
            "a_buy": "可以买入 (看涨)",
            "a_buy_r": "大盘环境很好，而且这只股票冲破了主力成本价！",
            "a_block": "禁止买入 (大盘太差)",
            "a_block_r": "虽然股票看着不错，但大盘在跌，安全第一。",
            "a_rev": "抄底机会 (博反弹)",
            "a_rev_r": "跌得太多了，随时可能报复性反弹。",
            "a_sell": "立刻卖出 (危险)",
            "a_sell_r": "情况不妙，大家都在抛售，赶紧避险！"
        }
    },
    "EN": {
        "PRO": {
            "sb_title": "### 📊 TK Quant Terminal",
            "sb_caption": "Institutional Quant & Actuarial Engine | **By Kai Teng**",
            "sb_settings": "⚙️ Engine Parameters",
            "sb_pool": "Watchlist (comma separated):",
            "sb_bm": "Macro Benchmark:",
            "sb_actuarial": "#### 💰 Actuarial & Capital Management",
            "sb_capital": "Simulated Capital ($):",
            "sb_winrate": "Expected Win Rate:",
            "sb_wlratio": "Win/Loss Ratio:",
            "sb_btn": "🚀 Launch TK Cloud Engine",
            "m_title": "📊 Macro-Micro Dual Cycle Quant Matrix",
            "m_subtitle": "Powered by **TK's Actuarial & Quant Architecture**",
            "m_fetching": "TK Engine fetching data from global nodes...",
            "m_bm_bull": "**Macro Risk Valve**: 🟢 {0} is in a bull structure, risk exposure enabled.",
            "m_bm_bear": "**Macro Risk Valve**: 🔴 {0} fell below 20-MA, global risk block engaged!",
            "m_calc": "Calculating multidimensional matrix for: {0}...",
            "m_nodata": "Cannot fetch valid data for {0}.",
            "m_report": "🏷️ {0} Deep Report Profile",
            "m_price": "Latest Price",
            "m_vwap": "Inst. Cost (VWAP)",
            "m_zscore": "Stat Momentum (Z-Score)",
            "m_kelly": "Kelly Target Pos",
            "m_var": "95% Daily VaR",
            "m_chart_title": "{0} Last 60 Periods Microstructure",
            "m_ai_decision": "#### 🤖 AI Decision",
            "m_logic": "Logic",
            "m_risk_params": "#### 🛡️ Actuarial Risk Params",
            "m_stop_loss": "Stop Loss",
            "m_kelly_ratio": "Kelly Ratio",
            "m_var_exp": "VaR Tail Exposure",
            "m_waiting": "👈 Please configure parameters in the sidebar and click **Launch**.",
            "a_hold": "HOLD",
            "a_hold_r": "Mixed momentum, trend unclear",
            "a_buy": "STRONG BUY",
            "a_buy_r": "Macro safe, breaks above Inst. VWAP",
            "a_block": "RISK BLOCKED",
            "a_block_r": "Passive risk control triggered",
            "a_rev": "REVERSION BUY",
            "a_rev_r": "Oversold, strong mean reversion demand",
            "a_sell": "PANIC SELL",
            "a_sell_r": "Technical breakdown, panic sell"
        },
        "BASIC": {
            "sb_title": "### 📊 TK Smart Investor",
            "sb_caption": "Easy-to-use AI Stock Assistant | **By Kai Teng**",
            "sb_settings": "⚙️ Investment Settings",
            "sb_pool": "Stocks to watch (comma separated):",
            "sb_bm": "Market Reference (e.g. SPY):",
            "sb_actuarial": "#### 💰 Money & Safety",
            "sb_capital": "Total Money to Invest ($):",
            "sb_winrate": "Your estimated win rate:",
            "sb_wlratio": "Reward vs Risk ratio:",
            "sb_btn": "🚀 Start AI Analysis",
            "m_title": "📊 Smart Stock Health Report",
            "m_subtitle": "Using big data to check your stocks",
            "m_fetching": "Fetching the latest market data...",
            "m_bm_bull": "**Market Environment**: 🟢 The {0} market is going up. Safe to invest.",
            "m_bm_bear": "**Market Environment**: 🔴 The {0} market is dropping. Better to wait and do nothing!",
            "m_calc": "Diagnosing stock: {0}...",
            "m_nodata": "Cannot find data for {0}. Check spelling.",
            "m_report": "🏷️ {0} AI Diagnosis Result",
            "m_price": "Current Price",
            "m_vwap": "Average Market Cost",
            "m_zscore": "Short-term Strength",
            "m_kelly": "Suggested Investment",
            "m_var": "Max Expected Daily Loss",
            "m_chart_title": "{0} Recent Price Trend",
            "m_ai_decision": "#### 🤖 AI Suggestion",
            "m_logic": "Reason",
            "m_risk_params": "#### 🛡️ Safety Tips",
            "m_stop_loss": "Safety Exit Price (Sell if it drops here)",
            "m_kelly_ratio": "Suggested % of your money",
            "m_var_exp": "Max money you might lose today",
            "m_waiting": "👈 Set your preferences on the left and click **Start AI Analysis**.",
            "a_hold": "WAIT & WATCH",
            "a_hold_r": "The trend is messy, do nothing for now.",
            "a_buy": "GOOD TO BUY",
            "a_buy_r": "Market is healthy, and the stock is rising above average cost!",
            "a_block": "DO NOT BUY",
            "a_block_r": "Stock looks okay, but the overall market is bad. Safety first.",
            "a_rev": "BARGAIN BUY",
            "a_rev_r": "Price dropped too much, likely to bounce back soon.",
            "a_sell": "SELL IMMEDIATELY",
            "a_sell_r": "Things look bad, everyone is selling. Get out!"
        }
    },
    "FR": {
        "PRO": {
            "sb_title": "### 📊 TK Quant Terminal",
            "sb_caption": "Moteur Quant. et Actuariel | **Par Kai Teng**",
            "sb_settings": "⚙️ Paramètres du Moteur",
            "sb_pool": "Liste de surveillance (séparées par virgules):",
            "sb_bm": "Référence Macro:",
            "sb_actuarial": "#### 💰 Gestion du Capital",
            "sb_capital": "Capital Simulé ($):",
            "sb_winrate": "Taux de Victoire Attendu:",
            "sb_wlratio": "Ratio Gain/Perte:",
            "sb_btn": "🚀 Lancer le Moteur Cloud TK",
            "m_title": "📊 Matrice Quant. Macro-Micro Double Cycle",
            "m_subtitle": "Propulsé par **l'Architecture Actuarielle & Quant. de TK**",
            "m_fetching": "Le moteur TK récupère les données mondiales...",
            "m_bm_bull": "**Valve de Risque Macro**: 🟢 {0} est en structure haussière, exposition activée.",
            "m_bm_bear": "**Valve de Risque Macro**: 🔴 {0} sous la MA-20, blocage global activé!",
            "m_calc": "Calcul de la matrice multidimensionnelle pour: {0}...",
            "m_nodata": "Données non valides pour {0}.",
            "m_report": "🏷️ Profil de Rapport Détaillé {0}",
            "m_price": "Dernier Prix",
            "m_vwap": "Coût Inst. (VWAP)",
            "m_zscore": "Momentum Stat. (Z-Score)",
            "m_kelly": "Pos. Cible Kelly",
            "m_var": "VaR Journalière 95%",
            "m_chart_title": "Microstructure des 60 Dernières Périodes de {0}",
            "m_ai_decision": "#### 🤖 Décision de l'IA",
            "m_logic": "Logique",
            "m_risk_params": "#### 🛡️ Paramètres de Risque",
            "m_stop_loss": "Stop Loss",
            "m_kelly_ratio": "Ratio Kelly",
            "m_var_exp": "Exposition Extrême VaR",
            "m_waiting": "👈 Veuillez configurer les paramètres et cliquer sur **Lancer**.",
            "a_hold": "ATTENTE",
            "a_hold_r": "Momentum mixte, tendance incertaine",
            "a_buy": "ACHAT FORT",
            "a_buy_r": "Macro sécurisé, cassure au-dessus du VWAP",
            "a_block": "RISQUE BLOQUÉ",
            "a_block_r": "Contrôle passif des risques déclenché",
            "a_rev": "ACHAT RÉVERSION",
            "a_rev_r": "Sur-vendu, forte demande de retour à la moyenne",
            "a_sell": "VENTE PANIQUE",
            "a_sell_r": "Effondrement technique, vente de panique"
        },
        "BASIC": {
            "sb_title": "### 📊 TK Investisseur Intelligent",
            "sb_caption": "Assistant IA facile à utiliser | **Par Kai Teng**",
            "sb_settings": "⚙️ Paramètres d'Investissement",
            "sb_pool": "Actions à surveiller (séparées par virgules):",
            "sb_bm": "Référence du Marché (ex: SPY):",
            "sb_actuarial": "#### 💰 Argent & Sécurité",
            "sb_capital": "Capital Total à Investir ($):",
            "sb_winrate": "Votre estimation de victoire:",
            "sb_wlratio": "Ratio Gain / Risque:",
            "sb_btn": "🚀 Lancer l'Analyse IA",
            "m_title": "📊 Bilan de Santé Intelligent",
            "m_subtitle": "L'IA analyse vos actions",
            "m_fetching": "Récupération des données du marché...",
            "m_bm_bull": "**Environnement de Marché**: 🟢 Le marché {0} monte. Sécurisé pour investir.",
            "m_bm_bear": "**Environnement de Marché**: 🔴 Le marché {0} baisse. Mieux vaut attendre!",
            "m_calc": "Diagnostic de l'action: {0}...",
            "m_nodata": "Données introuvables pour {0}.",
            "m_report": "🏷️ Résultat du Diagnostic IA {0}",
            "m_price": "Prix Actuel",
            "m_vwap": "Coût Moyen du Marché",
            "m_zscore": "Force à Court Terme",
            "m_kelly": "Investissement Suggéré",
            "m_var": "Perte Max Estimée (Jour)",
            "m_chart_title": "Tendance Récente de {0}",
            "m_ai_decision": "#### 🤖 Suggestion de l'IA",
            "m_logic": "Raison",
            "m_risk_params": "#### 🛡️ Conseils de Sécurité",
            "m_stop_loss": "Prix de Sortie de Sécurité",
            "m_kelly_ratio": "% suggéré de votre argent",
            "m_var_exp": "Argent max que vous pourriez perdre",
            "m_waiting": "👈 Définissez vos préférences à gauche et cliquez sur **Lancer**.",
            "a_hold": "ATTENDRE & OBSERVER",
            "a_hold_r": "La tendance est désordonnée, ne faites rien.",
            "a_buy": "BON À ACHETER",
            "a_buy_r": "Le marché est sain et l'action dépasse le coût moyen!",
            "a_block": "NE PAS ACHETER",
            "a_block_r": "L'action semble bonne, mais le marché global est mauvais.",
            "a_rev": "ACHAT D'OPPORTUNITÉ",
            "a_rev_r": "Le prix a trop baissé, rebond probable.",
            "a_sell": "VENDRE IMMÉDIATEMENT",
            "a_sell_r": "La situation est mauvaise, tout le monde vend. Sortez!"
        }
    }
}

# ==========================================
# 3. 顶栏控制台渲染（默认：中文、大众版、日间模式）
# ==========================================
st.markdown('<div class="top-control-card">', unsafe_allow_html=True)
col_ui1, col_ui2, col_ui3, col_logo = st.columns([3, 3, 3, 1])

with col_ui1:
    st.markdown('<div class="control-label">🌐 请选择语言 / SELECT LANGUAGE</div>', unsafe_allow_html=True)
    lang_str = st.radio("Language", ["🇨🇳 CN", "🇬🇧 EN", "🇫🇷 FR"], index=0, horizontal=True, label_visibility="collapsed")
    lang = "CN" if "CN" in lang_str else ("EN" if "EN" in lang_str else "FR")

with col_ui2:
    st.markdown('<div class="control-label">⚙️ 请选择版本 / SELECT MODE</div>', unsafe_allow_html=True)
    mode_str = st.radio("Mode", ["🟢 Basic (大众版)", "🔥 Pro (专业版)"], index=0, horizontal=True, label_visibility="collapsed")
    mode_key = "PRO" if "Pro" in mode_str else "BASIC"

with col_ui3:
    st.markdown('<div class="control-label">🎨 请选择外观 / THEME MODE</div>', unsafe_allow_html=True)
    theme_str = st.radio("Theme", ["☀️ 日间", "🌙 夜间", "💻 跟随系统"], index=0, horizontal=True, label_visibility="collapsed")

with col_logo:
    logo_path = "my_logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=45)
    else:
        st.markdown("<div style='text-align: right; margin-top: 15px; font-weight: bold; color: #38bdf8;'>🦅 TK</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. 高级舒适护眼配色引擎
# ==========================================
if "日间" in theme_str:
    bg_color = "#fbfbfa"
    text_color = "#2c2c2e"
    sb_bg = "#f3f3f2"
    in_bg = "#ffffff"
    in_color = "#1c1c1e"
    card_bg = "rgba(255, 255, 255, 0.95)"
    card_border = "#e2e2df"
    lbl_color = "#0066cc"
    radio_text_color = "#1c1c1e"
    plotly_template = "plotly_white"
elif "夜间" in theme_str:
    bg_color = "#12141c"
    text_color = "#e1e4e8"
    sb_bg = "#181b26"
    in_bg = "#212635"
    in_color = "#ffffff"
    card_bg = "rgba(27, 32, 45, 0.85)"
    card_border = "rgba(255, 255, 255, 0.08)"
    lbl_color = "#58a6ff"
    radio_text_color = "#ffffff"
    plotly_template = "plotly_dark"
else:
    bg_color = "#12141c"
    text_color = "#e1e4e8"
    sb_bg = "#181b26"
    in_bg = "#212635"
    in_color = "#ffffff"
    card_bg = "rgba(27, 32, 45, 0.85)"
    card_border = "rgba(255, 255, 255, 0.08)"
    lbl_color = "#58a6ff"
    radio_text_color = "#ffffff"
    plotly_template = "plotly_dark"

# 统一封装并安全注入 CSS 样式（强力隐藏右下角 Manage app 悬浮窗及其底层 iframe）
unified_css = f"""
<style>
#MainMenu {{visibility: hidden;}} 
footer {{visibility: hidden;}}
header {{visibility: hidden;}}

/* 强力隐藏右下角管理悬浮按钮及所有平台注入元素 */
[data-testid="stToolbar"], 
[data-testid="stDecoration"], 
div[class*="viewerBadge"], 
button[kind="header"],
iframe[title="streamlit"] {{
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}}

/* 隐藏所有底部固定浮动容器 */
.element-container:has(iframe) {{
    display: none;
}}

.block-container {{ padding-top: 2rem; padding-bottom: 2rem; }}
div.row-widget.stRadio > div {{ flex-direction: row; gap: 8px; }}

div.stRadio label, div.stRadio span, div.stRadio div, div.stRadio p {{
    color: {radio_text_color} !important;
    font-weight: 600 !important;
}}

.stApp {{
    background-color: {bg_color};
    color: {text_color};
}}

[data-testid="stSidebar"] {{ 
    background-color: {sb_bg} !important; 
    color: {text_color} !important; 
    border-right: 1px solid {card_border}; 
}}
[data-testid="stSidebar"] input {{ 
    background-color: {in_bg} !important; 
    color: {in_color} !important; 
}}
[data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown p {{ 
    color: {text_color} !important; 
    font-weight: 500; 
}}

.top-control-card {{ 
    background: {card_bg}; 
    border: 1px solid {card_border}; 
    padding: 15px 20px; 
    border-radius: 12px; 
    margin-bottom: 25px; 
    backdrop-filter: blur(12px); 
}}
.control-label {{ 
    font-size: 0.8rem; 
    font-weight: 800; 
    text-transform: uppercase; 
    letter-spacing: 0.06em; 
    color: {lbl_color} !important; 
    margin-bottom: 6px; 
}}
</style>
"""

st.markdown(unified_css, unsafe_allow_html=True)

t = LANG_DICT[lang][mode_key]

# ==========================================
# 5. 侧边栏：交互面板
# ==========================================
with st.sidebar:
    sidebar_avatar = "avatar.png"
    if os.path.exists(sidebar_avatar):
        st.image(sidebar_avatar, width=75)
    else:
        st.markdown("<h1 style='margin-top: -10px;'>👨‍💻</h1>", unsafe_allow_html=True)
        
    st.markdown(t["sb_title"])
    st.caption(t["sb_caption"])
    st.markdown("---")
    
    st.header(t["sb_settings"])
    symbols_input = st.text_input(t["sb_pool"], value="AAPL, TSLA, NVDA")
    watchlist = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]
    benchmark = st.text_input(t["sb_bm"], value="SPY").upper()
    
    st.markdown(t["sb_actuarial"])
    capital = st.number_input(t["sb_capital"], min_value=10000, value=100000, step=10000)
    win_rate = st.slider(t["sb_winrate"], min_value=0.1, max_value=0.9, value=0.55, step=0.01)
    win_loss_ratio = st.slider(t["sb_wlratio"], min_value=0.5, max_value=5.0, value=1.5, step=0.1)
    
    st.markdown("---")
    if st.button(t["sb_btn"], use_container_width=True, type="primary"):
        st.session_state['run_engine'] = True 

# ==========================================
# 6. 核心精算与策略函数 (纯 Pandas 实现，完美适配所有 Python 版本)
# ==========================================
def calculate_kelly(p, b):
    return (p * b - (1 - p)) / b

def calculate_var(df_1d, target_capital):
    returns = df_1d["Close"].pct_change().dropna()
    mu, sigma = returns.mean(), returns.std()
    var_pct = 1.645 * sigma - mu 
    return target_capital * var_pct if var_pct > 0 else 0

def calculate_zscore(close_series, period=20):
    ma = close_series.rolling(period).mean().iloc[-1]
    std = close_series.rolling(period).std().iloc[-1]
    return (close_series.iloc[-1] - ma) / std if std != 0 else 0

# ==========================================
# 7. 网页主界面渲染
# ==========================================
st.title(t["m_title"])
st.markdown(t["m_subtitle"])
st.markdown("---")

if st.session_state.get('run_engine', False):
    kelly_f = calculate_kelly(win_rate, win_loss_ratio)
    my_bar = st.progress(0, text=t["m_fetching"])
    
    try:
        bm_data = yf.Ticker(benchmark).history(period="1mo", interval="1d")
        bm_ma20 = bm_data["Close"].rolling(20).mean().iloc[-1]
        is_bull_market = bm_data["Close"].iloc[-1] > bm_ma20
    except Exception:
        is_bull_market = True 
        
    if is_bull_market:
        st.success(t["m_bm_bull"].format(benchmark))
    else:
        st.error(t["m_bm_bear"].format(benchmark))

    for idx, sym in enumerate(watchlist):
        my_bar.progress((idx + 1) / len(watchlist), text=t["m_calc"].format(sym))
        
        try:
            ticker = yf.Ticker(sym)
            df_1m = ticker.history(period="5d", interval="1m")
            if df_1m.empty: df_1m = ticker.history(period="1mo", interval="1d") 
            df_1d = ticker.history(period="6mo", interval="1d")
            
            if df_1m.empty or df_1d.empty:
                st.warning(t["m_nodata"].format(sym))
                continue
                
            # 纯 Pandas 计算技术指标，彻底规避云端编译报错
            df_1m["SMA_5"] = df_1m["Close"].rolling(5).mean()
            df_1m["SMA_20"] = df_1m["Close"].rolling(20).mean()
            df_1m["VWAP"] = (df_1m["Volume"] * (df_1m["High"] + df_1m["Low"] + df_1m["Close"]) / 3).cumsum() / df_1m["Volume"].cumsum()
            
            high_low = df_1m["High"] - df_1m["Low"]
            high_close = np.abs(df_1m["High"] - df_1m["Close"].shift())
            low_close = np.abs(df_1m["Low"] - df_1m["Close"].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df_1m["ATR"] = true_range.rolling(14).mean()
            
            curr = df_1m.iloc[-1]
            price = curr["Close"]
            vwap = curr["VWAP"] if not pd.isna(curr["VWAP"]) else price
            atr = curr["ATR"] if not pd.isna(curr["ATR"]) else price * 0.02
            sma_f = curr["SMA_5"] if not pd.isna(curr["SMA_5"]) else price
            sma_s = curr["SMA_20"] if not pd.isna(curr["SMA_20"]) else price
            z_score = calculate_zscore(df_1m["Close"])
            
            act, color, reason = t["a_hold"], "normal", t["a_hold_r"]
            
            if sma_f > sma_s and price > vwap and z_score > 1.0:
                if is_bull_market:
                    act, color, reason = t["a_buy"], "inverse", t["a_buy_r"]
                else:
                    act, color, reason = t["a_block"], "off", t["a_block_r"]
            elif sma_f < sma_s and price < vwap and z_score < -1.5:
                act, color, reason = t["a_rev"], "inverse", t["a_rev_r"]
            elif sma_f < sma_s and z_score < -2.0:
                act, color, reason = t["a_sell"], "normal", t["a_sell_r"]
                
            target_pos = capital * kelly_f if "BUY" in act else 0.0
            var_95 = calculate_var(df_1d, target_pos)

            with st.container(border=True):
                st.subheader(t["m_report"].format(sym))
                
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric(t["m_price"], f"${price:.2f}")
                col2.metric(t["m_vwap"], f"${vwap:.2f}", f"{(price-vwap)/vwap*100:.2f}%")
                col3.metric(t["m_zscore"], f"{z_score:+.2f}σ" if mode_key=="PRO" else f"{z_score:+.2f}", delta_color="off")
                col4.metric(t["m_kelly"], f"${target_pos:,.0f}")
                col5.metric(t["m_var"], f"${var_95:,.0f}" if target_pos>0 else "-", delta_color="inverse")
                
                chart_col, report_col = st.columns([2, 1])
                
                with chart_col:
                    plot_df = df_1m.tail(60)
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(
                        x=plot_df.index, open=plot_df['Open'], high=plot_df['High'],
                        low=plot_df['Low'], close=plot_df['Close'], name='Price'
                    ))
                    fig.add_trace(go.Scatter(
                        x=plot_df.index, y=plot_df['VWAP'], 
                        mode='lines', name='VWAP', line=dict(color='magenta', width=2, dash='dash')
                    ))
                    fig.update_layout(
                        title=t["m_chart_title"].format(sym),
                        template=plotly_template, 
                        margin=dict(l=0, r=0, t=40, b=0),
                        height=350,
                        xaxis_rangeslider_visible=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with report_col:
                    st.markdown(t["m_ai_decision"])
                    if "BUY" in act or "ACHAT" in act: st.success(f"**[{act}]**\n\n**{t['m_logic']}**: {reason}")
                    elif "SELL" in act or "VENTE" in act: st.error(f"**[{act}]**\n\n**{t['m_logic']}**: {reason}")
                    else: st.info(f"**[{act}]**\n\n**{t['m_logic']}**: {reason}")
                        
                    st.markdown(t["m_risk_params"])
                    st.write(f"- **{t['m_stop_loss']}**: `${price - 1.5 * atr:.2f}`")
                    st.write(f"- **{t['m_kelly_ratio']}**: `{kelly_f*100:.1f}%`")
                    st.write(f"- **{t['m_var_exp']}**: `${var_95:,.0f}`")

        except Exception as e:
            st.error(f"Error rendering {sym}: {e}")
            
    my_bar.empty()
else:
    st.info(t["m_waiting"])