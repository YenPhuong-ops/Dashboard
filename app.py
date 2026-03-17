import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="COOLMATE DASHBOARD PHÂN TÍCH KHÁCH HÀNG",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
  .stApp { background-color: #0D1B2A; color: #E2E8F0; }
  [data-testid="stSidebar"] { background-color: #0A1520; }
  [data-testid="metric-container"] {
    background: linear-gradient(135deg, #1B2A3B 0%, #162232 100%);
    border: 1px solid #1B998B44;
    border-radius: 12px;
    padding: 16px 20px;
  }
  [data-testid="metric-container"] label { color: #94A3B8 !important; font-size: 13px !important; }
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #1B998B !important; font-size: 28px !important; font-weight: 700 !important;
  }
  [data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 12px !important; }
  h1 { color: #1B998B !important; font-size: 28px !important; }
  h2 { color: #E2E8F0 !important; font-size: 20px !important; }
  h3 { color: #94A3B8 !important; font-size: 16px !important; }
  .section-header {
    background: linear-gradient(90deg, #1B998B22, transparent);
    border-left: 4px solid #1B998B;
    padding: 8px 16px; border-radius: 0 8px 8px 0;
    margin: 24px 0 16px 0;
    color: #1B998B; font-weight: 700; font-size: 16px;
  }
  .insight-box {
    background: #1B2A3B; border: 1px solid #1B998B44;
    border-radius: 10px; padding: 14px 18px; margin: 8px 0;
    font-size: 14px; color: #CBD5E1; line-height: 1.7;
  }
  .insight-box b { color: #1B998B; }
  .warn-box {
    background: #2A1B0D; border: 1px solid #FF6B3544;
    border-radius: 10px; padding: 14px 18px; margin: 8px 0;
    font-size: 14px; color: #CBD5E1;
  }
  .warn-box b { color: #FF6B35; }
  .dataframe { background: #1B2A3B !important; color: #E2E8F0 !important; }
  thead tr th { background: #0D1B2A !important; color: #1B998B !important; }
  .sidebar-title {
    color: #1B998B; font-weight: 700; font-size: 15px;
    border-bottom: 1px solid #1B998B33; padding-bottom: 8px; margin-bottom: 12px;
  }
  .js-plotly-plot { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Color palette ──────────────────────────────────────────────────────
COLORS = {
    "teal":    "#1B998B", "orange":  "#FF6B35", "blue":    "#3B82F6",
    "purple":  "#8B5CF6", "green":   "#10B981", "amber":   "#F59E0B",
    "red":     "#EF4444", "gray":    "#64748B",
}
SEG_COLORS = {
    "Office-Gym Power User": "#1B998B", "Gym Enthusiast":        "#10B981",
    "Office Professional":   "#F59E0B", "General Consumer":      "#64748B",
}
LC_COLORS = {
    "Subscriber": "#3B82F6", "Lead":       "#F59E0B",
    "MQL":        "#10B981", "SQL":        "#8B5CF6", "Customer":   "#1B998B",
}
SRC_COLORS = {
    "Facebook Ads":    "#1877F2", "TikTok Ads":      "#9B59B6",
    "Google Search":   "#EA4335", "Organic Search":  "#10B981",
    "Email Marketing": "#FF6B35", "Zalo OA":         "#0068FF",
}

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#111E2D",
    font=dict(color="#CBD5E1", family="Arial"),
    margin=dict(t=40, b=40, l=40, r=20),
    hoverlabel=dict(bgcolor="#1B2A3B", font_color="#E2E8F0", bordercolor="#1B998B"),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(27, 153, 139, 0.2)"),
    xaxis=dict(gridcolor="#1B2A3B", linecolor="#334155", tickcolor="#334155"),
    yaxis=dict(gridcolor="#1B2A3B", linecolor="#334155", tickcolor="#334155"),
)

# ── Load & process data ────────────────────────────────────────────────
@st.cache_data
def load_data():
    file_names = [
        "coolmate_contacts_T0_before (Autosaved).xlsx - coolmate_contacts_T0_before.csv",
        "coolmate_contacts_T0_before.csv",
        "coolmate_contacts_T0_before.xlsx"
    ]
    df = None
    for fn in file_names:
        try:
            if fn.endswith('.csv'):
                df = pd.read_csv(fn, encoding="utf-8-sig")
            else:
                df = pd.read_excel(fn)
            break
        except:
            continue

    if df is None:
        st.error("❌ Không tìm thấy file dữ liệu! Vui lòng tải lại file dữ liệu vào Colab.")
        st.stop()

    # Ép kiểu dữ liệu an toàn để tránh thông số bị lỗi
    df["lead_score_t0"] = pd.to_numeric(df["lead_score_t0"], errors="coerce").fillna(0)
    df["email_ctr_30d_t0"] = pd.to_numeric(df["email_ctr_30d_t0"], errors="coerce").fillna(0)
    df["page_views_30d_t0"] = pd.to_numeric(df["page_views_30d_t0"], errors="coerce").fillna(0)

    def seg(row):
        gym_hi = str(row.get("gym_frequency", "")) in ["3-4 lần/tuần","5+ lần/tuần"]
        office = str(row.get("office_worker_type", "")) == "Văn phòng toàn thời gian"
        if gym_hi and office:  return "Office-Gym Power User"
        elif gym_hi:           return "Gym Enthusiast"
        elif office:           return "Office Professional"
        else:                  return "General Consumer"
    df["segment"] = df.apply(seg, axis=1)

    def band(s):
        if s >= 40: return "MQL (≥40)"
        if s >= 20: return "Warm (20–39)"
        return "Cold (0–19)"
    df["score_band"] = df["lead_score_t0"].apply(band)

    def age_g(a):
        try:
            a = float(a)
            if pd.isna(a): return "Khác"
            if a < 25:  return "22–24"
            if a < 28:  return "25–27"
            if a < 31:  return "28–30"
            if a < 35:  return "31–34"
            return "35–38"
        except:
            return "Khác"
    df["age_group"] = df["age"].apply(age_g)
    df["create_date"] = pd.to_datetime(df["create_date"], errors="coerce")
    return df

df = load_data()

# ── SIDEBAR ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">🎛️ BỘ LỌC DỮ LIỆU</div>', unsafe_allow_html=True)
    cities_all = sorted([str(c) for c in df["city"].unique() if pd.notna(c)])
    sel_cities = st.multiselect("🏙️ Thành phố", cities_all, default=cities_all, key="city_filter")
    segs_all = list(SEG_COLORS.keys())
    sel_segs = st.multiselect("👥 Phân khúc", segs_all, default=segs_all, key="seg_filter")
    srcs_all = sorted([str(s) for s in df["source"].unique() if pd.notna(s)])
    sel_srcs = st.multiselect("📡 Nguồn traffic", srcs_all, default=srcs_all, key="src_filter")
    score_range = st.slider("⭐ Lead Score", 0, 35, (0, int(df["lead_score_t0"].max()) if not df.empty else 35), key="score_filter")
    st.markdown("---")
    st.markdown('<div class="sidebar-title">ℹ️ THÔNG TIN</div>', unsafe_allow_html=True)
    st.caption("Dataset: T0 — Tháng 1/2025")
    st.caption("Trước khi triển khai chiến dịch HubSpot")
    st.caption(f"Tổng raw: {len(df)} contacts")

dff = df[
    df["city"].astype(str).isin(sel_cities) &
    df["segment"].astype(str).isin(sel_segs) &
    df["source"].astype(str).isin(sel_srcs) &
    df["lead_score_t0"].between(score_range[0], score_range[1])
]

# ── HEADER ─────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.markdown("## 👔", unsafe_allow_html=True)
with col_title:
    st.markdown("# COOLMATE DASHBOARD PHÂN TÍCH KHÁCH HÀNG")
    st.markdown(
        f"<span style='color:#64748B;font-size:13px'>Trạng thái trước chiến dịch Tech-Wear "
        f"| Đang hiển thị <b style='color:#1B998B'>{len(dff)}</b> / {len(df)} contacts</span>",
        unsafe_allow_html=True
    )
st.markdown("---")

# ═══════════════════════════════════════════════════════
# SECTION 1 — KPI CARDS
# ═══════════════════════════════════════════════════════
st.markdown('<div class="section-header">📊 KPI TỔNG QUAN T0</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5, k6 = st.columns(6)
avg_score = dff["lead_score_t0"].mean() if not dff.empty else 0
mql_count = (dff["lead_score_t0"] >= 40).sum()
ctr_avg   = dff["email_ctr_30d_t0"].mean() * 100 if not dff.empty else 0
zalo_pct  = (dff["zalo_subscribed_t0"] == "Yes").mean() * 100 if not dff.empty else 0
paid_pct  = dff["source"].isin(["Facebook Ads","TikTok Ads"]).mean() * 100 if not dff.empty else 0

k1.metric("👥 Contacts",          f"{len(dff):,}",       f"Filtered: {len(dff)}/{len(df)}")
k2.metric("⭐ Avg Lead Score",     f"{avg_score:.1f}",    "Max: 31 | Target T6: 48")
k3.metric("🎯 MQL Ready (≥40)",    f"{mql_count}",        "0% MQL rate — cần nurture")
k4.metric("📧 Email CTR avg",      f"{ctr_avg:.2f}%",     "Benchmark ngành: 4.5%")
k5.metric("💬 Zalo Subscribed",    f"{zalo_pct:.0f}%",    "Owned channel tiềm năng")
k6.metric("📢 Paid Ads %",         f"{paid_pct:.0f}%",    "Phụ thuộc cao vào paid")

st.markdown('<div class="insight-box">💡 <b>Nhận định T0:</b> Phần lớn contacts ở nhóm Cold. '
            '0 contacts đạt MQL (≥40). Email CTR thấp hơn benchmark ngành 2x. '
            'Đây là baseline để so sánh sau khi triển khai chiến dịch HubSpot T1–T6.</div>',
            unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# SECTION 2 — PHÂN KHÚC
# ═══════════════════════════════════════════════════════
st.markdown('<div class="section-header">👥 PHÂN TÍCH PHÂN KHÚC KHÁCH HÀNG</div>', unsafe_allow_html=True)
col_a, col_b = st.columns([1, 1])
with col_a:
    seg_data = dff["segment"].value_counts().reset_index()
    seg_data.columns = ["Phân khúc", "Số contacts"]
    seg_data["Màu"] = seg_data["Phân khúc"].map(SEG_COLORS)

    fig_seg = go.Figure(go.Pie(
        labels=seg_data["Phân khúc"], values=seg_data["Số contacts"], hole=0.55,
        marker=dict(colors=seg_data["Màu"].tolist(), line=dict(color="#0D1B2A", width=3)),
        textinfo="label+percent", textfont=dict(size=12, color="#E2E8F0"),
    ))
    fig_seg.update_layout(**CHART_LAYOUT)
    fig_seg.update_layout(title="Phân Phối Phân Khúc", showlegend=True,
                          legend=dict(orientation="v", x=1.02, y=0.5, bgcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig_seg, use_container_width=True)

with col_b:
    seg_stats = dff.groupby("segment").agg(
        Contacts=("contact_id","count"), Avg_Score=("lead_score_t0","mean"),
        Avg_CTR=("email_ctr_30d_t0","mean"), Zalo_Yes=("zalo_subscribed_t0", lambda x: (x=="Yes").sum()),
    ).reset_index()
    seg_stats["Avg_CTR"] = (seg_stats["Avg_CTR"] * 100).round(2)
    seg_stats["Avg_Score"] = seg_stats["Avg_Score"].round(1)
    seg_stats["Zalo_%"] = (seg_stats["Zalo_Yes"] / seg_stats["Contacts"] * 100).fillna(0).round(0).astype(int)
    seg_stats = seg_stats.sort_values("Avg_Score", ascending=False)

    fig_seg_bar = go.Figure()
    for _, row in seg_stats.iterrows():
        color = SEG_COLORS.get(row["segment"], "#64748B")
        fig_seg_bar.add_trace(go.Bar(
            name=row["segment"], x=[row["segment"]], y=[row["Contacts"]],
            text=[f"{row['Contacts']}<br>Score: {row['Avg_Score']}"],
            textposition="outside", textfont=dict(size=11, color="#E2E8F0"),
            marker=dict(color=color, line=dict(color="#0D1B2A", width=1.5)), width=0.55,
        ))

    fig_seg_bar.update_layout(**CHART_LAYOUT)
    fig_seg_bar.update_layout(title="Số Contacts Theo Phân Khúc", barmode="group", showlegend=False)
    fig_seg_bar.update_yaxes(gridcolor="#1B2A3B", title="Số contacts")
    fig_seg_bar.update_xaxes(tickangle=-10)
    st.plotly_chart(fig_seg_bar, use_container_width=True)

# ═══════════════════════════════════════════════════════
# SECTION 3 — LEAD SCORE
# ═══════════════════════════════════════════════════════
st.markdown('<div class="section-header">⭐ PHÂN TÍCH LEAD SCORE</div>', unsafe_allow_html=True)
col_c, col_d = st.columns([3, 2])
with col_c:
    fig_hist = go.Figure(go.Histogram(
        x=dff["lead_score_t0"], xbins=dict(start=0, end=35, size=2),
        marker=dict(color=COLORS["teal"], opacity=0.85, line=dict(color="#0D1B2A", width=1.5)), name="Lead Score"
    ))
    for val, label, color in [(20,"Warm threshold","#F59E0B"),(40,"MQL threshold","#1B998B")]:
        fig_hist.add_vline(x=val, line_width=2, line_dash="dash", line_color=color, annotation_text=label, annotation_position="top right", annotation_font=dict(size=11, color=color))

    fig_hist.update_layout(title="Phân Phối Lead Score T0", **{k:v for k,v in CHART_LAYOUT.items() if k not in ['xaxis','yaxis']})
    fig_hist.update_xaxes(title="Lead Score", gridcolor="#1B2A3B")
    fig_hist.update_yaxes(title="Số contacts", gridcolor="#1B2A3B")
    st.plotly_chart(fig_hist, use_container_width=True)

with col_d:
    band_data = dff["score_band"].value_counts().reset_index()
    band_data.columns = ["Band","Count"]
    band_order = ["Cold (0–19)","Warm (20–39)","MQL (≥40)"]
    band_colors_map = {"Cold (0–19)":"#EF4444","Warm (20–39)":"#F59E0B","MQL (≥40)":"#1B998B"}
    band_data["order"] = band_data["Band"].map({b:i for i,b in enumerate(band_order)})
    band_data = band_data.sort_values("order")

    fig_band = go.Figure(go.Funnel(
        y=band_data["Band"], x=band_data["Count"], textinfo="value+percent initial",
        textfont=dict(size=13, color="#E2E8F0"),
        marker=dict(color=[band_colors_map.get(b,"#64748B") for b in band_data["Band"]], line=dict(color="#0D1B2A", width=2))
    ))
    fig_band.update_layout(**CHART_LAYOUT)
    fig_band.update_layout(title="Phễu Lead Score Bands")
    fig_band.update_yaxes(gridcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_band, use_container_width=True)

# ═══════════════════════════════════════════════════════
# DATA TABLE
# ═══════════════════════════════════════════════════════
st.markdown('<div class="section-header">📋 DỮ LIỆU GỐC</div>', unsafe_allow_html=True)
show_cols = ["contact_id","full_name","city","segment","lead_score_t0",
             "lifecycle_stage_t0","source","gym_frequency","email_ctr_30d_t0"]
display_df = dff[show_cols].copy()
display_df["email_ctr_30d_t0"] = (display_df["email_ctr_30d_t0"]*100).round(2).astype(str) + "%"
display_df.columns = ["ID","Tên","Thành phố","Phân khúc","Lead Score",
                       "Lifecycle","Nguồn","Gym","Email CTR"]

st.dataframe(display_df.head(50), use_container_width=True, height=380)
