# =========================================================================
# KNOWLEDGE BASE - ASISTEN OTOMOTIF CERDAS (OTOCERDAS AI)
# =========================================================================
# Berkas ini menyediakan data referensi otomotif lokal untuk memperkaya
# informasi yang diberikan oleh LLM pada sistem LangChain & LangGraph.

# 1. Spesifikasi Mobil Populer
CAR_SPECS = {
    "toyota avanza": {
        "nama": "Toyota Avanza",
        "tipe": "LMPV",
        "mesin": "1.3L atau 1.5L 4-silinder DOHC Dual VVT-i",
        "tenaga": "106 PS @ 6,000 RPM (1.5L)",
        "torsi": "137 Nm @ 4,200 RPM",
        "transmisi": "Manual 5-speed atau CVT",
        "konsumsi_bbm": "15 - 18 km/liter (kombinasi)",
        "fitur_utama": "Toyota Safety Sense (TSS) pada tipe tertinggi, 7-seater layout, penggerak roda depan (FWD)."
    },
    "honda civic rs": {
        "nama": "Honda Civic RS",
        "tipe": "Sedan Sport",
        "mesin": "1.5L VTEC Turbo DOHC",
        "tenaga": "178 PS @ 6,000 RPM",
        "torsi": "240 Nm @ 1,700-4,500 RPM",
        "transmisi": "CVT (Continuously Variable Transmission)",
        "konsumsi_bbm": "12 - 15 km/liter (kombinasi)",
        "fitur_utama": "Honda SENSING, dashboard digital 10.2 inci, sporty aero kit, dual exhaust pipe."
    },
    "hyundai ioniq 5": {
        "nama": "Hyundai Ioniq 5",
        "tipe": "Crossover EV (Listrik)",
        "mesin": "Permanent Magnet Synchronous Motor (PMSM) - Baterai Lithium-ion",
        "tenaga": "170 PS (Standard Range) / 217 PS (Long Range)",
        "torsi": "350 Nm",
        "transmisi": "Single Speed Reduction Gear",
        "konsumsi_bbm": "Jarak tempuh hingga 384 km (Standard) / 481 km (Long Range) per charge penuh",
        "fitur_utama": "V2L (Vehicle-to-Load), Hyundai SmartSense, ultra-fast charging 350 kW, interior ramah lingkungan."
    },
    "mitsubishi pajero sport": {
        "nama": "Mitsubishi Pajero Sport",
        "tipe": "Ladder Frame SUV",
        "mesin": "2.4L MIVEC Turbocharged Diesel (4N15)",
        "tenaga": "181 PS @ 3,500 RPM",
        "torsi": "430 Nm @ 2,500 RPM",
        "transmisi": "Otomatis 8-speed",
        "konsumsi_bbm": "10 - 13 km/liter (Solar)",
        "fitur_utama": "Super Select 4WD-II, Active Cornering Light, Hill Descent Control, jok kulit premium."
    }
}

# 2. Rekomendasi Perawatan Berkala berdasarkan Jenis Mobil
MAINTENANCE_RECOMMENDATIONS = {
    "sedan_hatchback": {
        "jenis": "Sedan & Hatchback (Bensin)",
        "10000": "Ganti oli mesin (SAE 0W-20/5W-30), ganti filter oli, cek minyak rem, cek tekanan ban, rotasi ban.",
        "20000": "Ganti oli mesin, filter oli, bersihkan filter udara, cek busi, cek sistem suspensi dan kemudi.",
        "40000": "Ganti oli mesin, filter oli, ganti filter udara, ganti filter AC, ganti minyak rem, cek fan belt.",
        "80000": "Ganti oli mesin, filter oli, ganti busi (iridium/platinum), ganti filter bahan bakar, ganti cairan pendingin (coolant), bersihkan throttle body."
    },
    "suv_mpv": {
        "jenis": "SUV & MPV (Bensin/Diesel)",
        "10000": "Ganti oli mesin (SAE 5W-30/10W-40), ganti filter oli, cek cairan radiator, rotasi ban, cek sistem rem.",
        "20000": "Ganti oli mesin, filter oli, bersihkan filter udara & AC, cek minyak rem, cek kaki-kaki (tie rod, rack end).",
        "40000": "Ganti oli mesin, filter oli, ganti filter udara & AC, ganti minyak rem, ganti oli transmisi dan oli gardan (jika RWD/4WD).",
        "80000": "Ganti oli mesin, filter oli, ganti filter bbm (terutama diesel), ganti van belt, ganti coolant, tune up mesin menyeluruh."
    },
    "ev": {
        "jenis": "Mobil Listrik (EV)",
        "15000": "Cek cairan pendingin baterai (coolant battery), cek minyak rem, cek wiper blades, rotasi ban, scan sistem elektrikal (OBD diagnostic).",
        "30000": "Ganti filter udara kabin (AC), cek minyak rem dan ganti jika perlu, cek ketebalan brake pads (lebih awet karena regenerative braking).",
        "60000": "Ganti cairan pendingin baterai (coolant battery khusus EV), ganti oli reducer gear, cek kesehatan baterai (SoH - State of Health), cek suspensi."
    }
}

