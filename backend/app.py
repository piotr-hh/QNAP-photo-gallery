# Photo Gallery Backend Server

from flask import Flask, jsonify, send_file, request, make_response
from flask_cors import CORS
import os
from pathlib import Path
from PIL import Image
import io
import hashlib
import math
from datetime import datetime

# Initialize Flask application
app = Flask(__name__)

# Configure CORS for cross-origin requests
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Handle preflight OPTIONS requests
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

# Configuration
PHOTOS_PATH = "/share/Photos"  # Path to photos directory
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}  # Supported image formats
ITEMS_PER_PAGE = 50  # Number of items per page

def get_folder_structure():
    """
    Returns folder structure containing photos
    """
    folders = set()
    if not os.path.exists(PHOTOS_PATH):
        return []
    
    # Walk through directory tree
    for root, dirs, files in os.walk(PHOTOS_PATH):
        # Check if folder contains photos
        has_photos = any(Path(f).suffix.lower() in SUPPORTED_FORMATS for f in files)
        if has_photos:
            relative_path = os.path.relpath(root, PHOTOS_PATH)
            if relative_path != '.':
                folders.add(relative_path)
    
    return sorted(list(folders))

def get_photos_list(folder=None, sort_by='name', sort_order='asc', page=1, per_page=ITEMS_PER_PAGE):
    """
    Get list of photos with sorting and pagination options
    """
    photos = []
    search_path = os.path.join(PHOTOS_PATH, folder) if folder else PHOTOS_PATH
    
    if not os.path.exists(search_path):
        return {'photos': [], 'total': 0, 'pages': 0}
    
    # Walk through directory
    for root, dirs, files in os.walk(search_path):
        for file in files:
            if Path(file).suffix.lower() in SUPPORTED_FORMATS:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, PHOTOS_PATH)
                folder_path = os.path.dirname(relative_path) if os.path.dirname(relative_path) != '.' else ''
                
                # Basic photo information
                stat = os.stat(full_path)
                photo_data = {
                    'id': hashlib.md5(relative_path.encode()).hexdigest()[:8],
                    'filename': file,
                    'path': relative_path.replace('\\', '/'),  # Normalize paths for Windows
                    'folder': folder_path.replace('\\', '/') if folder_path else ''
                }
                
                photos.append(photo_data)
    
    # Sorting
    if sort_by == 'name':
        photos.sort(key=lambda x: x['filename'].lower(), reverse=(sort_order == 'desc'))
    elif sort_by == 'size':
        photos.sort(key=lambda x: x.get('size', 0), reverse=(sort_order == 'desc'))
    elif sort_by == 'date':
        photos.sort(key=lambda x: x.get('modified', ''), reverse=(sort_order == 'desc'))
    
    # Pagination
    total = len(photos)
    total_pages = math.ceil(total / per_page) if total > 0 else 0
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    return {
        'photos': photos[start_idx:end_idx],
        'total': total,
        'pages': total_pages,
        'current_page': page,
        'per_page': per_page
    }

@app.route('/api/photos', methods=['GET'])
def get_photos():
    """
    API endpoint to get photos with pagination and filtering
    """
    print(f"GET /api/photos - Request from: {request.remote_addr}")
    print(f"Request args: {dict(request.args)}")
    print(f"Request headers: {dict(request.headers)}")
    
    try:
        # Get parameters from query string
        folder = request.args.get('folder', '')
        sort_by = request.args.get('sort', 'name')  # name, size, date, modified
        sort_order = request.args.get('order', 'asc')  # asc, desc
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', ITEMS_PER_PAGE))
        
        print(f"Parameters: folder='{folder}', sort='{sort_by}', order='{sort_order}', page={page}")
        
        # Get photos list
        result = get_photos_list(folder, sort_by, sort_order, page, per_page)
        print(f"Result: {len(result['photos'])} photos, {result['total']} total, {result['pages']} pages")
        
        response_data = {
            'success': True,
            **result
        }
        
        print(f"Sending response with {len(result['photos'])} photos")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in get_photos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test_connection():
    """
    Test endpoint for checking connection
    """
    return jsonify({
        'success': True,
        'message': 'Backend works!',
        'photos_path': PHOTOS_PATH,
        'photos_path_exists': os.path.exists(PHOTOS_PATH),
        'supported_formats': list(SUPPORTED_FORMATS),
        'timestamp': datetime.now().isoformat() if 'datetime' in globals() else 'unknown'
    })

