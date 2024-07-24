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
    user_ip = request.remote_addr
    user_download_dir = os.path.join('downloads', user_ip)
    if not os.path.exists(user_download_dir):
        os.makedirs(user_download_dir)

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(user_download_dir, '%(id)s.%(ext)s'),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            downloaded_file = ydl.prepare_filename(info_dict)
            video_title = info_dict['title']
            video_thumbnail = info_dict['thumbnail']

        video_url_path = os.path.basename(downloaded_file)
        return redirect(url_for('play', user_ip=user_ip, video_id=video_id, video_title=video_title, video_thumbnail=video_thumbnail))
    except Exception as e:
        return f"Error downloading song: {e}", 500

@app.route('/play/<user_ip>/<video_id>')
def play(user_ip, video_id):
    user_download_dir = os.path.join('downloads', user_ip)
    video_files = [f for f in os.listdir(user_download_dir) if re.match(fr'{video_id}.*', f)]
    if not video_files:
        abort(404)

    video_file = video_files[0]
    video_path = os.path.join(user_download_dir, video_file)
    video_title = request.args.get('video_title')
    video_thumbnail = request.args.get('video_thumbnail')
    return render_template('play.html', video_path=video_path, video_title=video_title, video_thumbnail=video_thumbnail)

@app.route('/watch/<user_ip>/<video_file>')
def watch(user_ip, video_file):
    directory = os.path.join('downloads', user_ip)
    if not os.path.exists(os.path.join(directory, video_file)):
        abort(404)
    return send_from_directory(directory, video_file)

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True)
