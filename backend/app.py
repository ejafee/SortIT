# ============================================================
#  SortIt — Backend (app.py)
#  Tugas: Terima foto dari frontend, kirim ke Gemini, balik hasilnya
# ============================================================

# -- Import library yang dibutuhkan --
from flask import Flask, request, jsonify   # Flask = framework web Python
from flask_cors import CORS                 # Supaya frontend bisa akses backend
from dotenv import load_dotenv              # Supaya bisa baca file .env
from google import genai                   # Library Gemini AI (versi baru)
import os                                  # Untuk baca environment variable

# -- Setup awal --
load_dotenv()   # Baca file .env supaya API Key bisa digunakan

app = Flask(__name__)   # Buat aplikasi Flask
CORS(app)               # Izinkan frontend (HTML) untuk hubungi backend ini

# -- Sambungkan ke Gemini pakai API Key dari .env --
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# ============================================================
#  ENDPOINT: /analyze
#  Cara pakai: Frontend kirim foto ke sini, kita balik hasilnya
# ============================================================
@app.route("/analyze", methods=["POST"])
def analyze():

    # 1. Cek apakah ada foto yang dikirim
    if "image" not in request.files:
        return jsonify({"error": "Tidak ada foto yang dikirim!"}), 400

    # 2. Ambil foto dari request
    image_file = request.files["image"]
    image_bytes = image_file.read()   # Baca isi fotonya

    # 3. Buat instruksi (prompt) untuk Gemini
    #    Ini bagian PALING PENTING — kamu yang tentukan cara AI menjawab!
    prompt = """
    You are a waste classification assistant for Malaysia and Indonesia.
    
    Look at this image and identify the waste item.
    
    Reply ONLY in this exact JSON format (no extra text):
    {
        "waste_type": "plastic" or "paper" or "glass" or "organic" or "ewaste" or "hazardous" or "unknown",
        "waste_name": "specific name of the item (e.g. Plastic Bottle, Newspaper)",
        "waste_detail": "more specific detail (e.g. Type 2 HDPE Plastic)",
        "confidence": a number from 0 to 100,
        "instructions": ["step 1", "step 2", "step 3"],
        "tip": "one helpful tip about this waste type"
    }
    
    If the image is not a waste item, set waste_type to "unknown".
    """

    # 5. Kirim foto + instruksi ke Gemini dan tunggu jawabannya
    try:
        from google.genai import types
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=image_file.content_type),
                prompt
            ]
        )
        result_text = response.text   # Ambil teks jawaban dari Gemini

        # 6. Bersihkan jawaban Gemini (kadang ada ```json di awal/akhir)
        result_text = result_text.strip()
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]

        # 7. Ubah teks JSON menjadi data Python
        import json
        result = json.loads(result_text)

        # 8. Kirim hasilnya ke frontend
        return jsonify(result), 200

    except Exception as e:
        # Kalau ada error, beritahu frontend
        return jsonify({"error": str(e)}), 500


# ============================================================
#  ENDPOINT: / (halaman utama — untuk cek apakah backend jalan)
# ============================================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "SortIt Backend is running! ♻️"})


# -- Jalankan aplikasi --
if __name__ == "__main__":
    app.run(debug=True, port=5000)
    # debug=True  = otomatis restart kalau ada perubahan kode
    # port=5000   = backend jalan di http://localhost:5000