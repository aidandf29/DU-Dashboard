import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import networkx as nx

# ==========================================
# 1. KONFIGURASI HALAMAN (WIDE)
# ==========================================
st.set_page_config(
    page_title="Supervision Dashboard",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. KONFIGURASI ICON CUSTOM 
# ==========================================
ICON_LOGO_URL = "https://api.iconify.design/streamline-ultimate/dice-bold.svg?color=%231e3a5f"
ICON_LOGO_SIZE = 32

ICON_NOTIF_URL = "https://api.iconify.design/basil/notification-on-solid.svg?color=%2364748b"
ICON_NOTIF_SIZE = 28

ICON_VOLUME_URL = "https://api.iconify.design/fluent-emoji-high-contrast/coin.svg?color=%230f172a"
ICON_VOLUME_SIZE = 22

ICON_INKLUSIF_URL = "https://api.iconify.design/carbon/help-desk.svg?color=%230f172a"
ICON_INKLUSIF_SIZE = 22

ICON_NET_URL = "https://api.iconify.design/lucide-lab/spider-web.svg?color=%230f172a"
ICON_NET_SIZE = 24


# ==========================================
# 3. CSS PALING AMAN 
# ==========================================
st.markdown("""
<style>
/* HAPUS HEADER BAWAAN STREAMLIT */
[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }

/* HAPUS ICON LINK (RANTAI) PADA JUDUL */
.header-anchor { display: none !important; }

/* LEBARKAN KONTEN & HAPUS BACKGROUND */
.block-container {
    max-width: 100% !important; 
    padding-top: 1rem !important;
    padding-bottom: 3rem !important;
    padding-left: 3rem !important; 
    padding-right: 3rem !important; 
}
.stApp { background-color: #f8fafc !important; }

/* DESAIN KARTU UNIFIED */
[data-testid="metric-container"],
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #ffffff !important;
    border-radius: 12px !important;
    border: none !important; 
    border-top: 4px solid #1e3a5f !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
}
[data-testid="metric-container"] { padding: 15px 20px !important; }
[data-testid="stVerticalBlockBorderWrapper"] { padding: 15px !important; }

/* CUSTOM NAVBAR */
.nav-container {
    display: flex; justify-content: space-between; align-items: center;
    padding-bottom: 25px; font-family: 'Inter', sans-serif;
    border-bottom: 1px solid #e2e8f0; margin-bottom: 25px;
}
.nav-logo { display: flex; align-items: center; gap: 12px; }
.nav-title { font-weight: 800; font-size: 16px; color: #0f172a; letter-spacing: 0.5px; margin-bottom: 2px;}
.nav-subtitle { font-size: 12px; color: #64748b; font-weight: 500; }
.nav-menu { display: flex; gap: 8px; background: #f1f5f9; padding: 6px; border-radius: 10px; }
.nav-item { padding: 6px 16px; font-size: 13px; font-weight: 600; color: #0f172a; border-radius: 6px; cursor: pointer; transition: 0.2s; }
.nav-item.active { background: #ffffff; color: #1e3a5f; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.nav-item.disabled { color: #94a3b8; cursor: not-allowed; } 
.nav-profile-name { font-size: 13px; font-weight: 700; color: #0f172a; }
.nav-profile-role { font-size: 11px; color: #64748b; font-weight: 500; }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 4. HTML NAVBAR CUSTOM
# ==========================================
st.markdown(f"""
<div class="nav-container">
<div class="nav-logo">
<img src="{ICON_LOGO_URL}&width={ICON_LOGO_SIZE}&height={ICON_LOGO_SIZE}" style="flex-shrink: 0;">
<div><div class="nav-title">SUPERVISION DASHBOARD</div><div class="nav-subtitle">Bank Indonesia • DPPK / PUVA</div></div>
</div>
<div class="nav-menu">
<div class="nav-item active">REPO</div>
<div class="nav-item disabled" title="Fitur SRBI sedang dalam pengembangan 🚧">SRBI</div>
<div class="nav-item disabled" title="Fitur OIS sedang dalam pengembangan 🚧">OIS</div>
</div>
<div style="display: flex; align-items: center; gap: 20px;">
<img src="{ICON_NOTIF_URL}&width={ICON_NOTIF_SIZE}&height={ICON_NOTIF_SIZE}" style="cursor: pointer; flex-shrink: 0;">
<div style="display: flex; align-items: center; gap: 12px;">
<div style="background: #e2e8f0; color: #1e3a5f; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0;">👤</div>
<div><div class="nav-profile-name">Admin BI</div><div class="nav-profile-role">Supervisor PUVA</div></div>
</div>
</div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 5. FUNGSI LOAD DATA EXCEL
# ==========================================
@st.cache_data
def load_excel_data():
    try:
        # Ambil link dari Streamlit Secrets
        raw_url = st.secrets["DATA_LINK"]
        
        # Ekstrak ID file dari link (berlaku untuk docs.google.com maupun drive.google.com)
        if "/d/" in raw_url:
            file_id = raw_url.split("/d/")[1].split("/")[0]
            # Paksa URL menjadi link "Direct Download" format xlsx
            download_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
        else:
            download_url = raw_url

        # Tambahkan engine='openpyxl' agar Pandas tidak bingung dengan format dari URL
        xls = pd.ExcelFile(download_url, engine='openpyxl')
        sheets_dict = {}
        
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            df.columns = df.columns.str.strip()
            
            if 'SANDI CASH LENDER (Masked)' in df.columns:
                df['SANDI CASH LENDER (Masked)'] = df['SANDI CASH LENDER (Masked)'].astype(str)
            if 'SANDI CASH BORROWER (Masked)' in df.columns:
                df['SANDI CASH BORROWER (Masked)'] = df['SANDI CASH BORROWER (Masked)'].astype(str)
                
            if 'STATUS PD CASH BORROWER' in df.columns:
                df['STATUS PD CASH BORROWER'] = df['STATUS PD CASH BORROWER'].astype(str).str.upper().str.strip()
                df['STATUS PD CASH BORROWER'] = df['STATUS PD CASH BORROWER'].replace('NON-DU', 'NON DU')
                
            if 'TANGGAL TRANSAKSI' in df.columns:
                df['TANGGAL TRANSAKSI'] = pd.to_datetime(df['TANGGAL TRANSAKSI'], errors='coerce')
                
            sheets_dict[sheet_name] = df
        return sheets_dict
    except Exception as e:
        st.error(f"Gagal memuat Excel: {e}")
        return None

sheets_data = load_excel_data()

# ==========================================
# 6. HERO TEXT & DROPDOWN PERIODE
# ==========================================
col_hero, col_filter = st.columns([4, 1])

if sheets_data is not None:
    daftar_periode = list(sheets_data.keys())
else:
    daftar_periode = ["2026 H1", "2025 H2", "2025 H1"] 

with col_filter:
    st.write("") 
    selected_period = st.selectbox("Periode", daftar_periode, label_visibility="collapsed")

if sheets_data is None: 
    st.stop()

df = sheets_data[selected_period]

if 'TANGGAL TRANSAKSI' in df.columns and not df['TANGGAL TRANSAKSI'].isnull().all():
    min_date = df['TANGGAL TRANSAKSI'].min().strftime('%d %b %Y')
    max_date = df['TANGGAL TRANSAKSI'].max().strftime('%d %b %Y')
    periode_teks = f"Periode Transaksi: {min_date} - {max_date}"
else:
    periode_teks = "Periode Transaksi: Data tanggal tidak tersedia"

with col_hero:
    st.markdown(f"""
    <div style="font-family: 'Inter', sans-serif;">
        <div style="margin-bottom: 5px; font-size: 28px; font-weight: 800; color: #0f172a;">Dashboard Pemantauan Dealer Utama</div>
        <p style="font-size: 13px; color: #64748b; font-weight: 500; margin-top: 0;">{periode_teks}</p>
    </div>
    """, unsafe_allow_html=True)
st.write("")

# ==========================================
# 7. PERHITUNGAN KPI UMUM (LOGIKA DIPERBARUI)
# ==========================================
# A. Buat Master Map Status Bank
lender_map = df[['SANDI CASH LENDER (Masked)', 'STATUS DU CASH LENDER']].rename(columns={'SANDI CASH LENDER (Masked)': 'ID', 'STATUS DU CASH LENDER': 'STATUS'})
borrower_map = df[['SANDI CASH BORROWER (Masked)', 'STATUS PD CASH BORROWER']].rename(columns={'SANDI CASH BORROWER (Masked)': 'ID', 'STATUS PD CASH BORROWER': 'STATUS'})
status_map = pd.concat([lender_map, borrower_map]).drop_duplicates()
status_map['STATUS'] = status_map['STATUS'].astype(str).str.upper().str.strip().replace('NON-DU', 'NON DU')
status_dict = status_map.set_index('ID')['STATUS'].to_dict()

# B. Gabungkan semua hubungan (Lender->Borrower dan Borrower->Lender)
rels = pd.concat([
    df[['SANDI CASH LENDER (Masked)', 'SANDI CASH BORROWER (Masked)']].rename(columns={'SANDI CASH LENDER (Masked)': 'Bank', 'SANDI CASH BORROWER (Masked)': 'Counterparty'}),
    df[['SANDI CASH BORROWER (Masked)', 'SANDI CASH LENDER (Masked)']].rename(columns={'SANDI CASH BORROWER (Masked)': 'Bank', 'SANDI CASH LENDER (Masked)': 'Counterparty'})
]).drop_duplicates()

# C. Tambahkan status pada relasi
rels['Counterparty_Status'] = rels['Counterparty'].map(status_dict)
rels['Bank_Status'] = rels['Bank'].map(status_dict)

# D. Filter hanya untuk Bank yang berstatus 'DU'
du_rels = rels[rels['Bank_Status'] == 'DU']

# E. Hitung jumlah unik counterparty per Bank DU
compliance_check = du_rels.groupby(['Bank', 'Counterparty_Status'])['Counterparty'].nunique().unstack(fill_value=0)

# F. Pastikan kolom DU dan NON DU ada
if 'DU' not in compliance_check.columns: compliance_check['DU'] = 0
if 'NON DU' not in compliance_check.columns: compliance_check['NON DU'] = 0

# G. Definisi Patuh: Minimal 5 DU dan 5 Non DU
compliance_check['Patuh'] = (compliance_check['DU'] >= 5) & (compliance_check['NON DU'] >= 5)

# H. Update KPI
total_du_banks = len(compliance_check)
lender_patuh_count = compliance_check['Patuh'].sum()
avg_kepatuhan = (lender_patuh_count / total_du_banks) * 100 if total_du_banks > 0 else 0
jumlah_bermasalah = total_du_banks - lender_patuh_count

# Update Total Volume (Tetap sama)
total_volume_t = df['NOMINAL (FULL AMOUNT)'].sum() / 1e12

# ==========================================
# 8. KPI CARDS + HALF DOUGHNUT CHART (STATIS)
# ==========================================
col_donut, c1, c2, c3 = st.columns(4)

LABEL_HTML = '<div style="color: #64748b; font-weight: 700; font-size: 12px; text-transform: uppercase; margin-bottom: 8px;">{}</div>'
VALUE_HTML = '<div style="color: #0f172a; font-size: 26px; font-weight: 800; margin-bottom: 15px;">{}</div>'

with col_donut:
    with st.container():
        st.markdown(LABEL_HTML.format("Komposisi Bank"), unsafe_allow_html=True)
        
        total_banks = 105
        du_count = 21
        non_du_count = 84
        
        donut_labels = ['DU', 'Non-DU', '']
        donut_values = [du_count, non_du_count, total_banks] 
        donut_colors = ['#1e3a5f', '#0ea5e9', 'rgba(0,0,0,0)']
        line_colors = ['#ffffff', '#ffffff', 'rgba(0,0,0,0)']
        line_widths = [2, 2, 0]

        fig_donut = go.Figure(data=[go.Pie(
            labels=donut_labels, values=donut_values, hole=0.75,
            rotation=270, direction='clockwise', sort=False,
            marker=dict(colors=donut_colors, line=dict(color=line_colors, width=line_widths)),
            textinfo='none', hoverinfo='label+value'
        )])

        fig_donut.update_layout(
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=60), height=80, 
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            annotations=[dict(
                text=f"<span style='font-size:22px; font-weight:800; color:#0f172a;'>{total_banks}</span><br><span style='font-size:11px; font-weight:600; color:#64748b;'>Bank</span>", 
                x=0.5, y=0.15, showarrow=False
            )]
        )
        st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})

