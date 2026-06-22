import os
import streamlit as st
from dotenv import load_dotenv

# Memuat berkas konfigurasi .env
load_dotenv(override=True)

# Konfigurasi halaman Streamlit wajib diletakkan di bagian paling atas
st.set_page_config(
    page_title="OtoCerdas AI - Asisten Otomotif Cerdas",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Impor pustaka internal setelah konfigurasi halaman
from core.graph import graph_app
from core.llm_manager import format_chat_history, llm_instance
from langchain_core.messages import HumanMessage, AIMessage

st.markdown("""
<style>
    /* Google Fonts Outfit */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Gaya Latar Belakang Aplikasi */
    .stApp {
        background-color: #0b0d10;
        color: #e2e8f0;
    }
    
    /* Gaya Header & Banner */
    .header-container {
        background: linear-gradient(135deg, #161a22 0%, #0b0d10 100%);
        padding: 30px;
        border-radius: 16px;
        border-bottom: 4px solid #d4af37; /* Emas */
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    
    /* Card Bertema Gelap */
    .custom-card {
        background-color: #161a22;
        border: 1px solid #232a35;
        border-left: 5px solid #d4af37; /* Default Aksen Emas */
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    
    .custom-card-red {
        background-color: #161a22;
        border: 1px solid #232a35;
        border-left: 5px solid #ff3333; /* Aksen Merah */
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }

    /* Badge Klasifikasi */
    .category-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85em;
        text-transform: uppercase;
        color: #ffffff;
        margin-bottom: 10px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #07090c !important;
        border-right: 1px solid #1a202c;
    }
    
    /* Tombol */
    .stButton>button {
        background: linear-gradient(90deg, #d4af37 0%, #b89626 100%) !important;
        color: #0b0d10 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# Menyimpan riwayat percakapan agar dapat digunakan oleh LangChain Memory dan diumpankan ke LangGraph.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Saya adalah **OtoCerdas AI**, Asisten Otomotif Cerdas Anda. Ada yang bisa saya bantu hari ini? Anda bisa berkonsultasi seputar servis kendaraan, spesifikasi mobil, rekomendasi pembelian, atau diagnosis masalah mekanis kendaraan."}
    ]

st.markdown("""
<div class="header-container">
    <h1 style="margin: 0; font-size: 2.8em; font-weight: 800; color: #ffffff; letter-spacing: 1px;">
        🏎️ OTO-CERDAS <span style="color: #d4af37;">AI</span>
    </h1>
    <p style="margin: 5px 0 0 0; font-size: 1.1em; color: #a0aec0;">
        Asisten Otomotif Pintar berbasis NLP/LLM dengan Integrasi <b>LangChain</b>, <b>LangGraph</b>, dan <b>LangSmith</b>.
    </p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h2 style='color: #d4af37;'>⚙️ Sistem Monitor</h2>", unsafe_allow_html=True)
    
    # Deteksi status model provider
    provider_name = os.getenv("MODEL_PROVIDER", "openai").upper()
    st.info(f" **Model Provider:** `{provider_name}`")
    
    # Deteksi Kunci API
    openai_active = len(os.getenv("OPENAI_API_KEY", "")) > 5
    google_active = len(os.getenv("GOOGLE_API_KEY", "")) > 5
    
    if (provider_name == "OPENAI" and openai_active) or (provider_name == "GOOGLE" and google_active):
        st.success("✅ **Status LLM:** API Key Terhubung")
    else:
        st.warning("⚠️ **Status LLM:** Mode Simulasi (Fallback)")
        
    # Status LangSmith Tracing
    tracing_active = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    langsmith_key_active = len(os.getenv("LANGCHAIN_API_KEY", "")) > 5
    
    if tracing_active and langsmith_key_active:
        st.success("✅ **LangSmith Tracing:** AKTIF (Terekam)")
        st.markdown(f"[Buka Dashboard LangSmith](https://smith.langchain.com/o/current/projects?find_by_project={os.getenv('LANGCHAIN_PROJECT', 'asisten-otomotif-cerdas')})")
    else:
        st.error("❌ **LangSmith Tracing:** TIDAK AKTIF")
        st.caption("Konfigurasi `LANGCHAIN_API_KEY` di `.env` untuk mengaktifkan tracing dashboard.")

    st.markdown("---")
    st.markdown("<h3 style='color: #ffffff;'>Tentang Integrasi</h3>", unsafe_allow_html=True)
    st.caption(" **LangChain:** Mengatur penyusunan Prompt, model LLM, dan format Memory pesan history.")
    st.caption(" **LangGraph:** Mengklasifikasikan pertanyaan secara otomatis dan merutekannya ke sub-bagian logika khusus.")
    st.caption(" **LangSmith:** Melakukan pelacakan performa, biaya token, dan visualisasi eksekusi node per node.")

    st.markdown("---")
    if st.button("🗑️ Hapus Riwayat Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Halo! Saya adalah **OtoCerdas AI**, Asisten Otomotif Cerdas Anda. Ada yang bisa saya bantu hari ini? Anda bisa berkonsultasi seputar servis kendaraan, spesifikasi mobil, rekomendasi pembelian, atau diagnosis masalah mekanis kendaraan."}
        ]
        st.rerun()

tab_chat, tab_service, tab_trouble = st.tabs([
    " Chatbot Asisten AI", 
    " Rekomendasi Servis", 
    " Diagnosis Troubleshooting"
])

with tab_chat:
    st.write("Silakan ajukan pertanyaan Anda seputar otomotif. LangGraph akan merutekan pertanyaan Anda ke spesialis yang tepat.")
    
    # Render riwayat percakapan dari session state
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Input user
    if user_query := st.chat_input("Tanyakan sesuatu (Contoh: 'Berapa tenaga mesin Honda Civic RS?' atau 'Mengapa setir mobil saya bergetar?')"):
        # Tampilkan input pengguna secara instan
        with st.chat_message("user"):
            st.markdown(user_query)
            
        # Simpan pesan pengguna ke session state
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        # Eksekusi LangGraph secara real-time
        with st.chat_message("assistant"):
            status_container = st.empty()
            response_container = st.empty()
            
            with status_container.container():
                st.markdown("<p style='color: #d4af37;'>🔄 Mengevaluasi pertanyaan menggunakan LangGraph Classifier...</p>", unsafe_allow_html=True)
                
            try:
                # 1. Konversi riwayat ke tipe data pesan LangChain
                langchain_history = format_chat_history(st.session_state.messages[:-1])
                
                # 2. Siapkan state awal LangGraph
                input_state = {
                    "question": user_query,
                    "history": langchain_history,
                    "category": "",
                    "reference_data": "",
                    "response": ""
                }
                
                # 3. Jalankan compiled graph. Eksekusi ini secara otomatis dikirimkan ke LangSmith (jika diaktifkan)
                output_state = graph_app.invoke(input_state)
                
                # 4. Ambil hasil olahan graf
                category = output_state.get("category", "general")
                response = output_state.get("response", "Maaf, saya gagal merumuskan respons.")
                
                # Desain visual routing LangGraph
                badge_color = "#3182ce" # Blue for general
                if category == "service":
                    badge_color = "#38a169" # Green
                elif category == "specs":
                    badge_color = "#d69e2e" # Yellow/Gold
                elif category == "recommendation":
                    badge_color = "#805ad5" # Purple
                elif category == "troubleshooting":
                    badge_color = "#e53e3e" # Red
                
                # Visualisasi graf di UI Streamlit
                with status_container.container():
                    st.markdown(f"""
                    <div style="background-color: #161a22; padding: 12px 18px; border-radius: 8px; border: 1px solid #2d3748; margin-bottom: 15px;">
                        <span style="font-weight: bold; color: #a0aec0;">🕸️ Alur Kerja LangGraph:</span>
                        <code style="background-color:#2d3748; padding: 2px 6px; border-radius:4px;">Input</code> ➡️ 
                        <code style="background-color:#2d3748; padding: 2px 6px; border-radius:4px;">classify_node</code> ➡️ 
                        <span style="background-color: {badge_color}; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.9em;">
                            {category.upper()}_NODE
                        </span> ➡️ 
                        <code style="background-color:#2d3748; padding: 2px 6px; border-radius:4px;">Output</code>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Tampilkan respons teks akhir
                response_container.markdown(response)
                
                # Simpan respons asisten ke session state
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                status_container.empty()
                response_container.error(f"Terjadi kesalahan saat memproses permintaan: {str(e)}")

with tab_service:
    st.markdown("<h3 style='color:#d4af37;'>📅 Jadwal Servis & Perawatan Berkala</h3>", unsafe_allow_html=True)
    st.write("Dapatkan rekomendasi jadwal servis kendaraan secara prosedural berdasarkan tipe kendaraan dan odometer Anda.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("##### Input Data Kendaraan")
        car_type = st.selectbox(
            "Tipe Kendaraan",
            options=["Sedan / Hatchback (Bensin)", "SUV / MPV (Bensin/Diesel)", "EV / Mobil Listrik"],
            index=0
        )
        
        car_model = st.text_input("Merek & Model Mobil", placeholder="Contoh: Toyota Avanza, Hyundai Ioniq 5")
        car_year = st.number_input("Tahun Pembuatan", min_value=1990, max_value=2027, value=2022)
        odometer = st.number_input("Odometer Saat Ini (KM)", min_value=0, max_value=1000000, value=25000, step=5000)
        
        btn_service = st.button("Jadwal Perawatan Saya")
        
    with col2:
        if btn_service:
            if not car_model:
                st.warning("Masukkan Merek & Model Mobil terlebih dahulu.")
            else:
                with st.spinner("Menganalisis data perawatan..."):
                    # Terjemahkan tipe ke kunci input model
                    car_type_key = "sedan_hatchback"
                    if "SUV" in car_type:
                        car_type_key = "suv_mpv"
                    elif "EV" in car_type:
                        car_type_key = "ev"
                        
                    # Buat query untuk diumpankan ke LangGraph
                    query = f"Berikan rekomendasi servis berkala untuk mobil {car_model} tipe {car_type} tahun {car_year} dengan kilometer saat ini {odometer} KM."
                    
                    # Force category ke service agar LangGraph langsung mengeksekusi service_node
                    input_state = {
                        "question": query,
                        "history": [],
                        "category": "service",
                        "reference_data": "",
                        "response": ""
                    }
                    
                    # Jalankan graph secara terisolasi (bypass classify node demi presisi tab formulir)
                    # Kami menggunakan workflow graph_app tapi menyimulasikan state input
                    output_state = graph_app.invoke(input_state)
                    
                    # Render visualisasi hasil dalam card bertema emas
                    st.markdown(f"""
                    <div class="custom-card">
                        <h4 style="color:#d4af37; margin-top:0;">📋 Jadwal Perawatan Rekomendasi untuk {car_model} ({car_year})</h4>
                        <p style="color:#a0aec0; font-size:0.95em;">
                            Tipe Mobil: <b>{car_type}</b> | Odometer: <b>{odometer:,} KM</b>
                        </p>
                        <hr style="border-color:#232a35;" />
                        <div>
                            {output_state['response']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Masukkan detail mobil Anda di panel kiri dan klik tombol untuk menampilkan rekomendasi servis.")

with tab_trouble:
    st.markdown("<h3 style='color:#ff3333;'>🛠️ Diagnosis Cepat Gejala Masalah Mobil</h3>", unsafe_allow_html=True)
    st.write("Identifikasi kemungkinan kerusakan pada mobil Anda berdasarkan gejala fisik yang dirasakan/didengar.")
    
    col_t1, col_t2 = st.columns([1, 2])
    
    with col_t1:
        st.markdown("##### Pilih Gejala Masalah")
        symptom_preset = st.selectbox(
            "Pilih Gejala Utama",
            options=[
                "Mesin Sulit Dinyalakan (Starter Lambat/Bunyi Tek-tek)",
                "Mesin Mengalami Overheat (Temperatur Sangat Tinggi)",
                "Setir Bergetar Hebat pada Kecepatan Tinggi",
                "Rem Mengeluarkan Bunyi Berdecit Saat Diinjak",
                "Input Gejala Lainnya secara Manual..."
            ],
            index=0
        )
        
        manual_symptom = ""
        if symptom_preset == "Input Gejala Lainnya secara Manual...":
            manual_symptom = st.text_area(
                "Detail Gejala yang Dirasakan", 
                placeholder="Contoh: Knalpot mengeluarkan asap hitam pekat dan tenaga mesin terasa hilang saat menanjak..."
            )
            
        btn_diagnose = st.button("Jalankan Diagnosa Kerusakan")
        
    with col_t2:
        if btn_diagnose:
            selected_symptom = manual_symptom if symptom_preset == "Input Gejala Lainnya secara Manual..." else symptom_preset
            
            if not selected_symptom:
                st.warning("Mohon sebutkan detail gejala kerusakan secara manual terlebih dahulu.")
            else:
                with st.spinner("Menganalisis gejala kerusakan..."):
                    # Buat query analisis
                    query = f"Saya mengalami masalah kendaraan berikut: {selected_symptom}. Tolong jelaskan kemungkinan penyebab dan solusinya."
                    
                    # Force category ke troubleshooting agar LangGraph memicu troubleshooting_node
                    input_state = {
                        "question": query,
                        "history": [],
                        "category": "troubleshooting",
                        "reference_data": "",
                        "response": ""
                    }
                    
                    # Jalankan alur graf
                    output_state = graph_app.invoke(input_state)
                    
                    # Render visualisasi hasil dalam card bertema merah (indikasi bahaya/peringatan mekanis)
                    st.markdown(f"""
                    <div class="custom-card-red">
                        <h4 style="color:#ff3333; margin-top:0;">⚠️ Hasil Analisis Kerusakan & Troubleshooting</h4>
                        <p style="color:#a0aec0; font-size:0.95em;">
                            Gejala Terdeteksi: <b>{selected_symptom}</b>
                        </p>
                        <hr style="border-color:#232a35;" />
                        <div>
                            {output_state['response']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Pilih gejala kerusakan di panel kiri dan klik tombol untuk menjalankan diagnosis AI.")
