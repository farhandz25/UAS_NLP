# 🏎️ OtoCerdas AI: Asisten Otomotif Cerdas

Sistem chatbot berbasis Large Language Model (LLM) untuk membantu memberikan rekomendasi servis berkala, pencarian spesifikasi detail, serta diagnosis mandiri gejala kerusakan mesin kendaraan (troubleshooting) secara cerdas. Proyek ini dibuat sebagai pemenuhan tugas Ujian Akhir Semester mata kuliah Natural Language Processing, dengan implementasi tiga library wajib: **LangChain**, **LangGraph**, dan **LangSmith**.

Aplikasi ini dibalut dengan antarmuka web Streamlit bertema gelap premium dengan aksen warna hitam-emas (#d4af37) dan merah (#ff3333) untuk memberikan estetika otomotif sport yang elegan.

---

## Daftar Isi
- [Gambaran Umum](#gambaran-umum)
- [Fitur](#fitur)
- [Arsitektur Sistem](#arsitektur-sistem)
- [Peran LangChain, LangGraph, dan LangSmith](#peran-langchain-langgraph-dan-langsmith)
- [Teknologi yang Digunakan](#teknologi-yang-digunakan)
- [Struktur Proyek](#struktur-proyek)
- [Clone Repository](#clone-repository)
- [Instalasi dan Menjalankan Aplikasi](#instalasi-dan-menjalankan-aplikasi)
- [Tangkapan Layar](#tangkapan-layar)
- [Identitas Mahasiswa](#identitas-mahasiswa)

---

## Gambaran Umum

Aplikasi **OtoCerdas AI** memungkinkan pengguna berkonsultasi dalam bahasa natural mengenai berbagai kebutuhan otomotif, seperti jadwal perawatan berkala, detail spesifikasi teknis mobil, perbandingan rekomendasi kendaraan, hingga diagnosis mandiri saat terjadi masalah pada mobil. 

Sistem menggunakan pendekatan **Rule-based Retrieval Context** yang dikawinkan dengan LLM. Informasi yang diberikan didasarkan pada data referensi lokal otomotif yang akurat dan terstruktur (seperti data spesifikasi Toyota Avanza, Honda Civic RS, Hyundai Ioniq 5, Mitsubishi Pajero Sport, serta tabel anjuran perawatan KM dan daftar diagnosis kerusakan mesin). Jika data tidak terdaftar secara spesifik di database lokal, sistem secara cerdas akan beralih menggunakan pengetahuan umum asisten kecerdasan buatan.

---

## Fitur

1. **💬 Chatbot Otomotif dengan State Router**:
   Ruang obrolan interaktif yang secara otomatis mengklasifikasikan pertanyaan pengguna dan mengarahkannya ke spesialisasi node yang tepat (servis, spesifikasi kendaraan, rekomendasi pembelian, atau diagnosis kerusakan). Status routing LangGraph divisualisasikan secara langsung kepada pengguna di antarmuka obrolan.

2. **📅 Rekomendasi Servis & Perawatan Berkala (Tab Form)**:
   Formulir input data kendaraan (Tipe Mobil, Model, Tahun, Odometer) yang menghasilkan panduan servis berkala berdasarkan kilometer kendaraan secara prosedural menggunakan database referensi terintegrasi.

3. **🛠️ Diagnosis Gejala Kerusakan / Troubleshooting (Tab Form)**:
   Sistem penilai tingkat bahaya (Rendah/Sedang/Tinggi) dan penyedia solusi mandiri atas gejala fisik mobil yang dirasakan (mesin sulit starter, overheat, setir bergetar, rem berdecit, dll).

4. **📈 Pelacakan Alur Sistem (LangSmith Tracing)**:
   Setiap interaksi obrolan, klasifikasi, durasi eksekusi, penggunaan token, dan pembuatan respons dipetakan langkah-demi-langkah ke dashboard monitoring LangSmith secara otomatis.

5. **🌙 Mode Gelap Premium & Aksen Sporty**:
   Antarmuka web dirancang dengan palet warna hitam dan abu-abu gelap dengan aksen emas (#d4af37) dan merah (#ff3333) untuk memberikan estetika otomotif yang premium.

---

## Arsitektur Sistem

```text
┌──────────────────────────────────────────────────────────┐
│                   Streamlit Web UI                       │
│     (Tabs: Chatbot AI, Rekomendasi, Troubleshooting)      │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                 State Graph (LangGraph)                  │
│   - classify_node        - service_node                  │
│   - specs_node           - recommendation_node           │
│   - troubleshooting_node - general_node                  │
└──────────┬───────────────────────┬───────────────────────┘
           │                       │
           ▼                       ▼
┌──────────────────────┐ ┌───────────────────┐
│      LangChain       │ │     LangSmith     │
│   (Prompt & LCEL)    │ │  (Tracing Logs)   │
└──────────┬───────────┘ └───────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────┐
│                  Knowledge Base Lokal                    │
│    (CAR_SPECS, MAINTENANCE, TROUBLESHOOTING_DATA)        │
└──────────────────────────────────────────────────────────┘
```

Pertanyaan pengguna masuk melalui antarmuka Streamlit, diteruskan ke orkestrator **LangGraph** yang menentukan kategori pertanyaan di `classify_node`. Setelah diklasifikasikan, graph mengarahkan ke node pemrosesan spesialis (misal: `service_node` atau `troubleshooting_node`). Node-node tersebut mengambil context relevan dari `core/knowledge_base.py`, lalu menyusun prompt terstruktur menggunakan **LangChain** dan mengirimkannya ke LLM (OpenAI/Gemini/Mock) untuk dirangkai menjadi jawaban akhir. Setiap langkah proses ini direkam oleh **LangSmith** untuk pemantauan dan debugging.

---

## Peran LangChain, LangGraph, dan LangSmith

### 1. LangChain (Logika Prompt, LLM, dan Memory)
* **Prompt Templates**: Mendefinisikan template instruksi asisten yang disesuaikan untuk masing-masing spesialisasi (`SERVICE_PROMPT`, `SPECS_PROMPT`, dll) dalam [core/llm_manager.py](file:///Users/farhandz/Desktop/%20UIR/UAS/core/llm_manager.py).
* **LLM Model Initialization**: Menghubungkan engine LLM dari penyedia OpenAI (`ChatOpenAI`) atau Google Gemini (`ChatGoogleGenerativeAI`) dengan fallback berupa simulasi Mock LLM jika API Key kosong agar aplikasi tetap berjalan.
* **LangChain Expression Language (LCEL)**: Menyusun alur prompt-to-model menggunakan operator pipe: `prompt | llm | StrOutputParser()`.
* **Memory Formatting**: Membaca riwayat pesan dari session state UI Streamlit dan memformatnya menjadi deretan `HumanMessage` dan `AIMessage` agar dimengerti LLM.

### 2. LangGraph (Workflow Graph & Dynamic Routing)
* **State Definition**: Menggunakan `TypedDict` untuk mendefinisikan objek `AgentState` yang membawa pesan, kategori, data referensi, dan hasil respons akhir melintasi node di [core/graph.py](file:///Users/farhandz/Desktop/%20UIR/UAS/core/graph.py).
* **Nodes**: Mengatur pemrosesan modular dengan mendefinisikan fungsi node: `classify_node`, `service_node`, `specs_node`, `recommendation_node`, `troubleshooting_node`, dan `general_node`.
* **Conditional Edges**: Menggunakan fungsi router `route_query` untuk mengevaluasi kategori teks pengguna hasil klasifikasi dan mengarahkannya secara dinamis ke node penanganan yang sesuai sebelum selesai (`END`).

### 3. LangSmith (Tracing & Telemetry)
* **Automatic Configuration**: Dengan memuat variabel lingkungan (`LANGCHAIN_TRACING_V2=true` dan `LANGCHAIN_API_KEY`) di file `.env`, semua rantai interaksi LLM LangChain dan alur graf LangGraph langsung dipetakan ke dalam bagan performa di platform LangSmith secara real-time.
* **Trace Monitoring**: Memantau biaya token, latensi waktu respons per node, serta melacak di mana node percakapan bercabang secara visual.

---

## Teknologi yang Digunakan

| Komponen | Teknologi | Biaya |
| :--- | :--- | :--- |
| **Backend & Frontend** | Python, Streamlit | Gratis (open source) |
| **Orkestrasi LLM** | LangChain, LangGraph | Gratis (open source) |
| **Observability** | LangSmith | Gratis (tier Developer, 5.000 trace/bulan) |
| **Model Bahasa & Embedding** | OpenAI (GPT-4o-mini) atau Gemini (Google AI Studio) | Gratis (Gemini tier free, tanpa kartu kredit) |
| **Database Referensi** | Local Memory Python (knowledge_base) | Gratis (lokal) |
| **Konfigurasi Lingkungan** | python-dotenv | Gratis (open source) |

---

## Struktur Proyek

```text
otocerdas-ai/
├── .streamlit/
│   └── config.toml          # Konfigurasi Streamlit (headless mode, telemetry off, port)
├── .vscode/
│   ├── launch.json          # Konfigurasi Run & Debug VS Code (F5)
│   └── settings.json        # Pengaturan default interpreter python venv
├── core/
│   ├── __init__.py          # Inisialisasi paket Python
│   ├── knowledge_base.py    # Database lokal (Spesifikasi, Jadwal Servis, Gejala Kerusakan)
│   ├── llm_manager.py       # Pengaturan LLM, Prompts, & Memory (LangChain)
│   └── graph.py             # Workflow State Graph & Logika Routing (LangGraph)
├── .env                     # Variabel lingkungan aktif (API Keys)
├── .env.example             # Contoh variabel lingkungan
├── app.py                   # Antarmuka utama aplikasi (Streamlit Dashboard)
├── requirements.txt         # Daftar dependensi Python
└── README.md                # Dokumentasi utama proyek (berkas ini)
```

---

## Clone Repository

```bash
git clone <url-repository-ini>
cd otocerdas-ai
```

---

## Instalasi dan Menjalankan Aplikasi

### Persyaratan
* Python 3.9 atau lebih baru.
* Koneksi internet (untuk mengunduh library dan melakukan panggilan API LLM).

### Langkah 1 — API Key Gemini atau OpenAI
* **Google Gemini (Rekomendasi Gratis)**:
  1. Buka [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).
  2. Masuk menggunakan akun Google, lalu klik **"Create API Key"** dan salin kuncinya.
* **OpenAI (Berbayar)**:
  1. Buka platform OpenAI API dan buat API key baru.

### Langkah 2 — Akun LangSmith (Opsional untuk Tracing)
1. Buka [smith.langchain.com](https://smith.langchain.com/) dan daftar akun.
2. Masuk ke menu **Settings**, lalu buat API key baru dan salin.

### Langkah 3 — Konfigurasi File Lingkungan (.env)
1. Salin isi berkas `.env.example` ke `.env`:
   ```bash
   cp .env.example .env
   ```
2. Buka berkas `.env` dan masukkan kunci API Anda:
   * Atur `MODEL_PROVIDER=google` dan isi `GOOGLE_API_KEY` jika menggunakan Gemini.
   * Atur `MODEL_PROVIDER=openai` dan isi `OPENAI_API_KEY` jika menggunakan OpenAI.
   * Untuk pelacakan visual LangSmith, isi `LANGCHAIN_API_KEY` dan pastikan `LANGCHAIN_TRACING_V2=true`.
   *(Jika Anda mengosongkan API Key, aplikasi akan otomatis menggunakan **Mode Simulasi (Mock LLM)** sehingga Anda tetap dapat mengujinya tanpa kunci API).*

### Langkah 4 — Instalasi Dependensi
Buat virtual environment dan pasang dependensi yang diperlukan:
```bash
python3 -m venv venv
source venv/bin/activate        # Di Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Langkah 5 — Menjalankan Aplikasi

Terdapat dua cara mudah untuk menjalankan aplikasi ini setelah dependensi terpasang:

#### Cara 1: Menggunakan VS Code (Rekomendasi & Sangat Mudah)
Kami telah menyediakan konfigurasi otomatis untuk VS Code di folder `.vscode/`:
1. Buka folder proyek ini di VS Code.
2. Buka panel **Run and Debug** (ikon play dengan gambar kumbang di sidebar kiri atau tekan `Ctrl+Shift+D` / `Cmd+Shift+D`).
3. Pilih opsi **"Python: Streamlit (OtoCerdas AI)"** dari dropdown di bagian atas.
4. Tekan tombol **Play (Hijau)** atau tekan tombol **F5**.
5. VS Code akan otomatis menggunakan virtual environment (`venv`) dan menjalankan server Streamlit dengan aman.

#### Cara 2: Menjalankan manual lewat Terminal
Luncurkan server Streamlit secara lokal menggunakan virtual environment interpreter:
```bash
./venv/bin/streamlit run app.py
```
Aplikasi web secara otomatis akan terbuka di browser Anda pada alamat default: `http://localhost:8501`.

---

## Tangkapan Layar

### 1. Antarmuka Pengguna (Web Interface)
*   **Halaman Dashboard Utama**: Antarmuka dashboard web bertema gelap premium dengan layout multi-kolom yang memuat Chatbot Asisten AI dan formulir tab.
*   **Visualisasi Alur Kerja**: Tampilan alur routing node LangGraph (`classify_node` -> `specialist_node` -> `Output`) yang tampil secara dinamis di atas balon chat asisten.

### 2. Monitoring & Tracing (LangSmith)
*   **Tracing Dashboard**: Rekaman detail eksekusi chain, biaya token, durasi waktu per node, serta visualisasi eksekusi node LangGraph di dasbor LangSmith.

---

## Identitas Mahasiswa

*   **Nama**: FARHAN DZAKYY AQILA
*   **NPM**: 233510430
*   **Kelas**: 6B
*   **Program Studi**: Teknik Informatika
*   **Fakultas**: Universitas Islam Riau
*   **Mata Kuliah**: Praktikum Natural Language Processing
