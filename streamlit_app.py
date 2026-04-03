#!/usr/bin/env python3
"""
WWL 环世物流 - 运营指挥中心 v5.0
Operational Command Center Dashboard
All text in Chinese. Dark gradient theme.
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re
import random

# ─── Page Config ───
st.set_page_config(
    page_title="WWL运营指挥中心 v5.0",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── 登录验证 ───
DASHBOARD_PASSWORD = "BRUCEWWL"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <div style="text-align:center; padding:100px 0 30px 0;">
        <h1 style="color:#fff; font-size:28px;">WWL 环世物流 运营指挥中心</h1>
        <p style="color:#a0a0c0;">请输入密码访问</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        pwd = st.text_input("密码", type="password", key="login_pwd")
        if st.button("登录", use_container_width=True):
            if pwd == DASHBOARD_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("密码错误")
    st.stop()

# ─── Dark Gradient Theme CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

/* Main background gradient */
.stApp {
    background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #1a1a2e 100%);
    color: #e0e0e0;
    font-family: 'Noto Sans SC', sans-serif;
}

/* Hide default streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: rgba(15,15,35,0.8);
    border-radius: 10px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: rgba(30,30,60,0.6);
    border-radius: 8px;
    color: #a0a0c0;
    font-weight: 500;
    padding: 8px 16px;
    font-size: 13px;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #e94560 0%, #c23152 100%) !important;
    color: white !important;
    font-weight: 700;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, rgba(30,30,60,0.9), rgba(20,20,50,0.9));
    border: 1px solid rgba(100,100,180,0.3);
    border-radius: 12px;
    padding: 18px;
    margin: 6px 0;
    text-align: center;
}
.metric-card h2 { color: #e94560; font-size: 32px; margin: 0; }
.metric-card p { color: #a0a0c0; font-size: 13px; margin: 4px 0 0 0; }

/* Alert cards */
.alert-red {
    background: linear-gradient(135deg, rgba(233,69,96,0.15), rgba(180,40,60,0.1));
    border-left: 4px solid #e94560;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 8px 0;
}
.alert-orange {
    background: linear-gradient(135deg, rgba(255,165,0,0.12), rgba(200,120,0,0.08));
    border-left: 4px solid #ffa500;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 8px 0;
}
.alert-yellow {
    background: linear-gradient(135deg, rgba(255,255,0,0.08), rgba(200,200,0,0.05));
    border-left: 4px solid #ffd700;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 8px 0;
}
.alert-green {
    background: linear-gradient(135deg, rgba(0,200,100,0.1), rgba(0,150,80,0.07));
    border-left: 4px solid #00c853;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 8px 0;
}
.alert-blue {
    background: linear-gradient(135deg, rgba(33,150,243,0.12), rgba(20,100,180,0.08));
    border-left: 4px solid #2196f3;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 8px 0;
}

/* Coach section - refined design */
.coach-box {
    background: linear-gradient(135deg, rgba(15,25,60,0.9), rgba(20,30,80,0.7));
    border: 1px solid rgba(100,150,255,0.15);
    border-left: 4px solid rgba(100,180,255,0.6);
    border-radius: 0 12px 12px 0;
    padding: 22px 24px;
    margin: 20px 0;
    font-size: 13.5px;
    line-height: 1.9;
    color: #b8c8e0;
    box-shadow: 0 4px 20px rgba(0,0,50,0.3);
    position: relative;
}
.coach-box::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, rgba(100,180,255,0.4), transparent);
}
.coach-box h4 {
    color: #7dc3ff;
    margin: 0 0 12px 0;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.coach-box b { color: #a8d4ff; }
.coach-box em { color: #fbbf24; font-style: normal; font-weight: 600; }

/* Efficiency banner */
.efficiency-banner {
    background: linear-gradient(90deg, #1a1a2e, #e94560, #ffa500, #00c853, #1a1a2e);
    background-size: 400% 400%;
    animation: gradient-shift 8s ease infinite;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin-bottom: 16px;
}
@keyframes gradient-shift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Star badge */
.star-badge {
    background: linear-gradient(135deg, #ffd700, #ffb300);
    color: #1a1a2e;
    border-radius: 20px;
    padding: 8px 20px;
    display: inline-block;
    font-weight: 700;
    font-size: 15px;
    margin: 6px 0;
}

/* Tables */
.stDataFrame { border-radius: 8px; overflow: hidden; }

/* Expander */
.streamlit-expanderHeader {
    background: rgba(30,30,60,0.8);
    border-radius: 8px;
    color: #e0e0e0;
}

/* Section headers */
.section-header {
    background: linear-gradient(90deg, rgba(233,69,96,0.3), transparent);
    padding: 10px 16px;
    border-radius: 8px;
    margin: 12px 0 8px 0;
    font-size: 16px;
    font-weight: 700;
    color: #fff;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #1a1a2e; }
::-webkit-scrollbar-thumb { background: #e94560; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ─── Load Data ───
@st.cache_data(ttl=300)
def load_all_data():
    data = {}
    files = {
        "analysis": "data/analysis.json",
        "analysis_30d": "data/analysis_30d.json",
        "arrears": "data/arrears_analysis.json",
        "overdue_sop": "data/overdue_sop_status.json",
        "action_items_file": "data/action_items.json",
        "graph_tasks": "data/graph_tasks.json",
        "vendors": "data/vendor_database.json",
        "supply_chain": "data/supply_chain_network.json",
        "contacts": "data/contacts_database.json",
        "deep_insights": "data/deep_insights.json",
        "deep_patterns": "data/deep_patterns.json",
        "us_consignee": "data/us_consignee_database.json",
    }
    for key, path in files.items():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data[key] = json.load(f)
        except Exception:
            data[key] = {}
    return data


DATA = load_all_data()
A = DATA.get("analysis", {})
A30 = DATA.get("analysis_30d", {})
ARR = DATA.get("arrears", {})
SOP = DATA.get("overdue_sop", {})
VDB = DATA.get("vendors", {})
SCN = DATA.get("supply_chain", {})
CON = DATA.get("contacts", {})
DI = DATA.get("deep_insights", {})
DP = DATA.get("deep_patterns", {})
USC = DATA.get("us_consignee", {})
AIF = DATA.get("action_items_file", [])
if isinstance(AIF, dict):
    AIF = []
GT = DATA.get("graph_tasks", {})
GT_TASKS = GT.get("tasks", []) if isinstance(GT, dict) else []

# ─── Derived data ───
bl = A.get("bl_status", {})
anom = A.get("anomalies", {})
no_tlx_mbl = bl.get("no_tlx_mbl", [])
no_tlx_hbl = bl.get("no_tlx_hbl", [])
an_no_prealert = bl.get("an_no_prealert", [])
hold_bl = bl.get("hold_bl", [])
tlx_mbl_confirmed = bl.get("tlx_confirmed_mbl", 0)
tlx_hbl_confirmed = bl.get("tlx_confirmed_hbl", 0)

cancel_it = anom.get("cancel_it", [])
cod_list = anom.get("cod", [])
non_standard = anom.get("non_standard", [])
stolen = anom.get("stolen", [])
urgent = anom.get("urgent", [])

inspection_mbls = A.get("inspection_mbls", [])
hold_count = A.get("hold_count", 0)
inspection_count = A.get("inspection_count", 0)

# ─── Action Items 分类提取 ───
ai_holds = [x for x in AIF if x.get("type") == "hold"]
ai_inspections = [x for x in AIF if x.get("type") in ("inspection", "inspection_broker")]
ai_dd_alerts = [x for x in AIF if x.get("type") == "dd_alert"]
ai_empty_returns = [x for x in AIF if x.get("type") == "empty_return"]
ai_cc_confirms = [x for x in AIF if x.get("type") == "cc_confirm"]

# ─── General Order 提取(从urgent中分离) ───
general_order_items = []
urgent_non_go = []
for u in urgent:
    subj = u.get("subject", "") if isinstance(u, dict) else str(u)
    if "general order" in subj.lower() or "pending general order" in subj.lower():
        general_order_items.append(u)
    else:
        urgent_non_go.append(u)

# Compute efficiency score (平衡版 — 有挑战但不打击士气)
total_7d = A.get("total_emails", 0)
biz_7d = A.get("business_emails", 0)
overdue_count = A.get("overdue_count", 0)
cancel_count = A.get("cancel_count", 0)

# 基础分75
eff_score = 75

# 扣分项(重大风险扣分重,一般事务扣分轻)
risk_items = len(cancel_it) + len(stolen) + len(hold_bl) + hold_count + inspection_count + len(general_order_items)
eff_score -= hold_count * 2              # Hold每个扣2分
eff_score -= len(stolen) * 10            # 被盗扣10分(严重!)
eff_score -= len(an_no_prealert) * 5     # 漏单扣5分(严重!)
eff_score -= overdue_count               # Overdue每封扣1分
eff_score -= cancel_count                # Cancel每个扣1分
eff_score -= len(general_order_items) * 8  # GO每个扣8分(CBP没收风险!)
# 未电放MBL: 只有超过50%未电放才扣分(12h窗口内大部分未电放是正常的)
tlx_rate = 1 - (len(no_tlx_mbl) / max(len(no_tlx_mbl) + bl.get('tlx_confirmed_mbl',0), 1))
if tlx_rate < 0.5: eff_score -= 5       # 电放率低于50%才扣5分

# 加分项
if biz_7d > 50: eff_score += 3          # 业务量达标+3
if biz_7d > 100: eff_score += 2         # 业务量优秀再+2
if overdue_count == 0: eff_score += 8   # 零Overdue+8
if hold_count == 0: eff_score += 5      # 零Hold+5
if inspection_count == 0: eff_score += 3 # 零查验+3
if len(cancel_it) == 0: eff_score += 2  # 零Cancel+2
if len(stolen) == 0: eff_score += 2     # 零失窃+2

eff_score = max(0, min(100, eff_score))


# ─── Helper functions ───
def metric_card(value, label, color="#e94560"):
    return f"""<div class="metric-card">
        <h2 style="color:{color}">{value}</h2>
        <p>{label}</p>
    </div>"""


def coach_box(title, content):
    # Strip leading whitespace from each line to prevent markdown code block detection
    import textwrap
    clean_content = textwrap.dedent(content).strip()
    html = f'<div class="coach-box"><h4>{title}</h4>{clean_content}</div>'
    st.markdown(html, unsafe_allow_html=True)


def section_header(text):
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


def clean_html(text):
    """Remove invalid characters that cause JavaScript errors in Streamlit."""
    if not isinstance(text, str):
        text = str(text)
    # Remove control characters (except newline/tab)
    import unicodedata
    cleaned = ''.join(c for c in text if unicodedata.category(c)[0] != 'C' or c in '\n\t')
    # Escape HTML special chars in user data
    cleaned = cleaned.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return cleaned

def alert_card(style, content):
    st.markdown(f'<div class="alert-{style}">{content}</div>', unsafe_allow_html=True)


def parse_sender_name(raw):
    """Extract clean name from email sender string."""
    if not raw:
        return raw
    match = re.match(r'"?([^"<]+)"?\s*<', raw)
    if match:
        return match.group(1).strip().strip('"')
    if "@" in raw:
        return raw.split("@")[0]
    return raw


# ─── Title Banner ───
scan_time = A.get("scan_time", "")
st.markdown(f"""
<div style="text-align:center; padding:20px 0 10px 0;">
    <h1 style="color:#fff; font-size:28px; margin:0;">
        WWL 环世物流 运营指挥中心 <span style="color:#e94560;">v5.0</span>
    </h1>
    <p style="color:#a0a0c0; font-size:13px; margin:4px 0 0 0;">
        数据更新: {scan_time[:19] if scan_time else "N/A"} &nbsp;|&nbsp;
        7日邮件: {total_7d} &nbsp;|&nbsp;
        30日邮件: {A30.get("total_emails", 0):,} &nbsp;|&nbsp;
        MBL: {A.get("mbl_total", 0)} &nbsp;|&nbsp;
        HBL: {A.get("hbl_total", 0)}
    </p>
