from flask import Flask, request, jsonify
from pytube import YouTube

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Zap Video Go API'

@app.route('/get_info', methods=['POST'])
def get_video_info():
    url = request.form['url']
    try:
        yt = YouTube(url)
        stream_data = yt.streams.filter(progressive=True, file_extension='mp4').all()
        formats = [{"resolution": stream.resolution, "size": round(stream.filesize / (1024 * 1024), 2), "ext": stream.mime_type.split('/')[1], "format_id": stream.itag} for stream in stream_data]
        return jsonify({"formats": formats})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form['url']
    format_id = request.form['format_id']
    try:
        yt = YouTube(url)
        stream = yt.streams.get_by_itag(format_id)
        stream.download(output_path='./downloads', filename=f"{yt.title}.mp4")
        return jsonify({"download_url": f"./downloads/{yt.title}.mp4"})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
