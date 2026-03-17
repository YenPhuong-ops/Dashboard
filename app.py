import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Coolmate Pre-Campaign Analytics",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS (Nền Hồng/Tím Pastel, Chữ Xanh Navy + Hover Effect CỰC MẠNH) ────────
st.markdown("""
<style>
  /* Nền tổng thể: Tím/Hồng pastel rất nhạt */
  .stApp { background-color: #FDF8FF; color: #1A237E; }
  
  /* Sidebar: Hồng phấn */
  [data-testid="stSidebar"] { background-color: #FFF0F5; border-right: 1px solid #FCE4EC; }
  
  /* 🌟 CÁC Ô SỐ LIỆU (METRIC CARDS) 🌟 */
  [data-testid="metric-container"] {
    background-color: #FFFFFF !important;
    border: 1px solid #F3E5F5 !important;
    border-radius: 12px !important;
    padding: 16px 15px !important; 
    box-shadow: 0 4px 10px rgba(156, 39, 176, 0.05) !important;
    /* Hiệu ứng chuyển động mượt */
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease !important; 
    cursor: pointer !important;
  }
  
  /* 🌟 HIỆU ỨNG KHI ĐƯA CHUỘT VÀO (HOVER) LIỀU CAO 🌟 */
  [data-testid="metric-container"]:hover {
    transform: translateY(-10px) scale(1.03) !important; /* Nảy lên cao hơn và hơi phóng to */
    box-shadow: 0 15px 25px rgba(216, 27, 96, 0.3) !important; /* Bóng đậm và rộng hơn */
    border-color: #D81B60 !important; /* Đổi màu viền */
  }

  [data-testid="metric-container"] label { color: #3949AB !important; font-size: 14px !important; font-weight: 700 !important; }
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #D81B60 !important; font-size: 26px !important; font-weight: 800 !important;
  }
  
  /* 🌟 FIX LỖI CHỮ BỊ CẮT THÀNH DẤU ... 🌟 */
  [data-testid="stMetricDelta"] > div {
    white-space: normal !important; 
    overflow: visible !important;
    text-overflow: clip !important;
    font-size: 12px !important;
    color: #5C6BC0 !important; 
    font-weight: 500 !important;
    line-height: 1.4 !important;
    margin-top: 5px !important;
  }
  
  /* Ẩn mũi tên mặc định của Streamlit ở phần ghi chú */
  [data-testid="stMetricDelta"] svg {
    display: none !important;
  }
  
  /* Tiêu đề */
  h1 { color: #880E4F !important; font-size: 28px !important; font-weight: 800 !important; text-transform: uppercase; }
  h2, h3 { color: #1A237E !important; font-weight: 700 !important; }
  
  /* Header của từng phần */
  .section-header {
    background: linear-gradient(90deg, #FCE4EC, transparent);
    border-left: 6px solid #D81B60;
    padding: 10px 16px; border-radius: 0 8px 8px 0;
    margin: 30px 0 16px 0;
    color: #AD1457; font-weight: 800; font-size: 18px;
    text-transform: uppercase; letter-spacing: 0.5px;
  }
  
  /* Hộp Insight */
  .insight-box {
    background: #E8EAF6; border: 1px solid #C5CAE9;
    border-radius: 10px; padding: 16px 20px; margin: 8px 0;
    font-size: 15px; color: #1A237E; line-height: 1.6;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
  }
  .insight-box b { color: #303F9F; font-size: 16px; }
  
  /* Bảng dữ liệu */
  .dataframe { background: #FFFFFF !important; color: #1A237E !important; border: 1px solid #F3E5F5 !important; }
  thead tr th { background: #FCE4EC !important; color: #880E4F !important; font-weight: 700 !important; }
  
  /* Thanh Sidebar */
  .sidebar-title {
    color: #D81B60; font-weight: 800; font-size: 16px;
    border-bottom: 2px solid #F8BBD0; padding-bottom: 8px; margin-bottom: 12px;
  }
  
  p, div, span, label { color: #1A237E; }
</style>
""", unsafe_allow_html=True)

