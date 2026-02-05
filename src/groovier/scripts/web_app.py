from flask import Flask, render_template, jsonify
from flask_cors import CORS
import json
from pathlib import Path
from groovier.constants import * 

app = Flask(__name__)
CORS(app)


def load_queue():
    """Load current queue state"""
    if Path(QUEUE_FILE).exists():
        with open(QUEUE_FILE, 'r') as f:
            return json.load(f)
    return {'current_song': None, 'queue': [], 'is_playing': False, 'is_paused': False}


def load_playlists():
    """Load saved playlists"""
    if Path(PLAYLISTS_FILE).exists():
        with open(PLAYLISTS_FILE, 'r') as f:
            return json.load(f)
    return {}


@app.route('/')
def index():
    return render_template('../../index.html')


@app.route('/api/queue')
def get_queue():
    """API endpoint to get current queue"""
    return jsonify(load_queue())


@app.route('/api/playlists')
def get_playlists():
    """API endpoint to get all playlists"""
    playlists = load_playlists()
    # Convert to list format for easier frontend handling
    playlist_list = [
        {
            'name': name,
            'songs': songs,
            'count': len(songs)
        }
        for name, songs in playlists.items()
    ]
    return jsonify(playlist_list)


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    Path('templates').mkdir(exist_ok=True)
    
    # Run on all interfaces so Cloudflare Tunnel can access it
    app.run(host='0.0.0.0', port=5000, debug=True)