</div>
""", unsafe_allow_html=True)

# ─── TABS ───
tabs = st.tabs([
    "风险与紧急事项",
    "提单状态监控",
    "催收与欠费",
    "团队任务看板",
    "趋势与效率",
    "客户全景",
    "供应商全景",
    "船公司全景",
    "目的港全景",
    "联系人搜索",
])

# ══════════════════════════════════════════════════════════════════
# TAB 1: 风险+紧急+异常预警
# ══════════════════════════════════════════════════════════════════
with tabs[0]:
    # Efficiency banner
    eff_color = "#00c853" if eff_score >= 80 else ("#ffa500" if eff_score >= 60 else "#e94560")
    st.markdown(f"""
    <div class="efficiency-banner">
        <span style="font-size:40px; font-weight:700; color:white;">{eff_score}</span>
        <span style="font-size:16px; color:rgba(255,255,255,0.8);"> / 100 运营效率评分</span><br>
        <span style="font-size:13px; color:rgba(255,255,255,0.7);">
            评分标准(严格版): 基础70分 | 扣分: Hold-3/Overdue-2/未电放-1/漏单-5/Cancel-1 | 加分: 零Overdue+10/零Hold+8/全电放+5 | 当前风险事件{risk_items}项
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── General Order 置顶(CBP没收风险, 最高优先级) ──
    import re as _re
    if general_order_items:
        section_header(f"General Order 警告: {len(general_order_items)}件 — CBP即将没收货物!")
        _go_mbls_seen = set()
        for item in general_order_items:
            subj = item.get("subject", "") if isinstance(item, dict) else str(item)
            frm = item.get("from", "") if isinstance(item, dict) else ""
            dt = item.get("date", "") if isinstance(item, dict) else ""
            _mbl_match = _re.search(r'(MEDU[A-Z0-9]+|COSU[0-9]+|OOLU[0-9]+|ONEY[A-Z0-9]+|ZIMU[A-Z0-9]+|CMDU[A-Z0-9]+|HLCU[A-Z0-9]+)', str(subj))
            _go_mbl = _mbl_match.group(1) if _mbl_match else ""
            if _go_mbl and _go_mbl in _go_mbls_seen:
                continue
            if _go_mbl:
                _go_mbls_seen.add(_go_mbl)
            # 从action_items中找到对应的客户和Hold信息
            _go_customer = ""
            _go_carrier = ""
            for ai in ai_holds:
                if ai.get("mbl") == _go_mbl:
                    _go_customer = ai.get("customer", "")
                    _go_carrier = ai.get("carrier", "")
                    break
            alert_card("red", f"""
                <b style='font-size:16px;'>GENERAL ORDER 没收警告</b> [{_go_mbl}]<br>
                客户: <b>{clean_html(_go_customer)}</b> | 船公司: <b>{clean_html(_go_carrier)}</b><br>
                主题: {clean_html(subj)}<br>来源: {clean_html(frm)} | 日期: {dt}<br><br>
                <b>什么是General Order:</b> CBP通知货物超过15天未清关, 即将进入GO状态。
                GO = 货物被美国海关接管, 转入政府监管仓库, 15天后可被拍卖或销毁。
                一旦进入GO, 除了货值损失, 还有GO仓储费($75-150/天)、处理费($500-2,000)、
                且会在CBP系统留下不良记录, 影响WWL作为NVOCC的合规评级。<br><br>
                <b>紧急处理链(24h内必须行动):</b><br>
                1) Everlyn立即确认该票当前清关状态 — 是否已提交7501? 报关行(YES/WFS)卡在哪一步?<br>
                2) 如果是Customs Hold导致: 补齐CBP要求的文件(ISF/PI/PL/HS Code证明)<br>
                3) 如果是Freight Hold导致: Sven立即通过PayCargo付清运费, 解除Hold拿到DO<br>
                4) 如果是客户弃货: Bruce决策 — 是追偿客户还是安排退运(退运费$3,000-8,000)<br>
                5) 同步通知origin和客户({clean_html(_go_customer)}), 邮件留痕记录所有行动<br>
                <b>关键时效:</b> GO通知后15天内不处理 = 货物永久丧失。这不是警告, 是最后通牒。
            """)
        st.markdown("---")

    # ═══ 预判预警(比人早一步) ═══
    _pred_path = 'data/predictions.json'
    try:
        with open(_pred_path) as _pf:
            _pred = json.load(_pf)
        _pred_list = _pred.get('predictions', [])
        _pred_critical = _pred.get('critical', 0)
        _pred_urgent = _pred.get('urgent', 0)
        _pred_total = _pred.get('total', 0)
    except:
        _pred_list = []
        _pred_critical = _pred_urgent = _pred_total = 0

    if _pred_list:
        section_header(f"预判预警: {_pred_total}条 (危急{_pred_critical} 紧急{_pred_urgent})")
        _shown = 0
        for p in _pred_list:
            if _shown >= 15:
                break
            sev = p.get('severity', '')
            color = 'red' if sev == 'critical' else 'orange' if sev == 'urgent' else 'yellow'
            sev_cn = '危急' if sev == 'critical' else '紧急' if sev == 'urgent' else '重要'
            ptype = p.get('type', '')
            type_cn = {
                'eta_overdue': 'ETA已过期未电放', 'eta_approaching': 'ETA即将到港',
                'eta_warning': 'ETA临近', 'freetime_expired': 'Free Time已超期',
                'freetime_urgent': 'Free Time即将到期', 'collection_sinosure': '催收-中信保窗口',
                'collection_legal': '催收-需追偿函', 'collection_escalate': '催收-需升级',
                'hold_overdue': 'Hold超期', 'inspection_overdue': '查验超期',
                'no_response': '48h未回复', 'invoice_overdue': '发票已过期',
                'invoice_due_soon': '发票即将到期',
            }.get(ptype, ptype)
            alert_card(color, f"""
                <b>[{sev_cn}] {type_cn}</b> | {p.get('mbl','')[:20]} | {p.get('customer','')[:15]} {p.get('carrier','')}<br>
                {p.get('message','')}<br>
                <b>行动:</b> {p.get('action','')}
            """)
            _shown += 1
        if _pred_total > 15:
            alert_card("yellow", f"还有 {_pred_total - 15} 条预警未展示")

    st.markdown("---")

    # ═══ 对话追踪: 谁在等谁 ═══
    _conv_path = 'data/conversation_status.json'
    try:
        with open(_conv_path) as _cf:
            _conv = json.load(_cf)
        _wu = _conv.get('waiting_us', [])
        _wt = _conv.get('waiting_them', [])
        _pp = _conv.get('ping_pong', [])
        _cs = _conv.get('summary', {})
    except:
        _wu = _wt = _pp = []
        _cs = {}

    if _wu or _pp:
        section_header(f"对话追踪: 等我们{_cs.get('waiting_us',0)}条 | 等对方{_cs.get('waiting_them',0)}条 | 乒乓{_cs.get('ping_pong',0)}条")

        # 等我们回复(最紧急! 影响服务质量)
        if _wu:
            for p in _wu[:5]:
                hrs = p.get('hours_waiting', 0)
                color = 'red' if hrs >= 48 else 'orange'
                alert_card(color, f"""
                    <b>等我们回复 {hrs}小时!</b> | {p.get('customer','')[:15]} | MBL: {p.get('mbl','')[:25]}<br>
                    线程: {p.get('thread','')[:50]}<br>
                    <b>{p.get('last_sender','')}</b>在等我们 → 立即回复
                """)

        # 乒乓球对话(>5轮没解决)
        if _pp:
            for p in _pp[:3]:
                alert_card("yellow", f"""
                    <b>乒乓对话 {p.get('rounds',0)}轮/{p.get('days',0)}天</b> | {p.get('customer','')[:15]} | MBL: {p.get('mbl','')[:25]}<br>
                    线程: {p.get('thread','')[:50]}<br>
                    {p.get('parties',0)}方参与,邮件往返多轮未解决 → 考虑电话会议直接沟通
                """)

    st.markdown("---")

    # ── 四列概览: Hold / 查验 / CC待确认 / D&D ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        # 用action_items中的hold去重统计(比hold_count更准确)
        _hold_mbls = set()
        for h in ai_holds:
            m = h.get("mbl", "")
            if m:
                _hold_mbls.add(m)
        _real_hold_count = max(hold_count, len(_hold_mbls))
        section_header(f"Hold事件: {_real_hold_count}件")
        if ai_holds or hold_bl:
            # 按MBL合并Hold详情(同一MBL可能多种Hold类型)
            _hold_by_mbl = {}
            for h in ai_holds:
                m = h.get("mbl", "") or "未知MBL"
                if m not in _hold_by_mbl:
                    _hold_by_mbl[m] = {"types": [], "customer": h.get("customer", ""), "carrier": h.get("carrier", "")}
                _hold_by_mbl[m]["types"].append(h.get("hold_type", "unknown"))
            # 如果action_items为空, 回退到hold_bl
            if not _hold_by_mbl:
                for hb in hold_bl:
                    m = hb.get("mbl", "") if isinstance(hb, dict) else ""
                    _hold_by_mbl[m or "未知MBL"] = {"types": [hb.get("type", "unknown") if isinstance(hb, dict) else "unknown"], "customer": "", "carrier": ""}

            hold_details = []
            for m, info in _hold_by_mbl.items():
                types_str = "+".join(sorted(set(info["types"])))
                cust = info["customer"]
                carr = info["carrier"]
                label = f"[{m[:18]}]" if m != "未知MBL" else ""
                cust_label = f" 客户:{cust}" if cust else ""
                carr_label = f" {carr}" if carr else ""

                if "customs" in types_str:
                    hold_details.append(f"<b>Customs Hold{carr_label} {label}{cust_label}:</b> CBP扣留 → 确认7501状态 → 补文件(ISF/PI/PL) → 报关行YES/WFS跟进放行")
                elif "freight" in types_str:
                    hold_details.append(f"<b>Freight Hold{carr_label} {label}{cust_label}:</b> 运费未结 → 确认collect/prepaid → collect由Rita收集确认→Sven通过PayCargo当天付款; prepaid联系origin确认入账")
                elif "regulatory" in types_str:
                    hold_details.append(f"<b>Regulatory Hold{carr_label} {label}{cust_label}:</b> CBP监管扣留 → 联系报关行确认缺什么文件 → 补齐后3-5个工作日放行")
                else:
                    hold_details.append(f"<b>Hold{carr_label} {label}{cust_label}:</b> 类型待确认 → Everlyn联系船公司确认Hold原因")

            hold_html = "<br>".join(hold_details)
            alert_card("red", f"""
                <b>当前Hold: {_real_hold_count}票 / {len(_hold_by_mbl)}个MBL</b><br>
                {hold_html}<br><br>
                <b>成本:</b> Hold每天Demurrage $150-300 + Per Diem $50-100, 3天=$600-1,200。
                MSC系统通知延迟12-24h; OOCL Regulatory Hold最严格需全套文件。<br>
                <b>处理链:</b> Everlyn确认Hold类型 → Rita收集费用确认 → Sven执行付款(PayCargo/APLAX) → Effy跟进放行
            """)
        else:
            alert_card("green", "当前无Hold事件 - 状态良好")

    with c2:
        section_header(f"查验预警: {inspection_count}件")
        if inspection_count > 0:
            mbl_list = ", ".join(inspection_mbls[:5])
            # 从action_items获取查验客户详情
            _insp_customers = set()
            for ai in ai_inspections:
                c = ai.get("customer", "")
                if c:
                    _insp_customers.add(c)
            _insp_cust_str = ", ".join(_insp_customers) if _insp_customers else "待确认"

            # 检查Hold+查验双重风险
            hold_mbl_set = set(hb.get("mbl","") for hb in hold_bl if isinstance(hb, dict))
            hold_mbl_set.update(h.get("mbl","") for h in ai_holds if h.get("mbl"))
            double_risk = [m for m in inspection_mbls if m in hold_mbl_set]
            double_warn = f"<br><b style='color:#ff1744;'>双重风险! {', '.join(double_risk)} 同时Hold+查验, 延误+费用叠加!</b>" if double_risk else ""

            # 客户集中度风险
            cust_warn = ""
            if len(_insp_customers) == 1:
                cust_warn = f"<br><b style='color:#ffa500;'>集中度风险: {inspection_count}票查验全部来自{_insp_cust_str}, 需关注该客户商品是否被CBP列入重点名单</b>"

            alert_card("orange", f"""
                <b>被查验MBL:</b> {clean_html(mbl_list)}{double_warn}<br>
                <b>涉及客户:</b> {clean_html(_insp_cust_str)}{cust_warn}<br>
                <b>查验类型判断:</b> X-Ray($150-250, 1-2天) / 开门检查($500-1,500, 2-3天) / 全掏($1,000-2,500, 3-5天)<br>
                <b>处理链:</b> Effy联系报关行(YES/WFS)确认查验类型 → 新能源产品需MSDS+电池报告 → 通知客户延迟和费用 → 每天跟进 → 放行后立即安排提柜
            """)
        else:
            alert_card("green", "当前无查验事件 - 状态良好")

    with c3:
        cc_count = max(A.get("categories", {}).get("charge_confirm", 0), len(ai_cc_confirms))
        section_header(f"CC待确认: {cc_count}件")
        if cc_count > 0:
            # 从action_items提取CC涉及的船公司和客户
            _cc_carriers = set()
            _cc_customers = set()
            for cc in ai_cc_confirms:
                cr = cc.get("carrier", "")
                cu = cc.get("customer", "")
                if cr:
                    _cc_carriers.add(cr)
                if cu:
                    _cc_customers.add(cu)
            _cc_carr_str = ", ".join(_cc_carriers) if _cc_carriers else ""
            _cc_cust_str = ", ".join(_cc_customers) if _cc_customers else ""
            alert_card("yellow", f"""
                <b>费用确认待处理: {cc_count}件</b><br>
                {f'涉及船公司: {clean_html(_cc_carr_str)}<br>' if _cc_carr_str else ''}
                {f'涉及客户: {clean_html(_cc_cust_str)}<br>' if _cc_cust_str else ''}
                <b>费用来源:</b> PLT平台(assistant@pltplt.com)自动推送 → Everlyn核实 → 确认承担方<br>
                <b>三种费用处置:</b><br>
                - <b>Collect(到付):</b> 收货人承担 → Rita向consignee催收 → Sven通过PayCargo付船公司 → APLAX号审计追踪<br>
                - <b>Prepaid(预付):</b> 发货人已付origin → 确认入账即结案<br>
                - <b>Advanced(垫付):</b> WWL先垫付 → Sven付款出APLAX → 后续向客户追偿<br>
                <b>注意:</b> D/O fee(换单费$30-75)在SA中已指定CC/PP; 文件费一律不接受到付
            """)
        else:
            alert_card("green", "当前无CC待确认")

    with c4:
        dd_count = len(ai_dd_alerts)
        section_header(f"D&D费用预警: {dd_count}件")
        if dd_count > 0:
            # 从action_items提取D&D涉及的客户
            _dd_customers = set()
            _dd_carriers = set()
            for dd in ai_dd_alerts:
                c = dd.get("customer", "")
                cr = dd.get("carrier", "")
                if c:
                    _dd_customers.add(c)
                if cr:
                    _dd_carriers.add(cr)
            alert_card("orange", f"""
                <b>D&D费用预警: {dd_count}件</b><br>
                {f'涉及客户: {clean_html(", ".join(list(_dd_customers)[:5]))}<br>' if _dd_customers else ''}
                {f'涉及船公司: {clean_html(", ".join(list(_dd_carriers)[:5]))}<br>' if _dd_carriers else ''}
                <b>什么是D&D:</b> Demurrage(滞箱费, 码头未提柜) + Detention(滞期费, 提柜未还空柜)<br>
                <b>费用量级:</b> Demurrage $150-300/天, Detention $75-200/天, Per Diem $50-100/天<br>
                <b>OSRA 2022合规武器:</b> 船公司D&D账单必须包含19项要素(柜号/LFD/费率/计费天数等), 缺一项WWL有权争议不付<br>
                <b>处理链:</b> Everlyn核对费用明细 → 缺要素则发争议函 → 合规则确认承担方 → Sven付款
            """)
        else:
            alert_card("green", "当前无D&D费用预警")

    st.markdown("---")

    # ── 空柜归还跟踪(运营闭环) ──
    if ai_empty_returns:
        er_count = len(ai_empty_returns)
        # 按客户分组统计
        _er_by_customer = {}
        for er in ai_empty_returns:
            c = er.get("customer", "未知客户")
            _er_by_customer[c] = _er_by_customer.get(c, 0) + 1
        _er_summary = " | ".join([f"{c}: {n}柜" for c, n in sorted(_er_by_customer.items(), key=lambda x: -x[1])[:5]])

        section_header(f"空柜归还跟踪: {er_count}柜待还")
        alert_card("yellow", f"""
            <b>待还空柜: {er_count}个</b><br>
            <b>客户分布:</b> {clean_html(_er_summary)}<br>
            <b>风险:</b> 空柜未按时归还 = Detention费持续累积($75-200/天/柜)。
            归还前必须确认POD(签收单)已收到, 否则无法向客户出Debit Note结案。<br>
            <b>处理链:</b> 提柜后跟踪签收 → 确认POD已收到 → 催促空柜归还 → 归还后通知Maggie出Debit Note → 该票结案
        """)
        st.markdown("---")

    # ── 异常邮件预警 ──
    section_header("异常邮件预警")

    # Coach — 教练总结
    coach_box("教练总结: 当前风险全景与业务影响", f"""
        <b>General Order = 最高风险:</b> CBP通知货物即将被没收拍卖。{len(general_order_items)}票GO警告 =
        必须在15天内完成清关, 否则货值全损+GO仓储费+合规黑记录。GO的根源通常是Customs Hold未解决导致清关超时。<br><br>
        <b>Hold → 无DO → 无法提货 → 滞期费叠加:</b> Hold的本质是船公司扣住Delivery Order不放。
        没有DO, 卡车到码头也提不了柜。每天Demurrage $150-300 + Per Diem $50-100,
        3天=$600-1,200。Hold期间Free Time照样在跑, 双重叠加。
        Customs Hold(CBP扣留)比Freight Hold(运费未结)更难解, 需要补文件+等待CBP审批。<br><br>
        <b>查验的连锁反应:</b> CBP查验成本不只检查费$500-2,000。真正损失:
        1) 仓库排期被打乱(DDP客户需重新预约delivery slot);
        2) Free Time在查验期间不停表(除非申请extension);
        3) 新能源产品(太阳能板/锂电池)是2026年CBP 5H类重点对象, 查验率比普通货高3倍;
        4) 同一客户多票同时被查验 = CBP可能已将该供应商列入重点监控名单。<br><br>
        <b>当前活跃风险概况:</b> {len(general_order_items)}票GO(最高!) + {inspection_count}票查验 +
        {_real_hold_count}票Hold + {len(cancel_it)}个Cancel IT + {len(cod_list)}个COD + {dd_count}个D&D + {len(ai_empty_returns)}柜待还。
        环世FMC注册NVOCC(ORG NO.019194), 每一票处理质量直接影响合规评级和续牌。
    """)

    # Cancel IT
    if cancel_it:
        section_header(f"Cancel IT请求: {len(cancel_it)}件")
        _cancel_seen = set()
        for item in cancel_it:
            subj = item.get("subject", item) if isinstance(item, dict) else str(item)
            frm = item.get("from", "") if isinstance(item, dict) else ""
            _mbl_match = _re.search(r'(MEDU[A-Z0-9]+|COSU[0-9]+|OOLU[0-9]+|ONEY[A-Z0-9]+|ZIMU[A-Z0-9]+|CMDU[A-Z0-9]+|HLCU[A-Z0-9]+)', str(subj))
            _cancel_mbl = _mbl_match.group(1) if _mbl_match else ""
            if _cancel_mbl and _cancel_mbl in _cancel_seen:
                continue
            if _cancel_mbl:
                _cancel_seen.add(_cancel_mbl)
            alert_card("red", f"""
                <b>Cancel IT 请求</b> {f'[{_cancel_mbl}]' if _cancel_mbl else ''}<br>
                主题: {clean_html(subj)}<br>来源: {clean_html(frm)}<br>
                <b>背景:</b> IT号(In-Transit, 内陆转关)已由BTL平台(switchbl.com)提交给CBP。
                Cancel IT = 不走内陆转关, 改为在入境港直接清关。
                如果IT已提交但不及时取消, 货到港后CBP系统显示该票应走转关,
                会导致清关冲突, 可能触发CBP罚款或货物被扣。<br>
                <b>处理链:</b> 1) Everlyn查BTL系统确认IT状态;
                2) 已提交 → 报关行(YES/WFS)向CBP申请取消;
                3) 通知origin确认取消原因(通常是客户改为港口直提);
                4) 更新MBL进度, 确认后续清关路径<br>
                <b>时效:</b> 必须在ETA前完成取消
            """)
    else:
        alert_card("green", "无Cancel IT请求")

    # COD
    if cod_list:
        # COD去重
        _cod_seen = set()
        _cod_unique = []
        for item in cod_list:
            subj = item.get("subject", item) if isinstance(item, dict) else str(item)
            _mbl_match = _re.search(r'(MEDU[A-Z0-9]+|COSU[0-9]+|OOLU[0-9]+|ONEY[A-Z0-9]+|ZIMU[A-Z0-9]+|CMDU[A-Z0-9]+|HLCU[A-Z0-9]+)', str(subj))
            _cod_key = _mbl_match.group(1) if _mbl_match else subj[:30]
            if _cod_key not in _cod_seen:
                _cod_seen.add(_cod_key)
                _cod_unique.append(item)
        section_header(f"COD改港请求: {len(_cod_unique)}件(去重后)")
        for item in _cod_unique:
            subj = item.get("subject", item) if isinstance(item, dict) else str(item)
            frm = item.get("from", "") if isinstance(item, dict) else ""
            alert_card("orange", f"""
                <b>COD 改港/改目的地请求</b><br>
                主题: {clean_html(subj)}<br>来源: {clean_html(frm)}<br>
                <b>背景:</b> Change of Destination需船公司批准, 费用$500-3,000。
                不是所有航线都能改, 尤其转运港之后的改港可能被拒。<br>
                <b>处理链:</b> 确认原因 → Everlyn联系船公司报价 → 客户书面确认费用(邮件留痕!) →
                Sven付款 → 船公司执行 → 同步更新ISF(10+2申报跟着改)<br>
                <b>风险:</b> 卸港后提出COD, 船公司可能拒绝或收全程二次运费
            """)
    else:
        alert_card("green", "无COD改港请求")

    # Non-standard
    if non_standard:
        section_header(f"非标操作请求: {len(non_standard)}件")
        for item in non_standard:
            subj = item.get("subject", "") if isinstance(item, dict) else str(item)
            frm = item.get("from", "") if isinstance(item, dict) else ""
            typ = item.get("type", "") if isinstance(item, dict) else ""
            alert_card("yellow", f"""
                <b>非标操作请求</b> [{typ}]<br>
                主题: {clean_html(subj)}<br>来源: {clean_html(frm)}<br>
                <b>处理链:</b> Effy评估可行性+费用 → 客户书面确认 → Bruce/Will审批 → 全程邮件留痕(FMC合规)
            """)
    else:
        alert_card("green", "无非标操作请求")

    # Stolen/lost
    if stolen:
        section_header(f"失窃/丢失: {len(stolen)}件")
        for item in stolen:
            subj = item.get("subject", item) if isinstance(item, dict) else str(item)
            frm = item.get("from", "") if isinstance(item, dict) else ""
            alert_card("red", f"""
                <b>集装箱失窃/丢失</b><br>
                主题: {clean_html(subj)}<br>来源: {clean_html(frm)}<br>
                <b>紧急处理链(72h内必须启动):</b><br>
                1) Bruce决策: 报警(当地警局+FBI IC3跨州案件);<br>
                2) Effy启动保险索赔(BL原件/Invoice/PL/警方报告);<br>
                3) 通知客户(不承诺赔偿金额);<br>
                4) origin留存装箱证据(照片/封条号/GPS);<br>
                5) 高价值新能源产品同步通知中信保<br>
                <b>关键:</b> 72h是保险受理黄金窗口
            """)
    else:
        alert_card("green", "无失窃/丢失报告")

    # Urgent(已剔除GO)
    if urgent_non_go:
        section_header(f"紧急邮件: {len(urgent_non_go)}封")
        _sorted_urgent = sorted(urgent_non_go, key=lambda x: x.get("urgency", 0) if isinstance(x, dict) else 0, reverse=True)
        for item in _sorted_urgent[:10]:
            subj = item.get("subject", "")
            frm = item.get("from", "")
            urg_level = item.get("urgency", 0)
            dt = item.get("date", "")
            urg_label = "极高" if urg_level >= 4 else ("高" if urg_level >= 3 else "中")
            urg_color = "red" if urg_level >= 4 else ("orange" if urg_level >= 3 else "yellow")
            alert_card(urg_color, f"""
                <b>紧急邮件</b> [紧急度: {urg_label} ({urg_level}/5)]<br>
                主题: {clean_html(subj)}<br>来源: {clean_html(frm)}<br>日期: {dt}<br>
                <b>处理原则:</b> 先读正文判断实际紧急程度(标题可能夸大) →
                涉及Hold/查验→立即处理; 费用确认→24h内; 客户投诉→升级Bruce; 船公司通知→Everlyn归档
            """)
        if len(urgent_non_go) > 10:
            alert_card("yellow", f"还有 {len(urgent_non_go) - 10} 封紧急邮件未展示")
    else:
        alert_card("green", "无紧急邮件")

    # ── 重要操作跟踪(从graph_tasks动态生成) ──
    gt_ops = [t for t in GT_TASKS if t.get("type") not in ("arrears", "supplier_followup")]
    gt_suppliers = [t for t in GT_TASKS if t.get("type") == "supplier_followup"]
    if gt_ops:
        st.markdown("---")
        section_header(f"重要操作跟踪: {len(gt_ops)}项")

        gt_rows = []
        for t in gt_ops:
            mbl = t.get("mbl", "")
            carrier = t.get("carrier", "")
            customer = t.get("customer", "")
            action = t.get("action", "")
            detail = t.get("detail_lines", [])
            ctx = t.get("progress_history", "")
            last = t.get("last_seen", "")
            typ = t.get("type", "")

            # 类型中文名
            type_map = {
                "fee_pending": "费用待确认",
                "fee_confirmed": "费用已确认",
                "payment_requested": "已申请付款",
                "hold_active": "Hold处理中",
                "inspection_active": "查验处理中",
            }
            type_cn = type_map.get(typ, typ)

            # 业务摘要(合并detail_lines)
            summary = " | ".join(detail[:2]) if detail else ""

            gt_rows.append({
                "类型": type_cn,
                "MBL": mbl[:40],
                "船公司": carrier,
                "客户": customer[:20],
                "当前动作": action[:60],
                "业务摘要": summary[:80],
                "关联方": ctx[:40],
                "最后活跃": last,
            })

        gt_df = pd.DataFrame(gt_rows)
        st.dataframe(gt_df, use_container_width=True, hide_index=True, key="tbl_gt_ops")

    # 供应商跟进
    if gt_suppliers:
        section_header(f"供应商沟通跟进: {len(gt_suppliers)}家")
        sup_rows = []
        for t in gt_suppliers:
            sup_rows.append({
                "供应商": t.get("action", "").split("来信")[0].split("已报价")[0].split("确认完成")[0].strip(),
                "状态": t.get("action", ""),
                "最后联系": t.get("progress_history", ""),
            })
        sup_df = pd.DataFrame(sup_rows)
        st.dataframe(sup_df, use_container_width=True, hide_index=True, key="tbl_gt_sup")

    st.markdown("---")

    # ═══ 业务洞察 & 询报价追踪 ═══
    section_header("业务洞察 & 商机追踪")

    # 从DB实时提取询报价和业务机会(线上版无DB时跳过)
    _biz_conn = None
    try:
        import sqlite3 as _sq
        import os
        if os.path.exists('data/wwl_email_graph.db'):
            _biz_conn = _sq.connect('data/wwl_email_graph.db')
    except:
        pass
    _d7 = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    # 询报价统计
    _rfq_categories = []

    if not _biz_conn:
        alert_card("yellow", "业务洞察需要数据库支持(线上版暂不可用,数据来自最近一次扫描)")

    # Trucking fee
    _tc = _biz_conn.execute(f"SELECT COUNT(*) FROM emails WHERE date_parsed>='{_d7}' AND subject LIKE '%Trucking fee%'").fetchone()[0] if _biz_conn else 0
    if _tc > 0:
        _samples = _biz_conn.execute(f"SELECT sender_name, subject, substr(body,1,300) FROM emails WHERE date_parsed>='{_d7}' AND subject LIKE '%Trucking fee%' ORDER BY date_parsed DESC LIMIT 3").fetchall()
        _detail = []
        for s in _samples:
            body = (s[2] or '').replace('\r','').replace('\n',' ')[:120]
            _detail.append(f"{s[0] or ''}: {body}")
        _rfq_categories.append(('卡车报价', _tc, 'THORNOVA SOLAR(Ellen Jin)频繁询价多州DDP送货费 → 说明THORNOVA业务量在增长, 且依赖我们安排内陆运输。这是持续收入来源,建议锁定长期合约价。', _detail))

    # Air freight
    _ac = _biz_conn.execute(f"SELECT COUNT(*) FROM emails WHERE date_parsed>='{_d7}' AND (subject LIKE '%Air Freight%' OR subject LIKE '%air rate%')").fetchone()[0]
    if _ac > 0:
        _samples = _biz_conn.execute(f"SELECT sender_name, subject, substr(body,1,300) FROM emails WHERE date_parsed>='{_d7}' AND (subject LIKE '%Air Freight%' OR subject LIKE '%air rate%') ORDER BY date_parsed DESC LIMIT 2").fetchall()
        _detail = [f"{s[0] or ''}: {(s[2] or '').replace(chr(13),'').replace(chr(10),' ')[:120]}" for s in _samples]
        _rfq_categories.append(('空运询价', _ac, '泰国线(BKK)有空运需求 → PTS(Sam Kim)提供中华航空JFK→TPE→BKK报价$2.75/KG。空运是高利润业务,如果能拿到稳定货量值得投入。关注客户是否因海运延误才转空运(一次性)还是常态需求。', _detail))

    # Transload/FTL
    _tlc = _biz_conn.execute(f"SELECT COUNT(*) FROM emails WHERE date_parsed>='{_d7}' AND (subject LIKE '%Transload%' OR subject LIKE '%FTL%' OR body LIKE '%transload%flatbed%')").fetchone()[0]
    if _tlc > 0:
        _samples = _biz_conn.execute(f"SELECT sender_name, subject, substr(body,1,300) FROM emails WHERE date_parsed>='{_d7}' AND (subject LIKE '%Transload%' OR subject LIKE '%FTL%') AND sender_email NOT LIKE '%pltplt%' ORDER BY date_parsed DESC LIMIT 2").fetchall()
        _detail = [f"{s[0] or ''}: {(s[2] or '').replace(chr(13),'').replace(chr(10),' ')[:120]}" for s in _samples]
        _rfq_categories.append(('Transload拆箱+FTL', _tlc, 'Effy在找FCC USA(Flora Wang)报价LA仓库transload+flatbed到TX。Transload是增值服务(不只是换单),利润比纯换单高2-3倍。FCC USA是我们最核心的综合供应商(2555次互动),已有成熟合作基础。', _detail))

    # BESS大件
    _bc = _biz_conn.execute(f"SELECT COUNT(*) FROM emails WHERE date_parsed>='{_d7}' AND (body LIKE '%BESS%' AND (subject LIKE '%Trucking%' OR body LIKE '%trucking%'))").fetchone()[0]
    if _bc > 0:
        _rfq_categories.append(('BESS储能大件', _bc, 'HITHIUM(海辰)BESS储能单元42T/台,需9轴特种车。这是新能源赛道高价值货物,单票利润远超普通集装箱。但客户自带trucker(Yancey: "my trucker"),我们目前只做清关+费用代收。机会:如果能拿下trucking也做,利润翻倍。', []))

    # EXW
    _ec = _biz_conn.execute(f"SELECT COUNT(*) FROM emails WHERE date_parsed>='{_d7}' AND subject LIKE '%EX WORK%'").fetchone()[0]
    if _ec > 0:
        _samples = _biz_conn.execute(f"SELECT sender_name, subject FROM emails WHERE date_parsed>='{_d7}' AND subject LIKE '%EX WORK%' ORDER BY date_parsed DESC LIMIT 2").fetchall()
        _detail = [f"{s[0]}: {s[1][:60]}" for s in _samples]
        _rfq_categories.append(('EXW工厂提货', _ec, 'Wang Jiong在催供应商报价,说明有客户需要从美国工厂直接提货的需求(EXW=Ex Works)。这类业务通常是出口或内陆调拨,如果频繁出现说明客户在扩大美国本地采购。', _detail))

    # Export booking
    _xc = _biz_conn.execute(f"SELECT COUNT(*) FROM emails WHERE date_parsed>='{_d7}' AND (subject LIKE '%export%Mombasa%' OR subject LIKE '%出口%' OR (subject LIKE '%BKG%' AND body LIKE '%export%'))").fetchone()[0]
    if _xc > 0:
        _rfq_categories.append(('出口新航线', _xc, '昊能(HOUNEN SOLAR)询价3×40HQ出口到蒙巴萨(肯尼亚)。非洲太阳能市场是2026年增长最快的区域,如果昊能开拓非洲线,后续会有持续货量。建议:给出有竞争力的报价锁定这个新航线。', []))

    # HAZMAT
    _hc = _biz_conn.execute(f"SELECT COUNT(*) FROM emails WHERE date_parsed>='{_d7}' AND (subject LIKE '%HAZMAT%' OR subject LIKE '%Class 9%')").fetchone()[0]
    if _hc > 0:
        _rfq_categories.append(('HAZMAT危险品清关', _hc, 'TQL(美国大型3PL)发来Class 9危险品CES查验清关RFQ。这是专业门槛高的业务,竞争少利润厚。如果拿下,打开HAZMAT清关新赛道。TQL作为大型3PL,后续可能有持续的HAZMAT货量。', []))

    # JEE Tesla
    _jc = _biz_conn.execute(f"SELECT COUNT(*) FROM emails WHERE date_parsed>='{_d7}' AND (body LIKE '%JEE%' OR body LIKE '%devanning%Tesla%')").fetchone()[0]
    if _jc > 0:
        _rfq_categories.append(('JEE→Tesla拆箱配送', _jc, 'JEE的LA/LB→Texas Tesla工厂拆箱配送新一轮竞标。当前市场底价$1,800/柜。Will在评估是否继续报价。Tesla供应链是长期大客户,即使利润薄也值得维持关系。', []))

    (_biz_conn.close() if _biz_conn else None)

    if _rfq_categories:
        coach_box("业务洞察: 从邮件中发现的商机信号", f"""
            <b>本周{sum(c[1] for c in _rfq_categories)}封询报价/业务机会邮件</b>,覆盖{len(_rfq_categories)}个业务方向。
            每一封询报价都是客户在告诉我们"我有需求" — 响应速度和报价质量直接决定能否拿到业务。<br><br>
            <b>关注重点:</b> 不是所有询价都值得全力投入。高利润(Transload/HAZMAT/BESS大件) > 持续性(DDP送货/出口新航线) > 一次性(EXW/空运)。
            对高利润业务要快速响应;对持续性业务要锁定长期合约;对一次性业务评估ROI后再决定。
        """)

        for cat_name, cnt, insight, details in _rfq_categories:
            alert_card("yellow", f"""
                <b>{cat_name}</b> — 本周{cnt}封<br><br>
                <b>洞察:</b> {insight}<br>
                {'<br><b>最新动态:</b><br>' + '<br>'.join(f'- {d[:150]}' for d in details[:2]) if details else ''}
            """)
    else:
        alert_card("green", "本周无新询报价/业务机会")

    st.markdown("---")

