import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import networkx as nx

# ==========================================
# 1. KONFIGURASI HALAMAN (WIDE MODE)
# ==========================================
st.set_page_config(
    page_title="Supervision Dashboard",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def inject_css(css: str):
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
def inject_html(html: str):
    st.markdown(html, unsafe_allow_html=True)


# ==========================================
# 2. CSS: PENEMBAK JITU WRAPPER & FULLSCREEN
# ==========================================
inject_css("""
/* --- 1. HANCURKAN WRAPPER PUTIH YANG ANDA TEMUKAN --- */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

/* --- 2. KEMBALIKAN WARNA PUTIH HANYA UNTUK KOTAK GRAFIK --- */
div.block-container [data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 24px rgba(30,58,95,0.08) !important;
    padding: 16px 16px 8px !important;
}

/* --- 3. SET BACKGROUND SPLIT HERO (EDGE-TO-EDGE) --- */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #f0f4f8 !important; 
    margin: 0 !important;
    padding: 0 !important;
}

.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 320px; 
    background-color: #1e3a5f !important;
    z-index: -1;
}

/* --- 4. PAKSA FULLSCREEN (MELEBAR 100%) --- */
.block-container {
    max-width: 100vw !important; 
    width: 100% !important;
    padding-top: 1rem !important;
    padding-left: 3rem !important; 
    padding-right: 3rem !important; 
    padding-bottom: 3rem !important;
}

/* --- 5. SEMBUNYIKAN ELEMEN STREAMLIT YANG TIDAK PERLU --- */
header[data-testid="stHeader"], #MainMenu, footer, 
[data-testid="stToolbar"], [data-testid="stDecoration"] {
    display: none !important;
    height: 0 !important;
    visibility: hidden !important;
}
""")


# ==========================================
# 3. CSS: KOMPONEN DESAIN ANDA
# ==========================================
inject_css("""
html, body { font-family: 'Inter', sans-serif !important; }
.bi-navbar { display: flex; align-items: center; justify-content: space-between; padding: 10px 0 14px 0; }
.bi-logo { display: flex; align-items: center; gap: 12px; }
.bi-logo-box { width: 42px; height: 42px; background: rgba(255,255,255,0.18); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.bi-logo-title { color: #fff; font-size: 14px; font-weight: 700; display: block; }
.bi-logo-sub { color: rgba(255,255,255,0.55); font-size: 11px; display: block; }
.bi-navlinks { display: flex; gap: 4px; background: rgba(255,255,255,0.12); padding: 4px; border-radius: 10px; }
.bi-navlink { padding: 6px 18px; border-radius: 7px; color: rgba(255,255,255,0.7); font-size: 13px; font-weight: 500; cursor: pointer; }
.bi-navlink.on { background: #fff; color: #1e3a5f; font-weight: 600; }
.bi-navright { display: flex; align-items: center; gap: 14px; }
.bi-bell { font-size: 18px; color: rgba(255,255,255,0.75); }
.bi-avatar-wrap { display: flex; align-items: center; gap: 9px; }
.bi-avatar { width: 36px; height: 36px; border-radius: 50%; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; font-size: 15px; }
.bi-uname { color: #fff; font-size: 13px; font-weight: 600; display: block; }
.bi-urole { color: rgba(255,255,255,0.55); font-size: 11px; display: block; }

.bi-hero-title { color: #fff; font-size: 26px; font-weight: 800; margin: 0 0 4px 0; }
.bi-hero-sub { color: rgba(255,255,255,0.65); font-size: 12.5px; margin: 0 0 24px 0; }
.bi-hero-link { color: #7dd3fc; text-decoration: none; font-weight: 500; }

[data-testid="stSelectbox"] > div > div { background: rgba(255,255,255,0.15) !important; border: 1px solid rgba(255,255,255,0.3) !important; color: #fff !important; border-radius: 8px !important; }
[data-testid="stSelectbox"] svg { fill: #fff !important; }

[data-testid="metric-container"] { background: #ffffff !important; border: none !important; border-top: 4px solid #1e3a5f !important; border-radius: 14px !important; padding: 20px 20px 16px !important; box-shadow: 0 4px 24px rgba(30,58,95,0.12) !important; }
[data-testid="metric-container"] label { color: #64748b !important; font-size: 11px !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.5px !important; }
[data-testid="stMetricValue"] { color: #0f172a !important; font-size: 26px !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"] { font-size: 11.5px !important; }

[data-testid="stDownloadButton"] button { background: #f1f5f9 !important; color: #1e3a5f !important; border: 1px solid #cbd5e1 !important; border-radius: 8px !important; font-size: 12px !important; font-weight: 600 !important; margin-top: 6px; }
[data-testid="stDownloadButton"] button:hover { background: #e2e8f0 !important; }

.bi-section-title { font-size: 13px; font-weight: 700; color: #0f172a; margin: 0 0 12px 2px; }
.bi-footer { text-align: center; color: #94a3b8; font-size: 11px; padding: 2rem 0 1rem; border-top: 1px solid #e2e8f0; margin-top: 1rem; }
div.stMarkdown p { margin: 0; }
""")


# ==========================================
# 4. HTML NAVBAR & HERO
# ==========================================
inject_html("""
<div class="bi-navbar">
  <div class="bi-logo">
    <div class="bi-logo-box">💠</div>
    <div>
      <span class="bi-logo-title">SUPERVISION DASHBOARD</span>
      <span class="bi-logo-sub">Bank Indonesia &middot; DPPK / PUVA</span>
    </div>
  </div>
  <div class="bi-navlinks">
    <div class="bi-navlink on">Dashboard</div>
    <div class="bi-navlink">SRBI</div>
    <div class="bi-navlink">DNDF</div>
    <div class="bi-navlink">OIS</div>
  </div>
  <div class="bi-navright">
    <div class="bi-bell">🔔</div>
    <div class="bi-avatar-wrap">
      <div class="bi-avatar">👤</div>
      <div>
        <span class="bi-uname">Admin BI</span>
        <span class="bi-urole">Supervisor PUVA</span>
      </div>
    </div>
  </div>
</div>
""")

# Mapping Nama Pilihan UI ke Nama File Asli
FILE_MAPPING = {
    "2026 H1": "Data Repo - Masked .xlsx - 2026 H1.csv",
    "2025 H2": "Data Repo - Masked .xlsx - 2025 H2.csv",
    "2025 H1": "Data Repo - Masked .xlsx - 2025 H1.csv",
    "2024 H2": "Data Repo - Masked .xlsx - 2024 H2.csv",
    "2024 H1 (Pasca DU)": "Data Repo - Masked .xlsx - 2024 H1 Pasca DU.csv",
    "2024 H1 (Pra DU)": "Data Repo - Masked .xlsx - 2024 H1 Pra DU.csv"
}

h_col, p_col = st.columns([4, 1])
with h_col:
    inject_html("""
    <p class="bi-hero-title">Dashboard Pimpinan</p>
    <p class="bi-hero-sub">
        Terakhir diperbarui: Hari Ini &nbsp;&middot;&nbsp;
        <a class="bi-hero-link" href="#">🔄 Update Data</a>
    </p>
    """)
with p_col:
    inject_html("<div style='height:20px'></div>")
    selected_period = st.selectbox("Periode", list(FILE_MAPPING.keys()), label_visibility="collapsed")


# ==========================================
# 5. FUNGSI LOAD DATA ASLI (Cachced)
# ==========================================
@st.cache_data
def load_data(filename):
    try:
        df = pd.read_csv(filename)
        # Standarisasi kolom status agar aman dari perbedaan huruf besar/kecil/spasi
        if 'STATUS PD CASH BORROWER' in df.columns:
            df['STATUS PD CASH BORROWER'] = df['STATUS PD CASH BORROWER'].astype(str).str.upper().str.strip()
            # Bersihkan spasi ekstra di "NON DU" jika ada
            df['STATUS PD CASH BORROWER'] = df['STATUS PD CASH BORROWER'].replace('NON-DU', 'NON DU')
        return df
    except Exception as e:
        return None

df = load_data(FILE_MAPPING[selected_period])

if df is None or df.empty:
    st.error(f"Gagal memuat file: {FILE_MAPPING[selected_period]}. Pastikan file berada di folder yang sama dengan app.py.")
    st.stop()


# ==========================================
# 6. PERHITUNGAN KPI LOGIKA COUNTERPARTY LINE
# ==========================================
# 1. Total Volume DU (Ubah Nominal ke Triliun)
total_volume_t = df['NOMINAL (FULL AMOUNT)'].sum() / 1e12

# 2. Logika Kepatuhan Counterparty Line (>= 5 DU dan >= 5 NON DU)
cp_stats = df.groupby(['SANDI CASH LENDER (Masked)', 'STATUS PD CASH BORROWER'])['SANDI CASH BORROWER (Masked)'].nunique().unstack(fill_value=0)

# Pastikan kolom DU dan NON DU eksis agar tidak error
if 'DU' not in cp_stats.columns: cp_stats['DU'] = 0
if 'NON DU' not in cp_stats.columns: cp_stats['NON DU'] = 0

cp_stats['Patuh'] = (cp_stats['DU'] >= 5) & (cp_stats['NON DU'] >= 5)

total_lenders = len(cp_stats)
lender_patuh_count = cp_stats['Patuh'].sum()
avg_kepatuhan = (lender_patuh_count / total_lenders) * 100 if total_lenders > 0 else 0

# Rata-rata pemenuhan per Lender
avg_du_met = int(cp_stats['DU'].mean())
avg_non_du_met = int(cp_stats['NON DU'].mean())

# 3. Bank Tidak Penuhi Capaian
pelanggar_list = cp_stats[~cp_stats['Patuh']].index.tolist()
jumlah_bermasalah = len(pelanggar_list)
df_bermasalah = df[df['SANDI CASH LENDER (Masked)'].isin(pelanggar_list)]


# ==========================================
# 7. RENDER KPI CARDS
# ==========================================
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("📊 Total Volume DU (Repo)",       f"Rp {total_volume_t:.2f} T",  "")
with c2:
    st.metric("✅ Rata-rata Kepatuhan Evaluasi",  f"{avg_kepatuhan:.1f}%",        "Target: 100%", delta_color="off")
with c3:
    st.metric("🔗 Rata-rata CP Line Terpenuhi",   f"{avg_du_met} DU & {avg_non_du_met} NON-DU", "Target: 5 DU & 5 NON-DU", delta_color="off")
with c4:
    st.metric("⚠️ Bank Tidak Penuhi Capaian",    f"{jumlah_bermasalah} Bank",    "", delta_color="inverse")
    
    if not df_bermasalah.empty:
        csv_data = df_bermasalah.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Data Bermasalah",
            data=csv_data,
            file_name=f'Laporan_Bermasalah_{selected_period}.csv',
            mime='text/csv',
            use_container_width=True
        )

