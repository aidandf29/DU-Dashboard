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
ICON_NOTIF_URL = "https://api.iconify.design/basil/notification-on-solid.svg?color=%2364748b"
ICON_VOLUME_URL = "https://api.iconify.design/fluent-emoji-high-contrast/coin.svg?color=%230f172a"
ICON_INKLUSIF_URL = "https://api.iconify.design/carbon/help-desk.svg?color=%230f172a"
ICON_NET_URL = "https://api.iconify.design/lucide-lab/spider-web.svg?color=%230f172a"
ICON_LOGO_SIZE = 32
ICON_NOTIF_SIZE = 28
ICON_VOLUME_SIZE = 22
ICON_INKLUSIF_SIZE = 22
ICON_NET_SIZE = 24

# ==========================================
# 3. CSS CUSTOM - FIX MAROON GLASS DENGAN BORDER TEBAL & SHADOW
# ==========================================
st.markdown("""
<style>
/* HAPUS HEADER BAWAAN STREAMLIT */
[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
.header-anchor { display: none !important; }

/* LEBARKAN KONTEN APLIKASI */
.block-container {
    max-width: 100% !important; 
    padding-top: 1rem !important;
    padding-bottom: 3rem !important;
    padding-left: 3rem !important; 
    padding-right: 3rem !important; 
}

/* BACKGROUND UTAMA DASHBOARD (ABU-ABU NETRAL BERSIH) */
.stApp { 
    background-color: #f1f5f9 !important; 
}

/* KARTU METRIC RINGKASAN ATAS (SOLID PUTIH) */
[data-testid="metric-container"] {
    background-color: #ffffff !important;
    border-radius: 12px !important;
    border: none !important; 
    border-top: 4px solid #1e3a5f !important;
    box-shadow: 0 4px 6px rgba(15, 23, 42, 0.05) !important;
    padding: 15px 20px !important;
}

/* SETTINGAN DASAR SEMUA KOTAK CONTAINER (Peta Jaringan Tetap Putih Solid) */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #ffffff !important;
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important; 
    border-top: 4px solid #1e3a5f !important;
    box-shadow: 0 4px 6px rgba(15, 23, 42, 0.05) !important;
    padding: 20px !important;
}

/* TARGET MUTLAK ANTI-GAGAL: HANYA KOTAK DI DALAM STCOLUMN (LEADERBOARD) */
/* Menggunakan multi-selector resmi Streamlit untuk menjamin kompatibilitas browser */
[data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stColumn"] div[data-testid="stVerticalBlockBorderWrapper"] {
    /* Perpaduan Transparansi Light Maroon Glass */
    background: linear-gradient(135deg, rgba(136, 19, 55, 0.15) 0%, rgba(255, 255, 255, 0.95) 100%) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border-radius: 16px !important;
    
    /* Spesifikasi Border Tebal Warna Maroon Tegas */
    border: 3px solid #881337 !important; 
    border-top: 5px solid #4c0519 !important; 
    
    /* Spesifikasi Heavy Shadow Mendalam */
    box-shadow: 0 20px 25px -5px rgba(136, 19, 55, 0.25), 0 10px 10px -5px rgba(0, 0, 0, 0.15) !important;
}

/* NAVBAR BRANDING STYLE */
.nav-container {
    display: flex; justify-content: space-between; align-items: center;
    padding-bottom: 25px; font-family: 'Inter', sans-serif;
    border-bottom: 1px solid #cbd5e1; margin-bottom: 25px;
}
.nav-logo { display: flex; align-items: center; gap: 12px; }
.nav-title { font-weight: 800; font-size: 16px; color: #0f172a; letter-spacing: 0.5px; margin-bottom: 2px;}
.nav-subtitle { font-size: 12px; color: #475569; font-weight: 500; }
.nav-menu { display: flex; gap: 8px; background: rgba(15, 23, 42, 0.05); padding: 6px; border-radius: 10px; }
.nav-item { padding: 6px 16px; font-size: 13px; font-weight: 600; color: #0f172a; border-radius: 6px; cursor: pointer; transition: 0.2s; }
.nav-item.active { background: #ffffff; color: #1e3a5f; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.nav-item.disabled { color: #64748b; cursor: not-allowed; } 
.nav-profile-name { font-size: 13px; font-weight: 700; color: #0f172a; }
.nav-profile-role { font-size: 11px; color: #475569; font-weight: 500; }
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
<div style="background: rgba(30, 58, 95, 0.12); color: #1e3a5f; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0;">👤</div>
<div><div class="nav-profile-name">Admin BI</div><div class="nav-profile-role">Supervisor PUVA</div></div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. FUNGSI LOAD DATA EXCEL & GENERATE KUARTAL
# ==========================================
@st.cache_data
def load_excel_data_quarterly():
    try:
        raw_url = st.secrets["DATA_LINK"]
        
        if "/d/" in raw_url:
            file_id = raw_url.split("/d/")[1].split("/")[0]
            download_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
        else:
            download_url = raw_url

        xls = pd.ExcelFile(download_url, engine='openpyxl')
        quarter_dict = {}
        
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            df.columns = df.columns.str.strip()
            
            if 'SANDI CASH LENDER (Masked)' in df.columns:
                df['SANDI CASH LENDER (Masked)'] = df['SANDI CASH LENDER (Masked)'].astype(str).str.strip()
            if 'SANDI CASH BORROWER (Masked)' in df.columns:
                df['SANDI CASH BORROWER (Masked)'] = df['SANDI CASH BORROWER (Masked)'].astype(str).str.strip()
                
            if 'STATUS PD CASH BORROWER' in df.columns:
                df['STATUS PD CASH BORROWER'] = df['STATUS PD CASH BORROWER'].astype(str).str.upper().str.strip()
                
            if 'STATUS DU CASH LENDER' in df.columns:
                df['STATUS DU CASH LENDER'] = df['STATUS DU CASH LENDER'].astype(str).str.upper().str.strip()
                
            if 'TANGGAL TRANSAKSI' in df.columns:
                df['TANGGAL TRANSAKSI'] = pd.to_datetime(df['TANGGAL TRANSAKSI'], errors='coerce')
                
            if 'BULAN TRANSAKSI' in df.columns and 'TAHUN TRANSAKSI' in df.columns:
                for label_bulan, sub_df in df.groupby('BULAN TRANSAKSI'):
                    if label_bulan in [1, 2, 3]:
                        q_name = "Q1 (Jan-Mar)"
                    elif label_bulan in [4, 5, 6]:
                        q_name = "Q2 (Apr-Jun)"
                    elif label_bulan in [7, 8, 9]:
                        q_name = "Q3 (Jul-Sep)"
                    else:
                        q_name = "Q4 (Okt-Des)"
                    
                    tahun = int(sub_df['TAHUN TRANSAKSI'].iloc[0])
                    nama_key = f"{tahun} {q_name}"
                    if "Pra DU" in sheet_name:
                        nama_key += " (Pra DU)"
                    elif "Pasca DU" in sheet_name:
                        nama_key += " (Pasca DU)"
                    
                    if nama_key in quarter_dict:
                        quarter_dict[nama_key] = pd.concat([quarter_dict[nama_key], sub_df]).drop_duplicates()
                    else:
                        quarter_dict[nama_key] = sub_df
                        
        sorted_keys = sorted(quarter_dict.keys(), reverse=True)
        sorted_quarter_dict = {k: quarter_dict[k] for k in sorted_keys}
        
        return sorted_quarter_dict
    except Exception as e:
        st.error(f"Gagal memuat Excel: {e}")
        return None

sheets_data = load_excel_data_quarterly()

# ==========================================
# 6. HERO TEXT & DROPDOWN PERIODE
# ==========================================
col_hero, col_filter = st.columns([3.5, 1.5])

if sheets_data is not None:
    daftar_periode = list(sheets_data.keys())
else:
    daftar_periode = ["2026 Q1 (Jan-Mar)", "2025 Q4 (Okt-Des)", "2025 Q3 (Jul-Sep)"] 

with col_filter:
    st.write("") 
    selected_period = st.selectbox("Periode Evaluasi", daftar_periode, label_visibility="collapsed")

if sheets_data is None: 
    st.stop()

df = sheets_data[selected_period]

if 'TANGGAL TRANSAKSI' in df.columns and not df['TANGGAL TRANSAKSI'].isnull().all():
    min_date = df['TANGGAL TRANSAKSI'].min().strftime('%d %b %Y')
    max_date = df['TANGGAL TRANSAKSI'].max().strftime('%d %b %Y')
    periode_teks = f"Periode Evaluasi 3 Bulanan: {min_date} - {max_date}"
else:
    periode_teks = "Periode Transaksi: Data tanggal tidak tersedia"

with col_hero:
    st.markdown(f"""
    <div style="font-family: 'Inter', sans-serif;">
        <div style="margin-bottom: 5px; font-size: 28px; font-weight: 800; color: #0f172a;">Dashboard Pemantauan Dealer Utama</div>
        <p style="font-size: 13px; color: #475569; font-weight: 500; margin-top: 0;">{periode_teks}</p>
    </div>
    """, unsafe_allow_html=True)
st.write("")

# ==========================================
# 7. PERHITUNGAN KPI UMUM & KLASIFIKASI ENTITAS
# ==========================================
DAFTAR_DU_RESMI = ['3', '9', '10', '12', '14', '15', '17', '20', '23', '24', '29', '47', '51', '68', '70', '88', '111', '115', '201', '214', '427']

l_status = df[['SANDI CASH LENDER (Masked)', 'STATUS DU CASH LENDER']].rename(columns={'SANDI CASH LENDER (Masked)': 'ID', 'STATUS DU CASH LENDER': 'RAW_STATUS'})
b_status = df[['SANDI CASH BORROWER (Masked)', 'STATUS PD CASH BORROWER']].rename(columns={'SANDI CASH BORROWER (Masked)': 'ID', 'STATUS PD CASH BORROWER': 'RAW_STATUS'})
raw_status_map = pd.concat([l_status, b_status]).dropna().drop_duplicates()
raw_status_map['RAW_STATUS'] = raw_status_map['RAW_STATUS'].astype(str).str.upper().str.strip()
base_status_dict = raw_status_map.set_index('ID')['RAW_STATUS'].to_dict()

all_active_data_banks = pd.concat([df['SANDI CASH LENDER (Masked)'], df['SANDI CASH BORROWER (Masked)']]).dropna().unique()
all_active_data_banks = [str(bank).strip() for bank in all_active_data_banks]

status_dict = {}
for bank in all_active_data_banks:
    if bank in DAFTAR_DU_RESMI:
        status_dict[bank] = 'DU'
    else:
        raw_st = base_status_dict.get(bank, 'NON DU')
        if any(keyword in raw_st for keyword in ['NON BANK', 'NON-BANK', 'BKN BANK', 'LEMBAGA NON', 'NB']):
            status_dict[bank] = 'NON BANK'
        else:
            status_dict[bank] = 'NON DU'

active_du_count = sum(1 for b in all_active_data_banks if status_dict[b] == 'DU')
active_non_du_count = sum(1 for b in all_active_data_banks if status_dict[b] == 'NON DU')
active_non_bank_count = sum(1 for b in all_active_data_banks if status_dict[b] == 'NON BANK')
total_active_banks = len(all_active_data_banks)

rels = pd.concat([
    df[['SANDI CASH LENDER (Masked)', 'SANDI CASH BORROWER (Masked)']].rename(columns={'SANDI CASH LENDER (Masked)': 'Bank', 'SANDI CASH BORROWER (Masked)': 'Counterparty'}),
    df[['SANDI CASH BORROWER (Masked)', 'SANDI CASH LENDER (Masked)']].rename(columns={'SANDI CASH BORROWER (Masked)': 'Bank', 'SANDI CASH LENDER (Masked)': 'Counterparty'})
]).dropna().drop_duplicates()

rels['Bank'] = rels['Bank'].astype(str)
rels['Counterparty'] = rels['Counterparty'].astype(str)

rels['Bank_Status'] = rels['Bank'].map(status_dict)
rels['Counterparty_Status'] = rels['Counterparty'].map(status_dict)

du_rels = rels[rels['Bank'].isin(DAFTAR_DU_RESMI)]
counts = du_rels.groupby(['Bank', 'Counterparty_Status'])['Counterparty'].nunique().unstack(fill_value=0)

if 'DU' not in counts.columns: counts['DU'] = 0
if 'NON DU' not in counts.columns: counts['NON DU'] = 0

compliance_check = pd.DataFrame(index=DAFTAR_DU_RESMI)
compliance_check = compliance_check.join(counts).fillna(0)
compliance_check['Patuh'] = (compliance_check['DU'] >= 5) & (compliance_check['NON DU'] >= 5)

lender_patuh_count = compliance_check['Patuh'].sum()
total_universe_du = len(DAFTAR_DU_RESMI)
jumlah_bermasalah = total_universe_du - lender_patuh_count
avg_kepatuhan = (lender_patuh_count / total_universe_du) * 100 if total_universe_du > 0 else 0
total_volume_t = df['NOMINAL (FULL AMOUNT)'].sum() / 1e12

# Cetak log bank bermasalah ke terminal background
bank_tidak_patuh_list = compliance_check[~compliance_check['Patuh']].index.tolist()
print("\n" + "="*50)
print(f"📡 LOG EVALUASI DASHBOARD - PERIODE: {selected_period}")
print(f"Total Universe DU: {total_universe_du} Bank")
print(f"Jumlah DU Tidak Patuh: {jumlah_bermasalah} Bank")
print(f"Daftar Nomor Bank DU Yang Tidak Patuh: {bank_tidak_patuh_list}")
print("="*50 + "\n")

# ==========================================
# 8. KARTU UTAMA & DIAGRAM DONUT DINAMIS
# ==========================================
col_donut, c1, c2, c3 = st.columns(4)

LABEL_HTML = '<div style="color: #475569; font-weight: 700; font-size: 12px; text-transform: uppercase; margin-bottom: 8px;">{}</div>'
VALUE_HTML = '<div style="color: #0f172a; font-size: 26px; font-weight: 800; margin-bottom: 15px;">{}</div>'

with col_donut:
    with st.container():
        st.markdown(LABEL_HTML.format("Komposisi Aktivitas Pasar"), unsafe_allow_html=True)
        
        donut_labels = ['DU', 'Non-DU', 'Non-Bank', '']
        donut_values = [active_du_count, active_non_du_count, active_non_bank_count, total_active_banks] 
        donut_colors = ['#1e3a5f', '#0ea5e9', '#f59e0b', 'rgba(0,0,0,0)']
        line_colors = ['#ffffff', '#ffffff', '#ffffff', 'rgba(0,0,0,0)']
        line_widths = [2, 2, 2, 0]

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
                text=f"<span style='font-size:20px; font-weight:800; color:#0f172a;'>{total_active_banks}</span><br><span style='font-size:10px; font-weight:600; color:#64748b;'>Entitas</span>", 
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
# 9. PAPAN PERINGKAT (LEADERBOARD MAROON GLASS)
# ==========================================
st.write("")
col_chart1, col_chart2 = st.columns(2)

CHART_BASE = dict(
    margin=dict(l=60, r=20, t=10, b=10), height=300,
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    xaxis_visible=False, yaxis_title=None,
)

df_vol = df.groupby('SANDI CASH LENDER (Masked)')['NOMINAL (FULL AMOUNT)'].sum().reset_index()
df_vol['SANDI CASH LENDER (Masked)'] = df_vol['SANDI CASH LENDER (Masked)'].astype(str).str.strip()
df_vol = df_vol[df_vol['SANDI CASH LENDER (Masked)'].isin(DAFTAR_DU_RESMI)]
df_vol['NOMINAL (TRILIUN)'] = df_vol['NOMINAL (FULL AMOUNT)'] / 1e12
df_vol = df_vol.sort_values('NOMINAL (TRILIUN)', ascending=True).tail(7)

with col_chart1:
    with st.container(border=True): 
        st.markdown(f"""
        <div style='color: #0f172a; font-weight: 700; font-size: 15px; margin-bottom: 10px; display: flex; align-items: center; gap: 8px;'>
            <img src="{ICON_VOLUME_URL}&width={ICON_VOLUME_SIZE}&height={ICON_VOLUME_SIZE}" style="flex-shrink: 0;">
            Dealer Utama Volume Transaksi Terbesar (Triliun Rp)
        </div>
        """, unsafe_allow_html=True)
        
        fig1 = px.bar(df_vol, x="NOMINAL (TRILIUN)", y="SANDI CASH LENDER (Masked)", orientation='h')
        fig1.update_layout(**CHART_BASE)
        
        max_vol = df_vol['NOMINAL (TRILIUN)'].max() if not df_vol.empty else 1
        fig1.update_xaxes(range=[0, max_vol * 1.25])
        
        colors1 = ['#bfdbfe'] * min(6, len(df_vol)-1) + ['#1e3a5f'] if len(df_vol) > 0 else ['#1e3a5f']
        
        fig1.update_traces(marker_color=colors1, width=0.6, texttemplate='<b>%{x:,.1f} T</b>', textposition='outside', textfont=dict(color="#0f172a"), cliponaxis=False)
        fig1.update_yaxes(type='category', tickfont=dict(color="#0f172a", size=11)) 
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

lender_counts_real = df.groupby('SANDI CASH BORROWER (Masked)')['SANDI CASH LENDER (Masked)'].nunique()
small_borrowers_real = lender_counts_real[lender_counts_real <= 2].index
df_inklusif = df[df['SANDI CASH BORROWER (Masked)'].isin(small_borrowers_real)].groupby('SANDI CASH LENDER (Masked)')['SANDI CASH BORROWER (Masked)'].nunique().reset_index()
df_inklusif.columns = ['LENDER', 'Score']
df_inklusif['LENDER'] = df_inklusif['LENDER'].astype(str).str.strip()
df_inklusif = df_inklusif[df_inklusif['LENDER'].isin(DAFTAR_DU_RESMI)]
df_inklusif = df_inklusif.sort_values('Score', ascending=True).tail(7)

with col_chart2:
    with st.container(border=True): 
        st.markdown(f"""
        <div style='color: #0f172a; font-weight: 700; font-size: 15px; margin-bottom: 10px; display: flex; align-items: center; gap: 8px;'>
            <img src="{ICON_INKLUSIF_URL}&width={ICON_INKLUSIF_SIZE}&height={ICON_INKLUSIF_SIZE}" style="flex-shrink: 0;">
            Apresiasi Inklusivitas Transaksi Dealer Utama
        </div>
        """, unsafe_allow_html=True)
        
        fig2 = px.bar(df_inklusif, x="Score", y="LENDER", orientation='h')
        fig2.update_layout(**CHART_BASE)
        
        max_score = df_inklusif['Score'].max() if not df_inklusif.empty else 1
        if pd.isna(max_score): max_score = 1
        fig2.update_xaxes(range=[0, max_score * 1.25])
        
        colors2 = ['#bfdbfe'] * min(6, len(df_inklusif)-1) + ['#1e3a5f'] if len(df_inklusif) > 0 else ['#1e3a5f']
        
        fig2.update_traces(marker_color=colors2, width=0.6, texttemplate='<b>%{x}</b>', textposition='outside', textfont=dict(color="#0f172a"), cliponaxis=False)
        fig2.update_yaxes(type='category', tickfont=dict(color="#0f172a", size=11)) 
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

# ==========================================
# 10. PETA JARINGAN EKOSISTEM (KOTAK PUTIH NORMAL)
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
        st.markdown("<div style='color: #0f172a; font-size: 13px; font-weight: 500; margin-bottom: 15px;'>Biru Tua = DU &nbsp;&nbsp;|&nbsp;&nbsp; Biru Muda = Bank Non DU &nbsp;&nbsp;|&nbsp;&nbsp; Jingga = Lembaga Non-Bank</div>", unsafe_allow_html=True)

    required_cols = ['SANDI CASH LENDER (Masked)', 'SANDI CASH BORROWER (Masked)']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"Data tidak lengkap untuk membuat Network Graph. Kolom berikut tidak ditemukan di periode ini: {', '.join(missing_cols)}")
    else:
        with col_filter_net:
            # Penggabungan Pandas yang sudah diperbaiki total dari typo kurung siku
            all_banks = pd.concat([df['SANDI CASH LENDER (Masked)'], df['SANDI CASH BORROWER (Masked)']]).dropna().unique()
            all_banks_sorted = sorted([str(b) for b in all_banks])
            
            st.write("") 
            selected_bank = st.selectbox(
                "Filter Bank", 
                ["Semua Bank"] + all_banks_sorted, 
                label_visibility="collapsed"
            )

        df_edges = df[['SANDI CASH LENDER (Masked)', 'SANDI CASH BORROWER (Masked)']].drop_duplicates()
        df_edges['SANDI CASH LENDER (Masked)'] = df_edges['SANDI CASH LENDER (Masked)'].astype(str)
        df_edges['SANDI CASH BORROWER (Masked)'] = df_edges['SANDI CASH BORROWER (Masked)'].astype(str)
        
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

            node_x, node_y, node_color, node_size, node_hover_text = [], [], [], [], []
            
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x); node_y.append(y)
                
                node_str = str(node)
                status = status_dict.get(node_str, 'NON DU')
                
                if status == 'DU':
                    node_color.append('#1e3a5f') 
                    node_size.append(26 if node_str == selected_bank else 14)
                    
                    du_trans = int(compliance_check.loc[node_str, 'DU']) if node_str in compliance_check.index else 0
                    non_du_trans = int(compliance_check.loc[node_str, 'NON DU']) if node_str in compliance_check.index else 0
                    
                    if (node_str in compliance_check.index and compliance_check.loc[node_str, 'Patuh']):
                        is_patuh = "✅ PATUH"
                    else:
                        is_patuh = "❌ TIDAK PATUH"
                    
                    node_hover_text.append(
                        f"<b>Bank DU: {node_str}</b><br>"
                        f"Status: {is_patuh}<br>"
                        f"Transaksi DU: {du_trans} (Min. 5)<br>"
                        f"Transaksi Non-DU: {non_du_trans} (Min. 5)"
                    )
                    
                elif status == 'NON BANK':
                    node_color.append('#f59e0b') 
                    node_size.append(26 if node_str == selected_bank else 12)
                    node_hover_text.append(f"<b>Lembaga Non-Bank: {node_str}</b>")
                else:
                    node_color.append('#0ea5e9') 
                    node_size.append(26 if node_str == selected_bank else 12) 
                    node_hover_text.append(f"<b>Bank Non-DU: {node_str}</b>")

            line_colors = ['#f59e0b' if str(node) == selected_bank else 'white' for node in G.nodes()]
            line_widths = [3 if str(node) == selected_bank else 1 for node in G.nodes()]

            node_trace = go.Scatter(
                x=node_x, y=node_y, mode='markers+text',
                hoverinfo='text',  
                text=list(G.nodes()), 
                hovertext=node_hover_text,
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
