from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import os

app = Flask(__name__, static_url_path='')

@app.route('/')
def serve_html():
    return send_from_directory(os.getcwd(), 'índice.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_url = info_dict['url']

    return jsonify({'video_url': video_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
