"""
Flask Web Application for Elderly Fall Detection System

Provides web interface for:
- Image gallery with filters
- System status monitoring
- Bulk image download
- Event log viewing

Author: ISDN3000C Project Team
Date: 2025-12-10
"""

import os
import sys
from flask import Flask, render_template, jsonify, send_file, request, Response
from flask_cors import CORS
import yaml
import io
import zipfile
from pathlib import Path
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import Database

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load configuration
config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Initialize database with absolute path
db_path = Path(__file__).parent.parent / config['storage']['database_path']
db = Database(str(db_path))

# Global system status (to be updated by main.py)
system_status = {
    'running': False,
    'camera_active': False,
    'fall_detector_active': False,
    'emergency_state': 'idle',
    'images_captured': 0,
    'falls_detected': 0,
    'emergencies_triggered': 0,
    'storage_used_mb': 0.0,
    'uptime_seconds': 0,
    'last_update': datetime.now(timezone.utc).isoformat()
}


def _to_iso_utc(ts_value):
    """Convert SQLite timestamp to ISO 8601 UTC string with timezone info for the UI."""
    try:
        # SQLite returns strings like '2025-12-16 08:15:30'
        if isinstance(ts_value, str):
            # Try common formats
            try:
                dt = datetime.fromisoformat(ts_value)
            except ValueError:
                dt = datetime.strptime(ts_value, '%Y-%m-%d %H:%M:%S')
        elif isinstance(ts_value, datetime):
            dt = ts_value
        else:
            return ts_value
        # Assume stored time is local server time if naive
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        return ts_value


@app.route('/')
def index():
    """Home page - Image gallery."""
    return render_template('index.html', config=config)


@app.route('/status')
def status_page():
    """System status page."""
    return render_template('status.html', config=config)


@app.route('/api/images')
def api_images():
    """
    Get list of images with optional filtering.
    
    Query parameters:
        - category: Filter by category (fall, emergency, normal)
        - limit: Maximum number of images (default: 100)
        - offset: Offset for pagination (default: 0)
        - order: Sort order (asc, desc; default: desc)
    """
    try:
        category = request.args.get('category', None)
        # Empty string should be treated as None
        if category == '':
            category = None
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        order = request.args.get('order', 'desc')
        
        # Get images from database
        images = db.get_images(
            category=category,
            limit=limit,
            offset=offset,
            order=order
        )
        
        # Format response
        image_list = []
        for img in images:
            image_list.append({
                'id': img[0],
                'filename': img[1],
                'filepath': img[2],
                'timestamp': _to_iso_utc(img[3]),
                'category': img[4],
                'fall_detected': bool(img[5]),
                'breathing_detected': img[6],
                'emergency_triggered': bool(img[7]),
                'confidence': img[8]
            })
        
        return jsonify({
            'success': True,
            'count': len(image_list),
            'images': image_list
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Unable to retrieve images from the database. The system may not be running properly.'
        }), 500


@app.route('/api/image/<int:image_id>')
def api_image(image_id):
    """Get specific image file."""
    try:
        # Get image info from database
        image = db.get_image_by_id(image_id)
        
        if not image:
            return jsonify({
                'success': False,
                'error': 'The requested image could not be found. It may have been deleted.'
            }), 404
        
        # Send image file - convert to absolute path
        filepath = image[2]  # filepath column
        # If path is relative, make it absolute from project root
        if not os.path.isabs(filepath):
            filepath = str(Path(__file__).parent.parent / filepath)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'The image file has been removed from storage.'
            }), 404
        
        return send_file(filepath, mimetype='image/jpeg')
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Unable to load the image. Please try refreshing the page.'
        }), 500


