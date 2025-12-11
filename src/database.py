"""
Database operations for elderly fall detection system.
Includes automatic cleanup functionality.
"""
import sqlite3
from datetime import datetime, timedelta
import yaml
import os
from pathlib import Path


class Database:
    def __init__(self, db_path='data/database.db'):
        """Initialize database connection."""
        self.db_path = db_path
        self.conn = None
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Create tables if they don't exist."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Images table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                category TEXT DEFAULT 'normal',
                fall_detected BOOLEAN DEFAULT 0,
                breathing_detected BOOLEAN,
                emergency_triggered BOOLEAN DEFAULT 0,
                confidence REAL,
                preserved BOOLEAN DEFAULT 0
            )
        ''')
        
        # Events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                image_id INTEGER,
                details TEXT,
                FOREIGN KEY(image_id) REFERENCES images(id)
            )
        ''')
        
        # Storage tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS storage_info (
                id INTEGER PRIMARY KEY,
                last_image_number INTEGER DEFAULT 0,
                total_images INTEGER DEFAULT 0,
                last_cleanup DATETIME
            )
        ''')
        
        # Initialize storage info if empty
        cursor.execute('SELECT COUNT(*) FROM storage_info')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO storage_info (id, last_image_number) VALUES (1, 0)')
        
        self.conn.commit()
    
    def get_next_image_number(self):
        """Get next sequential image number."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT last_image_number FROM storage_info WHERE id = 1')
        current = cursor.fetchone()[0]
        next_num = current + 1
        cursor.execute('UPDATE storage_info SET last_image_number = ?, total_images = total_images + 1 WHERE id = 1', (next_num,))
        self.conn.commit()
        return next_num
    
    def add_image(self, filename, filepath, category='normal', fall_detected=False, 
                  breathing_detected=None, emergency_triggered=False, confidence=None):
        """Add image record to database."""
        cursor = self.conn.cursor()
        preserved = fall_detected or emergency_triggered  # Preserve important images
        
        cursor.execute('''
            INSERT INTO images (filename, filepath, category, fall_detected, 
                              breathing_detected, emergency_triggered, confidence, preserved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (filename, filepath, category, fall_detected, breathing_detected, 
              emergency_triggered, confidence, preserved))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def add_event(self, event_type, image_id=None, details=None):
        """Log system event."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO events (event_type, image_id, details)
            VALUES (?, ?, ?)
        ''', (event_type, image_id, details))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_images(self, category=None, limit=None, offset=None, order='desc'):
        """Query images with optional filters."""
        cursor = self.conn.cursor()
        
        order_clause = 'DESC' if order.lower() == 'desc' else 'ASC'
        
        if category:
            query = f'SELECT * FROM images WHERE category = ? ORDER BY timestamp {order_clause}'
            params = (category,)
        else:
            query = f'SELECT * FROM images ORDER BY timestamp {order_clause}'
            params = ()
        
        if limit:
            query += f' LIMIT {limit}'
        
        if offset:
            query += f' OFFSET {offset}'
        
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def get_image_by_id(self, image_id):
        """Get a specific image by ID."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM images WHERE id = ?', (image_id,))
        return cursor.fetchone()
    
    def get_image_count(self):
        """Get total number of images."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM images')
        return cursor.fetchone()[0]
    
    def get_recent_events(self, limit=20):
        """Get recent system events."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM events ORDER BY timestamp DESC LIMIT ?
        ''', (limit,))
        return cursor.fetchall()
    
    def cleanup_old_images(self, max_images=5000, cleanup_threshold=0.85, 
                          keep_preserved=True, cleanup_days=7):
        """
        Automatic cleanup of old images to prevent storage full.
        
        Args:
            max_images: Maximum number of images to keep
            cleanup_threshold: Start cleanup when image count > threshold * max_images
            keep_preserved: Always keep fall/emergency images
            cleanup_days: Delete normal images older than this many days
        """
        cursor = self.conn.cursor()
        
        # Get current count
        current_count = self.get_image_count()
        threshold_count = int(max_images * cleanup_threshold)
        
        deleted_count = 0
        
        # Strategy 1: Delete by age (normal images older than cleanup_days)
        cutoff_date = datetime.now() - timedelta(days=cleanup_days)
        cursor.execute('''
            SELECT id, filepath FROM images 
            WHERE category = 'normal' 
            AND preserved = 0 
            AND timestamp < ?
        ''', (cutoff_date,))
        
        old_images = cursor.fetchall()
        for img_id, filepath in old_images:
            # Delete file
            if os.path.exists(filepath):
                os.remove(filepath)
            # Delete database record
            cursor.execute('DELETE FROM images WHERE id = ?', (img_id,))
            deleted_count += 1
        
        # Strategy 2: If still over threshold, delete oldest normal images (FIFO)
        current_count -= deleted_count
        if current_count > threshold_count:
            num_to_delete = current_count - threshold_count
            
            cursor.execute('''
                SELECT id, filepath FROM images 
                WHERE category = 'normal' 
                AND preserved = 0 
                ORDER BY timestamp ASC 
                LIMIT ?
            ''', (num_to_delete,))
            
            fifo_images = cursor.fetchall()
            for img_id, filepath in fifo_images:
                if os.path.exists(filepath):
                    os.remove(filepath)
                cursor.execute('DELETE FROM images WHERE id = ?', (img_id,))
                deleted_count += 1
        
        # Update last cleanup time
        cursor.execute('''
            UPDATE storage_info 
            SET last_cleanup = ?, total_images = total_images - ?
            WHERE id = 1
        ''', (datetime.now(), deleted_count))
        
        self.conn.commit()
        
        # Log cleanup event
        self.add_event('cleanup', details=f'Deleted {deleted_count} old images')
        
        return deleted_count
    
    def get_storage_stats(self):
        """Get storage statistics."""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total images
        cursor.execute('SELECT COUNT(*) FROM images')
        stats['total_images'] = cursor.fetchone()[0]
        
        # Images by category
        cursor.execute('SELECT category, COUNT(*) FROM images GROUP BY category')
        stats['by_category'] = dict(cursor.fetchall())
        
        # Preserved images
        cursor.execute('SELECT COUNT(*) FROM images WHERE preserved = 1')
        stats['preserved_images'] = cursor.fetchone()[0]
        
        # Last cleanup
        cursor.execute('SELECT last_cleanup FROM storage_info WHERE id = 1')
        stats['last_cleanup'] = cursor.fetchone()[0]
        
        # Disk usage (estimate)
        cursor.execute('SELECT filepath FROM images')
        total_size = 0
        for (filepath,) in cursor.fetchall():
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
        stats['total_size_mb'] = total_size / (1024 * 1024)
        
        return stats
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


if __name__ == '__main__':
    # Initialize database
    print("Initializing database...")
    db = Database()
    print("Database initialized successfully!")
    
    # Print storage stats
    stats = db.get_storage_stats()
    print(f"\nStorage Statistics:")
    print(f"  Total images: {stats['total_images']}")
    print(f"  Preserved images: {stats['preserved_images']}")
    print(f"  Total size: {stats['total_size_mb']:.2f} MB")
    print(f"  Last cleanup: {stats['last_cleanup']}")
    
    db.close()
