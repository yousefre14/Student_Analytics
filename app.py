# streamlit_app.py
# Kayfa Student Analytics Dashboard
# All 15 Questions answered with interactive visualizations

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from PIL import Image
from io import BytesIO
import requests
from datetime import datetime
import os
from pymongo import MongoClient

# ─────────────────────────────────────────────────────────────────────────────
# LOGO LOADER
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_logo2():
    """Try to load Kayfa logo from local or GitHub"""
    try:
        return Image.open("company_logo2.png")
    except FileNotFoundError:
        try:
            # Fallback to a simple text logo
            return None
        except Exception:
            return None

logo2 = load_logo2()

def load_logo1():
    """Try to load Kayfa logo from local or GitHub"""
    try:
        return Image.open("logo1.png")
    except FileNotFoundError:
        try:
            # Fallback to a simple text logo
            return None
        except Exception:
            return None

logo1 = load_logo1()

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  —  must be the very first Streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Student Analytics Intelligence · Kayfa",
    page_icon=logo1,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# BRAND CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
KB            = "#1A5AFF"      # Kayfa Blue
KB_DARK       = "#1245CC"
KB_LIGHT      = "#E8EFFF"
AMBER         = "#F59E0B"      # Reference/avg lines
GREEN         = "#16A34A"
RED           = "#DC2626"
ORANGE        = "#EA580C"

# ─────────────────────────────────────────────────────────────────────────────
# CSS  —  rgba backgrounds = dark-mode safe
# ─────────────────────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

* { font-family: 'Plus Jakarta Sans', sans-serif; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #1A5AFF 0%, #1245CC 100%) !important;
}
section[data-testid="stSidebar"] * { color: #FFFFFF !important; }
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.25) !important;
    margin: 0.8rem 0 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important; font-weight: 700;
}
section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background: rgba(255,255,255,0.2) !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.15) !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
}

/* ── Main padding ── */
[data-testid="stMainBlockContainer"] {
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
}

/* ── Insight box ── */
.insight-box {
    background: rgba(26,90,255,0.08);
    border-left: 4px solid #1A5AFF;
    border-radius: 8px;
    padding: 0.85rem 1.1rem;
    margin: 0.8rem 0;
    font-size: 0.84rem;
    line-height: 1.6;
}
.insight-box b { color: #1A5AFF; font-weight: 700; }

/* ── CTA box ── */
.cta-box {
    background: rgba(22,163,74,0.07);
    border-left: 4px solid #16A34A;
    border-radius: 8px;
    padding: 0.85rem 1.1rem;
    margin: 0.8rem 0;
    font-size: 0.84rem;
    line-height: 1.6;
}
.cta-box b { color: #16A34A; font-weight: 700; }

/* ── Risk box ── */
.risk-card {
    background: rgba(220,38,38,0.07);
    border: 1px solid rgba(220,38,38,0.25);
    border-left: 4px solid #DC2626;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
    line-height: 1.6;
}
.risk-card b { color: #DC2626; font-weight: 700; }

/* ── Q badge ── */
.q-badge {
    display: inline-block;
    background: #1A5AFF;
    color: white !important;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    border-radius: 4px;
    padding: 2px 9px;
    margin-bottom: 0.3rem;
    text-transform: uppercase;
}

/* ── Section title ── */
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    border-bottom: 3px solid #1A5AFF;
    padding-bottom: 0.5rem;
    margin: 1.4rem 0 0.9rem 0;
    color: #1245CC;
}

/* ── Hero ── */
.hero-title { font-size: 1.9rem; font-weight: 800; line-height: 1.2; margin: 0; }
.hero-sub   { font-size: 0.88rem; opacity: 0.65; margin-top: 0.3rem; }

/* ── KPI card ── */
.kpi-card {
    background: rgba(26,90,255,0.06);
    border-left: 4px solid #1A5AFF;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    box-shadow: 0 2px 8px rgba(26,90,255,0.08);
}
.kpi-num { font-size: 2rem; font-weight: 800; color: #1A5AFF; line-height: 1; }
.kpi-lbl {
    font-size: 0.72rem; font-weight: 600; opacity: 0.6;
    text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.2rem;
}

footer { visibility: hidden; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)



# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY HELPERS
# ─────────────────────────────────────────────────────────────────────────────
_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans, sans-serif", size=12),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    hovermode="closest",
)

def _theme(fig: go.Figure, height: int = 480) -> go.Figure:
    """Apply Kayfa theme"""
    fig.update_layout(**_LAYOUT, height=height)
    fig.update_xaxes(
        gridcolor="rgba(26,90,255,0.1)",
        linecolor="rgba(26,90,255,0.2)",
        tickfont_size=11, showgrid=True,
    )
    fig.update_yaxes(
        gridcolor="rgba(26,90,255,0.1)",
        linecolor="rgba(26,90,255,0.2)",
        tickfont_size=11, showgrid=True,
    )
    return fig

def _add_avg_line(fig: go.Figure, y_val: float,
                  label: str = "Platform Average",
                  orientation: str = "v") -> go.Figure:
    """Add a reference line with legend entry"""
    if orientation == "h":
        fig.add_vline(x=y_val, line_dash="dash",
                      line_color=AMBER, line_width=2.5)
    else:
        fig.add_hline(y=y_val, line_dash="dash",
                      line_color=AMBER, line_width=2.5)

    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="lines",
        line=dict(dash="dash", color=AMBER, width=2.5),
        name=label, showlegend=True,
    ))
    return fig

