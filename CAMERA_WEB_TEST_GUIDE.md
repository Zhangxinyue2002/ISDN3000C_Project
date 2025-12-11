# Camera to Web Interface Integration Test Guide

## Overview
This guide shows how to test that camera captures are properly saved to the database and displayed on the web interface.

## System Architecture

```
Camera → CameraService → Database → Web API → Browser
  ↓                          ↓
Save Image              Store Metadata
```

### Data Flow:
1. **Camera captures image** → `CameraService.capture_and_save()`
2. **Image saved to disk** → `data/images/{number}.jpg`
3. **Metadata stored in DB** → `database.add_image()`
4. **Web API serves images** → `/api/images` endpoint
5. **Browser displays gallery** → Web interface fetches from API

---

## Test Method 1: With Real Camera

### Prerequisites:
- Camera connected to RDK X5 (USB or CSI)
- Available at `/dev/video0` or `/dev/video8`

### Steps:

1. **Check camera availability:**
   ```bash
   ls /dev/video*
   # Should show: /dev/video0 or /dev/video8
   ```

2. **Run camera test:**
   ```bash
   python3 test_camera_web.py
   ```
   
   This will:
   - Open the camera
   - Capture 3 test images
   - Save them to database
   - Show recent images in database
   - Provide instructions for viewing in web

3. **Start the web server:**
   ```bash
   cd webapp
   python3 app.py
   ```
   
   Or start full system:
   ```bash
   ./scripts/run.sh
   ```

4. **View in browser:**
   - Open: `http://localhost:5000`
   - Check the gallery - recent images should appear
   - Try filtering by category
   - Download images

---

## Test Method 2: Without Camera (Simulated)

If no camera is available, you can simulate the process:

### Option A: Manual Image Import

1. **Copy test images to data folder:**
   ```bash
   cp PHOTO/stand1.jpeg data/images/test_capture_1.jpg
   cp PHOTO/stand2.jpg data/images/test_capture_2.jpg
   ```

2. **Add to database manually:**
   ```python
   from src.database import Database
   import yaml
   
   with open('config/config.yaml') as f:
       config = yaml.safe_load(f)
   
   db = Database(config['storage']['database_path'])
   
   db.add_image('test_capture_1.jpg', 'data/images/test_capture_1.jpg', 'normal')
   db.add_image('test_capture_2.jpg', 'data/images/test_capture_2.jpg', 'normal')
   ```

3. **Start web server and view**

### Option B: Use Existing Images

The system already has 2090 images in the database! You can test with these:

```bash
# Start web server
cd webapp
python3 app.py
```

Then open `http://localhost:5000` and browse existing images.

---

## Test Method 3: Full System Integration Test

This tests the complete workflow including fall detection:

1. **Start the full system:**
   ```bash
   ./scripts/run.sh
   ```

2. **The system will:**
   - Start camera continuous capture (every 2 seconds)
   - Run fall detection on each frame
   - Save images with category labels:
     - `normal` - No fall detected
     - `fall` - Fall detected
     - `emergency` - Emergency triggered
   - Store all metadata in database

3. **Monitor via web interface:**
   ```bash
   # In browser: http://localhost:5000
   ```
   
   - **Gallery**: See all captured images in real-time
   - **Filter**: By category (fall/normal/emergency)
   - **Status**: Check system stats (`/status` page)

4. **Test fall detection:**
   - Place a person in camera view
   - Have them simulate a fall (carefully!)
   - Check if fall is detected and marked in gallery
   - Verify image category changes to "fall"

---

## Verification Checklist

✅ **Camera Integration:**
- [ ] Camera opens successfully
- [ ] Images are captured and saved
- [ ] Files appear in `data/images/` directory
- [ ] Sequential numbering works (1.jpg, 2.jpg, etc.)

✅ **Database Integration:**
- [ ] Images are added to database
- [ ] Metadata is correct (filename, filepath, timestamp, category)
- [ ] Image count increases after captures
- [ ] Recent images query returns correct data

✅ **Web API Integration:**
- [ ] `/api/images` returns image list
- [ ] Filtering by category works
- [ ] Pagination works (limit/offset)
- [ ] Sorting works (asc/desc)

