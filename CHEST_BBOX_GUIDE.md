# Chest Bounding Box Guide for Breathing Detection

## Quick Start (For 640x480 Resolution)

If your camera is 640x480 (as detected), use these typical chest regions:

### Person Centered in Frame
```bash
python3 test_breathing_rdk.py --bbox 200,150,450,350
```
- Left edge (X1): 200
- Top edge (Y1): 150
- Right edge (X2): 450
- Bottom edge (Y2): 350
- Covers: Upper torso/chest area

### Person Close to Camera
```bash
python3 test_breathing_rdk.py --bbox 150,100,500,400
```
- Larger region for close-up view

### Person Far from Camera
```bash
python3 test_breathing_rdk.py --bbox 250,200,400,320
```
- Smaller region for distant view

## Visual Guide

```
Frame: 640 x 480 pixels

    0                    320                   640
    ├────────────────────┼────────────────────┤
  0 ┼────────────────────────────────────────┤
    │                                         │
    │         [Person Standing/Sitting]       │
    │                                         │
150 │         ┌─────────────────┐            │ ← Top of chest (Y1)
    │         │                 │            │
    │         │   CHEST REGION  │            │
    │         │   (Breathing)   │            │
350 │         └─────────────────┘            │ ← Bottom of chest (Y2)
    │                                         │
    │                                         │
480 └─────────────────────────────────────────┘
        ↑                   ↑
       200                 450
      (X1)                (X2)
```

## How to Find Your Coordinates

### Method 1: Capture Test Image
```bash
python3 capture_test_frame.py
```
This creates `test_frame.jpg` - open it and note the chest region coordinates.

### Method 2: Trial and Error
Start with default values and adjust:
```bash
# Try default
python3 test_breathing_rdk.py --bbox 200,150,450,350

# If person is too low in frame, decrease Y values
python3 test_breathing_rdk.py --bbox 200,100,450,300

# If person is to the left, decrease X values
python3 test_breathing_rdk.py --bbox 150,150,400,350

# If person is to the right, increase X values
python3 test_breathing_rdk.py --bbox 250,150,500,350
```

## Understanding Coordinates

The bounding box format is: `X1,Y1,X2,Y2`

- **X1**: Left edge (how far from left side of image)
- **Y1**: Top edge (how far from top of image)
- **X2**: Right edge (left edge + width)
- **Y2**: Bottom edge (top edge + height)

### Example Calculation
If you want a box:
- Starting 200 pixels from left: X1 = 200
- Starting 150 pixels from top: Y1 = 150
- Width of 250 pixels: X2 = 200 + 250 = 450
- Height of 200 pixels: Y2 = 150 + 200 = 350

Result: `--bbox 200,150,450,350`

## Tips for Best Results

1. **Include chest area only** - not the whole body
2. **Avoid arms** - focus on upper torso
3. **Sufficient size** - at least 150x150 pixels
4. **Center of frame** - easier for algorithm to track
5. **Good lighting** - chest area should be well-lit
6. **Textured clothing** - avoid plain white/black shirts

## Troubleshooting

### "Insufficient keypoints"
- Person too far from camera → Use larger bbox
- Plain clothing → Ask person to wear patterned shirt
- Poor lighting → Improve lighting on chest area

### "Motion amplitude too small"
- Person too far → Move closer or use larger bbox
- Camera too far → Position camera 1-2 meters away

### "Breathing rate too high/low"
- Camera not stable → Mount camera securely
- Background movement → Ensure stationary background
- Person moving → Ask person to sit/lie still

## Example Commands

```bash
# Basic test with default region
python3 test_breathing_rdk.py --bbox 200,150,450,350

# Longer capture (15 seconds instead of 12)
python3 test_breathing_rdk.py --bbox 200,150,450,350 --duration 15

# Lower FPS for faster processing
python3 test_breathing_rdk.py --bbox 200,150,450,350 --fps 20

# Combined
python3 test_breathing_rdk.py --bbox 200,150,450,350 --duration 10 --fps 25
```

---

**Start with:** `python3 test_breathing_rdk.py --bbox 200,150,450,350`
