# =========================================================================
# WORKFLOW LOGIC - INTEGRASI LANGGRAPH (OTOCERDAS AI)
# =========================================================================
# Berkas ini merancang Graph Logika menggunakan LangGraph. Alur dimulai dengan
# klasifikasi (routing) ke node yang sesuai, mengambil data pendukung dari
# knowledge base lokal, dan memicu LangChain untuk merumuskan respons terbaik.

import re
from typing import TypedDict, List, Dict, Any

# Import modul internal
from core.knowledge_base import CAR_SPECS, MAINTENANCE_RECOMMENDATIONS, TROUBLESHOOTING_DATA
from core.llm_manager import (
    classification_chain,
    service_chain,
    specs_chain,
    recommendation_chain,
    troubleshooting_chain,
    general_chain
)

# Import komponen utama LangGraph
from langgraph.graph import StateGraph, START, END

# ==========================================
# 1. DEFINISI STATE (LANGGRAPH STATE)
# ==========================================
# State mewakili memori internal dan konteks yang mengalir di antara node-node graph.
# Di sini kita mendefinisikan TypedDict untuk menampung data status percakapan.

class AgentState(TypedDict):
    question: str          # Pertanyaan terbaru dari pengguna
    history: List[Any]     # Riwayat pesan (HumanMessage / AIMessage)
    category: str          # Kategori pertanyaan hasil klasifikasi (service, specs, dll.)
    reference_data: str    # Konteks data referensi lokal dari knowledge base
    response: str          # Respons akhir yang dihasilkan oleh node pemrosesan

# ==========================================
# 2. DEFINISI NODES (LANGGRAPH NODES)
# ==========================================
# Node adalah unit kerja berupa fungsi Python yang memproses State dan mengembalikan
# pembaruan State (state update).

def classify_node(state: AgentState) -> Dict[str, Any]:
    """
    Node pertama yang dieksekusi. Berfungsi mengidentifikasi maksud/kategori pertanyaan
    pengguna menggunakan LangChain classification_chain.
    """
    print("\n--- [NODE: CLASSIFY] ---")
    question = state["question"]
    history = state["history"]
    
    # Jalankan Chain klasifikasi LangChain
    # LangSmith akan memantau eksekusi chain ini sebagai anak dari langkah graph.
    category_raw = classification_chain.invoke({
        "question": question,
        "history": history
    })
    
    # Sanitasi output klasifikasi
    category = category_raw.strip().lower()
    # Bersihkan jika ada tanda baca
    category = re.sub(r'[^\w\s]', '', category)
    
    # Pastikan kategori valid
    valid_categories = ["service", "specs", "recommendation", "troubleshooting", "general"]
    if category not in valid_categories:
        # Jika LLM mengembalikan kategori aneh, cari keyword manual sebagai fallback
        question_lower = question.lower()
        if any(kw in question_lower for kw in ["servis", "perawatan", "oli", "ban"]):
            category = "service"
        elif any(kw in question_lower for kw in ["spesifikasi", "spek", "mesin", "avanza", "civic", "pajero", "ioniq"]):
            category = "specs"
        elif any(kw in question_lower for kw in ["rekomendasi", "pilih", "beli", "saran", "mobil baru"]):
            category = "recommendation"
        elif any(kw in question_lower for kw in ["rusak", "bunyi", "overheat", "mogok", "getar", "starter", "rem", "decit"]):
            category = "troubleshooting"
        else:
            category = "general"
            
    print(f"Hasil Klasifikasi Kategori: {category}")
    return {"category": category}


def service_node(state: AgentState) -> Dict[str, Any]:
    """
    Node khusus menangani panduan servis & perawatan berkala.
    Mengambil data perawatan yang relevan dari knowledge_base.
    """
    print("--- [NODE: SERVICE] ---")
    question = state["question"]
    history = state["history"]
    
    # Cari data referensi jenis mobil yang dicari (EV, SUV/MPV, atau Sedan)
    question_lower = question.lower()
    if "ev" in question_lower or "listrik" in question_lower or "ioniq" in question_lower:
        rec = MAINTENANCE_RECOMMENDATIONS["ev"]
    elif "suv" in question_lower or "mpv" in question_lower or "pajero" in question_lower or "avanza" in question_lower or "diesel" in question_lower:
        rec = MAINTENANCE_RECOMMENDATIONS["suv_mpv"]
    else:
        rec = MAINTENANCE_RECOMMENDATIONS["sedan_hatchback"]
        
    reference_data = (
        f"Kategori Kendaraan: {rec['jenis']}\n"
        f"- 10.000 KM: {rec['10000']}\n"
        f"- 20.000 KM: {rec['20000']}\n"
        f"- 40.000 KM: {rec['40000']}\n"
        f"- 80.000 KM: {rec['80000']}"
    )
    
    # Panggil LangChain service chain
    response = service_chain.invoke({
        "question": question,
        "history": history,
        "reference_data": reference_data
    })
    
    return {"response": response, "reference_data": reference_data}


def specs_node(state: AgentState) -> Dict[str, Any]:
    """
    Node khusus menangani spesifikasi kendaraan teknis.
    Mencari spesifikasi mobil dari database lokal.
    """
    print("--- [NODE: VEHICLE SPECS] ---")
    question = state["question"]
    history = state["history"]
    
    # Cari kecocokan mobil populer dari knowledge base
    question_lower = question.lower()
    matches = []
    for key, spec in CAR_SPECS.items():
        if key in question_lower:
            matches.append(
                f"Mobil: {spec['nama']}\n"
                f"- Tipe: {spec['tipe']}\n"
                f"- Mesin: {spec['mesin']}\n"
                f"- Tenaga: {spec['tenaga']}\n"
                f"- Torsi: {spec['torsi']}\n"
                f"- Konsumsi BBM: {spec['konsumsi_bbm']}\n"
                f"- Fitur: {spec['fitur_utama']}"
            )
            
    if matches:
        reference_data = "\n\n".join(matches)
    else:
        # Tulis daftar mobil yang terdaftar jika tidak ada yang cocok
        available_cars = ", ".join([spec['nama'] for spec in CAR_SPECS.values()])
        reference_data = f"Mobil terdaftar di database lokal kami: {available_cars}. Berikan informasi umum atau informasikan mobil yang terdaftar tersebut."
        
    # Panggil LangChain specs chain
    response = specs_chain.invoke({
        "question": question,
        "history": history,
        "reference_data": reference_data
    })
    
    return {"response": response, "reference_data": reference_data}


