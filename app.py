from flask import Flask, render_template, jsonify
import subprocess
import threading
import os
import sys

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_conversation', methods=['POST'])
def start_conversation():
    """Start the emotion detection and conversation automatically"""
    try:
        # Run main.py directly using the same Python interpreter
        python_executable = sys.executable  # Gets the current Python executable
       # launches main.py without blocking the web server.
        # Run the script and wait for it to complete
        process = subprocess.Popen([python_executable, 'main.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # Don't wait for completion - let it run in background
        return jsonify({
            'success': True,
            'message': 'Emotion detection started! Look at your camera and speak when prompted.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to start: {str(e)}'
        })

@app.route('/status')
def status():
    return jsonify({
        'status': 'ready',
        'message': 'Emotion Recognition System is ready'
    })

if __name__ == '__main__':
    print("🚀 Starting Emotion Recognition Web Server...")
    print("📝 Open http://localhost:5000 in your browser")
    print("🎯 The system will automatically start emotion detection")
    app.run(debug=True, port=5000)