# ── Color palette ───────────────────────────
COLORS = {
    "pink":    "#F48FB1", "purple":  "#CE93D8", "blue":    "#90CAF9",
    "indigo":  "#9FA8DA", "rose":    "#FFAB91", "deep_pink": "#D81B60",
    "navy":    "#1A237E"
}
SEG_COLORS = {
    "Office-Gym Power User": "#F48FB1", 
    "Gym Enthusiast":        "#CE93D8", 
    "Office Professional":   "#90CAF9", 
    "General Consumer":      "#BCAAA4", 
}

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#1A237E", family="Arial", size=13),
    margin=dict(t=50, b=40, l=40, r=20),
    hoverlabel=dict(bgcolor="#FFFFFF", font_color="#1A237E", bordercolor="#CE93D8"),
    legend=dict(bgcolor="rgba(255,255,255,0.7)", bordercolor="#F3E5F5", borderwidth=1), 
    xaxis=dict(gridcolor="#F3E5F5", linecolor="#CE93D8", tickcolor="#CE93D8", title_font=dict(color="#3949AB")),
    yaxis=dict(gridcolor="#F3E5F5", linecolor="#CE93D8", tickcolor="#CE93D8", title_font=dict(color="#3949AB")),
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
        st.error("❌ Không tìm thấy file dữ liệu! Vui lòng kiểm tra lại GitHub.")
        st.stop()
        
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
    return df

df = load_data()

# ── SIDEBAR ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">🎛️ DATA FILTERS</div>', unsafe_allow_html=True)
    cities_all = sorted([str(c) for c in df["city"].unique() if pd.notna(c)])
    sel_cities = st.multiselect("🏙️ Location (City)", cities_all, default=cities_all)
    segs_all = list(SEG_COLORS.keys())
    sel_segs = st.multiselect("👥 Customer Segment", segs_all, default=segs_all)
    srcs_all = sorted([str(s) for s in df["source"].unique() if pd.notna(s)])
    sel_srcs = st.multiselect("📡 Traffic Source", srcs_all, default=srcs_all)
    score_range = st.slider("⭐ Lead Score Range", 0, 35, (0, int(df["lead_score_t0"].max()) if not df.empty else 35))
    
    st.markdown("---")
    st.markdown('<div class="sidebar-title">ℹ️ INFO</div>', unsafe_allow_html=True)
    st.caption("📍 **Dataset:** T0 — January 2025")
    st.caption("📍 **Status:** Pre-HubSpot Campaign")
    st.caption(f"📍 **Total Raw:** {len(df)} contacts")

dff = df[
    df["city"].astype(str).isin(sel_cities) &
    df["segment"].astype(str).isin(sel_segs) &
    df["source"].astype(str).isin(sel_srcs) &
    df["lead_score_t0"].between(score_range[0], score_range[1])
]

# ── HEADER ─────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([0.5, 6.5])
with col_logo:
    st.markdown("<h1 style='font-size: 40px; margin-top: 0;'>👔</h1>", unsafe_allow_html=True)
with col_title:
    st.markdown("# COOLMATE: PRE-CAMPAIGN CUSTOMER ANALYTICS")
    st.markdown(
        f"<span style='color:#3949AB;font-size:14px; font-weight: 500;'>Data from T0 (Before Tech-Wear Launch) "
        f"| Showing <b style='color:#D81B60'>{len(dff)}</b> / {len(df)} filtered contacts</span>",
        unsafe_allow_html=True
    )
st.markdown("---")

