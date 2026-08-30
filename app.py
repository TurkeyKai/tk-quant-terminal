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
# 1. 页面全局配置（强制常驻展开侧边栏）
# ==========================================
st.set_page_config(
    page_title="TK Quant Terminal", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 1.5 顶部风险提示与免责声明 (Risk Disclaimer)
# ==========================================
st.warning(
    "⚠️ **免责声明与风险提示 (Disclaimer)**: 本终端输出之所有量化指标、统计动量、动态仓位及策略回测结果，仅供数量化金融与精算研究参考，不构成任何具体的投资建议、买卖依据或金融产品邀约。金融市场具有高波动性与潜在资本回撤风险，用户须自行承担策略执行之所有敞口与损益。"
)

# ==========================================
# 2. 国际化与多语言词典（精简为：简体中文、英文、法语）
# ==========================================
LANG_DICT = {
    "CN": {
        "ui_lang": "🌐 语言 / LANGUAGE",
        "ui_mode": "⚙️ 版本 / MODE",
        "ui_theme": "🎨 外观 / THEME",
        "lang_options": ["🇨🇳 简体中文", "🇬🇧 English", "🇫🇷 Français"],
        "modes": ["🟢 基础策略版 (Basic)", "🔥 机构专业版 (Pro)"],
        "themes": ["☀️ 日间模式", "🌙 夜间模式", "💻 跟随系统"],
        "PRO": {
            "sb_title": "### 📊 TK Quant Terminal",
            "sb_caption": "机构级量化与精算风控引擎 | **By Kai Teng**",
            "sb_settings": "⚙️ 策略与因子参数",
            "sb_pool": "多资产自选监控池:",
            "sb_pool_help": "💡 **操作提示**: 输入后**必须按回车键 (Enter)** 确认保存！\n- **美股**: `AAPL`, `TSLA`\n- **港股**: `0700.HK`\n- **A股**: `002185.SZ` (华天科技)\n- **加密资产**: `BTC-USD`",
            "sb_bm": "宏观基准资产 (Benchmark):",
            "sb_bm_help": "💡 **操作提示**: 输入后**必须按回车键 (Enter)** 确认！\n- `SPY` (标普) / `000001.SS` (上证指数)",
            "sb_actuarial": "#### 💰 资本配置与风控管理",
            "sb_capital": "策略模拟初始本金 ($):",
            "sb_winrate": "策略历史胜率 (Win Rate):",
            "sb_wlratio": "盈亏赔率 (W/L Ratio):",
            "sb_btn": "🚀 执行多因子量化扫描",
            "m_title": "📊 宏微观双周期量化决策矩阵",
            "m_subtitle": "Powered by **TK's Actuarial & Quantitative Architecture**",
            "m_fetching": "核心引擎正在调动全球网络节点汇聚高频行情...",
            "m_bm_bull": "**宏观风控阀**: 🟢 基准资产 ({0}) 运行于长期均线上方，多头策略敞口正常释放。",
            "m_bm_bear": "**宏观风控阀**: 🔴 基准资产 ({0}) 下破 20 日生命线，全策略风控熔断启动！",
            "m_calc": "正在执行多维量价矩阵测算: {0}...",
            "m_nodata": "无法获取标的 {0} 的有效行情数据。",
            "m_price": "最新成交价",
            "m_vwap": "机构成本基准 (VWAP)",
            "m_zscore": "统计动量 (Z-Score)",
            "m_kelly": "凯利最优仓位",
            "m_var": "95% 单日 VaR 风险值",
            "m_chart_title": "{0} ({1}) - 近 60 周期微观结构与机构 VWAP 锚点",
            "m_ai_decision": "#### 🤖 策略信号裁决",
            "m_logic": "核心逻辑",
            "m_risk_params": "#### 🛡️ 精算风控边界",
            "m_stop_loss": "动态防守止损位",
            "m_kelly_ratio": "凯利配比",
            "m_var_exp": "VaR 尾部风险敞口",
            "m_waiting": "👈 请在左侧配置面板中输入资产代码（**输入后请按回车键确认**），并点击 **执行多因子量化扫描** 以加载终端。",
            "a_hold": "NEUTRAL (中性观望)",
            "a_hold_r": "多空动能交织，未触及统计显著性阈值",
            "a_buy": "LONG BREAKOUT (多头突破)",
            "a_buy_r": "宏观环境安全，价格强势上穿机构 VWAP 成本线",
            "a_block": "RISK BLOCKED (风控拦截)",
            "a_block_r": "触发系统级宏观风控阀阻断",
            "a_rev": "MEAN REVERSION (均值回归)",
            "a_rev_r": "价格出现统计学超跌，强烈的均值回归需求触发",
            "a_sell": "TECHNICAL EXIT (破位止损)",
            "a_sell_r": "微观结构崩塌，动量指标触及清仓警戒线"
        },
        "BASIC": {
            "sb_title": "### 📊 TK 策略观察终端",
            "sb_caption": "专业量化策略辅助系统 | **By Kai Teng**",
            "sb_settings": "⚙️ 策略参数配置",
            "sb_pool": "自选股票池代码:",
            "sb_pool_help": "💡 **提示**: 输入后请**按回车键 (Enter)** 保存！\n- **美股**: `AAPL`\n- **A股**: `002185.SZ` (华天科技)",
            "sb_bm": "大盘对标资产 (如 SPY):",
            "sb_bm_help": "💡 **提示**: 输入后请**按回车键 (Enter)** 保存！\n- `SPY` / `000001.SS` (上证指数)",
            "sb_actuarial": "#### 💰 资金分配与风控",
            "sb_capital": "初始投资资金 ($):",
            "sb_winrate": "策略预期胜率:",
            "sb_wlratio": "盈亏比 (Reward/Risk):",
            "sb_btn": "🚀 运行策略分析",
            "m_title": "📊 资产多维量化评估报告",
            "m_subtitle": "基于统计学与微观结构的多因子量化看板",
            "m_fetching": "正在建立市场数据连接...",
            "m_bm_bull": "**市场环境**: 🟢 对标大盘 ({0}) 趋势向上，整体环境安全。",
            "m_bm_bear": "**市场环境**: 🔴 对标大盘 ({0}) 出现破位下行，系统建议收缩防线！",
            "m_calc": "正在测算标的: {0}...",
            "m_nodata": "未能检索到 {0} 的行情，请核对代码或后缀。",
            "m_price": "当前成交价",
            "m_vwap": "机构均价 (VWAP)",
            "m_zscore": "动量指标",
            "m_kelly": "建议配置金额",
            "m_var": "单日最大风险敞口 (VaR)",
            "m_chart_title": "{0} ({1}) 近期走势与机构成本线",
            "m_ai_decision": "#### 🤖 策略信号输出",
            "m_logic": "触发原因",
            "m_risk_params": "#### 🛡️ 风险风控基准",
            "m_stop_loss": "建议止损价",
            "m_kelly_ratio": "建议仓位比例",
            "m_var_exp": "单日 VaR 风险值",
            "m_waiting": "👈 请在左侧输入代码（**按回车键确认**），点击 **运行策略分析** 开始评估。",
            "a_hold": "观望中性",
            "a_hold_r": "当前多空信号不明，建议保持流动性。",
            "a_buy": "符合多头策略",
            "a_buy_r": "大盘环境稳健，价格运行于机构平均成本之上。",
            "a_block": "触发风控拦截",
            "a_block_r": "大盘趋势走弱，暂停开仓以控制整体回撤。",
            "a_rev": "超跌反弹策略",
            "a_rev_r": "历史波动率偏离均值过大，存在技术性修复预期。",
            "a_sell": "触发离场信号",
            "a_sell_r": "趋势形态破位，建议执行纪律性减仓。"
        }
    },
    "EN": {
        "ui_lang": "🌐 LANGUAGE",
        "ui_mode": "⚙️ MODE",
        "ui_theme": "🎨 THEME",
        "lang_options": ["🇨🇳 简体中文", "🇬🇧 English", "🇫🇷 Français"],
        "modes": ["🟢 Basic Strategy", "🔥 Institutional Pro"],
        "themes": ["☀️ Day Mode", "🌙 Night Mode", "💻 System Default"],
        "PRO": {
            "sb_title": "### 📊 TK Quant Terminal",
            "sb_caption": "Institutional Quant & Actuarial Engine | **By Kai Teng**",
            "sb_settings": "⚙️ Strategy & Factor Settings",
            "sb_pool": "Global Asset Watchlist:",
            "sb_pool_help": "💡 **Tip**: Press **Enter** after typing!\n- US (`AAPL`), HK (`0700.HK`), CN (`002185.SZ`)",
            "sb_bm": "Macro Benchmark:",
            "sb_bm_help": "💡 **Tip**: Press **Enter** after typing! (e.g. `SPY`, `000001.SS`)",
            "sb_actuarial": "#### 💰 Capital & Risk Management",
            "sb_capital": "Simulated Capital ($):",
            "sb_winrate": "Strategy Win Rate:",
            "sb_wlratio": "Win/Loss Ratio:",
            "sb_btn": "🚀 Execute Multi-Factor Scan",
            "m_title": "📊 Macro-Micro Dual Cycle Quant Matrix",
            "m_subtitle": "Powered by **TK's Actuarial & Quantitative Architecture**",
            "m_fetching": "Fetching high-frequency feeds from global nodes...",
            "m_bm_bull": "**Macro Risk Valve**: 🟢 Benchmark ({0}) is bullish, risk exposure permitted.",
            "m_bm_bear": "**Macro Risk Valve**: 🔴 Benchmark ({0}) breached 20-MA, risk block engaged!",
            "m_calc": "Running multidimensional matrix calculations for: {0}...",
            "m_nodata": "Invalid data feed for {0}.",
            "m_price": "Last Price",
            "m_vwap": "Institutional Cost (VWAP)",
            "m_zscore": "Stat Momentum (Z-Score)",
            "m_kelly": "Kelly Target Position",
            "m_var": "95% Daily VaR",
            "m_chart_title": "{0} ({1}) - Microstructure & VWAP Anchor",
            "m_ai_decision": "#### 🤖 Strategy Signal Decision",
            "m_logic": "Core Logic",
            "m_risk_params": "#### 🛡️ Actuarial Risk Boundaries",
            "m_stop_loss": "Dynamic Stop Loss",
            "m_kelly_ratio": "Kelly Ratio",
            "m_var_exp": "VaR Tail Exposure",
            "m_waiting": "👈 Configure parameters and tickers in the left panel (press **Enter**), then click **Execute**.",
            "a_hold": "NEUTRAL",
            "a_hold_r": "Mixed momentum, statistical threshold not met",
            "a_buy": "LONG BREAKOUT",
            "a_buy_r": "Macro secure, price breaking above institutional VWAP",
            "a_block": "RISK BLOCKED",
            "a_block_r": "Systemic macro risk control triggered",
            "a_rev": "MEAN REVERSION",
            "a_rev_r": "Statistically oversold, strong reversion demand",
            "a_sell": "TECHNICAL EXIT",
            "a_sell_r": "Microstructure breakdown, momentum exit triggered"
        },
        "BASIC": {
            "sb_title": "### 📊 TK Quant Assistant",
            "sb_caption": "Quantitative Strategy Terminal | **By Kai Teng**",
            "sb_settings": "⚙️ Strategy Settings",
            "sb_pool": "Asset Watchlist:",
            "sb_pool_help": "💡 **Tip**: Press **Enter** to save!",
            "sb_bm": "Market Reference:",
            "sb_bm_help": "💡 **Tip**: Press **Enter** to save!",
            "sb_actuarial": "#### 💰 Capital & Safety",
            "sb_capital": "Total Investment Capital ($):",
            "sb_winrate": "Target Win Rate:",
            "sb_wlratio": "Reward/Risk Ratio:",
            "sb_btn": "🚀 Run Strategy Analysis",
            "m_title": "📊 Asset Quantitative Health Report",
            "m_subtitle": "Multi-factor quantitative dashboard",
            "m_fetching": "Connecting to market feed...",
            "m_bm_bull": "**Market Environment**: 🟢 Benchmark ({0}) uptrend. Environment stable.",
            "m_bm_bear": "**Market Environment**: 🔴 Benchmark ({0}) downtrend. Caution advised.",
            "m_calc": "Analyzing asset: {0}...",
            "m_nodata": "No data found for {0}.",
            "m_report": "🏷️ Report: {0} ({1})",
            "m_price": "Current Price",
            "m_vwap": "Institutional Cost",
            "m_zscore": "Momentum Score",
            "m_kelly": "Allocation Target",
            "m_var": "Max Daily Risk (VaR)",
            "m_chart_title": "{0} ({1}) Recent Trend & VWAP",
            "m_ai_decision": "#### 🤖 Strategy Signal",
            "m_logic": "Trigger Reason",
            "m_risk_params": "#### 🛡️ Risk Metrics",
            "m_stop_loss": "Suggested Stop Loss",
            "m_kelly_ratio": "Suggested Weight",
            "m_var_exp": "Daily VaR Exposure",
            "m_waiting": "👈 Set your preferences in the left panel, press **Enter**, and click **Run Strategy Analysis**.",
            "a_hold": "HOLD",
            "a_hold_r": "Trend unclear, maintaining liquidity.",
            "a_buy": "BUY SIGNAL",
            "a_buy_r": "Market healthy, price above institutional average cost.",
            "a_block": "BLOCK ENTRY",
            "a_block_r": "Market weak, risk management prioritized.",
            "a_rev": "OVERSOLD REBOUND",
            "a_rev_r": "Price deviation high, reversion expected.",
            "a_sell": "EXIT SIGNAL",
            "a_sell_r": "Trend breakdown, cutting exposure."
        }
    },
    "FR": {
        "ui_lang": "🌐 LANGUE",
        "ui_mode": "⚙️ MODE",
        "ui_theme": "🎨 THÈME",
        "lang_options": ["🇨🇳 简体中文", "🇬🇧 English", "🇫🇷 Français"],
        "modes": ["🟢 Version Basique", "🔥 Version Pro"],
        "themes": ["☀️ Mode Jour", "🌙 Mode Nuit", "💻 Système"],
        "PRO": {
            "sb_title": "### 📊 TK Quant Terminal",
            "sb_caption": "Moteur Quant. et Actuariel | **Par Kai Teng**",
            "sb_settings": "⚙️ Paramètres de Stratégie",
            "sb_pool": "Actifs surveillés:",
            "sb_pool_help": "💡 **Conseil**: Appuyez sur **Entrée (Enter)** après la saisie !\n- US (`AAPL`), Chine (`002185.SZ`)",
            "sb_bm": "Référence Macro:",
            "sb_bm_help": "💡 **Conseil**: Appuyez sur **Entrée** après la saisie !",
            "sb_actuarial": "#### 💰 Gestion du Capital",
            "sb_capital": "Capital Simulé ($):",
            "sb_winrate": "Taux de Victoire Attendu:",
            "sb_wlratio": "Ratio Gain/Perte:",
            "sb_btn": "🚀 Exécuter le Scan Quant.",
            "m_title": "📊 Matrice Quant. Macro-Micro Double Cycle",
            "m_subtitle": "Propulsé par **l'Architecture Actuarielle & Quant. de TK**",
            "m_fetching": "Récupération des flux de données mondiales...",
            "m_bm_bull": "**Valve de Risque Macro**: 🟢 Référence ({0}) haussière, exposition autorisée.",
            "m_bm_bear": "**Valve de Risque Macro**: 🔴 Référence ({0}) sous la MA-20, blocage actif!",
            "m_calc": "Calculs matriciels pour: {0}...",
            "m_nodata": "Données non valides pour {0}.",
            "m_price": "Dernier Prix",
            "m_vwap": "Coût Institutionnel (VWAP)",
            "m_zscore": "Momentum Stat. (Z-Score)",
            "m_kelly": "Pos. Cible Kelly",
            "m_var": "VaR Journalière 95%",
            "m_chart_title": "{0} ({1}) - Microstructure & Ancrage VWAP",
            "m_ai_decision": "#### 🤖 Décision de Stratégie",
            "m_logic": "Logique",
            "m_risk_params": "#### 🛡️ Limites de Risque Actuariel",
            "m_stop_loss": "Stop Loss Dynamique",
            "m_kelly_ratio": "Ratio Kelly",
            "m_var_exp": "Exposition VaR",
            "m_waiting": "👈 Configurez les paramètres dans le panneau de gauche (appuyez sur **Entrée**), puis cliquez sur **Exécuter**.",
            "a_hold": "NEUTRE",
            "a_hold_r": "Momentum mixte, seuil statistique non atteint",
            "a_buy": "CASSURE HAUSSIÈRE",
            "a_buy_r": "Macro sécurisé, prix au-dessus du VWAP",
            "a_block": "RISQUE BLOQUÉ",
            "a_block_r": "Contrôle macro de sécurité déclenché",
            "a_rev": "RÉVERSION À LA MOYENNE",
            "a_rev_r": "Sur-vendu statistiquement, fort besoin de rebond",
            "a_sell": "SORTIE TECHNIQUE",
            "a_sell_r": "Rupture de structure, signal de sortie déclenché"
        },
        "BASIC": {
            "sb_title": "### 📊 TK Assistant Quant.",
            "sb_caption": "Terminal de Stratégie | **Par Kai Teng**",
            "sb_settings": "⚙️ Paramètres",
            "sb_pool": "Actifs à surveiller:",
            "sb_pool_help": "💡 **Conseil**: Appuyez sur **Entrée** pour valider.",
            "sb_bm": "Référence:",
            "sb_bm_help": "💡 **Conseil**: Appuyez sur **Entrée** pour valider.",
            "sb_actuarial": "#### 💰 Argent & Sécurité",
            "sb_capital": "Capital Total ($):",
            "sb_winrate": "Taux de Victoire:",
            "sb_wlratio": "Ratio Gain/Risque:",
            "sb_btn": "🚀 Lancer l'Analyse",
            "m_title": "📊 Rapport de Santé Quantitatif",
            "m_subtitle": "Tableau de bord multifactoriel",
            "m_fetching": "Connexion aux flux de marché...",
            "m_bm_bull": "**Environnement**: 🟢 Référence ({0}) en hausse. Environnement sain.",
            "m_bm_bear": "**Environnement**: 🔴 Référence ({0}) en baisse. Prudence requise.",
            "m_calc": "Analyse de l'actif: {0}...",
            "m_nodata": "Aucune donnée pour {0}.",
            "m_report": "🏷️ Rapport: {0} ({1})",
            "m_price": "Prix Actuel",
            "m_vwap": "Coût Moyen",
            "m_zscore": "Score Momentum",
            "m_kelly": "Allocation Suggérée",
            "m_var": "Risque Max (VaR)",
            "m_chart_title": "{0} ({1}) Tendance & VWAP",
            "m_ai_decision": "#### 🤖 Signal de Stratégie",
            "m_logic": "Raison",
            "m_risk_params": "#### 🛡️ Métriques de Risque",
            "m_stop_loss": "Stop Loss Suggéré",
            "m_kelly_ratio": "Poids Suggéré",
            "m_var_exp": "Exposition VaR",
            "m_waiting": "👈 Définissez vos préférences dans le panneau de gauche (appuyez sur **Entrée**), puis cliquez sur **Lancer**.",
            "a_hold": "ATTENDRE & OBSERVER",
            "a_hold_r": "Tendance floue, conservation de liquidité.",
            "a_buy": "SIGNAL D'ACHAT",
            "a_buy_r": "Marché sain, prix supérieur au coût moyen.",
            "a_block": "BLOCAGE D'ACHAT",
            "a_block_r": "Marché faible, gestion des risques prioritaire.",
            "a_rev": "REBOND SURVENDU",
            "a_rev_r": "Écart de prix élevé, rebond attendu.",
            "a_sell": "SIGNAL DE VENTE",
            "a_sell_r": "Rupture de tendance, réduction d'exposition."
        }
    }
}

# ==========================================
# 3. 顶栏控制台渲染
# ==========================================
st.markdown('<div class="top-control-card">', unsafe_allow_html=True)
col_ui1, col_ui2, col_ui3, col_logo = st.columns([3, 3, 3, 1])

lang = "CN"
ui_t = LANG_DICT[lang]

with col_ui1:
    st.markdown(f'<div class="control-label">{ui_t["ui_lang"]}</div>', unsafe_allow_html=True)
    lang_str = st.radio("Language_Select", ui_t["lang_options"], index=0, horizontal=True, label_visibility="collapsed")
    if "简体中文" in lang_str:
        lang = "CN"
    elif "English" in lang_str:
        lang = "EN"
    else:
        lang = "FR"
    ui_t = LANG_DICT[lang]

with col_ui2:
    st.markdown(f'<div class="control-label">{ui_t["ui_mode"]}</div>', unsafe_allow_html=True)
    mode_str = st.radio("Mode", ui_t["modes"], index=0, horizontal=True, label_visibility="collapsed")
    mode_key = "PRO" if any(x in mode_str for x in ["Pro", "专业版"]) else "BASIC"

with col_ui3:
    st.markdown(f'<div class="control-label">{ui_t["ui_theme"]}</div>', unsafe_allow_html=True)
    theme_str = st.radio("Theme", ui_t["themes"], index=0, horizontal=True, label_visibility="collapsed")

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
if any(x in theme_str for x in ["日间", "Day", "Jour"]):
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
elif any(x in theme_str for x in ["夜间", "Night", "Nuit"]):
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

# 统一封装并安全注入 CSS 样式
# 【彻底隐藏 Header 和 收起按钮】
unified_css = f"""
<style>
/* 隐藏顶部整个 Header 区域，保持绝对干净 */
header {{visibility: hidden !important; display: none !important;}} 
#MainMenu {{visibility: hidden;}} 
footer {{visibility: hidden;}}

/* 彻底删掉侧边栏内的收起/折叠按钮，禁止用户将其收起 */
[data-testid="stSidebarCollapseButton"] {{
    display: none !important;
}}

/* 隐藏右上角工具栏和右下角 Manage App iframe */
[data-testid="stToolbar"], 
[data-testid="stDecoration"], 
div[class*="viewerBadge"], 
iframe[title="streamlit"] {{
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}}

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
    
    # ===============================
    # 新增：左上角高级系统状态指示牌
    # ===============================
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(56,189,248,0.1) 0%, rgba(56,189,248,0.02) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        padding: 12px 15px;
        border-radius: 12px;
        margin-top: -15px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    ">
        <div style="font-size: 2.2rem; margin-right: 12px; line-height: 1;">🦅</div>
        <div>
            <div style="font-weight: 800; font-size: 1.05rem; color: #38bdf8; letter-spacing: 0.5px; margin-bottom: 3px;">TK QUANT</div>
            <div style="font-size: 0.7rem; font-weight: 600; opacity: 0.8; letter-spacing: 0.5px;">
                <span style="color: #4ade80; font-size: 0.6rem;">●</span> SYS.ONLINE
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(t["sb_title"])
    st.caption(t["sb_caption"])
    st.markdown("---")
    
    st.header(t["sb_settings"])
    
    symbols_input = st.text_input(t["sb_pool"], value="")
    st.caption(t["sb_pool_help"]) 
    
    watchlist = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]
    
    benchmark = st.text_input(t["sb_bm"], value="").upper()
    st.caption(t["sb_bm_help"]) 
    
    st.markdown(t["sb_actuarial"])
    capital = st.number_input(t["sb_capital"], min_value=10000, value=100000, step=10000)
    win_rate = st.slider(t["sb_winrate"], min_value=0.1, max_value=0.9, value=0.55, step=0.01)
    win_loss_ratio = st.slider(t["sb_wlratio"], min_value=0.5, max_value=5.0, value=1.5, step=0.1)
    
    st.markdown("---")
    if st.button(t["sb_btn"], use_container_width=True, type="primary"):
        st.session_state['run_engine'] = True 

# ==========================================
# 6. 核心精算与策略函数
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
    if not watchlist:
        st.warning("⚠️ 请先在左侧配置面板中输入至少一个有效的资产代码，并**按回车键 (Enter)** 确认，然后再次点击执行按钮。")
    else:
        if not benchmark:
            benchmark = "SPY"

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
                
                try:
                    comp_name = ticker.info.get("longName", sym)
                except Exception:
                    comp_name = sym

                df_1m = ticker.history(period="5d", interval="1m")
                if df_1m.empty: df_1m = ticker.history(period="1mo", interval="1d") 
                df_1d = ticker.history(period="6mo", interval="1d")
                
                if df_1m.empty or df_1d.empty:
                    st.warning(t["m_nodata"].format(sym))
                    continue
                    
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
                    # 仅保留干净的卡片标题（公司名称与代码）
                    st.subheader(f"{comp_name} ({sym})")
                    
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
                            title=t["m_chart_title"].format(comp_name, sym),
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