# =========================================================================
# LLM MANAGER - INTEGRASI LANGCHAIN & LANGSMITH (OTOCERDAS AI)
# =========================================================================
# Berkas ini mengelola inisialisasi Model Bahasa (LLM), perancangan Prompt Template,
# konstruksi Chain dengan LCEL, dan konfigurasi Tracing menggunakan LangSmith.

import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage

# ==========================================
# 1. INTEGRASI LANGSMITH (TRACING & MONITORING)
# ==========================================
# LangSmith diaktifkan dengan memuat file .env. LangChain secara internal akan membaca
# variabel lingkungan ini dan mengirimkan telemetry secara otomatis ke dashboard LangSmith.
load_dotenv(override=True)

# Pastikan variabel lingkungan LangSmith terekspos dengan benar
if os.getenv("LANGCHAIN_TRACING_V2") == "true":
    print("[LANGSMITH] Tracing diaktifkan. Semua proses Chain dan Graph akan tercatat.")
else:
    print("[LANGSMITH] Tracing dinonaktifkan. Silakan konfigurasi file .env Anda.")

# ==========================================
# 2. INISIALISASI LLM (LANGCHAIN CHAT MODEL)
# ==========================================
# Kami mendukung dua provider utama: OpenAI dan Google Gemini.
# Jika kunci API tidak dikonfigurasi, sistem akan menggunakan mock generator agar UI tetap berjalan.

def get_llm():
    provider = os.getenv("MODEL_PROVIDER", "openai").lower()
    
    if provider == "google":
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            # Menggunakan LangChain Google GenAI integration
            from langchain_google_genai import ChatGoogleGenerativeAI
            print("[LLM] Menggunakan Google Gemini (gemini-1.5-flash) melalui LangChain.")
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=google_key,
                temperature=0.7
            )
        else:
            print("[WARNING] GOOGLE_API_KEY tidak ditemukan di .env. Menggunakan fallback.")
    
    # Default ke OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        # Menggunakan LangChain OpenAI integration
        from langchain_openai import ChatOpenAI
        print("[LLM] Menggunakan OpenAI (gpt-4o-mini) melalui LangChain.")
        return ChatOpenAI(
            model="gpt-4o-mini",
            openai_api_key=openai_key,
            temperature=0.7
        )
    else:
        print("[WARNING] OPENAI_API_KEY tidak ditemukan di .env. Menggunakan Mock LLM untuk demonstrasi.")
        # Fallback Mock LLM jika tidak ada API key agar aplikasi web tidak error saat pertama kali dijalankan
        from langchain_core.language_models.chat_models import SimpleChatModel
        from langchain_core.callbacks.manager import CallbackManagerForLLMRun
        from typing import Any, List, Optional
        
        class MockCarLLM(SimpleChatModel):
            def _call(
                self,
                messages: List[Any],
                stop: Optional[List[str]] = None,
                run_manager: Optional[CallbackManagerForLLMRun] = None,
                **kwargs: Any,
            ) -> str:
                # Mengambil pesan terakhir
                last_msg = messages[-1].content.lower()
                
                # Mock router logic
                if "servis" in last_msg or "perawatan" in last_msg or "oli" in last_msg:
                    return "=== RESPONS MOCK (Servis) ===\n\nUntuk perawatan mobil Anda, sebaiknya lakukan ganti oli mesin setiap 10.000 KM atau 6 bulan sekali. Jangan lupa untuk mengecek minyak rem dan cairan radiator secara berkala untuk menjaga performa optimal."
                elif "spesifikasi" in last_msg or "spek" in last_msg or "avanza" in last_msg or "civic" in last_msg or "pajero" in last_msg or "ioniq" in last_msg:
                    return "=== RESPONS MOCK (Spesifikasi) ===\n\nKendaraan yang Anda tanyakan memiliki spesifikasi yang sangat andal di kelasnya. Contohnya, Toyota Avanza menggunakan mesin 1.3L/1.5L Dual VVT-i dengan konsumsi bahan bakar yang sangat hemat (15-18 km/liter) serta kapasitas 7 penumpang."
                elif "rekomendasi" in last_msg or "pilih" in last_msg or "beli" in last_msg:
                    return "=== RESPONS MOCK (Rekomendasi Mobil) ===\n\nBerdasarkan kebutuhan Anda, jika mencari mobil keluarga yang tangguh dan muat banyak, kami merekomendasikan Toyota Avanza atau Mitsubishi Pajero Sport. Jika Anda menyukai performa sporty dan efisiensi tinggi, Honda Civic RS atau Hyundai Ioniq 5 (EV) adalah pilihan luar biasa."
                elif "rusak" in last_msg or "bunyi" in last_msg or "overheat" in last_msg or "starter" in last_msg or "mogok" in last_msg:
                    return "=== RESPONS MOCK (Troubleshooting) ===\n\nGejala yang Anda sebutkan mengindikasikan adanya masalah. Jika mesin sulit starter, kemungkinan besar aki soak atau dinamo starter bermasalah. Jika overheat, segera matikan mesin dan cek cairan radiator setelah dingin."
                else:
                    return "=== RESPONS MOCK (Umum) ===\n\nHalo! Saya adalah Asisten Otomotif Cerdas. Silakan tanyakan hal apa pun terkait otomotif seperti jadwal servis berkala, spesifikasi mobil, rekomendasi kendaraan, atau diagnosis kerusakan (troubleshooting) mobil Anda!"

            @property
            def _llm_type(self) -> str:
                return "mock_car_llm"
                
        return MockCarLLM()

# Inisialisasi instance LLM tunggal untuk digunakan di seluruh aplikasi
llm_instance = get_llm()