with c1:
    with st.container():
        st.markdown(LABEL_HTML.format("Total Volume DU (Repo)"), unsafe_allow_html=True)
        st.markdown(VALUE_HTML.format(f"Rp {total_volume_t:.2f} T"), unsafe_allow_html=True)

with c2:
    with st.container():
        st.markdown(LABEL_HTML.format("Rata-rata Kepatuhan"), unsafe_allow_html=True)
        st.markdown(VALUE_HTML.format(f"{avg_kepatuhan:.1f}%"), unsafe_allow_html=True)

with c3:
    with st.container():
        st.markdown(LABEL_HTML.format("Bank Tidak Patuh"), unsafe_allow_html=True)
        st.markdown(VALUE_HTML.format(f"{jumlah_bermasalah} Bank"), unsafe_allow_html=True)
    

# ==========================================
# 9. CHARTS
# ==========================================
st.write("")
col_chart1, col_chart2 = st.columns(2)

CHART_BASE = dict(
    margin=dict(l=60, r=20, t=10, b=10), height=300,
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    xaxis_visible=False, yaxis_title=None,
)

df_vol = df.groupby('SANDI CASH LENDER (Masked)')['NOMINAL (FULL AMOUNT)'].sum().reset_index()
df_vol['NOMINAL (TRILIUN)'] = df_vol['NOMINAL (FULL AMOUNT)'] / 1e12
df_vol = df_vol.sort_values('NOMINAL (TRILIUN)', ascending=True).tail(7)

