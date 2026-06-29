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
# 2. CSS PALING AMAN (FOKUS PADA VISIBILITAS)
# ==========================================
st.markdown("""
<style>
/* 1. HAPUS HEADER BAWAAN STREAMLIT */
[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }

/* 2. LEBARKAN KONTEN & HAPUS BACKGROUND YANG BIKIN ERROR */
.block-container {
    max-width: 100% !important; 
    padding-top: 1rem !important;
    padding-bottom: 3rem !important;
    padding-left: 3rem !important; 
    padding-right: 3rem !important; 
}
.stApp { background-color: #f8fafc !important; }

/* 3. DESAIN KARTU ANGKA (METRIC) */
[data-testid="metric-container"] {
    background-color: #ffffff !important;
    border-radius: 12px !important;
    border-top: 4px solid #1e3a5f !important;
    padding: 20px !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
}
[data-testid="metric-container"] label {
    color: #64748b !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    color: #0f172a !important;

    font-size: 26px !important;
    font-weight: 800 !important;
}

/* 4. DESAIN KARTU GRAFIK & NETWORK */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #ffffff !important;
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.03) !important;
    padding: 15px !important;
}

/* 5. CUSTOM NAVBAR - WARNA TEKS DIBUAT GELAP UTAMA AGAR TERBACA */
.nav-container {
    display: flex; justify-content: space-between; align-items: center;
    padding-bottom: 25px; font-family: 'Inter', sans-serif;
    border-bottom: 1px solid #e2e8f0; margin-bottom: 25px;
}
.nav-logo { display: flex; align-items: center; gap: 15px; }
.nav-logo-icon { background: #eff6ff; color: #1e3a5f; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; border-radius: 10px; font-size: 20px; }
.nav-title { font-weight: 800; font-size: 16px; color: #0f172a; letter-spacing: 0.5px; margin-bottom: 2px;}
.nav-subtitle { font-size: 12px; color: #64748b; font-weight: 500; }
.nav-menu { display: flex; gap: 8px; background: #f1f5f9; padding: 6px; border-radius: 10px; }
.nav-item { padding: 6px 16px; font-size: 13px; font-weight: 600; color: #0f172a; border-radius: 6px; cursor: pointer; }
.nav-item.active { background: #ffffff; color: #1e3a5f; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.nav-profile-name { font-size: 13px; font-weight: 700; color: #0f172a; }
.nav-profile-role { font-size: 11px; color: #64748b; font-weight: 500; }

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. HTML NAVBAR CUSTOM (TEKS GELAP)
# ==========================================
st.markdown("""
<div class="nav-container">
    <div class="nav-logo">
        <div class="nav-logo-icon">💠</div>
        <div>
            <div class="nav-title">SUPERVISION DASHBOARD</div>
            <div class="nav-subtitle">Bank Indonesia • DPPK / PUVA</div>
        </div>
    </div>
    <div class="nav-menu">
        <div class="nav-item active">Dashboard</div>
        <div class="nav-item">SRBI</div>
        <div class="nav-item">DNDF</div>
        <div class="nav-item">OIS</div>
    </div>
    <div style="display: flex; align-items: center; gap: 20px;">
        <span style="font-size: 18px; cursor: pointer;">🔔</span>
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="background: #e2e8f0; color: #1e3a5f; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">👤</div>
            <div>
                <div class="nav-profile-name">Admin BI</div>
                <div class="nav-profile-role">Supervisor PUVA</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 4. FUNGSI LOAD DATA EXCEL (MEMBACA SEMUA SHEET)
# ==========================================
@st.cache_data
def load_excel_data():
    filename = "Data Repo - Masked .xlsx"
    try:
        xls = pd.ExcelFile(filename)
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
                
            sheets_dict[sheet_name] = df
        return sheets_dict
    except Exception as e:
        st.error(f"Gagal memuat Excel: {e}")
        return None

sheets_data = load_excel_data()


# ==========================================
# 5. HERO TEXT (DINAMIS DARI TANGGAL TRANSAKSI)
# ==========================================
# Pastikan kolom tanggal diformat sebagai datetime
df['TANGGAL TRANSAKSI'] = pd.to_datetime(df['TANGGAL TRANSAKSI'])
min_date = df['TANGGAL TRANSAKSI'].min().strftime('%d %b %Y')
max_date = df['TANGGAL TRANSAKSI'].max().strftime('%d %b %Y')

col_hero, col_filter = st.columns([4, 1])

with col_hero:
    st.markdown(f"""
    <div style="font-family: 'Inter', sans-serif;">
        <h1 style="margin-bottom: 5px; font-size: 28px; font-weight: 800; color: #0f172a;">Dashboard Pimpinan</h1>
        <p style="font-size: 13px; color: #64748b; font-weight: 500; margin-top: 0;">Periode Data: {min_date} s.d. {max_date}</p>
    </div>
    """, unsafe_allow_html=True)

with col_filter:
    st.write("") 
    selected_period = st.selectbox("Periode", daftar_periode, label_visibility="collapsed")

# ==========================================
# 6. PERHITUNGAN KPI (BARU)
# ==========================================
total_volume_t = df['NOMINAL (FULL AMOUNT)'].sum() / 1e12

# Hitung Kepatuhan
cp_stats = df.groupby(['SANDI CASH LENDER (Masked)', 'STATUS PD CASH BORROWER'])['SANDI CASH BORROWER (Masked)'].nunique().unstack(fill_value=0)
if 'DU' not in cp_stats.columns: cp_stats['DU'] = 0
if 'NON DU' not in cp_stats.columns: cp_stats['NON DU'] = 0
cp_stats['Patuh'] = (cp_stats['DU'] >= 5) & (cp_stats['NON DU'] >= 5)

total_lenders = len(cp_stats)
lender_patuh_count = cp_stats['Patuh'].sum()
avg_kepatuhan = (lender_patuh_count / total_lenders) * 100 if total_lenders > 0 else 0
jumlah_bermasalah = total_lenders - lender_patuh_count

# ==========================================
# 7. KPI CARDS & HALF DONUT CHART
# ==========================================
# Kita buat 4 kolom: 1 untuk chart, 3 untuk metric
c_chart, c1, c2, c3 = st.columns([1, 1, 1, 1])

# A. Half Donut Chart untuk Komposisi DU/Non-DU
with c_chart:
    st.markdown("<div style='font-size: 12px; font-weight: 700; color: #64748b; margin-bottom: 5px;'>KOMPOSISI BANK</div>", unsafe_allow_html=True)
    fig_donut = go.Figure(data=[go.Pie(
        labels=['DU', 'Non DU'], 
        values=[21, 84], 
        hole=.6,
        marker_colors=['#1e3a5f', '#bfdbfe'],
        rotation=90,
        direction='clockwise',
        sort=False
    )])
    fig_donut.update_layout(height=120, margin=dict(t=0, b=0, l=0, r=0), showlegend=False)
    # Trik "Half Donut" dengan menyembunyikan bagian bawah
    fig_donut.update_traces(textinfo='none') 
    st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})

