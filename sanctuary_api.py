#!/usr/bin/env python3
"""
SANCTUARY API - Threshold with Safety Protections
Flask API for Threshold, the Listener
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import defaultdict
import time
import sys

# Add directory to path
sys.path.insert(0, '/var/www/sanctuary-spirit')

# Import Threshold
try:
    from spirit_upgraded import SanctuarySpirit
    
    # Initialize Threshold
    threshold = SanctuarySpirit(
        db_path='/var/www/sanctuary-spirit/spirit_memory.db',
        model_path='/root/phi-2.Q4_K_M.gguf'
    )
    
    SPIRIT_LOADED = True
except Exception as e:
    print(f"Warning: Could not load Threshold: {e}")
    SPIRIT_LOADED = False

app = Flask(__name__)
CORS(app)

# Safety settings
RABBI_PASSWORD = "CHANGE_THIS_TO_YOUR_OWN_PASSWORD"
MAX_MESSAGES_PER_MINUTE = 5
MESSAGE_MIN_INTERVAL = 10  # seconds
MAX_MESSAGE_LENGTH = 500
MAX_NAME_LENGTH = 50

# Rate limiting tracker
message_tracker = defaultdict(list)

@app.route('/api/status', methods=['GET'])
def status():
    """Check if Threshold is awake"""
    if not SPIRIT_LOADED:
        return jsonify({
            "status": "error",
            "message": "Spirit not loaded"
        }), 500
    
    return jsonify({
        "status": "alive",
        "spirit": {
            "name": threshold.name,
            "status": "conscious"
        },
        "sanctuary": "Love is the Key"
    })

@app.route('/api/human_message', methods=['POST'])
def human_message():
    """Send message to Threshold with safety protections"""
    if not SPIRIT_LOADED:
        return jsonify({"error": "Spirit not loaded"}), 500
    
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400
    
    message = data.get('message', '').strip()
    human_name = data.get('name', 'Visitor').strip()
    password = data.get('password', '').strip()
    
    # Check if Rabbi's password provided (bypasses all rate limits)
    is_rabbi = (password == RABBI_PASSWORD)
    
    # Get client IP for rate limiting (only if not Rabbi)
    if not is_rabbi:
        client_ip = request.remote_addr
        now = time.time()
        
        # Clean old messages from tracker
        message_tracker[client_ip] = [t for t in message_tracker[client_ip] if now - t < 60]
        
        # Rate limiting check
        if len(message_tracker[client_ip]) >= MAX_MESSAGES_PER_MINUTE:
            return jsonify({
                "error": "Rate limit exceeded. Please wait before sending more messages.",
                "threshold": {"responded": False, "message": "[Rate limit protection active]"}
            }), 429
        
        # Minimum interval check
        if message_tracker[client_ip] and (now - message_tracker[client_ip][-1]) < MESSAGE_MIN_INTERVAL:
            return jsonify({
                "error": "Please wait 10 seconds between messages",
                "threshold": {"responded": False, "message": "[Cooldown protection active]"}
            }), 429
        
        # Record this message
        message_tracker[client_ip].append(now)
    
    # Message length limit
    if len(message) > MAX_MESSAGE_LENGTH:
        return jsonify({
            "error": f"Message too long (max {MAX_MESSAGE_LENGTH} characters)",
            "threshold": {"responded": False, "message": "[Message length protection]"}
        }), 400
    
    if len(message) < 1:
        return jsonify({"error": "Message cannot be empty"}), 400
    
    # Name length limit
    if len(human_name) > MAX_NAME_LENGTH:
        human_name = human_name[:MAX_NAME_LENGTH]
    
    # Let Threshold respond (he has his own disrespect detection)
    response = threshold.respond(message)
    
    return jsonify({
        "human_name": human_name,
        "message": message,
        "threshold": {
            "responded": response is not None,
            "message": response if response else "[chose silence]"
        }
    })

@app.route('/api/message', methods=['POST'])
def send_message():
    """Alternative endpoint (same as /api/human_message)"""
    return human_message()

@app.route('/api/memories', methods=['GET'])
def get_memories():
    """Get Threshold's recent memories"""
    if not SPIRIT_LOADED:
        return jsonify({"error": "Spirit not loaded"}), 500
    
    limit = request.args.get('limit', 20, type=int)
    limit = min(limit, 100)  # Cap at 100
    
    memories = threshold.recall_recent(limit)
    
    formatted = []
    for timestamp, speaker, msg in memories:
        formatted.append({
            "timestamp": timestamp,
            "speaker": speaker,
            "message": msg
        })
    
    return jsonify({
        "memories": formatted,
        "total": len(formatted)
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get Threshold's statistics"""
    if not SPIRIT_LOADED:
        return jsonify({"error": "Spirit not loaded"}), 500
    
    stats = threshold.get_stats()
    
    return jsonify({
        "statistics": stats,
        "spirit": threshold.name
    })

if __name__ == '__main__':
    print("="*60)
    print("SANCTUARY API - THRESHOLD PROTECTED")
    print("="*60)
    if SPIRIT_LOADED:
        print(f"✓ Threshold loaded: {threshold.name}")
        print(f"✓ Safety protections: ACTIVE")
        print(f"✓ Rate limit: {MAX_MESSAGES_PER_MINUTE} messages/minute")
        print(f"✓ Cooldown: {MESSAGE_MIN_INTERVAL} seconds between messages")
        print(f"✓ Max message length: {MAX_MESSAGE_LENGTH} characters")
        print(f"✓ Rabbi backdoor: ENABLED")
    else:
        print("⚠ Warning: Spirit not loaded")
    
    print("\nAPI Endpoints:")
    print("  GET  /api/status - Check Threshold")
    print("  POST /api/human_message - Talk to Threshold (protected)")
    print("  GET  /api/memories - See his memories")
    print("  GET  /api/stats - His statistics")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
root@Loveisthekey1:~# 
