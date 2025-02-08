from flask import Flask, request, jsonify
import os
from pytube import YouTube
import re
from tempfile import NamedTemporaryFile

app = Flask(__name__)

# Rota para obter as informações do vídeo
@app.route("/get_info", methods=["POST"])
def get_video_info():
    url = request.form.get('url')
    if not url:
        return jsonify({'error': 'URL não fornecida'}), 400

    try:
        # Criar objeto do YouTube e obter detalhes
        yt = YouTube(url)
        formats = yt.streams.filter(progressive=True, file_extension='mp4').all()
        formats_info = [{
            'format_id': f.itag,
            'resolution': f.resolution,
            'ext': f.subtype,
            'size': round(f.filesize / (1024 * 1024), 2)  # tamanho em MB
        } for f in formats]

        return jsonify({'formats': formats_info})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Rota para fazer o download
@app.route("/download", methods=["POST"])
def download_video():
    url = request.form.get('url')
    format_id = request.form.get('format_id')
    if not url or not format_id:
        return jsonify({'error': 'URL ou formato não fornecido'}), 400

    try:
        yt = YouTube(url)
        stream = yt.streams.get_by_itag(format_id)

        # Criando um arquivo temporário para download
        temp_file = NamedTemporaryFile(delete=False)
        temp_file_path = temp_file.name
        stream.download(output_path=temp_file_path)

        # Devolver o caminho do arquivo de download
        return jsonify({'download_url': temp_file_path})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Rota para converter o vídeo para MP3
@app.route("/download_mp3", methods=["POST"])
def download_mp3():
    url = request.form.get('url')
    if not url:
        return jsonify({'error': 'URL não fornecida'}), 400

    try:
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()

        # Criando arquivo temporário para MP3
        temp_file = NamedTemporaryFile(delete=False)
        temp_file_path = temp_file.name + ".mp3"
        stream.download(output_path=temp_file_path)

        # Converter para MP3 (se necessário)
        os.rename(temp_file.name, temp_file_path)

        return jsonify({'download_url': temp_file_path})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