# B. Sisa Metrics
c1.metric("Total Volume DU", f"Rp {total_volume_t:.2f} T")
c2.metric("Rata-rata Kepatuhan", f"{avg_kepatuhan:.1f}%")
c3.metric("Bank Tidak Patuh", f"{jumlah_bermasalah} Bank")

# ==========================================
# 8. CHARTS
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
        st.markdown("<div style='color: #0f172a; font-weight: 700; font-size: 15px; margin-bottom: 10px;'>🏆 Bank dengan Volume Transaksi Terbesar (Triliun Rp)</div>", unsafe_allow_html=True)
        
        fig1 = px.bar(df_vol, x="NOMINAL (TRILIUN)", y="SANDI CASH LENDER (Masked)", orientation='h')
        fig1.update_layout(**CHART_BASE)
        colors1 = ['#bfdbfe'] * 6 + ['#1e3a5f']
        
        fig1.update_traces(marker_color=colors1, width=0.6, texttemplate='<b>%{x:,.1f} T</b>', textposition='outside', textfont=dict(color="#0f172a"))
        fig1.update_yaxes(type='category', tickfont=dict(color="#0f172a", size=11)) 
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

lender_counts_real = df.groupby('SANDI CASH BORROWER (Masked)')['SANDI CASH LENDER (Masked)'].nunique()
small_borrowers_real = lender_counts_real[lender_counts_real <= 2].index
df_inklusif = df[df['SANDI CASH BORROWER (Masked)'].isin(small_borrowers_real)].groupby('SANDI CASH LENDER (Masked)')['SANDI CASH BORROWER (Masked)'].nunique().reset_index()
df_inklusif.columns = ['LENDER', 'Score']
df_inklusif = df_inklusif.sort_values('Score', ascending=True).tail(7)

