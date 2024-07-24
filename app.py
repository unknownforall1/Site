from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
from youtubesearchpython.__future__ import VideosSearch
import yt_dlp
import os
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form['query']
    videosSearch = VideosSearch(search_query, limit=1)
    result = videosSearch.result()
    if not result or not result["result"]:
        return "Song not found", 404

    video_url = result["result"][0]["link"]
    video_id = result["result"][0]["id"]
    video_title = result["result"][0]["title"]
    video_thumbnail = result["result"][0]["thumbnails"][0]["url"]
    download_dir = 'downloads'
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(download_dir, '%(id)s.%(ext)s'),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            downloaded_file = ydl.prepare_filename(info_dict)

        video_url_path = os.path.basename(downloaded_file)
        return redirect(url_for('play', video_id=video_id, video_title=video_title, video_thumbnail=video_thumbnail, video_file=video_url_path))
    except Exception as e:
        return f"Error downloading song: {e}", 500

@app.route('/play/<video_id>')
def play(video_id):
    download_dir = 'downloads'
    video_files = [f for f in os.listdir(download_dir) if re.match(fr'{video_id}.*', f)]
    if not video_files:
        abort(404)

    video_file = video_files[0]
    video_path = os.path.join(download_dir, video_file)
    video_title = request.args.get('video_title')
    video_thumbnail = request.args.get('video_thumbnail')
    return render_template('play.html', video_path=video_path, video_title=video_title, video_thumbnail=video_thumbnail)

@app.route('/watch/<video_file>')
def watch(video_file):
    directory = 'downloads'
    if not os.path.exists(os.path.join(directory, video_file)):
        abort(404)
    return send_from_directory(directory, video_file)

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True)
