import subprocess

# Atualiza a biblioteca PyTube via GitHub
subprocess.run(['pip', 'install', '--upgrade', 'git+https://github.com/pytube/pytube.git'])

from flask import Flask, request, jsonify
from pytube import YouTube
import os

app = Flask(__name__)

# Função para baixar o vídeo no formato desejado
def download_video(url, format_type, format_id):
    yt = YouTube(url)
    if format_type == "mp4":
        stream = yt.streams.filter(file_extension='mp4').get_by_itag(format_id)
    elif format_type == "mp3":
        stream = yt.streams.filter(only_audio=True).get_by_itag(format_id)
    else:
        return None
    return stream.download()

@app.route('/get_info', methods=['POST'])
def get_video_info():
    video_url = request.form.get('url')
    try:
        yt = YouTube(video_url)
        formats = []
        for stream in yt.streams.filter(progressive=True, file_extension="mp4"):
            formats.append({
                'format_id': stream.itag,
                'resolution': stream.resolution,
                'ext': stream.subtype,
                'size': round(stream.filesize / (1024 * 1024), 2)  # Tamanho em MB
            })
        return jsonify({'formats': formats})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/download', methods=['POST'])
def download_video_route():
    video_url = request.form.get('url')
    format_id = request.form.get('format_id')
    try:
        yt = YouTube(video_url)
        stream = yt.streams.get_by_itag(format_id)
        download_path = stream.download()
        download_url = os.path.basename(download_path)
        return jsonify({'download_url': download_url})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/download_mp3', methods=['POST'])
def download_mp3_route():
    video_url = request.form.get('url')
    try:
        yt = YouTube(video_url)
        stream = yt.streams.filter(only_audio=True).first()
        download_path = stream.download(filename='audio.mp4')
        os.rename(download_path, download_path.replace('.mp4', '.mp3'))
        download_url = os.path.basename(download_path.replace('.mp4', '.mp3'))
        return jsonify({'download_url': download_url})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