with col_chart1:
    with st.container(border=True):
        st.markdown(f"""
        <div style='color: #0f172a; font-weight: 700; font-size: 15px; margin-bottom: 10px; display: flex; align-items: center; gap: 8px;'>
            <img src="{ICON_VOLUME_URL}&width={ICON_VOLUME_SIZE}&height={ICON_VOLUME_SIZE}" style="flex-shrink: 0;">
            Bank dengan Volume Transaksi Terbesar (Triliun Rp)
        </div>
        """, unsafe_allow_html=True)
        
        fig1 = px.bar(df_vol, x="NOMINAL (TRILIUN)", y="SANDI CASH LENDER (Masked)", orientation='h')
        fig1.update_layout(**CHART_BASE)
        
        max_vol = df_vol['NOMINAL (TRILIUN)'].max()
        fig1.update_xaxes(range=[0, max_vol * 1.25])
        
        colors1 = ['#bfdbfe'] * 6 + ['#1e3a5f']
        
        fig1.update_traces(marker_color=colors1, width=0.6, texttemplate='<b>%{x:,.1f} T</b>', textposition='outside', textfont=dict(color="#0f172a"), cliponaxis=False)
        fig1.update_yaxes(type='category', tickfont=dict(color="#0f172a", size=11)) 
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

