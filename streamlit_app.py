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

# v5.1 body-based progress: tasks → events → completed (2026-03-30 02:30)

# ─── Page Config ───
st.set_page_config(
    page_title="WWL运营指挥中心 v5.0",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ─── Password Protection ───
def check_password():
    """Returns True if the user has entered the correct password."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if st.session_state.authenticated:
        return True
    
    st.markdown("""
    <div style="text-align:center; padding:60px 0;">
        <h1 style="color:#e94560;">WWL 环世物流 运营指挥中心</h1>
        <p style="color:#a0a0c0;">请输入访问密码</p>
    </div>
    """, unsafe_allow_html=True)
    
    password = st.text_input("密码", type="password", key="pwd_input")
    if st.button("登录", key="login_btn"):
        if password == "WWL2026!":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("密码错误")
    
    st.markdown("<p style='text-align:center;color:#666;font-size:12px;margin-top:40px;'>环世物流内部系统 · 仅授权人员访问</p>", unsafe_allow_html=True)
    return False

if not check_password():
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
@st.cache_data(ttl=30)
def load_all_data():
    data = {}
    files = {
        "analysis": "data/analysis.json",
        "analysis_30d": "data/analysis_30d.json",
        "arrears": "data/arrears_analysis.json",
        "overdue_sop": "data/overdue_sop_status.json",
        "vendors": "data/vendor_database.json",
        "supply_chain": "data/supply_chain_network.json",
        "contacts": "data/contacts_database.json",
        "deep_insights": "data/deep_insights.json",
        "deep_patterns": "data/deep_patterns.json",
        "us_consignee": "data/us_consignee_database.json",
        "graph_tasks": "data/graph_tasks.json",
    }
    for key, path in files.items():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data[key] = json.load(f)
        except Exception:
            data[key] = {}
    return data


# ─── Task Board Persistence ───
TASK_FILE = "data/task_board.json"

def load_tasks():
    try:
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"completed": {}, "tasks": []}

def save_tasks(task_data):
    import os
    os.makedirs("data", exist_ok=True)
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        json.dump(task_data, f, ensure_ascii=False, indent=2)

def build_task_board(action_items, arrears_data, bl_status, overdue_sop, contacts_db, deep_insights, enhanced):
    """从多个数据源构建完整任务清单，按客户维度聚合，包含联系人+提单号+金额明细"""
    tasks = []
    seen_keys = set()

    # 内部销售负责人映射
    staff_customers = {}
    for staff_name, data in enhanced.get("staff_analysis", {}).items():
        if isinstance(data, dict):
            for cust in data.get("customers", []):
                staff_customers.setdefault(cust, []).append(staff_name.split("(")[0].strip())

    # 客户联系人映射
    cust_contacts_map = deep_insights.get("customer_contacts", {})

    # 联系人快速查找
    all_contacts = contacts_db.get("contacts", []) if isinstance(contacts_db, dict) else []

    def find_internal_staff(customer_name):
        """查找负责该客户的内部销售"""
        for alias, staffs in staff_customers.items():
            if alias.upper() in customer_name.upper() or customer_name.upper() in alias.upper():
                return ", ".join(staffs[:2])
        return ""

    def find_customer_contact(customer_name):
        """查找客户方联系人"""
        for cust_key, ppl in cust_contacts_map.items():
            if cust_key.upper() in customer_name.upper() or customer_name.upper() in cust_key.upper():
                if isinstance(ppl, dict):
                    top = sorted(ppl.items(), key=lambda x: x[1].get("count",0) if isinstance(x[1],dict) else x[1], reverse=True)[:2]
                    result = []
                    for email, info in top:
                        name = info.get("name", "") if isinstance(info, dict) else ""
                        phone = info.get("phone", "") if isinstance(info, dict) else ""
                        result.append(f"{name} {email}" + (f" {phone}" if phone else ""))
                    return " / ".join(result)
        return ""

    # 1. 从引擎action_items(查验/Hold/CC/AN/D&D/Overdue)
    for a in action_items:
        key = f"{a.get('type','')}__{a.get('mbl','')}__{a.get('source','')[:30]}"
        if key in seen_keys: continue
        seen_keys.add(key)
        cust = a.get("customer", "")
        tasks.append({
            "id": key, "category": a.get("type", "other"), "priority": a.get("priority", "medium"),
            "title": a.get("type", "").upper(),
            "action": a.get("action", ""),
            "assignee": a.get("assignee", ""),
            "mbl": a.get("mbl", ""), "hbl": a.get("hbl", ""),
            "customer": cust, "amount": a.get("amount", ""),
            "internal_staff": find_internal_staff(cust) if cust else "",
            "customer_contact": find_customer_contact(cust) if cust else "",
            "detail_lines": [],
            "source": a.get("source", ""), "date": a.get("date", ""),
        })

    # 2. 欠费催收(按客户聚合，含提单明细)
    for item in arrears_data.get("top20", [])[:20]:
        name = item.get("name", "")
        total = item.get("total", 0)
        if total < 500: continue
        key = f"arrears__{name}"
        if key in seen_keys: continue
        seen_keys.add(key)

        # 提单明细
        detail_lines = []
        types = item.get("types", {})
        for desc, amt in sorted(types.items(), key=lambda x: abs(x[1]) if isinstance(x[1],(int,float)) else 0, reverse=True)[:6]:
            if isinstance(amt, (int, float)) and amt > 0:
                detail_lines.append(f"{desc}: ${amt:,.0f}")

        mbls = item.get("mbls", [])
        hbls = item.get("hbls", [])
        mbl_str = ", ".join(mbls[:3]) if isinstance(mbls, list) else ""
        hbl_str = ", ".join(hbls[:3]) if isinstance(hbls, list) else ""

        priority = "urgent" if total > 20000 else "high" if total > 5000 else "medium"
        tasks.append({
            "id": key, "category": "arrears", "priority": priority,
            "title": "欠费催收",
            "action": f"总欠费${total:,.0f} — 确认T+X阶段: T+7首催/T+15升级/T+30追偿函/T+45中信保",
            "assignee": "",
            "mbl": mbl_str, "hbl": hbl_str,
            "customer": name[:30], "amount": f"${total:,.0f}",
            "internal_staff": find_internal_staff(name),
            "customer_contact": find_customer_contact(name),
            "detail_lines": detail_lines,
            "source": f"{item.get('records',0)}条记录", "date": item.get("latest", ""),
        })

    # 3. 未电放MBL
    for mbl in bl_status.get("no_tlx_mbl", [])[:10]:
        m = mbl if isinstance(mbl, str) else str(mbl)
        key = f"no_tlx__{m}"
        if key in seen_keys: continue
        seen_keys.add(key)
        # 从MBL前缀识别船公司
        carrier = ""
        for prefix, c in [("MEDU","MSC"),("COSU","COSCO"),("OOLU","OOCL"),("ONEY","ONE"),("ZIMU","ZIM"),("CMDU","CMA-CGM"),("HLCU","Hapag-Lloyd")]:
            if m.startswith(prefix): carrier = c; break
        tasks.append({
            "id": key, "category": "bl_release", "priority": "high",
            "title": "换单/电放",
            "action": f"MBL未电放 — 联系origin确认TLX状态{f' ({carrier})' if carrier else ''} → 催促放单 → 确认后通知目的港",
            "assignee": "", "mbl": m, "hbl": "", "customer": "", "amount": "",
            "internal_staff": "", "customer_contact": "",
            "detail_lines": [f"船公司: {carrier}"] if carrier else [],
            "source": "bl_status", "date": "",
        })

    # 4. AN无预报(漏单预警)
    for mbl in bl_status.get("an_no_prealert", [])[:10]:
        m = mbl if isinstance(mbl, str) else str(mbl)
        key = f"an_gap__{m}"
        if key in seen_keys: continue
        seen_keys.add(key)
        tasks.append({
            "id": key, "category": "prealert_gap", "priority": "urgent",
            "title": "漏单预警",
            "action": "AN已收但无PreAlert — 可能漏单! 立即核查是否有对应HBL，确认origin是否已发货",
            "assignee": "", "mbl": m, "hbl": "", "customer": "", "amount": "",
            "internal_staff": "", "customer_contact": "",
            "detail_lines": [], "source": "bl_status", "date": "",
        })

    # 5. Hold提单
    for h in bl_status.get("hold_bl", [])[:10]:
        m = h.get("mbl", "") if isinstance(h, dict) else str(h)
        htype = h.get("type", "?") if isinstance(h, dict) else "?"
        key = f"hold__{m}"
        if key in seen_keys: continue
        seen_keys.add(key)
        action_map = {
            "freight": "Freight Hold — 联系origin确认运费支付状态 → 付款后通知船公司释放",
            "customs": "Customs Hold — 联系报关行(YES/WFS)确认CBP要求 → 准备补充文件 → 跟进放行",
            "do fee": "DO Fee Hold — 确认DO费用金额 → Maggie安排付款 → 付款后拿DO",
        }
        tasks.append({
            "id": key, "category": "hold", "priority": "urgent",
            "title": f"HOLD ({htype})",
            "action": action_map.get(htype, f"{htype.upper()} HOLD — 确认Hold类型并处理"),
            "assignee": "", "mbl": m, "hbl": "", "customer": "", "amount": "",
            "internal_staff": "", "customer_contact": "",
            "detail_lines": [f"Hold来源: {h.get('from','?')}", f"邮件: {h.get('subject','')[:40]}"] if isinstance(h, dict) else [],
            "source": "bl_status", "date": "",
        })

    # 6. SOP跟进
    sop_list = overdue_sop if isinstance(overdue_sop, list) else []
    for item in sop_list[:10]:
        if not isinstance(item, dict): continue
        m = item.get("mbl", "")
        if not m: continue
        key = f"sop__{m}"
        if key in seen_keys: continue
        seen_keys.add(key)
        tasks.append({
            "id": key, "category": "sop", "priority": "high",
            "title": "SOP合规跟进",
            "action": f"Overdue SOP — {item.get('maggie_action', '按T+X时间线推进')}",
            "assignee": "", "mbl": m, "hbl": "", "customer": "",
            "amount": f"${item.get('amount', 0):,.0f}" if isinstance(item.get("amount"), (int, float)) else "",
            "internal_staff": "", "customer_contact": "",
            "detail_lines": [f"状态: {item.get('t_status','?')}"] if item.get('t_status') else [],
            "source": "overdue_sop", "date": "",
        })

    priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    tasks.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))
    return tasks


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

# v3.0 行动项
action_items = A.get("action_items", [])
action_summary = A.get("action_summary", {})
urgent_actions = [a for a in action_items if a.get("priority") == "urgent"]
high_actions = [a for a in action_items if a.get("priority") == "high"]
medium_actions = [a for a in action_items if a.get("priority") == "medium"]

# Compute efficiency score (平衡版 — 有挑战但不打击士气)
total_7d = A.get("total_emails", 0)
biz_7d = A.get("business_emails", 0)
overdue_count = A.get("overdue_count", 0)
cancel_count = A.get("cancel_count", 0)

# 基础分75
eff_score = 75

# 扣分项(重大风险扣分重,一般事务扣分轻)
risk_items = len(cancel_it) + len(stolen) + len(hold_bl) + hold_count + inspection_count
eff_score -= hold_count * 2              # Hold每个扣2分
eff_score -= len(stolen) * 10            # 被盗扣10分(严重!)
eff_score -= len(an_no_prealert) * 5     # 漏单扣5分(严重!)
eff_score -= overdue_count               # Overdue每封扣1分
eff_score -= cancel_count                # Cancel每个扣1分
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


def safe_tab(tab_name):
    """Decorator to wrap tab content in try/except and show full error details."""
    import functools, traceback as tb_mod
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                st.error(f"{tab_name} 加载出错: {type(e).__name__}: {e}")
                st.code(tb_mod.format_exc(), language="text")
        return wrapper
    return decorator


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

    # 教练总结紧跟效率评分
    coach_box("教练总结: 风险管理 — 法规+实战", f"""
        <b>当前状态:</b> Hold {hold_count}件 / 查验 {inspection_count}件 / 待办 {len(action_items)}项。
        {'⚠️ 有Hold必须立即处理!' if hold_count > 0 else '✅ 无Hold。'}
        {'⚠️ 有查验需跟进!' if inspection_count > 0 else ''}<br><br>
        <b>FMC D&D新规:</b> 船公司D&D账单必须含19项要素, 缺一项=无需付款。收到账单先核对合规性。<br>
        <b>UFLPA:</b> 太阳能/电池客户(正泰/科陆/海辰)每票确认溯源文件。77%中国货被扣后拒放。<br>
        <b>周五规则:</b> 周五收到Hold必须当天行动, 不等周一(省3天D&D)。
    """)

    # ─── 事件摘要(一行显示) ───
    cc_count = A.get("categories", {}).get("charge_confirm", 0)
    anomaly_total = len(cancel_it) + len(cod_list) + len(non_standard) + len(stolen) + len(urgent)
    _summary = DATA.get("graph_tasks", {}).get("summary", {})
    _sc1, _sc2, _sc3, _sc4, _sc5 = st.columns(5)
    with _sc1: st.markdown(f'<div class="metric-card"><h2 style="color:{"#e94560" if hold_count else "#00c853"}">{hold_count}</h2><p>Hold</p></div>', unsafe_allow_html=True)
    with _sc2: st.markdown(f'<div class="metric-card"><h2 style="color:{"#ffa500" if inspection_count else "#00c853"}">{inspection_count}</h2><p>查验</p></div>', unsafe_allow_html=True)
    with _sc3: st.markdown(f'<div class="metric-card"><h2 style="color:{"#ffa500" if cc_count else "#00c853"}">{cc_count}</h2><p>CC</p></div>', unsafe_allow_html=True)
    with _sc4: st.markdown(f'<div class="metric-card"><h2 style="color:{"#e94560" if anomaly_total else "#00c853"}">{anomaly_total}</h2><p>异常</p></div>', unsafe_allow_html=True)
    with _sc5: st.markdown(f'<div class="metric-card"><h2 style="color:#2196f3">{_summary.get("arrival_notices",0)}</h2><p>到港</p></div>', unsafe_allow_html=True)

    st.markdown("---")

    # ═══ v4.0 任务工作台(从知识图谱) ═══
    # 优先用graph_tasks(SQLite知识图谱推理), fallback到旧的build_task_board
    GRAPH = DATA.get("graph_tasks", {})
    graph_tasks_list = GRAPH.get("tasks", [])

    if graph_tasks_list:
        # 从知识图谱生成的任务(更丰富)
        all_tasks = []
        for gt in graph_tasks_list:
            task_id = f"{gt.get('type','')}__{gt.get('mbl','')}__{gt.get('customer','')}"
            all_tasks.append({
                "id": task_id,
                "category": gt.get("type", "other"),
                "priority": gt.get("priority", "medium"),
                "title": gt.get("title", ""),
                "action": gt.get("action", ""),
                "mbl": gt.get("mbl", ""),
                "hbl": gt.get("hbl", ""),
                "carrier": gt.get("carrier", ""),
                "customer": gt.get("customer", ""),
                "wwl_sender": gt.get("wwl_sender", ""),
                "wwl_branch": gt.get("wwl_branch", ""),
                "amount": gt.get("amount", ""),
                "contact": "",
                "consignee": "",
                "shipper": "",
                "internal_staff": "",
                "customer_contact": "",
                "detail_lines": ([gt.get('progress_history','')] if gt.get('progress_history') else []) + ([gt.get('detail','')] if gt.get('detail') else []),
                "assignee": "",
            })
        # 补充欠费催收任务(去重)
        existing_ids = {t["id"] for t in all_tasks}
        for extra in build_task_board([], ARR, {}, SOP, CON, DI, {}):
            if extra["id"] not in existing_ids:
                all_tasks.append(extra)
                existing_ids.add(extra["id"])
    else:
        # Fallback: only arrears (no action_items - those are unreliable)
        all_tasks = build_task_board([], ARR, {}, SOP, CON, DI, {})

    # 去重
    seen_ids = set()
    deduped = []
    for t in all_tasks:
        if t["id"] not in seen_ids:
            seen_ids.add(t["id"])
            deduped.append(t)
    all_tasks = deduped

    # 过滤掉3月15日前的旧任务(已经过期的不再显示)
    all_tasks = [t for t in all_tasks if not t.get("last_seen") or t.get("last_seen","9999") >= "2026-03-15"]

    # 过滤掉wwl_sender是US团队的(这些不是源头)
    US_TEAM_EMAILS = {
        'us.ops2@wwl.sg', 'us.ops@wwl.sg', 'us.effyhuo@wwl.sg',
        'maggiewu@wwl.cn', 'rita.tang@wwl.cn', 'willsun@wwl.cn',
        'bruce@wwl.cn', 'bruce@wwl.sg',
        'us.adamsum@worldwide-logistics.cn', 'bobc@worldwide-logistics.cn',
        'us.docs@wwl.sg', 'sha.overseassup2@wwl.cn',
    }
    for t in all_tasks:
        sender = t.get("wwl_sender", "")
        # 从sender字符串中提取email
        import re as _re
        _em = _re.search(r'[\w.+-]+@[\w.-]+', sender.lower()) if sender else None
        if _em and _em.group() in US_TEAM_EMAILS:
            t["wwl_sender"] = ""  # 清除US团队，不是源头
            t["wwl_branch"] = ""

    task_data = load_tasks()
    completed_ids = task_data.get("completed", {})

    # 分离未完成和已完成
    pending = [t for t in all_tasks if t["id"] not in completed_ids]
    done_today = [t for t in all_tasks if t["id"] in completed_ids]
    pending_urgent = [t for t in pending if t["priority"] == "urgent"]
    pending_high = [t for t in pending if t["priority"] == "high"]
    pending_medium = [t for t in pending if t["priority"] == "medium"]

    section_header(f"任务工作台: {len(pending)}条待办 / {len(done_today)}条已完成")

    # 分类统计
    cat_counts = {}
    for t in pending:
        c = t.get("category", "other")
        cat_counts[c] = cat_counts.get(c, 0) + 1
    cat_labels = {"hold":"Hold扣货","inspection":"查验","cc_confirm":"CC费用","arrival_notice":"到港通知",
                  "dd_alert":"D&D费用","overdue":"Overdue催收","arrears":"欠费催收","bl_release":"换单电放",
                  "prealert_gap":"漏单预警","sop":"SOP跟进",
                  "broker_followup":"报关行跟进","trucker_followup":"卡车跟进","post_clearance":"清关后跟进",
                  "empty_return":"空柜归还","post_booking":"订舱后跟进","supplier_reply":"供应商等回复",
                  "hold_active":"Hold扣货","inspection_active":"查验中","fee_confirmed":"费用已确认",
                  "payment_requested":"待付款","awaiting_reply":"等回复",
                  "inspection_broker":"查验报关跟进",
                  "stale_arrival":"到港停滞","awaiting_reply":"等回复"}
    cat_display = " | ".join(f"{cat_labels.get(k,k)}:{v}" for k,v in sorted(cat_counts.items(), key=lambda x:x[1], reverse=True))
    st.markdown(f"<p style='color:#a0a0c0;font-size:13px;margin:4px 0;'>{cat_display}</p>", unsafe_allow_html=True)

    def render_task_card(t, pri_color, bg_alpha):
        """渲染任务卡片 — 按客户维度展示，含提单/船公司/联系人/金额明细"""
        cat_label = cat_labels.get(t["category"], t["category"])
        cust = t.get("customer", "")
        mbl = t.get("mbl", "")
        hbl = t.get("hbl", "")
        amount = t.get("amount", "")
        carrier = t.get("carrier", "")
        sender = t.get("sender", "")
        contact = t.get("contact", "")
        internal = t.get("internal_staff", "")
        ext_contact = t.get("customer_contact", "")
        details = t.get("detail_lines", [])

        consignee = t.get("consignee", "")
        shipper = t.get("shipper", "")
        lines = []

        # 行1: 类别标签 + 客户 + 金额
        h = f'<span style="background:{pri_color};color:#fff;padding:2px 10px;border-radius:4px;font-size:11px;font-weight:600;">{cat_label}</span>'
        if cust:
            h += f'&nbsp; <b style="color:#fff;font-size:15px;">{cust}</b>'
        if amount:
            h += f'&nbsp; <span style="color:#ffd700;font-weight:700;">{amount}</span>'
        lines.append(h)

        # 行2: 收货人Consignee / 发货人Shipper (核心指向信息)
        party_parts = []
        if consignee:
            party_parts.append(f'<span style="color:#4fc3f7;">收货人: {consignee[:50]}</span>')
        if shipper and 'WORLDWIDE' not in shipper.upper():
            party_parts.append(f'<span style="color:#81c784;">发货人: {shipper[:35]}</span>')
        if party_parts:
            lines.append(f'<div style="font-size:12px;margin:3px 0;">{"&nbsp;&nbsp;|&nbsp;&nbsp;".join(party_parts)}</div>')

        # 行3: 行动指引
        lines.append(f'<div style="color:#c0c0d0;font-size:13px;margin:4px 0;">{t["action"]}</div>')

        # 行4: 提单号 + 船公司
        refs = []
        if mbl:
            ref = f'MBL: <span style="font-family:monospace;color:#a0a0e0;">{mbl}</span>'
            if carrier:
                ref += f' <span style="color:#888;">({carrier})</span>'
            refs.append(ref)
        if hbl:
            refs.append(f'HBL: <span style="font-family:monospace;color:#a0a0e0;">{hbl}</span>')
        if refs:
            lines.append(f'<div style="font-size:12px;margin:2px 0;">{"&nbsp;&nbsp;|&nbsp;&nbsp;".join(refs)}</div>')

        # 行5: 费用明细
        if details:
            detail_html = "&nbsp;/&nbsp;".join(d[:40] for d in details[:4])
            if len(details) > 4:
                detail_html += f" +{len(details)-4}项"
            lines.append(f'<div style="color:#777;font-size:11px;">明细: {detail_html}</div>')

        # 行6: 找谁(收货人联系方式 / 委托方WWL分公司 / origin操作人)
        wwl_sender = t.get("wwl_sender", "")
        wwl_branch = t.get("wwl_branch", "")
        who_lines = []

        # A: 收货人/客户方联系人
        if ext_contact:
            who_lines.append(f'<span style="color:#00c853;font-weight:600;">收货人: {ext_contact[:60]}</span>')
        elif contact:
            who_lines.append(f'<span style="color:#00c853;font-weight:600;">客户方: {contact[:60]}</span>')

        # B: 委托方(WWL哪个分公司发给我们的)
        if wwl_sender and wwl_branch.startswith("WWL"):
            who_lines.append(f'<span style="color:#ff9800;font-weight:600;">找: {wwl_sender[:45]}</span> <span style="color:#cc7700;">[{wwl_branch}]</span>')

        # C: 如果A和B都没有，显示origin端操作人(最后的兜底)
        if not who_lines and internal:
            who_lines.append(f'<span style="color:#2196f3;">Origin操作: {internal}</span>')

        for wl in who_lines:
            lines.append(f'<div style="font-size:12px;margin:2px 0;">{wl}</div>')

        body = "".join(lines)
        return f'<div style="background:rgba({bg_alpha});border-left:4px solid {pri_color};padding:10px 14px;border-radius:0 10px 10px 0;margin:5px 0;">{body}</div>'

    _chk_counter = [0]  # 用列表绕过scope限制

    def render_task_with_confirm(t, pri_color, bg_alpha):
        """渲染任务卡片 + 两步确认"""
        _chk_counter[0] += 1
        n = _chk_counter[0]
        st.markdown(render_task_card(t, pri_color, bg_alpha), unsafe_allow_html=True)
        c1, c2, c3 = st.columns([0.15, 0.15, 0.7])
        with c1:
            checked = st.checkbox("完成", key=f"chk_{n}", label_visibility="visible")
        with c2:
            if checked:
                if st.button("确认", key=f"cfm_{n}"):
                    completed_ids[t["id"]] = {"time": datetime.now().isoformat(), "by": "team"}
                    save_tasks({"completed": completed_ids, "tasks": all_tasks})
                    st.rerun()

    # ─── 紧急任务(折叠框) ───
    if pending_urgent:
        with st.expander(f"紧急待办 ({len(pending_urgent)})", expanded=True):
            for t in pending_urgent:
                render_task_with_confirm(t, "#e94560", "233,69,96,0.10")

    # ─── 重要任务 ───
    if pending_high:
        with st.expander(f"重要待办 ({len(pending_high)})", expanded=len(pending_urgent) == 0):
            for t in pending_high:
                render_task_with_confirm(t, "#ffa500", "255,165,0,0.06")

    # ─── 常规任务 ───
    if pending_medium:
        with st.expander(f"常规待办 ({len(pending_medium)})"):
            for t in pending_medium:
                render_task_with_confirm(t, "#2196f3", "33,150,243,0.05")

    # (Hold/查验/CC/异常已移到教练总结下方)

    # ─── 今日已完成 ───
    if done_today:
        with st.expander(f"已完成 ({len(done_today)})"):
            for t in done_today:
                info = completed_ids.get(t["id"], {})
                done_time = info.get("time", "")[:16] if isinstance(info, dict) else ""
                st.markdown(f"""<div style="border-left:3px solid #00c853;padding:4px 12px;margin:2px 0;opacity:0.6;">
                    <span style="color:#00c853;">✓</span> <s style="color:#888;">{t['title']}</s>
                    <span style="color:#555;font-size:11px;"> 完成于 {done_time}</span>
                </div>""", unsafe_allow_html=True)

    # 清除过期完成记录(超过24h的)
    now_ts = datetime.now()
    stale_keys = []
    for tid, info in completed_ids.items():
        if isinstance(info, dict) and info.get("time"):
            try:
                done_dt = datetime.fromisoformat(info["time"])
                if (now_ts - done_dt).total_seconds() > 86400:
                    stale_keys.append(tid)
            except:
                pass
    if stale_keys:
        for k in stale_keys:
            del completed_ids[k]
        save_tasks({"completed": completed_ids, "tasks": all_tasks})

    # (事件详情已移到常规待办后面)

# ══════════════════════════════════════════════════════════════════
# TAB 2: 提单状态监控
# ══════════════════════════════════════════════════════════════════
with tabs[1]:
    section_header("提单状态总览")

    coach_box("教练总结: 提单状态监控是换单操作的生命线", """
        <b>MBL没有TLX = origin还没放单, 我们无法换单。</b> 每一个未电放的MBL都是一个潜在的延误风险。
        如果货物已经到港但MBL未电放, 船公司不会释放DO(Delivery Order), 意味着我们无法安排提货,
        滞期费每天都在累积。<br><br>
        <b>AN已收但无预报 = 可能漏接了业务, 需要立即排查。</b> 这意味着船公司已经发了到港通知,
        但我们系统里没有对应的预报(Pre-alert)记录。可能是origin忘了发预报, 也可能是我们漏处理了。
        无论哪种情况, 都需要在24小时内查明并补录。<br><br>
        <b>Hold提单需要根据类型采取不同行动:</b><br>
        - <b>Freight Hold:</b> 运费未付, 联系origin催付, 通常1-2个工作日可解决<br>
        - <b>Regulatory Hold:</b> 海关/监管hold, 需要补充ISF/PI/PL等文件, 可能需要3-5天<br>
        - <b>DO Fee Hold:</b> 目的港费用未付, 联系财务确认并付款, 通常PayCargo当天可解决<br><br>
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
        mbl_df = pd.DataFrame({
            "序号": range(1, len(no_tlx_mbl) + 1),
            "MBL号": no_tlx_mbl,
            "船公司": [
                "MSC" if m.startswith("MEDU") else
                "CMA-CGM" if m.startswith("CMDU") else
                "COSCO" if m.startswith("COSU") else
                "ONE" if m.startswith("ONEY") else
                "OOCL" if m.startswith("OOLU") else
                "ZIM" if m.startswith("ZIMU") else
                "其他"
                for m in no_tlx_mbl
            ],
            "建议行动": ["联系origin确认TLX状态, 催促放单"] * len(no_tlx_mbl),
            "负责人": ["Everlyn"] * len(no_tlx_mbl),
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
            "建议行动": ["联系销售确认TLX, 确认客户是否已付款"] * len(no_tlx_hbl),
            "负责人": ["Everlyn + Maggie"] * len(no_tlx_hbl),
        })
        st.dataframe(hbl_df, use_container_width=True, hide_index=True, key="tbl_2")
    else:
        alert_card("green", "所有HBL已完成电放 - 优秀!")

    # AN no prealert
    section_header(f"AN已收但无预报 - 可能漏单! ({len(an_no_prealert)}个)")
    if an_no_prealert:
        an_df = pd.DataFrame({
            "序号": range(1, len(an_no_prealert) + 1),
            "MBL号": an_no_prealert,
            "风险等级": ["极高-可能漏单"] * len(an_no_prealert),
            "建议行动": ["可能漏单! 立即查找对应预报邮件, 确认是否有对应HBL, 联系origin核实"] * len(an_no_prealert),
            "负责人": ["Everlyn (查找) + Effy (确认)"] * len(an_no_prealert),
        })
        st.dataframe(an_df, use_container_width=True, hide_index=True, key="tbl_3")
    else:
        alert_card("green", "所有AN均有对应预报 - 无漏单风险")

    # Hold BL
    section_header(f"Hold提单 ({len(hold_bl)}个)")
    if hold_bl:
        hold_rows = []
        for h in hold_bl:
            hold_rows.append({
                "MBL": h.get("mbl", ""),
                "Hold类型": h.get("type", "Unknown"),
                "需补资料": "是" if h.get("needs_docs") else "否",
                "来源邮件主题": h.get("subject", ""),
                "来源": h.get("from", ""),
                "建议行动": (
                    "Freight Hold: 联系origin催付运费"
                    if "freight" in str(h.get("type", "")).lower()
                    else "Regulatory Hold: 准备ISF/PI/PL补充文件"
                    if "regulatory" in str(h.get("type", "")).lower()
                    else "DO Fee Hold: 联系Maggie确认付款"
                    if "do" in str(h.get("type", "")).lower() or "fee" in str(h.get("type", "")).lower()
                    else "检查Hold类型, 联系船公司确认具体要求"
                ),
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

    coach_box("教练总结: D&D费用审查 + 催收策略", """
        <b>第一步: 审查D&D账单合规性(FMC 46 CFR 541.6):</b>
        收到船公司D&D账单 → 核对19项必备要素(BL号/柜号/免费天数/起止日/费率/争议联系方式等)
        → <em>缺任何一项=无需付款, 直接争议</em>。2020-2025年全美D&D总额$154亿, 很多账单不合规。<br><br>
        <b>第二步: 区分费用类型:</b>
        D&D($52K/60天) — 受FMC监管, 可争议不合理收费;
        Chassis($1.7M!) — 不受FMC管, 需与DCLI/TRAC池运营商直接谈判。
        <em>Chassis是我们最大单项费用, 远超D&D, 必须重视!</em><br><br>
        <b>第三步: 催收时间线:</b>
        T+7首次催收 → T+15三方协同群 → T+30正式追偿函 → T+45中信保窗口(超时=理赔失效!)。
        Top欠费: NEXTERA $47K(可能含大量Houston Rail Detention), AVANTIX $36K, ELITE EAGLE $27K。<br><br>
        <b>FMC争议权利:</b> 被计费方有30天争议期; FMC CADRS提供免费调解;
        $50K以下走Small Claims快速通道; <em>OSRA禁止船公司因你投诉而报复拒舱</em>。
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

    # (按负责人分组已移除 — 等确认分工后再加)

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
  try:
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
  except Exception as _e7:
    import traceback as _tb7
    st.error(f"供应商全景 加载出错: {type(_e7).__name__}: {_e7}")
    st.code(_tb7.format_exc(), language="text")



# ══════════════════════════════════════════════════════════════════
# TAB 8: 船公司全景
# ══════════════════════════════════════════════════════════════════
with tabs[7]:
  try:
    section_header("船公司全景")

    coach_box("教练总结: 船公司选择 — 全成本+法规+集中度", """
        <b>全成本公式:</b> 运费 + 目的港费用 + D&D风险 + Chassis费 + Hold频率 + 查验概率 + 服务响应。
        <em>不要只看运费!</em><br><br>
        <b>FMC OSRA保护:</b> 船公司不得因我们投诉D&D或使用竞争对手而拒绝舱位(反报复条款)。
        也不得无合理理由拒绝我们订舱(拒绝交易规则, 2024.7生效)。遇到不合理拒舱, 可向FMC投诉。<br><br>
        <b>集中度红线(从14,825封邮件发现):</b>
        JINGZHOU 100%走Hapag-Lloyd(64次) — 必须开发备选!
        CLOU 71%走ZIM, HITHIUM 68%走ZIM — ZIM变动影响两家。
        建议: &gt;70%集中度的客户必须有B计划船公司。<br><br>
        <b>D&D账单对比:</b> 14天累计D&D最贵: NY($3,182) &gt; Long Beach($2,730) &gt; LA($2,673)。
        MSC邮件最多(2,211封/331 MBL)但目的港费用复杂。ONE/OOCL查验概率需持续观察。<br><br>
        <b>Demurrage免费天数:</b> LA/LB 4天 / NY 4天(不含周末) / Savannah 7天 / Houston 4天。
        Free Time从卸船后凌晨3:00开始计(LA/LB), 不是从我们收到AN开始!
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
  except Exception as _e8:
    import traceback as _tb8
    st.error(f"船公司全景 加载出错: {type(_e8).__name__}: {_e8}")
    st.code(_tb8.format_exc(), language="text")



# ══════════════════════════════════════════════════════════════════
# TAB 9: 目的港全景
# ══════════════════════════════════════════════════════════════════
with tabs[8]:
  try:
    section_header("美国目的港全景地图")

    coach_box("教练总结: 分港策略 — 费率/Free Time/操作要点", """
        <b>LA/LB (286次, 业务量最大):</b> Free Time仅4天, 超时40'柜$80-150/天。
        PierPass白天作业费$77.56/40'柜, 走OffPeak夜班可免。
        Chassis用DCLI/TRAC "Pool of Pools"(2025.6起共享池)。
        太阳能柜/电池柜(40,000+lbs)必须提前确认三轴chassis可用性!
        <em>操作: 到港前48h完成报关+DO准备, Free Time第2天安排卡车。</em><br><br>
        <b>NY/NJ (107次, D&D最贵!):</b> Free Time 4天(不含周末假日), 但D&D是全美最贵: $125-175/天,
        14天累计$3,182! Maher/APM/GCT等多码头, 注意不同码头费率差异。
        <em>NY票必须快进快出, Free Time第1天就安排卡车。</em><br><br>
        <b>Houston (208次):</b> Bayport和Barbours Cut两个码头。IPI铁路(BNSF/UP到Chicago约3天)
        是主力但Rail Detention $75-300/天。NEXTERA $47K欠费可能含大量Rail Detention。
        <em>IPI货提前7天通知收货人, 到达后48h内必须提柜。</em><br><br>
        <b>Savannah (112次, Free Time最长):</b> GPA给7天Free Time(全美最慷慨), 超时$32-47/TEU/天。
        REACH的主要目的港, 操作压力相对小。但出了Free Time后费用也会快速叠加。<br><br>
        <b>Chassis关键提醒:</b> 我们Chassis费用$1.7M是最大单项成本(远超D&D的$52K)。
        日租$20-35/天, 太阳能重柜需三轴chassis(费用更高, 供应有限)。
        Drop-and-hook比Live Unload省钱省时, 建议有仓库的客户优先用。
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
  except Exception as _e9:
    import traceback as _tb9
    st.error(f"目的港全景 加载出错: {type(_e9).__name__}: {_e9}")
    st.code(_tb9.format_exc(), language="text")



# ══════════════════════════════════════════════════════════════════
# TAB 10: 联系人搜索
# ══════════════════════════════════════════════════════════════════
with tabs[9]:
  try:
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
  except Exception as _e10:
    import traceback as _tb10
    st.error(f"联系人搜索 加载出错: {type(_e10).__name__}: {_e10}")
    st.code(_tb10.format_exc(), language="text")


# ─── Footer ───
st.markdown("""
<div style="text-align:center; padding:30px 0 10px 0; color:#4a4a6a; font-size:12px;">
    WWL 环世物流 运营指挥中心 v5.0 | Powered by OpenClaw Engine |
    数据源: 邮件智能扫描 + 供应商数据库 + 联系人数据库<br>
    所有建议仅供参考, 请结合实际情况判断执行
</div>
""", unsafe_allow_html=True)