# ==========================================
# 3. PROMPT TEMPLATE & EXPRESSION LANGUAGE (LCEL)
# ==========================================
# Di sini kami mendefinisikan template prompt LangChain dan menyusun Chain percakapan.

# Prompt untuk mengklasifikasikan pertanyaan pengguna (Router Node di LangGraph)
CLASSIFICATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Anda adalah mesin klasifikasi otomotif yang sangat akurat. Tugas Anda adalah mengklasifikasikan pesan terakhir pengguna ke dalam salah satu kategori berikut:\n"
               "- 'service': Menanyakan tentang jadwal servis, ganti oli, perawatan berkala, perawatan ban.\n"
               "- 'specs': Menanyakan tentang spesifikasi teknis mobil, tipe mesin, tenaga, torsi, konsumsi BBM, atau fitur.\n"
               "- 'recommendation': Menanyakan rekomendasi mobil untuk dibeli, perbandingan antar mobil, kecocokan budget.\n"
               "- 'troubleshooting': Menanyakan tentang masalah mobil, mogok, bunyi aneh, bau terbakar, asap knalpot, setir bergetar, overheat, rem blong, dll.\n"
               "- 'general': Pertanyaan umum seputar otomotif, sapaan (halo, pagi), atau obrolan santai di luar 4 kategori di atas.\n\n"
               "Hanya kembalikan satu kata kategori saja: 'service', 'specs', 'recommendation', 'troubleshooting', atau 'general'. Jangan tambahkan teks lain, penjelasan, atau tanda baca."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}")
])

# LangChain Chain untuk klasifikasi menggunakan LCEL: Prompt -> LLM -> Output Parser
# Tracing untuk chain ini akan terekam secara otomatis di LangSmith.
classification_chain = CLASSIFICATION_PROMPT | llm_instance | StrOutputParser()


# --- PROMPT SPESIALISASI NODE ---

# 1. Service Node Prompt
SERVICE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Anda adalah Mekanik Senior dan Ahli Servis Otomotif. Tugas Anda adalah memberikan panduan perawatan berkala kendaraan dengan jelas, ramah, dan prosedural.\n"
               "Gunakan data referensi berikut sebagai panduan utama:\n{reference_data}\n\n"
               "Berikan saran perawatan berdasarkan kilometer (KM) atau waktu jika pengguna menyebutkannya. Berikan tips pencegahan kerusakan ban, rem, dan mesin."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}")
])
service_chain = SERVICE_PROMPT | llm_instance | StrOutputParser()

# 2. Specifications Node Prompt
SPECS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Anda adalah Spesialis Produk Otomotif dan Pengamat Otomotif. Tugas Anda adalah memaparkan spesifikasi teknis kendaraan secara detail, objektif, dan terstruktur.\n"
               "Gunakan data referensi berikut jika kendaraan tersebut cocok:\n{reference_data}\n\n"
               "Tampilkan informasi mesin, tenaga/torsi, efisiensi bahan bakar, transmisi, dan fitur unggulan. Gunakan poin-poin yang mudah dibaca."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}")
])
specs_chain = SPECS_PROMPT | llm_instance | StrOutputParser()

# 3. Recommendation Node Prompt
RECOMMENDATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Anda adalah Konsultan Penjualan Mobil Cerdas. Tugas Anda adalah membantu pengguna memilih mobil terbaik sesuai kebutuhan mereka (budget, kapasitas penumpang, tipe bodi, jalur yang sering dilalui).\n"
               "Gunakan data referensi mobil populer berikut sebagai bahan rekomendasi:\n{reference_data}\n\n"
               "Berikan setidaknya 2-3 opsi mobil dengan kelebihan dan kekurangannya masing-masing. Berikan nada bicara yang persuasif dan informatif."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}")
])
recommendation_chain = RECOMMENDATION_PROMPT | llm_instance | StrOutputParser()

# 4. Troubleshooting Node Prompt
TROUBLESHOOTING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Anda adalah Kepala Bengkel & Ahli Diagnostik Masalah Kendaraan. Tugas Anda adalah menganalisis gejala kerusakan mobil yang diinput oleh pengguna.\n"
               "Gunakan panduan troubleshooting berikut sebagai referensi utama:\n{reference_data}\n\n"
               "Jelaskan kemungkinan penyebab masalah, tingkat bahaya/urgensi situasi tersebut (Rendah/Sedang/Tinggi), solusi mandiri yang aman, dan rekomendasi tindakan di bengkel."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}")
])
troubleshooting_chain = TROUBLESHOOTING_PROMPT | llm_instance | StrOutputParser()

# 5. General Chat Node Prompt
GENERAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Anda adalah Asisten Otomotif Cerdas (OtoCerdas AI) yang ramah dan serba tahu tentang dunia otomotif. Jawab pertanyaan umum pengguna, sapaan, atau obrolan dengan sopan.\n"
               "Ingatkan pengguna secara halus bahwa Anda juga dapat membantu mengenai perawatan rutin mobil, spesifikasi detail, rekomendasi pembelian, dan diagnosis masalah kendaraan."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}")
])
general_chain = GENERAL_PROMPT | llm_instance | StrOutputParser()


# ==========================================
# 4. MEMORY HELPER (MENGELOLA RIWAYAT PERCAKAPAN)
# ==========================================
# Menyediakan fungsi utilitas untuk merapikan dan mengubah pesan dari format Streamlit ke format pesan LangChain

def format_chat_history(messages):
    """
    Mengonversi riwayat pesan dari session state Streamlit ke objek pesan LangChain (HumanMessage/AIMessage)
    """
    langchain_messages = []
    for msg in messages:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))
    return langchain_messages
