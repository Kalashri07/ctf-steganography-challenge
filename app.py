#!/usr/bin/env python3
"""
Flask Web Application for CTF Challenge
Deploys on Render.com
"""

from flask import Flask, render_template, request, jsonify, send_file, session
from datetime import datetime
import os
import hashlib

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-secret-key-in-production')

# Challenge Configuration
CHALLENGE_CONFIG = {
    'name': 'Deep Steganography',
    'category': 'Forensics / Steganography',
    'difficulty': 'Hard',
    'points': 400,
    'flag': 'FLAG{deep_stego_master}',
    'description': '''
We intercepted this image from a suspicious source. Our analysts believe it 
contains hidden information, but they haven't been able to crack it yet. 
Can you find the flag?

The flag format is: FLAG{...}

Download the challenge file below and use your forensic skills to uncover the hidden flag.
    ''',
    'hints': [
        {
            'id': 1,
            'cost': 50,
            'text': 'Check what\'s hiding after the image data ends. Tools like binwalk might be useful.'
        },
        {
            'id': 2,
            'cost': 100,
            'text': 'The password is hidden in plain sight, just not in plain text. Look inside the archive for clues.'
        },
        {
            'id': 3,
            'cost': 150,
            'text': 'Not all files in the archive are what they seem. Look for binary data that might be encrypted.'
        }
    ]
}

# Simple in-memory storage (use database in production)
solves = []
attempts = []

def init_session():
    """Initialize session variables"""
    if 'points' not in session:
        session['points'] = CHALLENGE_CONFIG['points']
    if 'unlocked_hints' not in session:
        session['unlocked_hints'] = []
    if 'solved' not in session:
        session['solved'] = False
    if 'username' not in session:
        session['username'] = None

@app.route('/')
def index():
    """Main challenge page"""
    init_session()
    return render_template('index.html', 
                         challenge=CHALLENGE_CONFIG,
                         session=session)

@app.route('/download')
def download():
    """Download challenge file"""
    try:
        return send_file('static/challenge.png', 
                        as_attachment=True,
                        download_name='challenge.png')
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/submit', methods=['POST'])
def submit_flag():
    """Submit flag attempt"""
    init_session()
    
    data = request.get_json()
    submitted_flag = data.get('flag', '').strip()
    username = data.get('username', 'Anonymous').strip()
    
    if not submitted_flag:
        return jsonify({'success': False, 'message': 'Please enter a flag'})
    
    # Store username
    if username:
        session['username'] = username
    
    # Record attempt
    attempts.append({
        'username': username,
        'flag': submitted_flag,
        'timestamp': datetime.now().isoformat(),
        'correct': submitted_flag == CHALLENGE_CONFIG['flag']
    })
    
    # Check flag
    if submitted_flag == CHALLENGE_CONFIG['flag']:
        if not session['solved']:
            session['solved'] = True
            solves.append({
                'username': username,
                'points': session['points'],
                'timestamp': datetime.now().isoformat()
            })
            return jsonify({
                'success': True, 
                'message': f'Correct! You earned {session["points"]} points! 🎉',
                'points': session['points']
            })
        else:
            return jsonify({
                'success': True,
                'message': 'You already solved this challenge!',
                'points': session['points']
            })
    else:
        return jsonify({
            'success': False,
            'message': 'Incorrect flag. Try again!'
        })

@app.route('/hint/<int:hint_id>', methods=['POST'])
def unlock_hint(hint_id):
    """Unlock a hint"""
    init_session()
    
    if session['solved']:
        return jsonify({'success': False, 'message': 'Challenge already solved!'})
    
    # Find hint
    hint = next((h for h in CHALLENGE_CONFIG['hints'] if h['id'] == hint_id), None)
    if not hint:
        return jsonify({'success': False, 'message': 'Hint not found'})
    
    # Check if already unlocked
    if hint_id in session['unlocked_hints']:
        return jsonify({
            'success': True,
            'hint': hint['text'],
            'message': 'Hint already unlocked',
            'points': session['points']
        })
    
    # Deduct points
    session['points'] -= hint['cost']
    session['unlocked_hints'].append(hint_id)
    session.modified = True
    
    return jsonify({
        'success': True,
        'hint': hint['text'],
        'points': session['points'],
        'message': f'Hint unlocked! -{hint["cost"]} points'
    })

@app.route('/leaderboard')
def leaderboard():
    """Show leaderboard"""
    sorted_solves = sorted(solves, key=lambda x: (-x['points'], x['timestamp']))
    return jsonify({'solves': sorted_solves[:10]})  # Top 10

@app.route('/stats')
def stats():
    """Show statistics"""
    return jsonify({
        'total_attempts': len(attempts),
        'total_solves': len(solves),
        'solve_rate': f"{(len(solves) / max(len(attempts), 1) * 100):.1f}%"
    })

@app.route('/reset', methods=['POST'])
def reset_session():
    """Reset session (for testing)"""
    session.clear()
    return jsonify({'success': True, 'message': 'Session reset'})

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