# ═══════════════════════════════════════════════════════
# SECTION 1 — KPI CARDS
# ═══════════════════════════════════════════════════════
st.markdown('<div class="section-header">📊 TỔNG QUAN HIỆU SUẤT (OVERVIEW KPI)</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5, k6 = st.columns(6)
avg_score = dff["lead_score_t0"].mean() if not dff.empty else 0
mql_count = (dff["lead_score_t0"] >= 40).sum()
ctr_avg   = dff["email_ctr_30d_t0"].mean() * 100 if not dff.empty else 0
zalo_pct  = (dff["zalo_subscribed_t0"] == "Yes").mean() * 100 if not dff.empty else 0
paid_pct  = dff["source"].isin(["Facebook Ads","TikTok Ads"]).mean() * 100 if not dff.empty else 0

k1.metric("👥 Total Contacts",     f"{len(dff):,}",       "Filtered selection")
k2.metric("⭐ Avg Lead Score",     f"{avg_score:.1f}",    "Target for T6: 48")
k3.metric("🎯 MQL Ready (≥40)",    f"{mql_count}",        "Needs nurturing")
k4.metric("📧 Email CTR",          f"{ctr_avg:.2f}%",     "Industry Bench: 4.5%")
k5.metric("💬 Zalo Subs",          f"{zalo_pct:.0f}%",    "Owned Channel")
k6.metric("📢 Paid Ads %",         f"{paid_pct:.0f}%",    "High dependency")

st.markdown('<div class="insight-box">💡 <b>Phân tích (Insight):</b> Hầu hết danh sách khách hàng đang ở trạng thái <b>Cold</b> (Lạnh). '
            'Chưa có khách hàng nào đạt chuẩn MQL (≥40 điểm). Chỉ số Email CTR thấp hơn 2 lần so với trung bình ngành. '
            'Đây là thước đo cơ sở để đánh giá sự tăng trưởng sau khi kích hoạt chiến dịch HubSpot.</div>',
            unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# SECTION 2 — PHÂN KHÚC
# ═══════════════════════════════════════════════════════
st.markdown('<div class="section-header">👥 PHÂN KHÚC KHÁCH HÀNG (CUSTOMER SEGMENTS)</div>', unsafe_allow_html=True)
col_a, col_b = st.columns([1, 1])
with col_a:
    seg_data = dff["segment"].value_counts().reset_index()
    seg_data.columns = ["Phân khúc", "Số contacts"]
    seg_data["Màu"] = seg_data["Phân khúc"].map(SEG_COLORS)
    
    fig_seg = go.Figure(go.Pie(
        labels=seg_data["Phân khúc"], values=seg_data["Số contacts"], hole=0.55,
        marker=dict(colors=seg_data["Màu"].tolist(), line=dict(color="#FFFFFF", width=3)),
        textinfo="label+percent", textfont=dict(size=13, color="#1A237E"),
    ))
    fig_seg.update_layout(**CHART_LAYOUT)
    fig_seg.update_layout(title="Tỷ lệ Phân Khúc", showlegend=True,
                          legend=dict(orientation="v", x=1.02, y=0.5, bgcolor="rgba(255,255,255,0)"))
    st.plotly_chart(fig_seg, use_container_width=True)

with col_b:
    seg_stats = dff.groupby("segment").agg(
        Contacts=("contact_id","count"), Avg_Score=("lead_score_t0","mean")
    ).reset_index().sort_values("Avg_Score", ascending=False)
    seg_stats["Avg_Score"] = seg_stats["Avg_Score"].round(1)
    
    fig_seg_bar = go.Figure()
    for _, row in seg_stats.iterrows():
        color = SEG_COLORS.get(row["segment"], "#CE93D8")
        fig_seg_bar.add_trace(go.Bar(
            name=row["segment"], x=[row["segment"]], y=[row["Contacts"]],
            text=[f"{row['Contacts']} (Score: {row['Avg_Score']})"],
            textposition="outside", textfont=dict(size=12, color="#1A237E"),
            marker=dict(color=color, line=dict(color="#D81B60", width=1.5)), width=0.55,
        ))
    
    fig_seg_bar.update_layout(**CHART_LAYOUT)
    fig_seg_bar.update_layout(title="Số Lượng & Điểm Số Phân Khúc", barmode="group", showlegend=False)
    fig_seg_bar.update_yaxes(title="Số contacts")
    fig_seg_bar.update_xaxes(tickangle=-15)
    st.plotly_chart(fig_seg_bar, use_container_width=True)

# ═══════════════════════════════════════════════════════
# SECTION 3 — LEAD SCORE
# ═══════════════════════════════════════════════════════
st.markdown('<div class="section-header">⭐ CHẤT LƯỢNG TIỀM NĂNG (LEAD SCORING)</div>', unsafe_allow_html=True)
col_c, col_d = st.columns([3, 2])
with col_c:
    fig_hist = go.Figure(go.Histogram(
        x=dff["lead_score_t0"], xbins=dict(start=0, end=35, size=2),
        marker=dict(color=COLORS["purple"], opacity=0.9, line=dict(color="#880E4F", width=1)), name="Lead Score"
    ))
    for val, label, color in [(20,"Warm (20)","#3949AB"),(40,"MQL (40)","#D81B60")]:
        fig_hist.add_vline(x=val, line_width=2, line_dash="dash", line_color=color, annotation_text=label, annotation_font=dict(size=12, color=color))
    
    fig_hist.update_layout(title="Phân Phối Điểm Chất Lượng (Lead Score)", **{k:v for k,v in CHART_LAYOUT.items() if k not in ['xaxis','yaxis']})
    fig_hist.update_xaxes(title="Điểm Lead Score", gridcolor="#F3E5F5", linecolor="#CE93D8")
    fig_hist.update_yaxes(title="Số lượng contacts", gridcolor="#F3E5F5", linecolor="#CE93D8")
    st.plotly_chart(fig_hist, use_container_width=True)

with col_d:
    band_data = dff["score_band"].value_counts().reset_index()
    band_data.columns = ["Band","Count"]
    band_order = ["Cold (0–19)","Warm (20–39)","MQL (≥40)"]
    band_colors_map = {"Cold (0–19)":COLORS["blue"],"Warm (20–39)":COLORS["purple"],"MQL (≥40)":COLORS["pink"]}
    band_data["order"] = band_data["Band"].map({b:i for i,b in enumerate(band_order)})
    band_data = band_data.sort_values("order")
    
    fig_band = go.Figure(go.Funnel(
        y=band_data["Band"], x=band_data["Count"], textinfo="value+percent initial",
        textfont=dict(size=14, color="#1A237E", weight="bold"),
        marker=dict(color=[band_colors_map.get(b,"#CE93D8") for b in band_data["Band"]], line=dict(color="#FFFFFF", width=2))
    ))
    fig_band.update_layout(**CHART_LAYOUT)
    fig_band.update_layout(title="Phễu Chuyển Đổi Lead")
    fig_band.update_yaxes(gridcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_band, use_container_width=True)

# ═══════════════════════════════════════════════════════
# SECTION 4 — NGUỒN TRAFFIC & ĐỊA LÝ
# ═══════════════════════════════════════════════════════
st.markdown('<div class="section-header">📡 NGUỒN KHÁCH & VỊ TRÍ (TRAFFIC & LOCATION)</div>', unsafe_allow_html=True)
col_g, col_h = st.columns(2)
with col_g:
    src_data = dff.groupby("source").agg(Contacts=("contact_id","count")).reset_index().sort_values("Contacts", ascending=True)
    fig_src = go.Figure(go.Bar(
        x=src_data["Contacts"], y=src_data["source"], orientation="h",
        marker=dict(color=COLORS["indigo"], line=dict(color="#3949AB", width=1)),
        text=[f"  {v} contacts" for v in src_data["Contacts"]], textposition="inside", textfont=dict(size=12, color="#1A237E"),
    ))
    fig_src.update_layout(title="Kênh Thu Hút Khách Hàng (Source)", **{k:v for k,v in CHART_LAYOUT.items() if k not in ['xaxis']})
    fig_src.update_xaxes(title="Số contacts", gridcolor="#F3E5F5")
    st.plotly_chart(fig_src, use_container_width=True)

with col_h:
    city_data = dff.groupby("city").agg(Contacts=("contact_id","count")).reset_index().sort_values("Contacts", ascending=False).head(8)
    city_colors = [COLORS["pink"] if c in ["TP.HCM","Hà Nội"] else COLORS["purple"] for c in city_data["city"]]
    fig_city = go.Figure(go.Bar(
        x=city_data["city"], y=city_data["Contacts"],
        marker=dict(color=city_colors, line=dict(color="#D81B60", width=1.5)),
        text=city_data["Contacts"], textposition="outside", textfont=dict(size=12, color="#1A237E"),
    ))
    fig_city.update_layout(**CHART_LAYOUT)
    fig_city.update_layout(title="Top 8 Thành Phố")
    fig_city.update_yaxes(title="Số contacts", gridcolor="#F3E5F5")
    fig_city.update_xaxes(tickangle=-20)
    st.plotly_chart(fig_city, use_container_width=True)

# ═══════════════════════════════════════════════════════
# DATA TABLE
# ═══════════════════════════════════════════════════════
st.markdown('<div class="section-header">📋 BẢNG DỮ LIỆU GỐC (RAW DATA)</div>', unsafe_allow_html=True)
show_cols = ["contact_id","full_name","city","segment","lead_score_t0",
             "lifecycle_stage_t0","source","gym_frequency","email_ctr_30d_t0"]
display_df = dff[show_cols].copy()
display_df["email_ctr_30d_t0"] = (display_df["email_ctr_30d_t0"]*100).round(2).astype(str) + "%"
display_df.columns = ["ID","Họ Tên","Thành phố","Phân khúc","Lead Score",
                       "Lifecycle","Nguồn","Gym","Email CTR"]

st.dataframe(display_df.head(50), use_container_width=True, height=380)

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#3949AB;font-size:13px; font-weight:600;'>"
    "COOLMATE ANALYTICS DASHBOARD | Pre-Campaign Snapshot 2025"
    "</div>",
    unsafe_allow_html=True
)