✅ **Web UI Integration:**
- [ ] Gallery loads and displays images
- [ ] Thumbnails render correctly
- [ ] Image details show (timestamp, category)
- [ ] Filter buttons work
- [ ] Download function works
- [ ] Modal popups work

---

## Troubleshooting

### Camera Not Found
```
ERROR: Failed to open camera!
```

**Solutions:**
1. Check camera connection:
   ```bash
   ls /dev/video*
   v4l2-ctl --list-devices
   ```

2. Try different camera index in code:
   ```python
   self.cap = cv2.VideoCapture(0)  # Try 0, 1, 2, 8, 10
   ```

3. Check camera permissions:
   ```bash
   sudo chmod 666 /dev/video0
   ```

### Images Not Appearing in Web

**Check database:**
```python
from src.database import Database
db = Database('data/fall_detection.db')
images = db.get_images(limit=5)
print(images)
```

**Check file existence:**
```bash
ls -la data/images/ | tail -10
```

**Check web server logs:**
```bash
# Look for errors in terminal where app.py is running
```

### Web Page Shows "No Images"

1. Make sure images exist in database
2. Clear browser cache
3. Check browser console for errors (F12)
4. Verify API endpoint works:
   ```bash
   curl http://localhost:5000/api/images
   ```

---

## Expected Results

### Successful Camera Test Output:
```
======================================================================
           📸 Camera to Web Interface Test 📸
======================================================================

📥 Initializing database...
   Current images in database: 2090

📷 Initializing camera service...
Camera service initialized
  Resolution: [1280, 720]
  Capture interval: 2s
  Images directory: data/images
Camera opened successfully
  Actual resolution: 1280x720
  Actual FPS: 30

✅ Camera opened successfully!

📸 Capturing 3 test images...
   Capture 1/3... ✓ Saved: 2091.jpg
   Capture 2/3... ✓ Saved: 2092.jpg
   Capture 3/3... ✓ Saved: 2093.jpg

📊 Verifying database entries...
   Images before test: 2090
   Images after test:  2093
   New images added:   3

✅ SUCCESS: All images saved to database!

📋 Recent images in database:
   • 2093.jpg        - 2025-12-11 18:59:45 - Category: normal
   • 2092.jpg        - 2025-12-11 18:59:44 - Category: normal
   • 2091.jpg        - 2025-12-11 18:59:43 - Category: normal
```

### Successful Web Interface:
- Browser shows gallery with thumbnails
- Images load correctly
- Timestamps are accurate
- Category labels are correct
- Filter buttons work
- Download creates zip file

---

## API Endpoints Reference

### Get Images
```
GET /api/images?category=fall&limit=50&offset=0&order=desc
```

Response:
```json
{
  "images": [
    {
      "id": 2093,
      "filename": "2093.jpg",
      "filepath": "data/images/2093.jpg",
      "timestamp": "2025-12-11 18:59:45",
      "category": "normal"
    }
  ],
  "total": 2093,
  "category": "fall",
  "limit": 50,
  "offset": 0
}
```

### Get Image File
```
GET /api/image/<filename>
```

Returns: JPEG image binary data

### Get System Status
```
GET /api/status
```

Returns: System statistics and state

---

## Next Steps After Successful Test

1. **Deploy to RDK X5:**
   - Copy project to device
   - Connect camera
   - Run full system: `./scripts/run.sh`

2. **Test Fall Detection:**
   - Have someone in camera view
   - Simulate fall (safely!)
   - Check if detected and categorized

3. **Test Emergency Workflow:**
   - Trigger fall detection
   - Test breathing detection
   - Verify countdown and buttons
   - Check GPIO outputs (LEDs, buzzer)

4. **Long-term Testing:**
   - Run system for extended period
   - Monitor storage usage
   - Check automatic cleanup
   - Verify database integrity

---

## Summary

The camera-to-web integration is **already fully implemented** in the system:

✅ `CameraService` captures images  
✅ Images saved to `data/images/`  
✅ Metadata stored in SQLite database  
✅ Web API serves image list  
✅ Web UI displays gallery  
✅ Real-time updates work  

You just need to connect a camera and run the system!