st.write("")


# ==========================================
# 8. CHARTS (SPLIT 50:50)
# ==========================================
BLUE_DARK   = "#1e3a5f"
BLUE_MID    = "#2563eb"
BLUE_ACCENT = "#0ea5e9"
BLUE_LIGHT  = "#bfdbfe"

def rank_colors(n):
    c = [BLUE_LIGHT] * n
    if n > 0: c[-1] = BLUE_DARK
    if n > 1: c[-2] = BLUE_MID
    if n > 2: c[-3] = BLUE_ACCENT
    return c

CHART_BASE = dict(
    margin=dict(l=0, r=30, t=5, b=5), height=290,
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    xaxis_visible=False, yaxis_title=None,
    font=dict(family="Inter,sans-serif", size=12, color="#475569"),
)

# CHART 1: Volume Terbesar (Dikonversi ke Triliun)
df_vol = df.groupby('SANDI CASH LENDER (Masked)')['NOMINAL (FULL AMOUNT)'].sum().reset_index()
df_vol['NOMINAL (TRILIUN)'] = df_vol['NOMINAL (FULL AMOUNT)'] / 1e12
df_vol = df_vol.sort_values('NOMINAL (TRILIUN)', ascending=True).tail(7)

# CHART 2: Inklusivitas (Borrower Kecil)
lender_counts   = df.groupby('SANDI CASH BORROWER (Masked)')['SANDI CASH LENDER (Masked)'].nunique()
small_borrowers = lender_counts[lender_counts <= 2].index
df_inklusif = (df[df['SANDI CASH BORROWER (Masked)'].isin(small_borrowers)]
               .groupby('SANDI CASH LENDER (Masked)')['SANDI CASH BORROWER (Masked)'].nunique().reset_index())