def _insight(text: str):
    st.markdown(f"<div class='insight-box'>{text}</div>", unsafe_allow_html=True)

def _cta(text: str):
    st.markdown(f"<div class='cta-box'>{text}</div>", unsafe_allow_html=True)

def _risk(text: str):
    st.markdown(f"<div class='risk-card'>{text}</div>", unsafe_allow_html=True)

def _qbadge(label: str):
    st.markdown(f"<span class='q-badge'>{label}</span>", unsafe_allow_html=True)

def _section(title: str):
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)

def _safe_pct(num: float, denom: float, fallback: float = 0.0) -> float:
    return (num / denom * 100) if denom > 0 else fallback

def _safe_first(series: pd.Series, fallback: float = 0.0) -> float:
    return float(series.values[0]) if len(series) > 0 else fallback

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING  —  cached, runs once per session
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_mongodb_client():
    """Get MongoDB connection (cached at session level)"""
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        st.error("MONGODB_URI not set in environment")
        st.stop()
    
    client = MongoClient(mongo_uri)
    return client

@st.cache_data(show_spinner="Loading data from MongoDB…")
def load_all_data():
    """Load all data from MongoDB Atlas"""
    client = get_mongodb_client()
    db = client["kayfa_analytics"]
    
    data = {}
    
    # Main collections
    collections = {
        'students': 'students',
        'groups': 'groups',
        'courses': 'courses',
        'grades': 'grades',
        'attendance': 'attendance',
        'concepts': 'concepts',
        'engagement': 'engagement',
        'submissions': 'submissions',
        'full_model': 'full_model',
    }
    
    # Question collections
    questions = {
        'q1': 'q1_attendance',
        'q2': 'q2_scores',
        'q3': 'q3_courses',
        'q4': 'q4_correlation',
        'q4_scatter_data': 'q4_scatter',
        'q5': 'q5_engagement',
        'q5_scatter_data': 'q5_scatter',
        'q6': 'q6_concepts',
        'q7': 'q7_trends',
        'q8': 'q8_late',
        'q9': 'q9_cohort',
        'q10': 'q10_age',
        'q11': 'q11_segments',
        'q12': 'q12_groups',
        'q13': 'q13_viability',
        'q13_group_metrics': 'q13_metrics',
        'q14': 'q14_risk',
        'q15': 'q15_trends',
    }
    
    # Load main collections
    for key, collection_name in collections.items():
        try:
            records = list(db[collection_name].find({}, {'_id': 0}))
            data[key] = pd.DataFrame(records) if records else pd.DataFrame()
            print(f"{key}: {len(records)} records")
        except Exception as e:
            st.warning(f"Missing collection: {collection_name}")
            data[key] = pd.DataFrame()
    
    # Load question collections
    for key, collection_name in questions.items():
        try:
            records = list(db[collection_name].find({}, {'_id': 0}))
            data[key] = pd.DataFrame(records) if records else pd.DataFrame()
        except Exception:
            data[key] = pd.DataFrame()
    
    return data

# Load data
data = load_all_data()

# ─────────────────────────────────────────────────────────────────────────
# SIDEBAR — Logo + Filters
# ─────────────────────────────────────────────────────────────────────────
with st.sidebar:
    if logo1 is not None:
        st.image(logo1, width="stretch")
    else:
        st.markdown(
            "<div style='direction:rtl;text-align:center;font-size:2.5rem;font-weight:900;padding:0.5rem 0;color:#1A5AFF;'>كيف</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 🎯 Filters")

    # Get full model
    full_model = data.get('full_model', pd.DataFrame())

    if not full_model.empty:
        # ── GROUP FILTER ──
        all_groups = sorted(full_model['group_id'].dropna().unique().tolist()) if 'group_id' in full_model.columns else []
        sel_groups = st.multiselect("Group", all_groups, default=all_groups, key="groups")
        
        # ── COURSE FILTER ──
        all_courses = sorted(full_model['course_id'].dropna().unique().tolist()) if 'course_id' in full_model.columns else []
        sel_courses = st.multiselect("Course", all_courses, default=all_courses, key="courses")
        
        # ── ATTENDANCE FILTER ──
        if 'attendance_rate' in full_model.columns:
            att_min = float(full_model['attendance_rate'].min())
            att_max = float(full_model['attendance_rate'].max())
            sel_att = st.slider("Min Attendance Rate (%)", att_min, att_max, (att_min, att_max), key="attendance")
        else:
            sel_att = (0, 100)
        
        # ── APPLY FILTERS TO FULL MODEL ──
        mask = pd.Series([True] * len(full_model))
        if 'group_id' in full_model.columns and sel_groups:
            mask &= full_model['group_id'].isin(sel_groups)
        if 'course_id' in full_model.columns and sel_courses:
            mask &= full_model['course_id'].isin(sel_courses)
        if 'attendance_rate' in full_model.columns:
            mask &= full_model['attendance_rate'].between(sel_att[0], sel_att[1])
        
        filtered_model = full_model[mask] if mask.any() else full_model
        filtered_student_ids = set(filtered_model['student_id'].dropna().unique()) if 'student_id' in filtered_model.columns else set()
        filtered_group_ids = set(filtered_model['group_id'].dropna().unique()) if 'group_id' in filtered_model.columns else set()
        filtered_course_ids = set(filtered_model['course_id'].dropna().unique()) if 'course_id' in filtered_model.columns else set()
        
    else:
        filtered_model = full_model
        filtered_student_ids = set()
        filtered_group_ids = set()
        filtered_course_ids = set()
        sel_groups = []
        sel_courses = []
        sel_att = (0, 100)

    st.markdown("---")
    st.caption(
        "🎓 Kayfa AI & Data Analytics\n"
        "Week 2 · Student Analytics Track\n"
        f"Last updated: {datetime.now().strftime('%Y-%m-%d')}"
    )