def recommendation_node(state: AgentState) -> Dict[str, Any]:
    """
    Node khusus menangani rekomendasi pembelian mobil.
    """
    print("--- [NODE: RECOMMENDATION] ---")
    question = state["question"]
    history = state["history"]
    
    # Sediakan daftar seluruh spesifikasi mobil sebagai bahan referensi rekomendasi
    ref_list = []
    for spec in CAR_SPECS.values():
        ref_list.append(f"- {spec['nama']} ({spec['tipe']}): Tenaga {spec['tenaga']}, BBM {spec['konsumsi_bbm']}, Fitur {spec['fitur_utama']}")
    reference_data = "\n".join(ref_list)
    
    # Panggil LangChain recommendation chain
    response = recommendation_chain.invoke({
        "question": question,
        "history": history,
        "reference_data": reference_data
    })
    
    return {"response": response, "reference_data": reference_data}


def troubleshooting_node(state: AgentState) -> Dict[str, Any]:
    """
    Node khusus menangani diagnosa keluhan / gejala kerusakan mobil.
    """
    print("--- [NODE: TROUBLESHOOTING] ---")
    question = state["question"]
    history = state["history"]
    
    # Cari kecocokan gejala dari knowledge base
    question_lower = question.lower()
    reference_data = "Gejala umum tidak terdaftar di database lokal. Analisis menggunakan pengetahuan otomotif umum Anda."
    
    for key, trouble in TROUBLESHOOTING_DATA.items():
        # Cek kesamaan kata kunci
        keywords = key.split("_")
        if any(kw in question_lower for kw in keywords):
            reference_data = (
                f"Gejala: {trouble['gejala']}\n"
                f"- Kemungkinan Penyebab: {', '.join(trouble['penyebab_kemungkinan'])}\n"
                f"- Tingkat Urgensi: {trouble['tingkat_bahaya']}\n"
                f"- Solusi Mandiri: {trouble['solusi_mandiri']}\n"
                f"- Tindakan Rekomendasi: {trouble['rekomendasi_tindakan']}"
            )
            break
            
    # Panggil LangChain troubleshooting chain
    response = troubleshooting_chain.invoke({
        "question": question,
        "history": history,
        "reference_data": reference_data
    })
    
    return {"response": response, "reference_data": reference_data}


def general_node(state: AgentState) -> Dict[str, Any]:
    """
    Node cadangan untuk sapaan atau percakapan umum.
    """
    print("--- [NODE: GENERAL CHAT] ---")
    question = state["question"]
    history = state["history"]
    
    response = general_chain.invoke({
        "question": question,
        "history": history
    })
    
    return {"response": response, "reference_data": "Tidak ada data referensi khusus."}

# ==========================================
# 3. KONDISIONAL ROUTER (EDGES ROUTING)
# ==========================================
# Fungsi ini menentukan node berikutnya berdasarkan nilai 'category' di State.

def route_query(state: AgentState) -> str:
    """
    Router kondisional yang menentukan target node setelah klasifikasi.
    """
    category = state["category"]
    
    # Petakan kategori ke nama node LangGraph
    mapping = {
        "service": "service_node",
        "specs": "specs_node",
        "recommendation": "recommendation_node",
        "troubleshooting": "troubleshooting_node",
        "general": "general_node"
    }
    
    # Kembalikan nama node tujuan
    return mapping.get(category, "general_node")

# ==========================================
# 4. MEMBANGUN DAN MENGUMPILKAN GRAPH (LANGGRAPH CONSTRUCT)
# ==========================================
# Di sini kita merangkai state graph, mendefinisikan edges, dan mengompilasinya.

# Inisialisasi graf dengan State skema
builder = StateGraph(AgentState)

# Daftarkan semua node ke graf
builder.add_node("classify", classify_node)
builder.add_node("service_node", service_node)
builder.add_node("specs_node", specs_node)
builder.add_node("recommendation_node", recommendation_node)
builder.add_node("troubleshooting_node", troubleshooting_node)
builder.add_node("general_node", general_node)

# Set titik masuk utama (Entry Point)
builder.set_entry_point("classify")

# Sambungkan node 'classify' ke node spesialis secara dinamis menggunakan conditional edges
builder.add_conditional_edges(
    "classify",
    route_query,  # Fungsi router
    {
        "service_node": "service_node",
        "specs_node": "specs_node",
        "recommendation_node": "recommendation_node",
        "troubleshooting_node": "troubleshooting_node",
        "general_node": "general_node"
    }
)

# Sambungkan semua node keluaran ke END untuk mengakhiri alur kerja graf
builder.add_edge("service_node", END)
builder.add_edge("specs_node", END)
builder.add_edge("recommendation_node", END)
builder.add_edge("troubleshooting_node", END)
builder.add_edge("general_node", END)

# Kompilasi graf agar menjadi aplikasi yang dapat dijalankan (compiled graph)
graph_app = builder.compile()
print("[LANGGRAPH] State Graph berhasil dibangun dan dikompilasi.")