df_inklusif.columns = ['SANDI CASH LENDER (Masked)', 'Score Inklusivitas']
df_inklusif = df_inklusif.sort_values('Score Inklusivitas', ascending=True).tail(7)

cc1, cc2 = st.columns(2)
with cc1:
    with st.container(border=True):
        inject_html('<div class="bi-section-title">🏆 Bank dengan Volume Transaksi Terbesar (Triliun Rp)</div>')
        fig1 = px.bar(df_vol, x="NOMINAL (TRILIUN)", y="SANDI CASH LENDER (Masked)", orientation='h')
        fig1.update_layout(**CHART_BASE)
        fig1.update_traces(
            marker_color=rank_colors(len(df_vol)), width=0.55,
            texttemplate='<b>%{x:,.1f} T</b>', textposition='outside',
            textfont=dict(size=11, color="#334155")
        )
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

with cc2:
    with st.container(border=True):
        inject_html('<div class="bi-section-title">🌐 Apresiasi Inklusivitas Transaksi (Risk-Taking)</div>')
        fig2 = px.bar(df_inklusif, x="Score Inklusivitas", y="SANDI CASH LENDER (Masked)", orientation='h')
        fig2.update_layout(**CHART_BASE)
        fig2.update_traces(
            marker_color=rank_colors(len(df_inklusif)), width=0.55,
            texttemplate='<b>%{x}</b>', textposition='outside',
            textfont=dict(size=11, color="#334155")
        )
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})