# ─────────────────────────────────────────────────────────────────────────
# HELPER: Filter question data by sidebar selections
# ─────────────────────────────────────────────────────────────────────────
def filter_by_sidebar(df, by='group'):
    """Filter dataframe by sidebar selections"""
    if df.empty:
        return df
    
    if by == 'group' and 'group_id' in df.columns and filtered_group_ids:
        return df[df['group_id'].isin(filtered_group_ids)]
    elif by == 'course' and 'course_id' in df.columns and filtered_course_ids:
        return df[df['course_id'].isin(filtered_course_ids)]
    elif by == 'student' and 'student_id' in df.columns and filtered_student_ids:
        return df[df['student_id'].isin(filtered_student_ids)]
    
    return df

# ─────────────────────────────────────────────────────────────────────────────
# HELPER METRICS
# ─────────────────────────────────────────────────────────────────────────────
def _kpi_row():
    """Display key metrics row"""
    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
        total_students = len(filtered_model) if not filtered_model.empty else 0
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-lbl'>Total Students</div>"
            f"<div class='kpi-num'>{total_students:,}</div>"
            f"<div style='font-size:.75rem;opacity:.6;'>in filters</div></div>",
            unsafe_allow_html=True)
    
    with k2:
        avg_attendance = filtered_model['attendance_rate'].mean() if 'attendance_rate' in filtered_model.columns else 0
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-lbl'>Avg Attendance</div>"
            f"<div class='kpi-num'>{avg_attendance:.1f}%</div>"
            f"<div style='font-size:.75rem;opacity:.6;'>rate</div></div>",
            unsafe_allow_html=True)
    
    with k3:
        score_col = 'avg_score' if 'avg_score' in filtered_model.columns else 'score_mean'
        avg_score = filtered_model[score_col].mean() if score_col in filtered_model.columns else 0
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-lbl'>Avg Grade</div>"
            f"<div class='kpi-num'>{avg_score:.1f}</div>"
            f"<div style='font-size:.75rem;opacity:.6;'>out of 100</div></div>",
            unsafe_allow_html=True)
    
    with k4:
        total_events = filtered_model['total_events'].sum() if 'total_events' in filtered_model.columns else 0
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-lbl'>Total Engagement</div>"
            f"<div class='kpi-num'>{total_events:,.0f}</div>"
            f"<div style='font-size:.75rem;opacity:.6;'>events</div></div>",
            unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE — OVERVIEW (All 15 Questions via Tabs)