@app.route('/api/image/<int:image_id>/info')
def api_image_info(image_id):
    """Get specific image metadata without the file."""
    try:
        # Get image info from database
        image = db.get_image_by_id(image_id)
        
        if not image:
            return jsonify({
                'success': False,
                'error': 'Image not found'
            }), 404
        
        # Format image data
        image_data = {
            'id': image[0],
            'filename': image[1],
            'filepath': image[2],
            'timestamp': _to_iso_utc(image[3]),
            'category': image[4],
            'fall_detected': bool(image[5]),
            'breathing_detected': bool(image[6]) if image[6] is not None else None,
            'emergency_triggered': bool(image[7]),
            'confidence': float(image[8]) if image[8] is not None else None,
            'preserved': bool(image[9])
        }
        
        return jsonify({
            'success': True,
            'image': image_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/events')
def api_events():
    """
    Get system events.
    
    Query parameters:
        - limit: Maximum number of events (default: 50)
        - event_type: Filter by event type
    """
    try:
        limit = int(request.args.get('limit', 50))
        event_type = request.args.get('event_type', None)
        
        events = db.get_recent_events(limit=limit, event_type=event_type)
        
        event_list = []
        for event in events:
            event_list.append({
                'id': event[0],
                'event_type': event[1],
                'timestamp': _to_iso_utc(event[2]),
                'image_id': event[3],
                'details': event[4]
            })
        
        return jsonify({
            'success': True,
            'count': len(event_list),
            'events': event_list
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Unable to retrieve event history. The database may be unavailable.'
        }), 500


@app.route('/api/stats')
def api_stats():
    """Get statistics for the gallery page."""
    try:
        stats = db.get_statistics()
        
        # Format for frontend
        return jsonify({
            'success': True,
            'total_images': stats['total_images'],
            'falls_detected': stats['falls_detected'],
            'emergencies_triggered': stats['emergencies'],
            'button1_count': stats['emergencies'],  # Button1 count = emergency count
            'storage_used': f"{stats['storage_mb']:.1f} MB"
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/status')
def api_status():
    """Get current system status."""
    try:
        # Update image count
        system_status['images_captured'] = db.get_image_count()
        
        # Get comprehensive statistics
        stats = db.get_statistics()
        system_status['stats'] = {
            'images_captured': stats['total_images'],
            'falls_detected': stats['falls_detected'],
            'emergencies_triggered': stats['emergencies'],
            'storage_used': f"{stats['storage_mb']:.1f} MB"
        }
        
        # Update timestamp
        # Use UTC with timezone info so the UI can display accurate local time
        system_status['last_update'] = datetime.now(timezone.utc).isoformat()
        
        return jsonify({
            'success': True,
            **system_status
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Cannot retrieve system status. Make sure the detection system is running.'
        }), 500


@app.route('/api/download_all')
def api_download_all():
    """Download all images as a ZIP file."""
    try:
        # Get all images
        images = db.get_images(limit=10000)  # Large limit to get all
        
        if not images:
            return jsonify({
                'success': False,
                'error': 'No images available to download. Please capture some images first.'
            }), 404
        
        # Create ZIP in memory
        memory_file = io.BytesIO()
        
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for img in images:
                filepath = img[2]
                filename = img[1]
                
                if os.path.exists(filepath):
                    # Add file to ZIP
                    zf.write(filepath, arcname=filename)
        
        # Prepare response
        memory_file.seek(0)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f'elderly_images_{timestamp}.zip'
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=zip_filename
        )
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to create the download file. Some images may be inaccessible.'
        }), 500


@app.route('/api/statistics')
def api_statistics():
    """Get system statistics."""
    try:
        stats = db.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Unable to calculate statistics. The database may be unavailable.'
        }), 500


def get_storage_info():
    """Get storage information."""
    # Get absolute path to images directory
    images_dir = Path(__file__).parent.parent / config['storage']['images_directory']
    
    total_size = 0
    image_count = 0
    
    if images_dir.exists():
        for file in images_dir.glob('*.jpg'):
            total_size += file.stat().st_size
            image_count += 1
    
    return {
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'image_count': image_count
    }


def update_system_status(status_dict):
    """
    Update system status (called from main.py).
    
    Args:
        status_dict: Dictionary with status updates
    """
    global system_status
    system_status.update(status_dict)
    system_status['last_update'] = datetime.now().isoformat()


def run_webapp(host='0.0.0.0', port=5000, debug=False):
    """
    Run Flask web application.
    
    Args:
        host: Host to bind to
        port: Port to listen on
        debug: Debug mode
    """
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    # Run standalone for testing
    print("Starting Flask web application...")
    print(f"Access at: http://localhost:5000")
    run_webapp(debug=True)
