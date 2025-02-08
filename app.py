from flask import Flask, request, send_file
from pytube import YouTube
import os

app = Flask(__name__)

# Função para download de vídeo
def download_video(url, resolution='720p', save_path="downloads"):
    yt = YouTube(url)
    stream = yt.streams.filter(res=resolution, file_extension='mp4').first()
    
    if not stream:
        # Se não encontrar o formato solicitado, pega o default
        stream = yt.streams.get_highest_resolution()

    video_path = os.path.join(save_path, f"{yt.title}.mp4")
    stream.download(output_path=save_path, filename=f"{yt.title}.mp4")
    return video_path

# Função para download de áudio
def download_audio(url, save_path="downloads"):
    yt = YouTube(url)
    stream = yt.streams.filter(only_audio=True).first()
    audio_path = os.path.join(save_path, f"{yt.title}.mp3")
    stream.download(output_path=save_path, filename=f"{yt.title}.mp3")
    return audio_path

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    format = data.get('format')  # MP4 or MP3
    resolution = data.get('resolution', '720p')  # Default resolution

    # Cria a pasta de downloads se não existir
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    try:
        # Baixa o vídeo ou áudio
        if format == 'mp4':
            video_path = download_video(url, resolution)
            return send_file(video_path, as_attachment=True)
        elif format == 'mp3':
            audio_path = download_audio(url)
            return send_file(audio_path, as_attachment=True)
        else:
            return {'error': 'Formato inválido!'}, 400
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True)