# ═════════════════════════════════════════════════════════════════════════════
def page_overview():
    # ── Hero header ──────────────────────────────────────────────────────────
    col_title, _, col_logo = st.columns([6, 1, 2])
    with col_title:
        st.markdown(
            "<p class='hero-sub'>Week #2 Task:</p>"
            "<h1 class='hero-title'>Student Analytics Intelligence</h1>"
            "<p class='hero-sub'>Data Analytics · Kayfa · 15 Questions Answered</p>",
            unsafe_allow_html=True,
        )
    with col_logo:
        if logo2 is not None:
            st.image(logo2, width=480)
        else:
            st.markdown(
                "<div style='direction:rtl;text-align:right;font-size:2rem;"
                "font-weight:900;color:#1A5AFF;'>كيف</div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")
    _kpi_row()
    st.markdown("---")

    # ── 15 question tabs ──────────────────────────────────────────────────────
    tabs = st.tabs([
        "Q1 · Attendance",
        "Q2 · Scores",
        "Q3 · Courses",
        "Q4 · Attendance-Grade",
        "Q5 · Engagement",
        "Q6 · Concepts",
        "Q7 · Trends",
        "Q8 · Late Work",
        "Q9 · Cohort",
        "Q10 · Age",
        "Q11 · Segments",
        "Q12 · Groups",
        "Q13 · Viability",
        "Q14 · At-Risk",
        "Q15 · Performance",
    ])

    # ────────────────────────────────────────────────────────────────────────
    # Q1: ATTENDANCE BY GROUP
    # ────────────────────────────────────────────────────────────────────────
    with tabs[0]:
        _qbadge("Q1 · Attendance Rate per Group")
        _section("Which Groups Sit Below the Platform Average?")
        
        q1_data = data.get('q1', pd.DataFrame())
        
        # ✅ FILTER by sidebar selections
        q1_data = filter_by_sidebar(q1_data, by='group')
        
        if not q1_data.empty:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                fig = px.bar(
                    q1_data.sort_values('attendance_rate_mean'),
                    x='attendance_rate_mean', y='group_id',
                    orientation='h',
                    title="Attendance Rate by Group",
                    text='attendance_rate_mean',
                    color='attendance_rate_mean',
                    color_continuous_scale=[RED, KB_LIGHT, GREEN],
                )
                fig.update_traces(
                    texttemplate="%{x:.1f}%",
                    textposition="outside",
                    marker_line=dict(width=0),
                )
                fig.update_layout(
                    xaxis_title="Attendance Rate (%)",
                    yaxis_title="",
                    showlegend=False,
                    margin=dict(l=80, r=60, t=55, b=45),
                    xaxis=dict(range=[0, 105]),
                )
                if 'platform_avg' in q1_data.columns:
                    platform_avg = q1_data['attendance_rate_mean'].mean()
                    _add_avg_line(fig, platform_avg, orientation="h")
                    fig.add_annotation(
                            x=platform_avg,
                            y=1.07, 
                            text=f"{platform_avg:.1f}%",
                            showarrow=False,
                            font=dict(size=12, color="orange"),
                            xref="x",
                            yref="paper"
                        )
                st.plotly_chart(_theme(fig, height=420), width='stretch')
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if 'platform_avg' in q1_data.columns:
                    platform_avg = q1_data['platform_avg'].iloc[0]
                    below_avg = (q1_data['attendance_rate_mean'] < platform_avg).sum()
                    st.markdown(
                        f"<div class='kpi-card'><div class='kpi-lbl'>Platform Avg</div>"
                        f"<div class='kpi-num'>{platform_avg:.1f}%</div>"
                        f"<div style='font-size:.75rem;opacity:.6;'>{below_avg} groups below</div></div>",
                        unsafe_allow_html=True)
                    
                    _insight(
                        f"<b>{below_avg}</b> groups fall below the <b>{platform_avg:.1f}%</b> platform average. "
                        f"These groups need targeted support for attendance improvement."
                    )
        else:
            st.warning("No data available for selected filters")

    #q2

    with tabs[1]:
        _qbadge("Q2 · Score Distribution by Assessment Type")
        _section("How Are Scores Distributed by Assessment Type?")
        
        grades_data = data.get('grades', pd.DataFrame())
        
        # ✅ FILTER by sidebar selections
        if 'student_id' in grades_data.columns and filtered_student_ids:
            grades_data = grades_data[grades_data['student_id'].isin(filtered_student_ids)]
        
        if not grades_data.empty:
            fig = px.box(
                grades_data,
                x='type', y='score',
                title="Score Distribution by Assessment Type",
                labels={'type': 'Assessment Type', 'score': 'Score (0-100)'},
                color='type',
                points='outliers'
            )
            fig.update_layout(
                showlegend=False,
                margin=dict(l=50, r=40, t=55, b=45),
            )
            st.plotly_chart(_theme(fig, height=480), width='stretch')
            
            q2_data = data.get('q2', pd.DataFrame())
            if 'volatility_cv' in q2_data.columns:
                _insight(
                    f"Assessment type volatility (Coefficient of Variation) ranges from "
                    f"<b>{q2_data['volatility_cv'].min():.3f}</b> to "
                    f"<b>{q2_data['volatility_cv'].max():.3f}</b>. "
                    f"Higher CV indicates less consistent performance."
                )
        else:
            st.warning(" No data available for selected filters")

    # ────────────────────────────────────────────────────────────────────────
    # Q3: COURSE PERFORMANCE
    # ────────────────────────────────────────────────────────────────────────
    with tabs[2]:
        _qbadge("Q3 · Course Performance Comparison")
        _section("Which Course Has Highest/Lowest Average Grade?")
        
        q3_data = data.get('q3', pd.DataFrame())
        
        q3_data = filter_by_sidebar(q3_data, by='course')
        
        if not q3_data.empty:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                fig = px.bar(
                    q3_data.sort_values('avg_score', ascending=False),
                    x='course_id', y='avg_score',
                    error_y='std_dev',
                    title="Average Grade by Course (with Std Dev)",
                    text='avg_score',
                    color='avg_score',
                    color_continuous_scale='Viridis',
                )
                fig.update_traces(
                    texttemplate="%{y:.1f}",
                    textposition="outside",
                    marker_line=dict(width=0),
                )
                fig.update_layout(
                    xaxis_title="Course",
                    yaxis_title="Average Score",
                    showlegend=False,
                    margin=dict(l=50, r=40, t=55, b=45),
                    yaxis=dict(range=[0, 110]),
                )
                st.plotly_chart(_theme(fig, height=450), width='stretch')
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                highest = q3_data.iloc[0]
                lowest = q3_data.iloc[-1]
                
                st.markdown(
                    f"<div class='insight-box'>"
                    f"<b>Highest:</b> {highest['course_id']}<br>"
                    f"{highest['avg_score']:.1f} (±{highest['std_dev']:.1f})<br><br>"
                    f"<b>Lowest:</b> {lowest['course_id']}<br>"
                    f"{lowest['avg_score']:.1f} (±{lowest['std_dev']:.1f})"
                    f"</div>",
                    unsafe_allow_html=True)
        else:
            st.warning("No data available for selected filters")

    # ────────────────────────────────────────────────────────────────────────
    # Q4: ATTENDANCE VS GRADE
    # ────────────────────────────────────────────────────────────────────────
    with tabs[3]:
        _qbadge("Q4 · Attendance vs Grade Relationship")
        _section("Is There a Relationship Between Attendance and Grades?")
        
        q4_scatter = data.get('q4_scatter_data', pd.DataFrame())
        q4_scatter = filter_by_sidebar(q4_scatter, by='student')  
        
        q4_stats = data.get('q4', pd.DataFrame())
        
        if not q4_scatter.empty:
            score_col = 'avg_score' if 'avg_score' in q4_scatter.columns else 'score_mean'
            
            fig = px.scatter(
                q4_scatter,
                x='attendance_rate', y=score_col,
                trendline='ols',
                title="Attendance Rate vs Average Grade",
                labels={'attendance_rate': 'Attendance Rate (%)', score_col: 'Average Score'},
                opacity=0.6
            )
            fig.update_layout(margin=dict(l=50, r=40, t=55, b=45))
            st.plotly_chart(_theme(fig, height=480), width='stretch')
            # Display metrics if available
        if not q4_stats.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            # Extract values safely
            try:
                corr_val = float(q4_stats[q4_stats['metric'] == 'correlation']['value'].values[0])
                col1.metric("Correlation", f"{corr_val:.4f}")
            except:
                col1.metric("Correlation", "N/A")
            
            try:
                r2_val = float(q4_stats[q4_stats['metric'] == 'r_squared']['value'].values[0])
                col2.metric("R²", f"{r2_val:.4f}")
            except:
                col2.metric("R²", "N/A")
            
            try:
                slope_val = float(q4_stats[q4_stats['metric'] == 'slope']['value'].values[0])
                col3.metric("Slope", f"{slope_val:.6f}")
            except:
                col3.metric("Slope", "N/A")
            
            try:
                p_val = float(q4_stats[q4_stats['metric'] == 'p_value']['value'].values[0])
                col4.metric("P-value", f"{p_val:.2e}")
            except:
                col4.metric("P-value", "N/A")
            
            _insight(
                "Attendance and grades show a <b>positive relationship</b>. "
                "Students who attend more frequently tend to earn higher grades."
            )
        elif not q4_scatter.empty:
            _insight("Scatter plot shows relationship between attendance and grades.")
        else:
            st.warning("No data available for selected filters")

    # ────────────────────────────────────────────────────────────────────────
    # Q5: ENGAGEMENT VS PERFORMANCE
    # ────────────────────────────────────────────────────────────────────────
    with tabs[4]:
        _qbadge("Q5 · Engagement vs Performance")
        _section("Does Engagement Relate to Academic Performance?")
        
        q5_scatter = data.get('q5_scatter_data', pd.DataFrame())
        q5_scatter = filter_by_sidebar(q5_scatter, by='student') 
        q5_stats = data.get('q5', pd.DataFrame())

        
        if not q5_scatter.empty:
            score_col = 'avg_score' if 'avg_score' in q5_scatter.columns else 'score_mean'
            
            fig = px.scatter(
                q5_scatter,
                x='total_events', y=score_col,
                trendline='ols',
                title="Total Engagement Events vs Average Grade",
                labels={'total_events': 'Total Events', score_col: 'Average Score'},
                opacity=0.6
            )
            fig.update_layout(margin=dict(l=50, r=40, t=55, b=45))
            st.plotly_chart(_theme(fig, height=480), width='stretch')
            # Display metrics if available
        if not q5_stats.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            # Extract from long-format CSV
            try:
                corr = float(q5_stats[q5_stats['metric'] == 'correlation']['value'].values[0])
                col1.metric("Correlation", f"{corr:.4f}")
            except:
                col1.metric("Correlation", "N/A")
            
            try:
                r2 = float(q5_stats[q5_stats['metric'] == 'r_squared']['value'].values[0])
                col2.metric("R²", f"{r2:.4f}")
            except:
                col2.metric("R²", "N/A")
            
            try:
                p_val = float(q5_stats[q5_stats['metric'] == 'p_value']['value'].values[0])
                col3.metric("P-value", f"{p_val:.2e}")
            except:
                col3.metric("P-value", "N/A")
            
            try:
                samples = int(q5_stats[q5_stats['metric'] == 'samples']['value'].values[0])
                col4.metric("Samples", f"{samples:,}")
            except:
                col4.metric("Samples", "N/A")
            
            _insight(
                "Engagement events show <b>positive correlation</b> with academic performance. "
                "Students who engage more tend to perform better."
            )
        elif not q5_scatter.empty:
             _insight("Scatter plot shows relationship between engagement and grades.")
        else:
            st.warning("No data available for selected filters")

    # ────────────────────────────────────────────────────────────────────────
    # Q6: CONCEPT FAILURES
    # ────────────────────────────────────────────────────────────────────────
    with tabs[5]:
        _qbadge("Q6 · Concept Failure Rates")
        _section("Which Concepts Have the Highest Failure Rates?")
        
        q6_data = data.get('q6', pd.DataFrame())
        q6_data = filter_by_sidebar(q6_data, by='student') 
        
        if not q6_data.empty:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                fig = px.bar(
                    q6_data.head(10).sort_values('failure_rate', ascending=True),
                    x='failure_rate', y='concept_name',
                    orientation='h',
                    title="Top 10 Concepts by Failure Rate",
                    text='failure_rate',
                    color='failure_rate',
                    color_continuous_scale='Reds',
                )
                fig.update_traces(
                    texttemplate="%{x:.1f}%",
                    textposition="outside",
                    marker_line=dict(width=0),
                )
                fig.update_layout(
                    xaxis_title="Failure Rate (%)",
                    yaxis_title="",
                    showlegend=False,
                    margin=dict(l=150, r=60, t=55, b=45),
                    xaxis=dict(range=[0, q6_data['failure_rate'].max() + 10]),
                )
                st.plotly_chart(_theme(fig, height=420), width='stretch')
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                weakest = q6_data.iloc[0]
                st.markdown(
                    f"<div class='risk-card'>"
                    f"<b>🚨 Weakest Concept:</b><br>"
                    f"{weakest['concept_name']}<br><br>"
                    f"<b>Failure Rate:</b> {weakest['failure_rate']:.1f}%<br>"
                    f"<b>Failed:</b> {int(weakest['failed'])} / {int(weakest['total'])}"
                    f"</div>",
                    unsafe_allow_html=True)
                
                _cta(
                    f"Focus curriculum improvement on <b>{weakest['concept_name']}</b>. "
                    f"This is the biggest weak spot in the curriculum."
                )
        else:
            st.warning("Q6 data not available")

    # ────────────────────────────────────────────────────────────────────────
    # Q7: CONCEPT TRENDS
    # ────────────────────────────────────────────────────────────────────────
    with tabs[6]:
        _qbadge("Q7 · Weakest Concept Mastery Trend")
        _section("How Does Mastery Change Over Time for the Weakest Concept?")
        
        q7_data = data.get('q7', pd.DataFrame())
        q7_data = filter_by_sidebar(q7_data, by='student') 
        
        if not q7_data.empty:
            fig = px.line(
                q7_data,
                x='period', y='score_pct_mean',
                title="Mastery Trend for Weakest Concept Over Time",
                markers=True,
                labels={'period': 'Time Period', 'score_pct_mean': 'Average Mastery %'}
            )
            fig.update_traces(line_color=KB, marker_color=KB, marker_size=8)
            fig.update_layout(margin=dict(l=50, r=40, t=55, b=45))
            st.plotly_chart(_theme(fig, height=450), width='stretch')

            if not q7_data.empty:
                first_val = q7_data['score_pct_mean'].iloc[0]
                last_val = q7_data['score_pct_mean'].iloc[-1]
                trend = "improving" if last_val > first_val else "declining" if last_val < first_val else "flat"
            _insight(
            f"Mastery trend is <b>{trend}</b> from <b>{first_val:.1f}%</b> to <b>{last_val:.1f}%</b>. "
            f"This shows how students' understanding of the weakest concept is evolving."
        )
        else:
            st.warning("No data available for selected filters")

    # ────────────────────────────────────────────────────────────────────────
    # Q8: LATE SUBMISSIONS
    # ────────────────────────────────────────────────────────────────────────
    with tabs[7]:
        _qbadge("Q8 · Late Submission Impact")
        _section("Do Late Submitters Score Lower?")
        
        q8_data = data.get('q8', pd.DataFrame())
        q8_data = filter_by_sidebar(q8_data, by='student')  # ✅ FILTER
        
        if not q8_data.empty:
            fig = px.bar(
                q8_data,
                x='is_late', y='avg_score',
                error_y='std_dev',
                title="Average Score: On-Time vs Late Submissions",
                text='avg_score',
                color='is_late',
                color_discrete_map={True: RED, False: GREEN},
            )
            fig.update_traces(
                texttemplate="%{y:.1f}",
                textposition="outside",
                marker_line=dict(width=0),
            )
            fig.update_layout(
                xaxis_title="Submitted Late?",
                yaxis_title="Average Score",
                showlegend=False,
                margin=dict(l=50, r=40, t=55, b=45),
            )
            st.plotly_chart(_theme(fig, height=450), width='stretch')
            on_time = q8_data[q8_data['is_late'] == False]
            late = q8_data[q8_data['is_late'] == True]
            
            if not on_time.empty and not late.empty:
                on_time_score = on_time['avg_score'].values[0]
                late_score = late['avg_score'].values[0]
                gap = on_time_score - late_score
                
                _insight(
                    f"On-time submitters score <b>{on_time_score:.1f}</b> vs "
                    f"<b>{late_score:.1f}</b> for late submitters — "
                    f"a <b>{gap:.1f} point gap</b>. Procrastination clearly impacts grades."
                )
        else:
            st.warning("No data available for selected filters")

    # ────────────────────────────────────────────────────────────────────────
    # Q9: COHORT TRENDS
    # ────────────────────────────────────────────────────────────────────────
    with tabs[8]:
        _qbadge("Q9 · Cohort Trends Over 6 Months")
        _section("Attendance & Engagement Over the Term")
        
        q9_data = data.get('q9', pd.DataFrame())
        q9_data = filter_by_sidebar(q9_data, by='group') 
        
        if not q9_data.empty:
            fig = px.line(
                q9_data,
                x='month', y='attendance_rate',
                title="Cohort Attendance Rate Over 6 Months",
                markers=True,
                labels={'month': 'Month', 'attendance_rate': 'Attendance Rate (%)'}
            )
            fig.update_traces(line_color=KB, marker_color=KB, marker_size=8)
            fig.update_layout(margin=dict(l=50, r=40, t=55, b=45))
            st.plotly_chart(_theme(fig, height=450), width='stretch')
                # Find dips
            min_att = q9_data['attendance_rate'].min()
            min_month = q9_data[q9_data['attendance_rate'] == min_att]['month'].values[0]
            
            _insight(
                f"Attendance dips to <b>{min_att:.1f}%</b> in <b>{min_month}</b>. "
                f"Look for external events (exams, holidays, projects) that may explain the drop."
            )
        else:
            st.warning("No data available for selected filters")

    # ────────────────────────────────────────────────────────────────────────
    # Q10: AGE ANALYSIS
    # ────────────────────────────────────────────────────────────────────────
    with tabs[9]:
        _qbadge("Q10 · Age-Based Performance")
        _section("Does Age Relate to Outcomes?")
        
        q10_data = data.get('q10', pd.DataFrame())
        q10_data = filter_by_sidebar(q10_data, by='student')  # ✅ FILTER
        
        if not q10_data.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                score_col = [c for c in q10_data.columns if 'score_mean_mean' in c or 'avg_score_mean' in c]
                if score_col:
                    fig = px.bar(
                        q10_data,
                        x='age_band', y=score_col[0],
                        title="Average Grade by Age Band",
                        color=score_col[0],
                        color_continuous_scale='Viridis',
                    )
                    fig.update_layout(
                        showlegend=False,
                        margin=dict(l=50, r=40, t=55, b=45),
                    )
                    st.plotly_chart(_theme(fig, height=400), width="stretch")
            
            with col2:
                att_col = 'attendance_rate_mean' if 'attendance_rate_mean' in q10_data.columns else None
                if att_col:
                    fig = px.line(
                        q10_data,
                        x='age_band', y=att_col,
                        title="Average Attendance by Age Band",
                        markers=True,
                    )
                    fig.update_traces(line_color=KB, marker_color=KB)
                    fig.update_layout(
                        margin=dict(l=50, r=40, t=55, b=45),
                    )
                    st.plotly_chart(_theme(fig, height=400), width="stretch")
            
            with col3:
                eng_col = [c for c in q10_data.columns if 'total_events_mean' in c]
                if eng_col:
                    fig = px.bar(
                        q10_data,
                        x='age_band', y=eng_col[0],
                        title="Engagement by Age Band",
                        color=eng_col[0],
                        color_continuous_scale='Blues',
                    )
                    fig.update_layout(
                        showlegend=False,
                        margin=dict(l=50, r=40, t=55, b=45),
                    )
                    st.plotly_chart(_theme(fig, height=400), width="stretch")
            
            st.write(q10_data)
        else:
            st.warning("Q10 data not available")

    # ────────────────────────────────────────────────────────────────────────
    # Q11: STUDENT SEGMENTS
    # ────────────────────────────────────────────────────────────────────────
    with tabs[10]:
        _qbadge("Q11 · Student Segmentation")
        _section("How Do We Cluster Students by Performance?")
        
        q11_summary = data.get('q11', pd.DataFrame())
        
        if not q11_summary.empty:
            st.write("**Segment Profiles:**")
            st.dataframe(q11_summary, width='stretch', hide_index=True)
            _insight(
        "Students are grouped into 4 distinct segments based on "
        "attendance, engagement, and grades. Each segment has unique needs and risks.")
        else:
            st.warning("No data available")

    # ────────────────────────────────────────────────────────────────────────
    # Q12: GROUP SIZE COMPARISON
    # ────────────────────────────────────────────────────────────────────────
    with tabs[11]:
        _qbadge("Q12 · Group Size Discrepancies")
        _section("Do Actual Sizes Match Self-Reported?")
        
        q12_data = data.get('q12', pd.DataFrame())
        q12_data = filter_by_sidebar(q12_data, by='group')  
        
        if not q12_data.empty:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=q12_data['group_id'],
                    y=q12_data['true_count'],
                    name='Actual',
                    marker_color=KB,
                ))
                fig.add_trace(go.Bar(
                    x=q12_data['group_id'],
                    y=q12_data['stated_num_students'],
                    name='Reported',
                    marker_color=KB_LIGHT,
                ))
                fig.update_layout(
                    title="Actual vs Reported Group Sizes",
                    xaxis_title="Group",
                    yaxis_title="Number of Students",
                    barmode='group',
                    margin=dict(l=50, r=40, t=55, b=45),
                )
                st.plotly_chart(_theme(fig, height=450), width="stretch")
            
            with col1:
                problem = q12_data[q12_data['is_problem'] == True] if 'is_problem' in q12_data.columns else q12_data[abs(q12_data['discrepancy']) > 2]
                if not problem.empty:
                    st.markdown("**Problem Groups:**")
                    st.dataframe(problem, width="stretch", hide_index=True)
                    _risk(f"<b>{len(problem)}</b> groups have significant discrepancies between reported and actual sizes.")
                else:
                    st.success("✅ All group sizes match accurately!")
        else:
            st.warning("Q12 data not available")

    # ────────────────────────────────────────────────────────────────────────
    # Q13: GROUP VIABILITY
    # ────────────────────────────────────────────────────────────────────────
    with tabs[12]:
        _qbadge("Q13 · Group Viability Analysis")
        _section("Which Groups Are Too Small to be Viable?")
        
        q13_metrics = data.get('q13_group_metrics', pd.DataFrame())
        q13_metrics = filter_by_sidebar(q13_metrics, by='group')  # ✅ FILTER
        q13_rec = data.get('q13', pd.DataFrame())

        
        if not q13_metrics.empty:
            fig = px.bar(
                q13_metrics.sort_values('num_students'),
                x='num_students', y='group_id',
                orientation='h',
                title="Group Sizes",
                text='num_students',
                color='num_students',
                color_continuous_scale='RdYlGn',
            )
            fig.update_traces(
                texttemplate="%{x}",
                textposition="outside",
                marker_line=dict(width=0),
            )
            fig.update_layout(
                xaxis_title="Number of Students",
                yaxis_title="",
                showlegend=False,
                margin=dict(l=80, r=60, t=55, b=45),
            )
            st.plotly_chart(_theme(fig, height=450), width="stretch")
            
            st.markdown("**Group Metrics:**")
            st.dataframe(q13_metrics, width="stretch", hide_index=True)

        if not q13_rec.empty:
            st.markdown("**Viability Recommendations:**")
            st.dataframe(q13_rec, width="stretch", hide_index=True)

        if q13_metrics.empty and q13_rec.empty:
            st.warning("❌ Q13 data not found. Ensure q13_group_metrics.csv and q13_group_viability.csv exist in ./cleaned_data/")

    # ────────────────────────────────────────────────────────────────────────
    # Q14: AT-RISK STUDENTS
    # ────────────────────────────────────────────────────────────────────────
    with tabs[13]:
        _qbadge("Q14 · At-Risk Student Ranking")
        _section("Top 10 Students Needing Immediate Support")

        q14_data = data.get('q14', pd.DataFrame())
        if not q14_data.empty and len(q14_data) > 0:
            top10 = q14_data.head(10)
            
            st.markdown("**Top 10 At-Risk Students:**")
            st.dataframe(top10, width="stretch", hide_index=True)
            
            highest_risk = top10.iloc[0]

        else:
            st.warning("Q14 data not available")
    # ────────────────────────────────────────────────────────────────────────
    # Q15: GROUP TRENDS
    # ────────────────────────────────────────────────────────────────────────
    with tabs[14]:
        _qbadge("Q15 · Group Performance Trends")
        _section("Which Groups Are Trending Up or Down?")
        
        q15_data = data.get('q15', pd.DataFrame())
        q15_data = filter_by_sidebar(q15_data, by='group')  
        
        if not q15_data.empty:
            # Pivot for visualization
            pivot = q15_data.pivot(
                index='group_id',
                columns='month',
                values='avg_grade'
            )
            
            fig = px.line(
                q15_data,
                x='month', y='avg_grade',
                color='group_id',
                title="Group Average Grade Trajectory Over Term",
                markers=True,
                labels={'month': 'Month', 'avg_grade': 'Average Grade'}
            )
            fig.update_layout(
                margin=dict(l=50, r=40, t=55, b=45),
                legend=dict(title="Group")
            )
            st.plotly_chart(_theme(fig, height=480), width="stretch")
            
            # Summary
            st.markdown("**Monthly Averages:**")
            st.dataframe(pivot, width="stretch")
        else:
            st.warning("Q15 data not available")
# ═════════════════════════════════════════════════════════════════════════════
# NAVIGATION  —  st.navigation / st.Page
# ═════════════════════════════════════════════════════════════════════════════
pg = st.navigation({
    "📚 Dashboard": [
        st.Page(page_overview, title="Student Analytics", icon="📊", default=True),
    ],
})
pg.run()