lender_counts_real = df.groupby('SANDI CASH BORROWER (Masked)')['SANDI CASH LENDER (Masked)'].nunique()
small_borrowers_real = lender_counts_real[lender_counts_real <= 2].index
df_inklusif = df[df['SANDI CASH BORROWER (Masked)'].isin(small_borrowers_real)].groupby('SANDI CASH LENDER (Masked)')['SANDI CASH BORROWER (Masked)'].nunique().reset_index()
df_inklusif.columns = ['LENDER', 'Score']
df_inklusif = df_inklusif.sort_values('Score', ascending=True).tail(7)

with col_chart2:
    with st.container(border=True):
        st.markdown(f"""
        <div style='color: #0f172a; font-weight: 700; font-size: 15px; margin-bottom: 10px; display: flex; align-items: center; gap: 8px;'>
            <img src="{ICON_INKLUSIF_URL}&width={ICON_INKLUSIF_SIZE}&height={ICON_INKLUSIF_SIZE}" style="flex-shrink: 0;">
            Apresiasi Inklusivitas Transaksi (Risk-Taking)
        </div>
        """, unsafe_allow_html=True)
        
        fig2 = px.bar(df_inklusif, x="Score", y="LENDER", orientation='h')
        fig2.update_layout(**CHART_BASE)
        
        max_score = df_inklusif['Score'].max()
        fig2.update_xaxes(range=[0, max_score * 1.25])
        
        colors2 = ['#bfdbfe'] * 6 + ['#1e3a5f']
        
        fig2.update_traces(marker_color=colors2, width=0.6, texttemplate='<b>%{x}</b>', textposition='outside', textfont=dict(color="#0f172a"), cliponaxis=False)
        fig2.update_yaxes(type='category', tickfont=dict(color="#0f172a", size=11)) 
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

