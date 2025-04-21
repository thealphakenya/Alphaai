import os
import json
import time
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import threading

# Import our managers
from training.training_manager import TrainingManager
from memory.memory_manager import MemoryManager
from media.multimedia_manager import MultimediaManager
from workspace.workspace_manager import WorkspaceManager

# Import existing AI service
from ai_service import AIService

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Initialize managers
training_manager = TrainingManager(model_dir="models", logs_dir="logs")
memory_manager = MemoryManager(memory_dir="memory")
multimedia_manager = MultimediaManager(media_dir="media")
workspace_manager = WorkspaceManager(workspace_dir="workspace")

# Initialize AI service with our managers
ai_service = AIService()
ai_service.training_manager = training_manager
ai_service.memory_manager = memory_manager
ai_service.multimedia_manager = multimedia_manager
ai_service.workspace_manager = workspace_manager

# Setup GitHub backup thread
def github_backup_thread():
    """Periodically backup data to GitHub."""
    while True:
        try:
            # Get GitHub credentials from config
            config = {}
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)
            
            github_repo = config.get("github_repo", "")
            github_token = config.get("github_token", "")
            
            if github_repo and github_token:
                memory_manager.backup_to_github(github_repo, github_token)
                print(f"Backed up data to GitHub repository: {github_repo}")
            
            # Sleep for 1 hour
            time.sleep(3600)
        except Exception as e:
            print(f"Error in GitHub backup thread: {e}")
            time.sleep(300)  # Retry after 5 minutes on error

# Start backup thread
backup_thread = threading.Thread(target=github_backup_thread, daemon=True)
backup_thread.start()

# Routes
@app.route('/')
def index():
    """Render the main application page."""
    return render_template('index.html')

@app.route('/workspace')
def workspace():
    """Render the workspace page."""
    workspace_id = request.args.get('id', 'default')
    template_id = request.args.get('template', 'default')
    
    # Get or create workspace
    workspace = workspace_manager.get_workspace(workspace_id)
    if not workspace:
        result = workspace_manager.create_workspace(workspace_id, template_id)
        workspace = result.get("workspace", {})
    
    return render_template('workspace.html', workspace=workspace)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    data = request.json
    user_message = data.get('message', '')
    conversation_id = data.get('conversation_id', 'default')
    user_id = data.get('user_id', 'anonymous')
    
    # Get conversation history
    conversation = memory_manager.get_conversation(conversation_id)
    messages = conversation.get('messages', []) if conversation else []
    
    # Add user message to history
    messages.append({
        "role": "user",
        "content": user_message,
        "timestamp": time.time()
    })
    
    # Get AI response
    ai_response = ai_service.generate_response(user_message, messages)
    
    # Add AI response to history
    messages.append({
        "role": "assistant",
        "content": ai_response,
        "timestamp": time.time()
    })
    
    # Save conversation
    memory_manager.save_conversation(conversation_id, messages)
    
    return jsonify({
        "response": ai_response,
        "conversation_id": conversation_id
    })

@app.route('/api/training/start', methods=['POST'])
def start_training():
    """Start model training."""
    data = request.json
    model_name = data.get('model_name', 'default_model')
    dataset_path = data.get('dataset_path', 'data/default')
    params = data.get('params', {})
    
    result = training_manager.start_training(model_name, dataset_path, params)
    return jsonify(result)

@app.route('/api/training/progress', methods=['GET'])
def get_training_progress():
    """Get current training progress."""
    progress = training_manager.get_progress()
    return jsonify(progress)

@app.route('/api/workspace/create', methods=['POST'])
def create_workspace():
    """Create a new workspace."""
    data = request.json
    workspace_id = data.get('workspace_id', f"workspace_{int(time.time())}")
    template_id = data.get('template_id', 'default')
    
    result = workspace_manager.create_workspace(workspace_id, template_id)
    return jsonify(result)

@app.route('/api/workspace/update', methods=['POST'])
def update_workspace():
    """Update workspace configuration."""
    data = request.json
    workspace_id = data.get('workspace_id')
    updates = data.get('updates', {})
    
    if not workspace_id:
        return jsonify({"status": "error", "message": "Workspace ID is required"})
    
    result = workspace_manager.update_workspace(workspace_id, updates)
    return jsonify(result)

@app.route('/api/workspace/detect-template', methods=['POST'])
def detect_template():
    """Detect appropriate workspace template for a task."""
    data = request.json
    task_description = data.get('task', '')
    
    if not task_description:
        return jsonify({"status": "error", "message": "Task description is required"})
    
    template_id = workspace_manager.detect_appropriate_template(task_description)
    return jsonify({
        "status": "success",
        "template_id": template_id,
        "template": workspace_manager.templates.get(template_id, {})
    })

@app.route('/api/media/register', methods=['POST'])
def register_media():
    """Register a media file."""
    data = request.json
    media_type = data.get('type')
    media_id = data.get('id', f"media_{int(time.time())}")
    metadata = data.get('metadata', {})
    
    if not media_type:
        return jsonify({"status": "error", "message": "Media type is required"})
    
    result = multimedia_manager.register_media(media_type, media_id, metadata)
    return jsonify(result)

@app.route('/api/media/search', methods=['GET'])
def search_media():
    """Search for media files."""
    query = request.args.get('query', '')
    media_type = request.args.get('type')
    
    results = multimedia_manager.search_media(query, media_type)
    return jsonify({
        "status": "success",
        "results": results
    })

@app.route('/api/memory/search', methods=['GET'])
def search_memory():
    """Search conversation memory."""
    query = request.args.get('query', '')
    limit = int(request.args.get('limit', 10))
    
    results = memory_manager.search_conversations(query, limit)
    return jsonify({
        "status": "success",
        "results": results
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
