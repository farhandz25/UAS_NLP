# 🏎️ OtoCerdas AI: Asisten Otomotif Cerdas

OtoCerdas AI adalah sistem asisten otomotif berbasis kecerdasan buatan (NLP/LLM) yang dirancang untuk menjawab pertanyaan umum kendaraan, merumuskan jadwal perawatan berkala, serta melakukan diagnosis mandiri keluhan mesin (*troubleshooting*). Proyek ini dibuat untuk mendemonstrasikan integrasi nyata tiga pustaka utama dari ekosistem LangChain: **LangChain**, **LangGraph**, dan **LangSmith** dengan antarmuka web Streamlit bertema gelap premium.

---

## 📸 Tampilan Aplikasi (Web Interface)
![OtoCerdas AI Dark Dashboard Placeholder](https://images.unsplash.com/photo-1486006920555-c77dce18193b?auto=format&fit=crop&w=1200&q=80)
*Catatan: Antarmuka web Streamlit dirancang dengan palet warna hitam dan abu-abu gelap dengan aksen premium emas (#d4af37) dan merah (#ff3333) untuk memberikan estetika otomotif sport yang elegan.*

---

## ✨ Fitur Utama

1. **💬 Chatbot Otomotif dengan State Router**: 
   Chatbot interaktif yang mengenali maksud obrolan Anda dan secara otomatis mengarahkannya ke node spesialisasi (servis, spesifikasi kendaraan, rekomendasi, diagnosis kerusakan). Status routing LangGraph divisualisasikan secara langsung kepada pengguna di antarmuka obrolan.
2. **📅 Rekomendasi Servis & Perawatan**: 
   Formulir input data kendaraan (Model, Tahun, Odometer) yang menghasilkan panduan servis berkala berdasarkan kilometer kendaraan menggunakan data referensi terintegrasi.
3. **🛠️ Diagnosis Gejala Kerusakan (Troubleshooting)**: 
   Sistem penilai tingkat bahaya dan penyedia solusi mandiri atas gejala kerusakan fisik mobil yang dirasakan (starter sulit, mesin overheat, setir getar, rem berdecit, dll).
4. **📈 Pelacakan Alur Sistem (LangSmith Tracing)**: 
   Setiap interaksi obrolan, klasifikasi, dan pembuatan respons dipetakan langkah-demi-langkah ke dashboard monitoring LangSmith secara otomatis.

---

## 📁 Struktur Folder Proyek

```text
/Users/farhandz/Desktop/ UIR/UAS/
├── .env.example            # Contoh variabel lingkungan
├── .env                    # Variabel lingkungan aktif (API Keys)
├── requirements.txt        # Daftar dependensi Python
├── README.md               # Dokumentasi utama (berkas ini)
├── app.py                  # Antarmuka web utama (Streamlit Dashboard)
└── core/                   # Logika inti sistem AI
    ├── __init__.py         # Inisialisasi paket Python
    ├── knowledge_base.py   # Database lokal (Spesifikasi, Jadwal Servis, Gejala Kerusakan)
    ├── llm_manager.py      # Pengaturan LLM, Prompts, & Memory (LangChain)
    └── graph.py            # Workflow State Graph & Logika Routing (LangGraph)
```

---

## ⚙️ Integrasi Nyata Tiga Library Wajib

Aplikasi ini mendemonstrasikan penggunaan nyata ketiga library secara mendalam:

### 1. LangChain (Logika Prompt, LLM, dan Memory)
*   **Prompt Templates**: Mendefinisikan template instruksi asisten yang disesuaikan untuk masing-masing spesialisasi (`SERVICE_PROMPT`, `SPECS_PROMPT`, dll) dalam [core/llm_manager.py](file:///Users/farhandz/Desktop/%20UIR/UAS/core/llm_manager.py).
*   **LLM Model Initialization**: Menghubungkan engine LLM dari penyedia OpenAI (`ChatOpenAI`) atau Google Gemini (`ChatGoogleGenerativeAI`) dengan fallback berupa simulasi Mock LLM jika API Key kosong.
*   **LangChain Expression Language (LCEL)**: Menyusun alur prompt-to-model menggunakan operator pipe: `prompt | llm | StrOutputParser()`.
*   **Memory Formatting**: Membaca riwayat pesan dari session state UI Streamlit dan memformatnya menjadi deretan `HumanMessage` dan `AIMessage` agar dimengerti LLM.

### 2. LangGraph (Workflow Graph & Dynamic Routing)
*   **State Definition**: Menggunakan `TypedDict` untuk mendefinisikan objek `AgentState` yang membawa pesan, klasifikasi kategori, data referensi, dan hasil respons akhir melintasi node di [core/graph.py](file:///Users/farhandz/Desktop/%20UIR/UAS/core/graph.py).
*   **Nodes**: Mengatur pemrosesan modular dengan mendefinisikan fungsi node: `classify_node`, `service_node`, `specs_node`, `recommendation_node`, `troubleshooting_node`, dan `general_node`.
*   **Conditional Edges**: Menggunakan fungsi router `route_query` untuk mengevaluasi kategori teks pengguna hasil klasifikasi dan mengarahkannya secara dinamis ke node penanganan yang sesuai sebelum selesai (`END`).

### 3. LangSmith (Tracing & Telemetry)
*   **Automatic Configuration**: Cukup dengan memuat variabel lingkungan (`LANGCHAIN_TRACING_V2=true` dan `LANGCHAIN_API_KEY`) di file `.env`, semua rantai interaksi LLM LangChain dan alur graf LangGraph langsung dipetakan ke dalam bagan performa di platform LangSmith.
*   **Trace Monitoring**: Dapat memantau biaya token, latensi waktu respons per node, serta melacak di mana node percakapan bercabang secara visual.

---

## 🚀 Petunjuk Instalasi & Cara Menjalankan

### Prerequisites
*   Python 3.9 atau versi di atasnya.
*   Koneksi internet (untuk mengunduh pustaka dan melakukan panggilan API LLM).

### Langkah 1: Kloning / Salin File Proyek
Pastikan file-file proyek Anda sudah tersusun di dalam folder workspace:
`/Users/farhandz/Desktop/ UIR/UAS/`

### Langkah 2: Buat & Aktifkan Virtual Environment (Direkomendasikan)
Buka terminal Anda di folder proyek tersebut dan jalankan:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Langkah 3: Instalasi Dependensi
Instal semua modul wajib yang didefinisikan dalam `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Langkah 4: Konfigurasi File Lingkungan (.env)
1. Salin isi berkas `.env.example` ke `.env`:
   ```bash
   cp .env.example .env
   ```
2. Buka `.env` dan masukkan kunci API Anda:
   *   Jika ingin menggunakan OpenAI, atur `MODEL_PROVIDER=openai` dan isi `OPENAI_API_KEY`.
   *   Jika ingin menggunakan Google Gemini, atur `MODEL_PROVIDER=google` dan isi `GOOGLE_API_KEY`.
   *   Untuk pelacakan visual, isi variabel `LANGCHAIN_API_KEY` dari platform LangSmith dan pastikan `LANGCHAIN_TRACING_V2=true`.
   *(Jika Anda tidak memasukkan kunci API apa pun, aplikasi akan otomatis beralih ke **Mode Simulasi (Mock LLM)** sehingga Anda tetap dapat menelusuri alur kerja UI).*

### Langkah 5: Jalankan Aplikasi

Terdapat dua cara untuk menjalankan aplikasi ini:

#### Cara 1: Menggunakan VS Code (Rekomendasi & Sangat Mudah)
Kami telah menyediakan konfigurasi otomatis untuk VS Code di dalam folder `.vscode/`:
1. Buka folder proyek ini di VS Code.
2. Buka panel **Run and Debug** (klik ikon play/kumbang di sidebar kiri atau tekan `Ctrl+Shift+D` / `Cmd+Shift+D`).
3. Pilih opsi **"Python: Streamlit (OtoCerdas AI)"** dari dropdown di bagian atas.
4. Tekan tombol **Play (Hijau)** atau tombol **F5**.
5. VS Code akan otomatis menggunakan virtual environment (`venv`) dan menjalankan server Streamlit dengan aman.

#### Cara 2: Menjalankan manual lewat Terminal
Luncurkan server Streamlit secara lokal menggunakan virtual environment interpreter:
```bash
./venv/bin/streamlit run app.py
```
Aplikasi web secara otomatis akan terbuka di peramban Anda pada alamat default: `http://localhost:8501`.
# UAS_NLP