# ==========================================
# 10. NETWORK GRAPH
# ==========================================
st.write("")
with st.container(border=True):
    col_title, col_filter_net = st.columns([3, 1])
    
    with col_title:
        st.markdown(f"""
        <div style='color: #0f172a; font-weight: 700; font-size: 16px; margin-bottom: 5px; display: flex; align-items: center; gap: 8px;'>
            <img src="{ICON_NET_URL}&width={ICON_NET_SIZE}&height={ICON_NET_SIZE}" style="flex-shrink: 0;">
            Peta Jaringan Transaksi Ekosistem Repo
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='color: #0f172a; font-size: 13px; font-weight: 500; margin-bottom: 15px;'>Biru Tua = DU &nbsp;&nbsp;|&nbsp;&nbsp; Biru Muda = Non DU</div>", unsafe_allow_html=True)

    with col_filter_net:
        all_banks = pd.concat([df['SANDI CASH LENDER (Masked)'], df['SANDI CASH BORROWER (Masked)']]).dropna().unique()
        all_banks_sorted = sorted(list(all_banks))
        
        st.write("") 
        selected_bank = st.selectbox(
            "Filter Bank", 
            ["Semua Bank"] + all_banks_sorted, 
            label_visibility="collapsed"
        )
    
    lender_map = df[['SANDI CASH LENDER (Masked)', 'STATUS DU CASH LENDER']].rename(columns={'SANDI CASH LENDER (Masked)': 'ID_BANK', 'STATUS DU CASH LENDER': 'STATUS'})
    borrower_map = df[['SANDI CASH BORROWER (Masked)', 'STATUS PD CASH BORROWER']].rename(columns={'SANDI CASH BORROWER (Masked)': 'ID_BANK', 'STATUS PD CASH BORROWER': 'STATUS'})
    all_mapping_status = pd.concat([lender_map, borrower_map]).dropna()
    all_mapping_status['STATUS'] = all_mapping_status['STATUS'].astype(str).str.upper().str.strip().replace('NON-DU', 'NON DU')
    bank_status_dict = all_mapping_status.groupby('ID_BANK')['STATUS'].apply(lambda x: 'DU' if 'DU' in x.values else 'NON DU').to_dict()

    df_edges = df[['SANDI CASH LENDER (Masked)', 'SANDI CASH BORROWER (Masked)']].drop_duplicates()
    
    if selected_bank != "Semua Bank":
        df_edges = df_edges[
            (df_edges['SANDI CASH LENDER (Masked)'] == selected_bank) | 
            (df_edges['SANDI CASH BORROWER (Masked)'] == selected_bank)
        ]

    if df_edges.empty:
        st.info(f"Tidak ada transaksi untuk {selected_bank} pada periode ini.")
    else:
        G = nx.from_pandas_edgelist(df_edges, 'SANDI CASH LENDER (Masked)', 'SANDI CASH BORROWER (Masked)')
        pos = nx.spring_layout(G, seed=42, k=0.15)

        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#cbd5e1'), hoverinfo='none', mode='lines')

        # === INI BAGIAN YANG DIPERBAIKI (DITAMBAH 1 KURUNG SIKU KOSONG) ===
        node_x, node_y, node_color, node_size = [], [], [], []
        # ================================================================
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x); node_y.append(y)
            
            status = bank_status_dict.get(str(node), 'NON DU')
            
            if status == 'DU':
                node_color.append('#1e3a5f') 
                node_size.append(26 if str(node) == selected_bank else 14)
            else:
                node_color.append('#0ea5e9') 
                node_size.append(26 if str(node) == selected_bank else 12) 

        line_colors = ['#f59e0b' if str(node) == selected_bank else 'white' for node in G.nodes()]
        line_widths = [3 if str(node) == selected_bank else 1 for node in G.nodes()]

        node_trace = go.Scatter(
            x=node_x, y=node_y, mode='markers+text', hoverinfo='text',
            text=list(G.nodes()),
            textfont=dict(color="#0f172a", size=10),
            textposition="bottom center",
            marker=dict(
                color=node_color, 
                size=node_size, 
                line=dict(width=line_widths, color=line_colors)
            )
        )

        fig_net = go.Figure(data=[edge_trace, node_trace],
            layout=go.Layout(showlegend=False, hovermode='closest', margin=dict(b=0, l=0, r=0, t=0),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=500) 
        )
        st.plotly_chart(fig_net, use_container_width=True, config={'displayModeBar': False})