# ══════════════════════════════════════════════════════════════════
# TAB 2: 提单状态监控
# ══════════════════════════════════════════════════════════════════
with tabs[1]:
    section_header("提单状态总览")

    coach_box("教练总结: 提单生命周期 — 从预报到结案的完整链路", f"""
        <b>MBL是索引, HBL才是核心。</b> 但MBL的TLX(Telex Release/电放)是整个换单流程的前提:
        MBL未电放 → 无法在BTL/PLT平台换单 → 拿不到HBL → 无法清关 → 无法提货。
        每一个未电放的MBL都是一个正在累积成本的定时炸弹。<br><br>
        <b>换单流程:</b> Origin发SA(预报) → MBL电放(SWB/Surrendered) → BTL平台(switchbl.com)换出HBL →
        HBL电放给consignee → 报关行(YES/WFS)用HBL清关 → 船公司发AN(到港通知) →
        付费拿DO → 安排卡车提柜 → Delivery → 结案<br><br>
        <b>两种MBL模式:</b><br>
        - <b>BTL模式:</b> MBL consignee是BTL → 通过switchbl.com换单 → 大部分票走这个流程<br>
        - <b>WWL USA直接模式:</b> MBL consignee是WWL USA → 我们直接操作, 不经过BTL<br><br>
        <b>AN已收但无预报 = 最危险的漏单信号:</b> 船公司已通知到港, 但我们系统无记录。
        两种可能: 1) origin忘发SA(催origin补发); 2) 我们漏处理了(查收件箱)。
        漏单=客户的货在码头没人管, 滞期费从Day 1开始跑, 且可能影响WWL在船公司的信用评级。<br><br>
        <b>当前状态:</b> {len(no_tlx_mbl)}个MBL未电放 / {len(no_tlx_hbl)}个HBL未电放 /
        {len(an_no_prealert)}个AN无预报(漏单风险) / {len(hold_bl)}个Hold /
        电放确认MBL:{tlx_mbl_confirmed} HBL:{tlx_hbl_confirmed}<br>
        <b>目标:</b> MBL电放率>95%, HBL电放率>90%, AN无预报=0, Hold提单24h内有行动方案。
    """)


    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card(len(no_tlx_mbl), "MBL未电放", "#e94560"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card(len(no_tlx_hbl), "HBL未电放", "#ffa500"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card(len(an_no_prealert), "AN无预报(漏单!)", "#ff1744"), unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card(len(hold_bl), "Hold提单", "#e94560"), unsafe_allow_html=True)

    c5, c6 = st.columns(2)
    with c5:
        st.markdown(metric_card(tlx_mbl_confirmed, "已确认TLX MBL", "#00c853"), unsafe_allow_html=True)
    with c6:
        st.markdown(metric_card(tlx_hbl_confirmed, "已确认TLX HBL", "#00c853"), unsafe_allow_html=True)

    st.markdown("---")

    # MBL not TLX
    section_header(f"MBL未电放列表 ({len(no_tlx_mbl)}个)")
    if no_tlx_mbl:
        def _mbl_carrier(m):
            if m.startswith("MEDU"): return "MSC"
            if m.startswith("CMDU"): return "CMA-CGM"
            if m.startswith("COSU"): return "COSCO"
            if m.startswith("ONEY"): return "ONE"
            if m.startswith("OOLU"): return "OOCL"
            if m.startswith("ZIMU"): return "ZIM"
            if m.startswith("HLCU"): return "Hapag-Lloyd"
            if m.startswith("YMJA"): return "YML(阳明)"
            if m.startswith("WHLC"): return "WHL(万海)"
            if m.startswith("HDMU"): return "HMM(韩新)"
            if m.startswith("MAEU"): return "Maersk"
            return "其他"
        def _mbl_action(m):
            c = _mbl_carrier(m)
            if c == "MSC": return "联系origin催TLX → MSC电放后通过BTL平台换单 → MSC系统通知常延迟12-24h"
            if c == "CMA-CGM": return "联系origin催TLX → CMA通过BTL换单 → 注意CMA Hold释放需BTL平台确认"
            if c == "COSCO": return "联系origin催TLX → COSCO电放后BTL换单 → COSCO系统相对稳定"
            if c == "OOCL": return "联系origin催TLX → OOCL直接模式或BTL换单 → OOCL Regulatory Hold最严格"
            if c == "ONE": return "联系origin催TLX → ONE通过BTL换单 → ONE系统响应较快"
            if c == "ZIM": return "联系origin催TLX → ZIM通过BTL换单 → ZIM的AN通常在ETA前3天发"
            if c == "Hapag-Lloyd": return "联系origin催TLX → HL通过BTL换单 → HL系统稳定但费用结构复杂"
            return "联系origin确认TLX状态 → 确认换单路径(BTL/直接)"
        mbl_df = pd.DataFrame({
            "序号": range(1, len(no_tlx_mbl) + 1),
            "MBL号": no_tlx_mbl,
            "船公司": [_mbl_carrier(m) for m in no_tlx_mbl],
            "建议行动": [_mbl_action(m) for m in no_tlx_mbl],
        })
        st.dataframe(mbl_df, use_container_width=True, hide_index=True, key="tbl_1")
    else:
        alert_card("green", "所有MBL已完成电放 - 优秀!")

    # HBL not TLX
    section_header(f"HBL未电放列表 ({len(no_tlx_hbl)}个)")
    if no_tlx_hbl:
        hbl_df = pd.DataFrame({
            "序号": range(1, len(no_tlx_hbl) + 1),
            "HBL号": no_tlx_hbl,
            "建议行动": [
                "确认对应MBL是否已电放 → MBL未放则先催MBL → MBL已放则通过BTL/PLT平台出HBL → HBL电放给consignee后报关行才能清关"
            ] * len(no_tlx_hbl),
        })
        st.dataframe(hbl_df, use_container_width=True, hide_index=True, key="tbl_2")
    else:
        alert_card("green", "所有HBL已完成电放 - 优秀!")

    # AN no prealert
    section_header(f"AN已收但无预报 - 可能漏单! ({len(an_no_prealert)}个)")
    if an_no_prealert:
        def _an_action(m):
            c = _mbl_carrier(m) if 'no_tlx_mbl' in dir() else ""
            return (f"漏单风险! 1) 搜索收件箱查SA预报邮件; "
                    f"2) 联系origin确认是否有对应HBL和SA; "
                    f"3) 如确认有业务立即补录系统; "
                    f"4) AN意味着船已到港, Free Time已开始倒计时!")
        an_df = pd.DataFrame({
            "序号": range(1, len(an_no_prealert) + 1),
            "MBL号": an_no_prealert,
            "船公司": [_mbl_carrier(m) for m in an_no_prealert],
            "风险等级": ["极高-漏单"] * len(an_no_prealert),
            "建议行动": [_an_action(m) for m in an_no_prealert],
        })
        st.dataframe(an_df, use_container_width=True, hide_index=True, key="tbl_3")
    else:
        alert_card("green", "所有AN均有对应预报 - 无漏单风险")

    # Hold BL
    section_header(f"Hold提单 ({len(hold_bl)}个)")
    if hold_bl:
        hold_rows = []
        for h in hold_bl:
            htype = str(h.get("type", "")).lower()
            hmbl = h.get("mbl", "")
            carrier = _mbl_carrier(hmbl)
            if "freight" in htype:
                action = f"Freight Hold → 确认费用是collect还是prepaid: collect由Sven通过PayCargo付款(当天解除); prepaid联系origin提供付款凭证给{carrier}"
            elif "regulatory" in htype:
                action = f"Regulatory Hold → 联系报关行确认CBP要求的具体文件 → 新能源产品需MSDS+电池报告 → {carrier}的Regulatory Hold通常需全套文件才放行(3-5天)"
            elif "do" in htype or "fee" in htype:
                action = f"DO Fee Hold → Sven通过PayCargo付目的港费用 → 付款确认后联系{carrier}释放DO → 通常当天可解决"
            else:
                action = f"Hold类型待确认 → Everlyn联系{carrier}确认具体Hold原因和所需文件"
            hold_rows.append({
                "MBL": hmbl,
                "船公司": carrier,
                "Hold类型": h.get("type", "Unknown"),
                "来源": h.get("from", ""),
                "建议行动": action,
            })
        hold_df = pd.DataFrame(hold_rows)
        st.dataframe(hold_df, use_container_width=True, hide_index=True, key="tbl_4")
    else:
        alert_card("green", "当前无Hold提单 - 状态良好")



# ══════════════════════════════════════════════════════════════════
# TAB 3: 催收与欠费
# ══════════════════════════════════════════════════════════════════
with tabs[2]:
    section_header("欠费总览")

    coach_box("教练总结: 催收 — WWL作为NVOCC的连带责任防线", """
        <b>为什么催收不是可选项:</b> WWL作为FMC注册NVOCC(ORG NO.019194), 对所有目的港费用承担连带责任。
        Consignee(收货人, 即客户的客户)不付费, 船公司直接向WWL追偿。
        这就是为什么每一笔collect费用都必须及时催收 — 不是帮客户催, 是保护我们自己。<br><br>
        <b>T+X催收时间线(铁律):</b><br>
        - T+7: Rita首次催收(邮件+电话), 建立催收记录<br>
        - T+15: Maggie升级催收, 建立三方协同群(origin+客户+我们), 发正式催款通知<br>
        - T+30: 正式追偿函(Legal Letter), Will审批, 邮件留痕<br>
        - T+45: 中信保理赔窗口! 超过此期限=理赔资格失效, 公司自行承担损失<br>
        - T+60: 法律途径(如金额超过$5,000, 考虑Small Claims Court或委托律师)<br><br>
        <b>中信保申请四件套(缺一不可):</b><br>
        1) 服务协议(含费用承担条款 — 证明是谁该付钱);<br>
        2) 书面费用通知(含7日默认认可条款 — 证明我们通知了);<br>
        3) 完整催收记录(邮件链 — 证明我们尽力催了);<br>
        4) 垫付凭证(APLAX付款号 — 证明我们确实垫了)<br><br>
        <b>费用类型与催收路径:</b><br>
        - <b>Collect到付:</b> Consignee承担 → Rita/Maggie催consignee → 确认后Sven付船公司(PayCargo)<br>
        - <b>Prepaid预付:</b> Shipper已付origin → 确认入账即结案<br>
        - <b>Advanced垫付:</b> WWL先付(Sven执行, APLAX号追踪) → 后续向客户追偿 → 这是最大风险点<br><br>
        <b>2026行业动态:</b> FMC强化OSRA 2022执法, 船公司D&D账单必须包含19项要素(按46 CFR 541),
        缺少任何要素我们有权在30天争议期内提出异议不付。所有记录保留5年供FMC审计。
    """)

    st.markdown("---")

    total_arrears = ARR.get("total_amount", 0)
    by_sheet = ARR.get("by_sheet", {})
    cnee_self = by_sheet.get("收货人自付", {}).get("total", 0)
    shipper_bear = by_sheet.get("委托人承担", {}).get("total", 0)
    collect_cnee = by_sheet.get("代收-收货人", {}).get("total", 0)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card(f"${total_arrears:,.0f}", "总欠费", "#e94560"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card(f"${cnee_self:,.0f}", "收货人自付", "#ffa500"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card(f"${shipper_bear:,.0f}", "委托人承担", "#2196f3"), unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card(f"${collect_cnee:,.0f}", "代收-收货人", "#9c27b0"), unsafe_allow_html=True)

    st.markdown("---")

    # Overdue SOP table
    section_header("重点催收跟踪 (Overdue SOP)")
    if SOP:
        sop_rows = []
        for name, info in SOP.items():
            if isinstance(info, dict):
                # Build the Rita/Maggie/Will action column by combining available info
                actions_parts = []
                if info.get("maggie_action"):
                    actions_parts.append(info["maggie_action"])
                if info.get("jim_action"):
                    actions_parts.append(f"Jim: {info['jim_action']}")
                if info.get("will_sun"):
                    actions_parts.append(f"Will: {info['will_sun']}")
                combined_action = " | ".join(actions_parts) if actions_parts else "-"

                # Build suggested next action
                next_action_parts = []
                if info.get("sinosure_ready"):
                    next_action_parts.append(info["sinosure_ready"])
                if info.get("pending"):
                    next_action_parts.append(info["pending"])
                if info.get("resolution"):
                    next_action_parts.append(info["resolution"])
                if not next_action_parts:
                    next_action_parts.append("持续跟进")
                next_action = " | ".join(next_action_parts)

                sop_rows.append({
                    "客户": name,
                    "提单": info.get("mbl", ""),
                    "金额": info.get("amount", ""),
                    "Rita/Maggie/Will行动": combined_action,
                    "T+X状态": info.get("t_status", ""),
                    "建议后续行动": next_action,
                    "风险": info.get("risk", ""),
                })
        if sop_rows:
            sop_df = pd.DataFrame(sop_rows)
            st.dataframe(sop_df, use_container_width=True, hide_index=True, key="tbl_5")

    st.markdown("---")

    # TOP 15 arrears
    section_header("TOP 15 欠费客户")
    top20 = ARR.get("top20", [])
    if top20:
        top_rows = []
        for i, item in enumerate(top20[:15]):
            risk = item.get("risk", "未评估")
            suggested = (
                "紧急催收! 发正式追偿函, 准备中信保材料"
                if "高" in risk
                else "常规催收, 发催款邮件并跟进"
                if "中" in risk
                else "观察, 低优先级"
            )
            top_rows.append({
                "排名": i + 1,
                "客户名称": item.get("name", ""),
                "欠费金额": f"${item.get('total', 0):,.0f}",
                "记录数": item.get("records", 0),
                "风险等级": risk,
                "费用类型": ", ".join(list(item.get("sheets", []))),
                "建议行动": suggested,
            })
        top_df = pd.DataFrame(top_rows)
        st.dataframe(top_df, use_container_width=True, hide_index=True, key="tbl_6")


# ══════════════════════════════════════════════════════════════════
# TAB 4: 团队任务看板
# ══════════════════════════════════════════════════════════════════
with tabs[3]:
    section_header("团队任务看板")

    # Star Employee/Manager (rotate by week number)
    week_num = datetime.now().isocalendar()[1]
    employees = ["Everlyn", "Rita", "Maggie"]
    managers = ["Effy", "Will", "Bruce"]
    star_emp = employees[week_num % len(employees)]
    star_mgr = managers[week_num % len(managers)]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div style="text-align:center; padding:15px;">
            <div class="star-badge">本周之星员工: {star_emp}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div style="text-align:center; padding:15px;">
            <div class="star-badge">本周之星经理: {star_mgr}</div>
        </div>""", unsafe_allow_html=True)

    # Sub-tabs
    person_tabs = st.tabs(["Everlyn", "Rita+Maggie+Will", "Effy", "Bruce"])

    with person_tabs[0]:
        section_header("Everlyn - 操作核心")
        insights = DI.get("people_topics", {})
        ev_topics = insights.get("Everlyn Shaw", {})
        ev_connections = DI.get("people_connections", {}).get("Everlyn Shaw", {})

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**工作领域分布 (30天)**")
            if ev_topics:
                ev_df = pd.DataFrame(list(ev_topics.items()), columns=["领域", "邮件数"])
                fig = px.pie(ev_df, names="领域", values="邮件数",
                             color_discrete_sequence=px.colors.sequential.RdBu)
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#e0e0e0",
                    height=300,
                )
                st.plotly_chart(fig, use_container_width=True, key="pchart_1")
        with c2:
            st.markdown("**协作网络 (Top 5)**")
            if ev_connections:
                max_val = max(ev_connections.values()) if ev_connections else 1
                for person, count in list(ev_connections.items())[:5]:
                    pct = min(count / max_val * 100, 100)
                    st.markdown(f"""
                        <div style="margin:6px 0;">
                            <span style="color:#a0a0c0;">{person}</span>
                            <span style="float:right; color:#e94560;">{count}封</span>
                            <div style="background:rgba(50,50,80,0.5); border-radius:4px; height:8px; margin-top:4px;">
                                <div style="background:#e94560; width:{pct:.0f}%; height:8px; border-radius:4px;"></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

        alert_card("blue", f"""
            <b>本周重点任务:</b><br>
            1. 处理{A.get("categories", {}).get("charge_confirm", 0)}封CC待确认邮件<br>
            2. 跟踪{inspection_count}票查验进度<br>
            3. 推进{len(no_tlx_mbl)}个MBL电放确认<br>
            4. 检查所有AN是否有对应预报<br>
            <b>成长建议:</b> Everlyn是操作部门的核心枢纽, 处理邮件量最大。建议建立标准化checklist,
            每天早上9点先处理Hold和查验, 再处理CC, 最后处理常规booking。效率会提升30%+。
        """)

    with person_tabs[1]:
        section_header("Rita + Maggie + Will - 业务+催收+管理")

        # Rita
        st.markdown("#### Rita")
        rita_topics = insights.get("Rita Tang", {})
        rita_conn = DI.get("people_connections", {}).get("Rita Tang", {})
        rita_topics_str = ", ".join([f"{k}({v})" for k, v in rita_topics.items()]) if rita_topics else "暂无数据"
        rita_conn_str = ", ".join([f"{k}({v}封)" for k, v in list(rita_conn.items())[:3]]) if rita_conn else "暂无数据"
        alert_card("blue", f"""
            <b>Rita 30天工作领域:</b> {rita_topics_str}<br>
            <b>主要协作:</b> {rita_conn_str}<br>
            <b>本周重点:</b> 配合Maggie催收, 跟进booking进度, 维护客户关系<br>
            <b>成长建议:</b> Rita在催收方面越来越成熟, 建议增加与客户直接沟通的机会, 培养独立处理中等风险案件的能力。
        """)

        # Maggie
        st.markdown("#### Maggie")
        maggie_topics = insights.get("Maggie Wu", {})
        maggie_conn = DI.get("people_connections", {}).get("Maggie Wu", {})
        maggie_topics_str = ", ".join([f"{k}({v})" for k, v in maggie_topics.items()]) if maggie_topics else "暂无数据"
        maggie_conn_str = ", ".join([f"{k}({v}封)" for k, v in list(maggie_conn.items())[:3]]) if maggie_conn else "暂无数据"
        alert_card("blue", f"""
            <b>Maggie 30天工作领域:</b> {maggie_topics_str}<br>
            <b>主要协作:</b> {maggie_conn_str}<br>
            <b>本周重点:</b> MERSY案件催收(最高优先), TOP5欠费客户跟进, SOP状态更新<br>
            <b>成长建议:</b> Maggie是催收和booking的双料能手, 邮件量462封/月。建议适当分配部分booking工作给Rita,
            让Maggie更多精力聚焦高风险催收。
        """)

        # Will
        st.markdown("#### Will")
        will_conn = DI.get("people_connections", {}).get("Will Sun", {})
        will_conn_str = ", ".join([f"{k}({v}封)" for k, v in list(will_conn.items())[:3]]) if will_conn else "暂无数据"
        alert_card("blue", f"""
            <b>Will 主要协作:</b> {will_conn_str}<br>
            <b>本周重点:</b> MERSY决策(垫付?法律?), 大客户关系维护, 团队效率审查<br>
            <b>成长建议:</b> Will作为管理层, 需要更多关注策略而非执行。建议每周花1小时review催收进度,
            对T+30以上案件亲自决策。
        """)

    with person_tabs[2]:
        section_header("Effy - 目的港操作经理")
        effy_topics = insights.get("Effy Huo", {})
        effy_conn = DI.get("people_connections", {}).get("Effy Huo", {})

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**工作领域分布**")
            if effy_topics:
                effy_df = pd.DataFrame(list(effy_topics.items()), columns=["领域", "邮件数"])
                fig = px.bar(effy_df, x="领域", y="邮件数",
                             color="邮件数", color_continuous_scale="RdBu")
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#e0e0e0",
                    height=300,
                    showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True, key="pchart_2")
        with c2:
            st.markdown("**协作网络 (Top 5)**")
            if effy_conn:
                max_val = max(effy_conn.values()) if effy_conn else 1
                for person, count in list(effy_conn.items())[:5]:
                    pct = min(count / max_val * 100, 100)
                    st.markdown(f"""
                        <div style="margin:6px 0;">
                            <span style="color:#a0a0c0;">{person}</span>
                            <span style="float:right; color:#2196f3;">{count}封</span>
                            <div style="background:rgba(50,50,80,0.5); border-radius:4px; height:8px; margin-top:4px;">
                                <div style="background:#2196f3; width:{pct:.0f}%; height:8px; border-radius:4px;"></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

        alert_card("blue", """
            <b>本周重点任务:</b><br>
            1. 跟踪所有查验票放行进度<br>
            2. 协调报关行YES处理科陆/海柔清关<br>
            3. 监控Delivery进度, 确保无延误<br>
            4. 处理Hold事件协调<br>
            <b>成长建议:</b> Effy作为目的港操作经理, 是客户体验的最后一道防线。
            建议建立"到港日+3"预警机制 - 货物到港3天内如果没有开始提货流程, 自动升级预警。
        """)

    with person_tabs[3]:
        section_header("Bruce - 战略决策")
        alert_card("blue", """
            <b>Bruce 本周关注点:</b><br>
            1. MERSY $89K案件最终决策 - 垫付还是法律途径?<br>
            2. 团队效率评审 - 本月处理5,169封邮件, 人均日处理量如何?<br>
            3. MSC关系维护 - MERSY案件可能影响全线业务<br>
            4. 新客户开发策略 - Astronergy(147封邮件)是否值得深度绑定?<br>
            <b>战略建议:</b> 当前团队最大风险是SPOF(单点故障) - Everlyn离开后操作会瘫痪,
            Maggie离开后催收会停滞。建议Q2启动交叉培训计划。
        """)

    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(15,25,60,0.9),rgba(20,30,80,0.7));
                border:1px solid rgba(100,150,255,0.15);border-left:4px solid rgba(100,180,255,0.6);
                border-radius:0 12px 12px 0;padding:24px;margin:20px 0;
                box-shadow:0 4px 20px rgba(0,0,50,0.3);">
        <h4 style="color:#7dc3ff;margin:0 0 16px 0;font-size:16px;">教练总结: 团队结构与成长</h4>
        <div style="display:flex;gap:20px;margin-bottom:16px;">
            <div style="flex:1;background:rgba(10,20,50,0.6);border-radius:8px;padding:14px;border:1px solid rgba(100,150,255,0.1);">
                <div style="color:#64b5f6;font-weight:600;margin-bottom:8px;">管理架构</div>
                <div style="color:#b8c8e0;font-size:13px;line-height:1.8;">
                    Bruce(整体运营)<br>
                    Effy(美国目的港)<br>
                    Will(中国端协调)
                </div>
            </div>
            <div style="flex:1;background:rgba(10,20,50,0.6);border-radius:8px;padding:14px;border:1px solid rgba(100,150,255,0.1);">
                <div style="color:#64b5f6;font-weight:600;margin-bottom:8px;">执行团队</div>
                <div style="color:#b8c8e0;font-size:13px;line-height:1.8;">
                    Everlyn(换单操作核心)<br>
                    Rita+Maggie(催收+SA)<br>
                    Adam Sum(战略客户)
                </div>
            </div>
        </div>
        <div style="color:#b8c8e0;font-size:13px;line-height:2;">
            <b style="color:#a8d4ff;">成长方向:</b><br>
            <span style="color:#fbbf24;">Everlyn</span> — 从执行者转向指导者，培养Jason接手SA和PreAlert<br>
            <span style="color:#fbbf24;">Effy</span> — 从客户协调扩展到团队管理，关注每个人的负荷和成长<br>
            <span style="color:#fbbf24;">Rita+Maggie</span> — 学习中信保理赔流程，从催收员成长为风控专家<br>
            <span style="color:#fbbf24;">Will</span> — 复杂升级案件(MERSY/MSC危机)处理，团队的判断力安全网<br><br>
            <b style="color:#a8d4ff;">管理原则:</b> 不要让任何人长期超负荷。连续3天邮件超50封，<b style="color:#ef4444;">必须主动分流</b>。团队可持续性比单月效率更重要。
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# TAB 5: 趋势+效率+激励
# ══════════════════════════════════════════════════════════════════
with tabs[4]:
    section_header("邮件趋势分析 (32天)")

    # Pre-compute variables needed by coach_box
    total_30d = A30.get("total_emails", 0)
    daily_counts_30d = A30.get("daily_counts", {})
    total_days = len(daily_counts_30d) if daily_counts_30d else 1
    team_size = 5
    avg_daily = total_30d / max(total_days, 1)
    avg_per_person = avg_daily / team_size

    coach_box("教练总结: 从数据看运营节奏", f"""
        <b>邮件量模式:</b> 工作日平均{avg_daily:.0f}封, 周末明显下降。这说明大部分业务集中在美国工作时间。
        建议团队错峰安排: 中国早上优先处理origin邮件, 下午处理美国目的港邮件。<br><br>
        <b>Top发件人分析:</b> PLT系统(658封)和Everlyn(542封)是最大邮件来源,
        说明系统自动邮件和内部操作邮件占比最高。Maggie(462封)紧随其后, 反映催收和booking的工作强度。<br><br>
        <b>效率提升空间:</b> 如果能将CC费用确认中小额($50以下)的部分自动化处理,
        预计可以减少15-20%的操作邮件量, 释放Everlyn约100封/月的工作量。
    """)


    daily = A30.get("daily_counts", {})
    if daily:
        dates = sorted(daily.keys())
        counts = [daily[d] for d in dates]

        # Color weekends differently
        colors = []
        for d in dates:
            try:
                dt = datetime.strptime(d, "%Y-%m-%d")
                if dt.weekday() >= 5:
                    colors.append("#4a4a6a")
                else:
                    colors.append("#e94560")
            except Exception:
                colors.append("#e94560")

        fig = go.Figure(data=[
            go.Bar(x=dates, y=counts, marker_color=colors,
                   text=counts, textposition='outside', textfont=dict(size=10, color="#a0a0c0"))
        ])
        fig.update_layout(
            title="每日邮件量 (红色=工作日, 灰色=周末)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e0e0e0",
            height=400,
            xaxis=dict(gridcolor="rgba(50,50,80,0.3)"),
            yaxis=dict(gridcolor="rgba(50,50,80,0.3)"),
        )
        st.plotly_chart(fig, use_container_width=True, key="pchart_3")

    # Week over week
    st.markdown("---")
    section_header("周对比")

    if daily:
        sorted_dates = sorted(daily.keys())
        this_week = sum(daily.get(d, 0) for d in sorted_dates[-7:])
        last_week = sum(daily.get(d, 0) for d in sorted_dates[-14:-7])
        change = ((this_week - last_week) / max(last_week, 1)) * 100

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(metric_card(f"{this_week:,}", "本周邮件", "#2196f3"), unsafe_allow_html=True)
        with c2:
            st.markdown(metric_card(f"{last_week:,}", "上周邮件", "#a0a0c0"), unsafe_allow_html=True)
        with c3:
            chg_color = "#00c853" if change <= 0 else "#ffa500"
            st.markdown(metric_card(f"{change:+.1f}%", "周环比变化", chg_color), unsafe_allow_html=True)

    # Team efficiency
    st.markdown("---")
    section_header("团队效率评分")

    total_30d = A30.get("total_emails", 0)
    total_days = A30.get("total_days", 32)
    avg_daily = total_30d / max(total_days, 1)
    team_size = 5
    avg_per_person = avg_daily / team_size

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card(f"{total_30d:,}", "本月总邮件", "#e94560"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card(f"{avg_daily:.0f}", "日均邮件", "#ffa500"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card(f"{avg_per_person:.0f}", "人均日处理", "#2196f3"), unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card(f"{eff_score}/100", "效率评分", eff_color), unsafe_allow_html=True)

    # Motivational
    st.markdown(f"""
    <div style="text-align:center; padding:20px; margin:16px 0;
         background: linear-gradient(135deg, rgba(233,69,96,0.15), rgba(100,50,200,0.1));
         border-radius: 12px;">
        <span style="font-size:24px; font-weight:700; color:#ffd700;">
            本月处理 {total_30d:,} 封邮件!
        </span><br>
        <span style="font-size:14px; color:#a0a0c0;">
            相当于每个工作日处理 {avg_daily:.0f} 封, 每人每天 {avg_per_person:.0f} 封。这是一支高效的团队!
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Top senders
    st.markdown("---")
    section_header("TOP 20 发件人 (30天)")
    top_senders = A30.get("top_senders", [])
    if top_senders:
        sender_rows = []
        for i, item in enumerate(top_senders[:20]):
            raw_sender = item[0] if isinstance(item, list) else item
            count = item[1] if isinstance(item, list) else 0
            name = parse_sender_name(raw_sender)
            # Extract email from raw string
            email_match = re.search(r'<([^>]+)>', raw_sender)
            email_addr = email_match.group(1) if email_match else (raw_sender if "@" in raw_sender else "")
            sender_rows.append({
                "排名": i + 1,
                "姓名": name,
                "邮箱": email_addr,
                "邮件数": count,
                "占比": f"{count / max(total_30d, 1) * 100:.1f}%",
            })
        sender_df = pd.DataFrame(sender_rows)
        st.dataframe(sender_df, use_container_width=True, hide_index=True, key="tbl_7")



# ══════════════════════════════════════════════════════════════════
# TAB 6: 客户全景
# ══════════════════════════════════════════════════════════════════
with tabs[5]:
    section_header("客户全景 - 紧急度 x 重要度矩阵")

    coach_box("教练总结: 紧急 vs 重要 - 艾森豪威尔矩阵", """
        <b>右上角(重要且紧急):</b> 这些客户邮件量大、活跃度高、可能有欠费。需要指定专人负责, 每天review。
        典型代表: REACH INDUSTRY(103封)、HAIROBOT(60封)。<br><br>
        <b>左上角(重要不紧急):</b> 长期价值客户, 当前没有紧急事务。定期维护关系, 预防性沟通。<br><br>
        <b>右下角(紧急不重要):</b> 突发事务多但客户价值一般。快速处理, 不要投入过多精力。<br><br>
        <b>左下角(不重要不紧急):</b> 可以放在队列最后处理。但注意: 长期忽略可能让客户流失。<br><br>
        <b>核心原则:</b> 不要让"紧急"挤掉"重要"。每天60%的时间给重要客户, 40%给紧急事务。
    """)


    customers_30d = A30.get("customers", {})
    if customers_30d:
        cust_rows = []
        for name, info in customers_30d.items():
            emails = info.get("emails", 0)
            active = info.get("active_days", 0)
            # Find arrears for this customer
            arrears_amount = 0
            for arr_item in ARR.get("top20", []):
                if name.upper() in arr_item.get("name", "").upper():
                    arrears_amount = arr_item.get("total", 0)
                    break

            # Score urgency (email volume + arrears) and importance (active days + relationship)
            urgency = min(5, max(1, emails // 15 + (3 if arrears_amount > 10000 else (2 if arrears_amount > 1000 else 0))))
            importance = min(5, max(1, active // 4 + (2 if emails > 50 else (1 if emails > 20 else 0))))

            cust_rows.append({
                "客户": name,
                "30天邮件": emails,
                "活跃天数": active,
                "欠费": f"${arrears_amount:,.0f}" if arrears_amount > 0 else "-",
                "紧急度": urgency,
                "重要度": importance,
                "紧急度星": "★" * urgency,
                "重要度星": "★" * importance,
                "建议": (
                    "高度关注! 频繁沟通+有欠费, 需要专人跟进"
                    if urgency >= 4 and importance >= 4
                    else "重要客户, 保持服务质量"
                    if importance >= 4
                    else "紧急处理当前事务"
                    if urgency >= 4
                    else "常规维护"
                ),
            })

        # Display table
        cust_display = pd.DataFrame([{
            "客户": r["客户"],
            "30天邮件": r["30天邮件"],
            "活跃天数": r["活跃天数"],
            "欠费": r["欠费"],
            "紧急度": r["紧急度星"],
            "重要度": r["重要度星"],
            "建议": r["建议"],
        } for r in cust_rows])
        cust_display = cust_display.sort_values("30天邮件", ascending=False)
        st.dataframe(cust_display, use_container_width=True, hide_index=True, key="tbl_8")

        # Scatter plot
        sdf = pd.DataFrame([{
            "客户": r["客户"],
            "紧急度": r["紧急度"],
            "重要度": r["重要度"],
            "邮件量": r["30天邮件"],
        } for r in cust_rows])

        fig = px.scatter(sdf, x="紧急度", y="重要度", size="邮件量", text="客户",
                         color="邮件量", color_continuous_scale="RdBu",
                         size_max=50)
        fig.update_traces(textposition="top center", textfont_size=10)
        fig.update_layout(
            title="客户紧急度 x 重要度矩阵",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e0e0e0",
            height=500,
            xaxis=dict(title="紧急度", gridcolor="rgba(50,50,80,0.3)", range=[0, 6]),
            yaxis=dict(title="重要度", gridcolor="rgba(50,50,80,0.3)", range=[0, 6]),
        )
        # Add quadrant lines
        fig.add_hline(y=3, line_dash="dash", line_color="rgba(255,255,255,0.2)")
        fig.add_vline(x=3, line_dash="dash", line_color="rgba(255,255,255,0.2)")
        # Quadrant labels
        fig.add_annotation(x=1.5, y=5.5, text="重要不紧急<br>长期维护",
                           showarrow=False, font=dict(color="rgba(255,255,255,0.3)", size=12))
        fig.add_annotation(x=4.5, y=5.5, text="重要且紧急<br>立即行动!",
                           showarrow=False, font=dict(color="rgba(233,69,96,0.5)", size=12))
        fig.add_annotation(x=1.5, y=0.5, text="不重要不紧急<br>观察",
                           showarrow=False, font=dict(color="rgba(255,255,255,0.2)", size=12))
        fig.add_annotation(x=4.5, y=0.5, text="紧急不重要<br>快速处理",
                           showarrow=False, font=dict(color="rgba(255,165,0,0.4)", size=12))

        st.plotly_chart(fig, use_container_width=True, key="pchart_4")



# ══════════════════════════════════════════════════════════════════
# TAB 7: 供应商全景
# ══════════════════════════════════════════════════════════════════
with tabs[6]:
    section_header("供应商全景")

    coach_box("教练总结: 供应商管理要点", """
        <b>核心原则: 不要等供应商回复，要主动追进度。</b><br><br>
        <b>YES报关行</b>是我们的清关Hub——服务科陆/海柔/PREVALON/HORIZON等8家客户。如果YES出现延误，多家客户同时受影响。
        <em>建议: 每天上午主动向YES确认当天清关进度，不要等他们通知我们。</em><br><br>
        <b>PTT和Rome</b>是两大卡车合作方，分别服务科陆(PTT 22次)和正泰(Rome 41次)。
        <em>注意: 不要让PTT和Rome交叉服务导致调度混乱——PTT专做科陆，Rome专做正泰。</em><br><br>
        <b>FCC USA</b>是Houston的核心代理(Adrian Juarez)，同时处理海亮出口和TERRA电商。
        <em>如果开Houston分公司，FCC将是最重要的本地合作伙伴。</em><br><br>
        <b>供应商评分说明:</b> A级(70+)=核心合作方 / B级(50-69)=合格 / C级(30-49)=需关注 / D级(&lt;30)=寻找替代
    """)


    vendors = VDB.get("vendors", [])
    # 排除船公司! 船公司在Tab8单独展示
    service_vendors = [v for v in vendors if v.get("vendor_category") != "ship_carrier"]

    if service_vendors:
        # Build customer-vendor mapping from supply chain network
        cs = SCN.get("customer_service", {})
        # Fallback: build from supply_chains if customer_service is empty
        if not cs:
            for cust, chain in SCN.get("supply_chains", {}).items():
                for cat in ["brokers", "truckers", "agents"]:
                    for svc_name, count in chain.get(cat, {}).items():
                        cs.setdefault(cust, {})[svc_name] = {"count": count, "types": [cat]}
        vendor_customers = {}
        for cust, svcs in cs.items():
            for svc_name in svcs:
                vendor_customers.setdefault(svc_name, []).append(cust)

        v_rows = []
        for v in service_vendors:
            name = v.get("vendor_name", "")
            cn = v.get("vendor_name_cn", "")
            pm = v.get("performance_metrics", {})

            # Find which customers this vendor serves
            custs = []
            for vk, vc in vendor_customers.items():
                if name.upper()[:6] in vk.upper() or vk.upper()[:6] in name.upper():
                    custs.extend(vc)
            custs = list(set(custs))

            # Category label
            cat = v.get("vendor_category", "")
            cat_cn = {"trucking":"卡车","customs_broker":"报关行","agent_partner":"代理"}.get(cat, cat)

            # Current business description
            if name == "YES" or "YES" in name:
                current_biz = "科陆清关/海柔清关/PREVALON清关/HORIZON清关"
                pending = "科陆锂电池查验文件准备中"
                our_action = "确认查验文件齐全→催YES加快清关→通知客户预计延误"
            elif "PTT" in name or "PACIFIC" in name:
                current_biz = "科陆储能柜卡车配送(22次)/双鱼项目卡车"
                pending = "COSCO COSU6446478520 DO已签→待提箱"
                our_action = "联系Jack PTT确认提箱时间→协调仓库收货→通知科陆"
            elif "Rome" in name or "ROME" in name:
                current_biz = "正泰新能卡车配送(41次)/Houston项目"
                pending = "正泰ZTLO260031后续提货安排"
                our_action = "与Rome确认下批次提货计划→对接Adam Sum→通知正泰"
            elif "FCC" in name:
                current_biz = "海亮Houston出口订舱/TERRA电商ReExport"
                pending = "YCH26240119 7x40HQ装箱计划"
                our_action = "联系Adrian确认装箱日期→协调Everlyn操作→通知海亮"
            elif "PTS" in name:
                current_biz = "SAV区域卡车/COSCO Round Trip"
                pending = "SAV Bid Cargo 27柜报价评估"
                our_action = "汇总Sam Kim报价→与IDC/PTT比价→回复客户"
            else:
                current_biz = "常规合作"
                pending = "-"
                our_action = "保持定期沟通"

            v_rows.append({
                "供应商": f"{name}({cn})",
                "类型": cat_cn,
                "评分": v.get("capability_score", 0),
                "等级": v.get("capability_level", "")[:6],
                "服务客户": "/".join(custs[:4]) if custs else "-",
                "当前业务": current_biz[:30],
                "待处理": pending[:25],
                "我方建议行动": our_action[:35],
            })
        v_df = pd.DataFrame(v_rows)
        v_df = v_df.sort_values("评分", ascending=False)
        st.dataframe(v_df, use_container_width=True, hide_index=True,
                     column_config={"评分": st.column_config.ProgressColumn(min_value=0, max_value=100)},
                     key="tbl_9")

    # Key vendor details
    st.markdown("---")
    section_header("重点供应商详情")

    # 重点供应商详情(排除船公司，显示所有有评分的)
    key_vendors = [v for v in service_vendors if v.get("capability_score", 0) > 0]
    if key_vendors:
        for v in sorted(key_vendors, key=lambda x: x.get("capability_score", 0), reverse=True):
            name = v.get("vendor_name", "")
            cn = v.get("vendor_name_cn", "")
            pm = v.get("performance_metrics", {})
            sc = v.get("scoring_components", {})
            cat = {"trucking":"卡车","customs_broker":"报关行","agent_partner":"代理"}.get(v.get("vendor_category",""), "")

            # Business-specific details
            if "YES" in name:
                biz_detail = "正在处理: 科陆锂电池清关(LITHIUM BATTERIES查验中) / 海柔MEDUEK846578清关 / PREVALON COSU6446478520清关"
                pending_detail = "科陆查验文件待CBP确认 / 海柔清关等待放行"
                action_detail = "催YES确认科陆查验进展→准备补充MSDS文件→协调Effy通知客户延误预期"
            elif "PTT" in name or "PACIFIC" in name:
                biz_detail = "正在处理: 科陆储能柜提箱配送(COSU6446478520 DO已签) / ZIM双鱼2x20HC卡车安排"
                pending_detail = "COSCO提箱时间待确认 / ZIM票卡车报价待回复"
                action_detail = "联系Jack PTT确认COSCO提箱时间→跟进ZIM卡车报价→通知Effy安排Delivery"
            elif "Rome" in name:
                biz_detail = "正在处理: 正泰新能ZTLO260031项目(41次配送) / Houston大件运输"
                pending_detail = "下批次正泰提货时间待确认"
                action_detail = "与Rome确认正泰下周提货计划→对接Adam Sum→确保16柜按时配送"
            elif "FCC" in name:
                biz_detail = "正在处理: 海亮Houston出口YCH26240119(7x40HQ) / TERRA电商ReExport操作"
                pending_detail = "海亮装箱日期待确认 / TERRA 20GP拆箱方案待确认"
                action_detail = "催Adrian确认海亮装箱日→协调TERRA拆箱→Effy跟进客户沟通"
            elif "PTS" in name:
                biz_detail = "正在处理: SAV区域卡车 / COSCO Round Trip(Jingzhou-Charleston)"
                pending_detail = "SAV Bid Cargo 27柜报价待比较"
                action_detail = "汇总Sam Kim报价与IDC/PTT比价→选择最优方案→回复客户"
            else:
                biz_detail = "常规合作中"
                pending_detail = "-"
                action_detail = "保持定期沟通维护关系"

            with st.expander(f"{cat} | {name} ({cn}) - 评分{v.get('capability_score', 0)}/100"):
                st.markdown(f"**当前业务:** {biz_detail}")
                st.markdown(f"**待处理/待回复:** {pending_detail}")
                st.markdown(f"**我方建议行动:** {action_detail}")
                st.markdown(f"**服务邮件:** {pm.get('email_volume_7d', 0)}封 | **Hold:** {pm.get('hold_events_7d', 0)} | **查验:** {pm.get('inspection_events_7d', 0)}")

                # Scoring radar
                if sc:
                    categories = list(sc.keys())
                    values = list(sc.values())
                    fig = go.Figure(data=go.Scatterpolar(
                        r=values + [values[0]],
                        theta=categories + [categories[0]],
                        fill='toself',
                        fillcolor='rgba(233,69,96,0.2)',
                        line_color='#e94560',
                    ))
                    fig.update_layout(
                        polar=dict(
                            bgcolor="rgba(0,0,0,0)",
                            radialaxis=dict(visible=True, range=[0, 25], gridcolor="rgba(50,50,80,0.3)"),
                            angularaxis=dict(gridcolor="rgba(50,50,80,0.3)"),
                        ),
                        paper_bgcolor="rgba(0,0,0,0)",
                        font_color="#e0e0e0",
                        height=300,
                        showlegend=False,
                    )
                    st.plotly_chart(fig, use_container_width=True, key=f"radar_{name}")



# ══════════════════════════════════════════════════════════════════
# TAB 8: 船公司全景
# ══════════════════════════════════════════════════════════════════
with tabs[7]:
    section_header("船公司全景")

    coach_box("教练总结: 船公司选择的全成本思维", """
        <b>不要只看运费:</b> 船公司选择需要考虑"全成本" = 运费 + 目的港费用 + Hold/查验频率 + 延误成本 + 服务响应速度。<br><br>
        <b>MSC:</b> 邮件量最高(955封), 说明业务量大但同时管理成本高。MSC的目的港费用结构复杂,
        经常有额外的Chassis和Per Diem收费。<br><br>
        <b>ONE:</b> 虽然运费可能有竞争力, 但本周有1票查验, 查验=额外$500-2000+2-5天延误。<br><br>
        <b>OOCL:</b> 本周有2票查验, 需要观察是否是偶发还是趋势。如果持续出现查验,
        可能需要评估OOCL的舱位分配是否有问题。<br><br>
        <b>建议:</b> 对每个船公司维护一个"全成本记分卡", 每月更新, 作为舱位分配的决策依据。
    """)


    carriers_30d = A30.get("carriers", {})
    carrier_fees = A.get("carrier_fees", {})

    # Build carrier table
    carrier_vendors = {v.get("vendor_name"): v for v in vendors if v.get("vendor_category") == "ship_carrier"}

    if carriers_30d:
        c_rows = []
        for name, vol in sorted(carriers_30d.items(), key=lambda x: x[1], reverse=True):
            vinfo = carrier_vendors.get(name, {})
            pm = vinfo.get("performance_metrics", {}) if vinfo else {}
            sc = vinfo.get("scoring_components", {}) if vinfo else {}
            fees = carrier_fees.get(name, {})

            # Find which customers use this carrier
            custs_using = []
            cc_network = SCN.get("customer_carrier", {})
            # Fallback: build from supply_chains if empty
            if not cc_network:
                for cust, chain in SCN.get("supply_chains", {}).items():
                    for carrier, count in chain.get("carriers", {}).items():
                        cc_network.setdefault(cust, {})[carrier] = count
            for cust, carriers_map in cc_network.items():
                if name in carriers_map:
                    custs_using.append(f"{cust}({carriers_map[name]})")

            c_rows.append({
                "船公司": f"{name} ({vinfo.get('vendor_name_cn', '')})" if vinfo else name,
                "30天邮件": vol,
                "能力评分": vinfo.get("capability_score", "-") if vinfo else "-",
                "等级": vinfo.get("capability_level", "-") if vinfo else "-",
                "7日Hold": pm.get("hold_events_7d", 0),
                "7日查验": pm.get("inspection_events_7d", 0),
                "费用笔数": fees.get("count", 0),
                "费用总额": f"${fees.get('total', 0):,.0f}" if fees.get("total", 0) > 0 else "-",
                "平均费用": f"${fees.get('avg', 0):,.0f}" if fees.get("avg", 0) > 0 else "-",
                "风险标签": ", ".join(vinfo.get("risk_tags", ["-"])) if vinfo else "-",
                "服务客户": ", ".join(custs_using[:4]) if custs_using else "-",
            })

        c_df = pd.DataFrame(c_rows)
        st.dataframe(c_df, use_container_width=True, hide_index=True, key="tbl_10")

        # Market share pie chart
        fig = px.pie(
            names=list(carriers_30d.keys()),
            values=list(carriers_30d.values()),
            title="船公司30天邮件量占比",
            color_discrete_sequence=px.colors.sequential.RdBu,
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e0e0e0",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True, key="pchart_6")

    # PLT scoring radar comparison
    section_header("船公司能力评分对比")
    active_carriers = [v for v in vendors
                       if v.get("vendor_category") == "ship_carrier"
                       and v.get("performance_metrics", {}).get("email_volume_7d", 0) > 0]
    if active_carriers:
        fig = go.Figure()
        color_list = ["#e94560", "#2196f3", "#00c853", "#ffa500", "#9c27b0", "#ff9800"]
        for i, v in enumerate(active_carriers):
            sc = v.get("scoring_components", {})
            if sc:
                categories = list(sc.keys())
                values = list(sc.values())
                fig.add_trace(go.Scatterpolar(
                    r=values + [values[0]],
                    theta=categories + [categories[0]],
                    name=v.get("vendor_name", ""),
                    line_color=color_list[i % len(color_list)],
                    fill='toself',
                    opacity=0.6,
                ))
        fig.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, 25], gridcolor="rgba(50,50,80,0.3)"),
                angularaxis=dict(gridcolor="rgba(50,50,80,0.3)"),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e0e0e0",
            height=400,
            title="活跃船公司能力雷达图",
        )
        st.plotly_chart(fig, use_container_width=True, key="pchart_7")



# ══════════════════════════════════════════════════════════════════
# TAB 9: 目的港全景
# ══════════════════════════════════════════════════════════════════
with tabs[8]:
    section_header("美国目的港全景地图")

    coach_box("教练总结: 区域差异决定操作策略", """
        <b>西海岸 (LA/LB):</b> 业务量最大, 但港口拥堵和底盘车紧缺是常态。Free Time通常只有4-5天,
        超过后Demurrage高达$300+/天。建议: 到港前48小时就开始准备DO和报关文件。<br><br>
        <b>德州 (Houston):</b> NEXTERA是最大客户, Rail Detention是主要成本。
        从港口到内陆仓库的铁路转运经常延误, 每次延误产生$185/天的Rail Detention。
        建议: 与铁路公司建立直接沟通渠道, 提前锁定铁路舱位。<br><br>
        <b>东海岸 (NY/NJ):</b> 清关速度相对快, 但港口费用结构不同于西海岸。
        需要特别注意NYCT(New York Container Terminal)的特殊收费。<br><br>
        <b>内陆转运 (Chicago IPI):</b> Rail Detention是最大痛点。建议对所有IPI货物提前7天通知收货人,
        确保到达后48小时内提柜。
    """)


    # Port data with coordinates
    port_data = [
        {"port": "Los Angeles/Long Beach", "lat": 33.75, "lon": -118.19, "state": "CA",
         "volume": 280, "desc": "最大港口, 科陆/海柔/Astronergy主要目的港"},
        {"port": "New York/Newark", "lat": 40.68, "lon": -74.04, "state": "NJ",
         "volume": 95, "desc": "东海岸主要港口, PTS/FCC USA目的港"},
        {"port": "Savannah", "lat": 32.08, "lon": -81.10, "state": "GA",
         "volume": 65, "desc": "东南部枢纽, REACH INDUSTRY目的港"},
        {"port": "Houston", "lat": 29.75, "lon": -95.27, "state": "TX",
         "volume": 110, "desc": "德州枢纽, NEXTERA/Project Delivery"},
        {"port": "Norfolk", "lat": 36.85, "lon": -76.29, "state": "VA",
         "volume": 25, "desc": "东海岸次要港口"},
        {"port": "Charleston", "lat": 32.78, "lon": -79.93, "state": "SC",
         "volume": 20, "desc": "东南部次要港口"},
        {"port": "Seattle/Tacoma", "lat": 47.45, "lon": -122.30, "state": "WA",
         "volume": 15, "desc": "西北部港口"},
        {"port": "Chicago (IPI)", "lat": 41.88, "lon": -87.63, "state": "IL",
         "volume": 40, "desc": "内陆转运枢纽, Rail Detention高发"},
    ]

    port_df = pd.DataFrame(port_data)

    fig = go.Figure()

    # Scatter geo for port markers
    fig.add_trace(go.Scattergeo(
        lon=port_df["lon"],
        lat=port_df["lat"],
        text=port_df.apply(lambda r: f"<b>{r['port']}</b><br>月均票数: ~{r['volume']}<br>{r['desc']}", axis=1),
        mode="markers+text",
        marker=dict(
            size=port_df["volume"] / 5 + 10,
            color=port_df["volume"],
            colorscale="RdBu",
            showscale=True,
            colorbar=dict(title="业务量"),
            line=dict(width=1, color="#fff"),
        ),
        textposition="top center",
        textfont=dict(size=10, color="#e0e0e0"),
        name="目的港",
        hoverinfo="text",
    ))
    # Port name labels
    fig.add_trace(go.Scattergeo(
        lon=port_df["lon"],
        lat=port_df["lat"],
        text=port_df["port"],
        mode="text",
        textposition="top center",
        textfont=dict(size=9, color="#ffd700"),
        showlegend=False,
        hoverinfo="skip",
    ))

    fig.update_geos(
        scope="usa",
        projection_type="albers usa",
        showland=True,
        landcolor="rgb(20,20,40)",
        showlakes=True,
        lakecolor="rgb(15,52,96)",
        showocean=True,
        oceancolor="rgb(10,10,30)",
        showcountries=True,
        countrycolor="rgba(100,100,180,0.3)",
        showsubunits=True,
        subunitcolor="rgba(100,100,180,0.2)",
        bgcolor="rgba(0,0,0,0)",
    )
    fig.update_layout(
        title="WWL美国目的港分布 (气泡大小=业务量)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e0e0e0",
        height=550,
        margin=dict(l=0, r=0, t=40, b=0),
        geo=dict(bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig, use_container_width=True, key="pchart_8")

    # Port detail table
    st.markdown("---")
    section_header("目的港详情")
    port_detail_df = pd.DataFrame([{
        "港口": p["port"],
        "州": p["state"],
        "月均票数": f"~{p['volume']}",
        "主要客户": p["desc"],
        "风险提示": (
            "Rail Detention高发区"
            if p["state"] in ["IL", "TX"]
            else "港口拥堵风险"
            if p["state"] in ["CA"]
            else "正常"
        ),
        "建议": (
            "关注Rail Detention, 提前通知客户提柜时限"
            if p["state"] in ["IL", "TX"]
            else "关注Demurrage, LB港Free Time短"
            if p["state"] == "CA"
            else "常规监控"
        ),
    } for p in port_data])
    st.dataframe(port_detail_df, use_container_width=True, hide_index=True, key="tbl_11")



# ══════════════════════════════════════════════════════════════════
# TAB 10: 联系人搜索
# ══════════════════════════════════════════════════════════════════
with tabs[9]:
    section_header("联系人搜索")

    contacts = CON.get("contacts", [])

    search_query = st.text_input("搜索 (姓名/公司/邮箱/电话)", placeholder="输入关键词...")

    if contacts:
        # Filter
        if search_query:
            query_lower = search_query.lower()
            filtered = [c for c in contacts if (
                query_lower in c.get("name", "").lower()
                or query_lower in c.get("company", "").lower()
                or query_lower in c.get("email", "").lower()
                or query_lower in c.get("domain", "").lower()
                or query_lower in c.get("title", "").lower()
                or any(query_lower in p for p in c.get("phones", []))
            )]
        else:
            filtered = contacts[:50]  # Show first 50 by default

        st.markdown(f"**找到 {len(filtered)} 个联系人** (共 {len(contacts)} 个)")

        if filtered:
            contact_rows = []
            for c in filtered[:100]:
                contact_rows.append({
                    "姓名": c.get("name", "") or "-",
                    "公司": c.get("company", "") or "-",
                    "邮箱": c.get("email", ""),
                    "域名": c.get("domain", ""),
                    "职位": c.get("title", "").replace("\r\n", " ").replace("\n", " ").strip()[:50] if c.get("title") else "-",
                    "电话": ", ".join(c.get("phones", [])[:3]) if c.get("phones") else "-",
                    "邮件数": c.get("email_count", 0),
                    "最后联系": c.get("last_seen", "")[:20] if c.get("last_seen") else "-",
                })
            ct_df = pd.DataFrame(contact_rows)
            ct_df = ct_df.sort_values("邮件数", ascending=False)
            st.dataframe(ct_df, use_container_width=True, hide_index=True, key="tbl_12")

        # Stats
        st.markdown("---")
        meta = CON.get("metadata", {})
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(metric_card(meta.get("total_contacts", 0), "总联系人", "#2196f3"), unsafe_allow_html=True)
        with c2:
            st.markdown(metric_card(meta.get("internal_wwl", 0), "WWL内部", "#00c853"), unsafe_allow_html=True)
        with c3:
            st.markdown(metric_card(meta.get("external", 0), "外部联系人", "#ffa500"), unsafe_allow_html=True)
        with c4:
            st.markdown(metric_card(meta.get("total_companies", 0), "关联公司", "#9c27b0"), unsafe_allow_html=True)
    else:
        st.info("联系人数据库为空或加载失败")


# ─── Footer ───
st.markdown("""
<div style="text-align:center; padding:30px 0 10px 0; color:#4a4a6a; font-size:12px;">
    WWL 环世物流 运营指挥中心 v5.0 | Powered by OpenClaw Engine |
    数据源: 邮件智能扫描 + 供应商数据库 + 联系人数据库<br>
    所有建议仅供参考, 请结合实际情况判断执行
</div>
""", unsafe_allow_html=True)