# ==========================================
# 9. NETWORK GRAPH
# ==========================================
st.write("")
with st.container(border=True):
    inject_html('<div class="bi-section-title">🕸️ Peta Jaringan Transaksi Ekosistem Repo</div>')
    st.caption("● Biru tua = Dealer Utama (Lender)  |  ● Biru muda = Borrower  |  Node di pinggiran = konektivitas rendah")

    G   = nx.from_pandas_edgelist(df.head(100), 'SANDI CASH LENDER (Masked)', 'SANDI CASH BORROWER (Masked)')
    pos = nx.spring_layout(G, seed=42, k=1.2)

    ex, ey = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]; x1, y1 = pos[v]
        ex.extend([x0, x1, None]); ey.extend([y0, y1, None])

    edge_t = go.Scatter(
        x=ex, y=ey, line=dict(width=0.8, color='#cbd5e1'), hoverinfo='none', mode='lines'
    )

    nx_, ny_, nc_, ns_, nt_ = [], [], [], [], []
    lenders = set(df['SANDI CASH LENDER (Masked)'].values)
    for node in G.nodes():
        x, y = pos[node]
        nx_.append(x); ny_.append(y); nt_.append(node)
        if node in lenders:
            nc_.append(BLUE_DARK); ns_.append(16)
        else:
            nc_.append(BLUE_LIGHT); ns_.append(11)

    node_t = go.Scatter(
        x=nx_, y=ny_, mode='markers+text',
        textposition="bottom center", hoverinfo='text',
        text=[n for n in nt_],
        textfont=dict(size=9, family="Inter,sans-serif", color="#475569"),
        marker=dict(showscale=False, color=nc_, size=ns_, line_width=2, line_color='white')
    )

    fig_net = go.Figure(
        data=[edge_t, node_t],
        layout=go.Layout(
            showlegend=False, hovermode='closest',
            margin=dict(b=5, l=5, r=5, t=5),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=440
        )
    )
    st.plotly_chart(fig_net, use_container_width=True, config={'displayModeBar': False})


# ==========================================
# 10. FOOTER
# ==========================================
inject_html("""
<div class="bi-footer">
    Bank Indonesia &nbsp;&middot;&nbsp; Departemen Pengembangan Pasar Keuangan (DPPK)
    &nbsp;&middot;&nbsp; Sistem Pengawasan PUVA &nbsp;&middot;&nbsp; &copy; 2026
</div>
""")