# 3. Troubleshooting Masalah Kendaraan berdasarkan Gejala
TROUBLESHOOTING_DATA = {
    "mesin_sulit_starter": {
        "gejala": "Mesin tidak mau menyala saat kunci diputar atau tombol start ditekan. Terdengar bunyi tek-tek lambat atau tidak ada suara sama sekali.",
        "penyebab_kemungkinan": [
            "Aki (Battery) lemah atau soak (tegangan di bawah 12 Volt).",
            "Terminal aki kendor, berkarat, atau kotor.",
            "Dinamo starter (starting motor) rusak atau arang dinamo habis.",
            "Alternator rusak sehingga tidak mengisi daya aki."
        ],
        "tingkat_bahaya": "Sedang (Mobil tidak bisa jalan, tapi tidak berbahaya jika sedang parkir)",
        "solusi_mandiri": "Lakukan jumper aki dengan mobil lain, pastikan terminal kencang. Ketuk perlahan rumah dinamo starter jika macet.",
        "rekomendasi_tindakan": "Jika di-jumper berhasil menyala tapi mati lagi setelah dilepas, ganti aki atau periksakan alternator ke bengkel kelistrikan."
    },
    "mesin_overheat": {
        "gejala": "Jarum indikator suhu naik melebihi batas tengah (ke arah H/Merah), lampu indikator suhu menyala, atau keluar uap air dari kap mesin.",
        "penyebab_kemungkinan": [
            "Air radiator (coolant) habis atau bocor pada selang/radiator.",
            "Kipas radiator (extra fan) mati atau putarannya lemah.",
            "Thermostat macet dalam posisi tertutup.",
            "Water pump (pompa air) rusak atau tidak berputar."
        ],
        "tingkat_bahaya": "Tinggi (Dapat merusak mesin secara permanen / melengkungkan cylinder head)",
        "solusi_mandiri": "Segera pinggirkan mobil ke tempat aman dan matikan mesin. JANGAN langsung membuka tutup radiator saat mesin masih panas karena air mendidih bisa menyembur.",
        "rekomendasi_tindakan": "Tunggu mesin dingin (minimal 30-45 menit), cek tangki cadangan air radiator. Jika habis, isi sementara dengan air bersih. Segera derek ke bengkel terdekat."
    },
    "setir_bergetar": {
        "gejala": "Setir kemudi terasa bergetar hebat saat mobil berjalan, terutama pada kecepatan tinggi (di atas 80 km/jam).",
        "penyebab_kemungkinan": [
            "Ban tidak seimbang (out of balance) atau pelek peang.",
            "Keausan ban tidak merata (ban makan sebelah atau bergelombang).",
            "Komponen kaki-kaki longgar (tie rod end, ball joint, atau bushing arm rusak).",
            "Disk brake (piringan rem) bergelombang (getaran terasa hanya saat mengerem)."
        ],
        "tingkat_bahaya": "Sedang (Mempengaruhi kenyamanan dan stabilitas berkendara)",
        "solusi_mandiri": "Periksa secara visual apakah ada benjolan pada ban atau baut roda yang kendor.",
        "rekomendasi_tindakan": "Bawa ke bengkel ban untuk melakukan Spooring dan Balancing roda. Jika getaran masih ada, cek komponen suspensi/rem."
    },
    "rem_berbunyi_decit": {
        "gejala": "Terdengar suara decitan nyaring (squeaking) dari arah roda saat pedal rem diinjak perlahan maupun kuat.",
        "penyebab_kemungkinan": [
            "Kampas rem (brake pads) sudah tipis dan indikator logamnya mulai menggesek piringan.",
            "Ada kotoran, debu, atau pasir yang terselip di antara kampas dan piringan rem.",
            "Kampas rem berkualitas rendah atau mengeras (glazed) karena panas berlebih.",
            "Piringan rem berkarat setelah mobil dicuci atau terkena hujan (biasanya hilang sendiri setelah beberapa kali rem)."
        ],
        "tingkat_bahaya": "Sedang menuju Tinggi (Jika kampas habis total dapat merusak piringan rem dan mengurangi daya cengkeram)",
        "solusi_mandiri": "Semprot sela-sela rem dengan Brake Cleaner untuk membersihkan debu/pasir.",
        "rekomendasi_tindakan": "Bawa ke bengkel untuk memeriksa ketebalan kampas rem. Segera ganti jika ketebalan kampas di bawah 2 mm."
    }
}
