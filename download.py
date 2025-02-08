from flask import Flask, request, jsonify, send_file
import yt_dlp
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/get_info', methods=['POST'])
def get_info():
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL não fornecida"}), 400

    ydl_opts = {"quiet": True, "noplaylist": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = [
            {"format_id": f["format_id"], "resolution": f.get("resolution", "N/A"),
             "ext": f["ext"], "size": round(f.get("filesize", 0) / 1024 / 1024, 2)}
            for f in info["formats"] if f.get("filesize")
        ]
        return jsonify({"formats": formats})

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get("url")
    format_id = data.get("format_id")

    if not url or not format_id:
        return jsonify({"error": "URL ou formato não fornecido"}), 400

    ydl_opts = {
        "format": format_id,
        "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s"
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)

    return jsonify({"download_url": file_path})

@app.route('/download_mp3', methods=['POST'])
def download_mp3():
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL não fornecida"}), 400

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info).replace(info["ext"], "mp3")

    return jsonify({"download_url": file_path})

@app.route('/downloads/<filename>')
def serve_file(filename):
    return send_file(f"{DOWNLOAD_FOLDER}/{filename}", as_attachment=True)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
