# Triangular Arbitrage Bot

Bot Triangular Arbitrage Cryptocurrency untuk Binance & Indodax.

## Fitur Utama

### 🟢 Binance Bot
*   **Two-Phase Scanning**: Surface Rate (BookTicker) -> Depth Rate (Order Book).
*   **High Performance**: Filter ratusan pair dalam hitungan detik.
*   **Slack Notification**: Notifikasi real-time saat peluang ditemukan.

### 🔴 Indodax Bot
*   **Direct Depth Calculation**: Validasi order book langsung untuk akurasi maksimal.
*   **IDR & USDT Pairs**: Mendukung arbitrase berbasis Rupiah dan USDT.

### 🖥️ Dashboard & API
*   **FastAPI Backend**: API Server yang ringan dan cepat.
*   **Real-time Logs**: Streaming log via SSE (Server-Sent Events).
*   **Web Dashboard**: UI untuk memonitor bot dan melihat history profit.

---
## Panduan Instalasi

### Persyaratan
*   Python 3.9+
*   Pip (Python Package Manager)

### Langkah-langkah

1.  **Clone Repository**
    ```bash
    git clone https://github.com/username/triangular-arbitrage.git
    cd triangular-arbitrage
    ```

2.  **Buat Virtual Environment (Disarankan)**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate   # Windows
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

---

## Cara Menjalankan

Ini akan menjalankan API Server dan Dashboard di `http://localhost:8000`.

```bash
uvicorn backend.main:app --reload
```

*   Buka browser dan akses `http://localhost:8000/app/index.html` untuk melihat UI.
*   Gunakan tombol "Start/Stop" di UI untuk mengontrol bot.
---