with col_chart2:
    with st.container(border=True):
        st.markdown("<div style='color: #0f172a; font-weight: 700; font-size: 15px; margin-bottom: 10px;'>🌐 Apresiasi Inklusivitas Transaksi (Risk-Taking)</div>", unsafe_allow_html=True)
        
        fig2 = px.bar(df_inklusif, x="Score", y="LENDER", orientation='h')
        fig2.update_layout(**CHART_BASE)
        colors2 = ['#bfdbfe'] * 6 + ['#1e3a5f']
        
        fig2.update_traces(marker_color=colors2, width=0.6, texttemplate='<b>%{x}</b>', textposition='outside', textfont=dict(color="#0f172a"))
        fig2.update_yaxes(type='category', tickfont=dict(color="#0f172a", size=11)) 
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})



# ==========================================
# 9. NETWORK GRAPH (LOGIKA PEWARNAAN BERDASARKAN KOLOM STATUS)
# ==========================================
st.write("")
with st.container(border=True):
    # Membagi area atas menjadi dua kolom: Kiri untuk Judul, Kanan untuk Filter
    col_title, col_filter = st.columns([3, 1])
    
    with col_title:
        st.markdown("<div style='color: #0f172a; font-weight: 700; font-size: 16px; margin-bottom: 5px;'>🕸️ Peta Jaringan Transaksi Ekosistem Repo</div>", unsafe_allow_html=True)
        st.markdown("<div style='color: #0f172a; font-size: 13px; font-weight: 500; margin-bottom: 15px;'>Biru Tua = DU &nbsp;&nbsp;|&nbsp;&nbsp; Biru Muda = Non DU</div>", unsafe_allow_html=True)

    with col_filter:
        # 1. Ambil daftar semua bank unik
        all_banks = pd.concat([df['SANDI CASH LENDER (Masked)'], df['SANDI CASH BORROWER (Masked)']]).dropna().unique()
        all_banks_sorted = sorted(list(all_banks))
        
        # 2. Dropdown ditaruh di sini dengan label yang disembunyikan (collapsed)
        st.write("") # Sedikit spasi agar sejajar dengan judul
        selected_bank = st.selectbox(
            "Filter Bank", 
            ["Semua Bank"] + all_banks_sorted, 
            label_visibility="collapsed"
        )
    
    # 3. Buat pemetaan status bank (ID Bank -> Status)
    lender_map = df[['SANDI CASH LENDER (Masked)', 'STATUS DU CASH LENDER']].rename(
        columns={'SANDI CASH LENDER (Masked)': 'ID_BANK', 'STATUS DU CASH LENDER': 'STATUS'}
    )
    borrower_map = df[['SANDI CASH BORROWER (Masked)', 'STATUS PD CASH BORROWER']].rename(
        columns={'SANDI CASH BORROWER (Masked)': 'ID_BANK', 'STATUS PD CASH BORROWER': 'STATUS'}
    )
    all_mapping = pd.concat([lender_map, borrower_map])
    all_mapping['STATUS'] = all_mapping['STATUS'].astype(str).str.upper().str.strip().replace('NON-DU', 'NON DU')
    
    # Jika bank punya status DU, maka labelnya DU
    bank_status_dict = all_mapping.groupby('ID_BANK')['STATUS'].apply(lambda x: 'DU' if 'DU' in x.values else 'NON DU').to_dict()

    # 4. Ambil semua relasi unik
    df_edges = df[['SANDI CASH LENDER (Masked)', 'SANDI CASH BORROWER (Masked)']].drop_duplicates()
    
    # --- LOGIKA FILTERING ---
    if selected_bank != "Semua Bank":
        df_edges = df_edges[
            (df_edges['SANDI CASH LENDER (Masked)'] == selected_bank) | 
            (df_edges['SANDI CASH BORROWER (Masked)'] == selected_bank)
        ]

    if df_edges.empty:
        st.info(f"Tidak ada transaksi untuk {selected_bank} pada periode ini.")
    else:
        # 5. Buat Graph
        G = nx.from_pandas_edgelist(df_edges, 'SANDI CASH LENDER (Masked)', 'SANDI CASH BORROWER (Masked)')
        
        pos = nx.spring_layout(G, seed=42, k=0.15)

        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#cbd5e1'), hoverinfo='none', mode='lines')

        # 6. Pewarnaan dan Ukuran Node
        node_x, node_y, node_color, node_size = [], [], [], []
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
