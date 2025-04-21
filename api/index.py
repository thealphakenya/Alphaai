from flask import Flask, request, jsonify, render_template, send_from_directory
from flask.helpers import send_from_directory
import os
import json
from http import HTTPStatus

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """Serve the main application or static files."""
    if path != "" and os.path.exists(os.path.join('static', path)):
        return send_from_directory('static', path)
    
    # For now, return a simple HTML response
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Alpha AI</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
            }
            .container {
                max-width: 800px;
                padding: 2rem;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                backdrop-filter: blur(10px);
            }
            h1 {
                font-size: 2.5rem;
                margin-bottom: 1rem;
            }
            p {
                font-size: 1.2rem;
                margin-bottom: 2rem;
                opacity: 0.9;
            }
            .status {
                display: inline-block;
                padding: 0.5rem 1rem;
                background-color: rgba(0, 255, 0, 0.2);
                border-radius: 20px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Alpha AI</h1>
            <p>Your intelligent assistant with training capabilities is deployed successfully.</p>
            <div class="status">API Online</div>
        </div>
    </body>
    </html>
    """

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "service": "Alpha AI"
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Simple chat endpoint."""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        # For now, just echo the message back with a prefix
        response = f"Alpha AI is processing: {user_message}"
        
        return jsonify({
            "response": response,
            "status": "success"
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), HTTPStatus.INTERNAL_SERVER_ERROR

# This is used when running locally
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