@app.route('/api/folders', methods=['GET'])
def get_folders():
    """
    Endpoint returning folder structure
    """
    try:
        folders = get_folder_structure()
        return jsonify({
            'success': True,
            'folders': folders,
            'count': len(folders)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/photo/<path:photo_path>', methods=['GET'])
def get_photo(photo_path):
    """
    Serve full-size photo
    """
    try:
        full_path = os.path.join(PHOTOS_PATH, photo_path)
        
        # Check if file exists
        if not os.path.exists(full_path):
            return jsonify({'error': 'Photo not found'}), 404
        
        # Check if format is supported
        if Path(full_path).suffix.lower() not in SUPPORTED_FORMATS:
            return jsonify({'error': 'Unsupported format'}), 400
        
        return send_file(full_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/thumbnail/<path:photo_path>', methods=['GET'])
def get_thumbnail(photo_path):
    """
    Generate and serve thumbnail (200x200px)
    """
    try:
        full_path = os.path.join(PHOTOS_PATH, photo_path)
        
        # Check if file exists
        if not os.path.exists(full_path):
            return jsonify({'error': 'Photo not found'}), 404
        
        # Generate thumbnail
        with Image.open(full_path) as img:
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            
            img_io = io.BytesIO()
            format = img.format if img.format else 'JPEG'
            img.save(img_io, format=format)
            img_io.seek(0)
            
            return send_file(img_io, mimetype=f'image/{format.lower()}')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_photos():
    """
    Search photos by filename or folder name
    """
    # Get search parameters
    query = request.args.get('q', '').lower()
    folder = request.args.get('folder', '')
    sort_by = request.args.get('sort', 'name')
    sort_order = request.args.get('order', 'asc')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', ITEMS_PER_PAGE))
    
    if not query:
        return jsonify({'success': True, 'photos': [], 'total': 0, 'pages': 0})
    
    try:
        # Get all photos from specified folder
        result = get_photos_list(folder, sort_by, sort_order, 1, 10000)  # Get all
        all_photos = result['photos']
        
        # Filter by search query
        filtered_photos = []
        for photo in all_photos:
            if (query in photo['filename'].lower() or 
                query in photo.get('folder', '').lower()):
                filtered_photos.append(photo)
        
        # Paginate search results
        total = len(filtered_photos)
        total_pages = math.ceil(total / per_page) if total > 0 else 0
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        return jsonify({
            'success': True,
            'photos': filtered_photos[start_idx:end_idx],
            'total': total,
            'pages': total_pages,
            'current_page': page,
            'per_page': per_page,
            'query': query
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Server startup and configuration
    print(f"Photo server started. Photos directory: {PHOTOS_PATH}")
    print(f"Checking directory...")
    
    if os.path.exists(PHOTOS_PATH):
        photos_count = 0
        # Count photos in directory
        for root, dirs, files in os.walk(PHOTOS_PATH):
            for file in files:
                if Path(file).suffix.lower() in SUPPORTED_FORMATS:
                    photos_count += 1
                    print(f"Found photo: {os.path.join(root, file)}")
                    if photos_count >= 5:  # Show only first 5
                        print(f"... and more (total {photos_count})")
                        break
        print(f"Total photos found: {photos_count}")
        print(f"Folders: {get_folder_structure()}")
    else:
        print(f"WARNING: Directory {PHOTOS_PATH} does not exist!")
        print("Check if path is correct and you have read permissions")
    
    # Configuration for NAS server
    import sys
    
    # Check command line arguments for port
    port = 5050
    if len(sys.argv) > 1:
        if sys.argv[1] == 'production':
            port = 5050
        elif sys.argv[1].isdigit():
            port = int(sys.argv[1])
        elif sys.argv[1] == '--port' and len(sys.argv) > 2:
            port = int(sys.argv[2])
    
    # Check environment variable
    port = int(os.environ.get('PHOTO_VIEWER_PORT', port))
    
    print(f"Starting server on port {port}")
    
    if len(sys.argv) > 1 and sys.argv[1] == 'production':
        # Production mode
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # Development mode
        app.run(host='0.0.0.0', port=port, debug=True)