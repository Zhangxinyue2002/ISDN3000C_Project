# 呼吸检测模块 - 快速测试指南

## 📋 模块概述

呼吸检测模块 (`src/breathing_detector.py`) 使用SIFT关键点跟踪和FFT分析来检测跌倒人员的呼吸。

### 算法原理
1. **提取胸部ROI** - 从跌倒检测的边界框中提取胸部区域
2. **SIFT关键点检测** - 在胸部区域检测特征点
3. **运动跟踪** - 跨多帧跟踪关键点运动
4. **FFT分析** - 使用快速傅里叶变换检测周期性呼吸运动
5. **呼吸验证** - 验证呼吸频率在正常范围内（12-20次/分钟）

---

## 🚀 快速开始

### 方法1: 在你的电脑上测试（推荐先这样做）

```powershell
# 1. 确保你在项目根目录
cd f:\ISDN3000C_Project

# 2. 安装依赖（如果还没安装）
pip install opencv-python opencv-contrib-python numpy pyyaml

# 3. 运行自动化测试
python test_breathing_detection.py

# 4. 运行包含摄像头的测试（可选）
python test_breathing_detection.py --camera
```

### 方法2: 在RDK X5上测试

```bash
# 1. 传输文件到RDK X5
# 使用 transfer_to_rdk.bat 或手动复制

# 2. SSH到RDK X5
ssh user@your-rdkx5-ip

# 3. 进入项目目录
cd ~/ISDN3000C_Project

# 4. 激活虚拟环境
source venv/bin/activate

# 5. 安装依赖（如果需要）
pip install opencv-python opencv-contrib-python

# 6. 运行测试
python3 test_breathing_detection.py

# 7. 运行摄像头测试
python3 test_breathing_detection.py --camera
```

---

## 📊 测试说明

### 自动化测试包含3个测试用例：

#### 测试1: 模拟呼吸运动
- **目的**: 验证算法能检测到周期性呼吸运动
- **预期**: 
  - 应该检测到呼吸（breathing_detected = True）
  - 呼吸频率应接近16次/分钟（误差<5）
  - 置信度应该较高（>0.5）

#### 测试2: 静态帧
- **目的**: 验证算法不会产生误报
- **预期**:
  - 不应检测到呼吸（breathing_detected = False）
  - 运动幅度应该很小（<2像素）

#### 测试3: 随机运动
- **目的**: 验证算法能区分周期性和非周期性运动
- **预期**:
  - 不应检测到呼吸（breathing_detected = False）
  - 或检测到的频率不在正常范围内

### 摄像头测试（可选）

如果运行 `--camera` 选项：
1. 程序会打开摄像头
2. 按**空格键**开始测试
3. 使用鼠标在胸部区域画一个边界框
4. 保持静止，正常呼吸12秒
5. 程序会分析并显示结果

---

## 📈 输出结果解释

### 成功检测到呼吸的输出示例：
```
✓ Analysis Complete
  Breathing Detected: YES
  Confidence: 78%
  Detected Rate: 15.8 breaths/min
  Expected Rate: 16 breaths/min
  Rate Error: 0.2 breaths/min
  Motion Amplitude: 5.43 pixels
  Keypoints Tracked: 127

✅ TEST PASSED: Breathing correctly detected
```

### 各参数含义：

- **Breathing Detected**: 是否检测到呼吸
  - `YES` = 检测到正常呼吸
  - `NO` = 未检测到呼吸（可能是无呼吸或数据不足）

- **Confidence**: 置信度 (0-100%)
  - >70% = 高置信度，结果可靠
  - 50-70% = 中等置信度
  - <50% = 低置信度，可能需要重新检测

- **Detected Rate**: 检测到的呼吸频率（次/分钟）
  - 正常范围: 12-20 次/分钟
  - 低于12 = 呼吸过慢（可能危险）
  - 高于20 = 呼吸过快（可能紧张或运动后）

- **Motion Amplitude**: 运动幅度（像素）
  - >2 像素 = 有明显运动
  - <2 像素 = 运动很小或无运动

- **Keypoints Tracked**: 跟踪的特征点数量
  - >50 = 良好
  - 10-50 = 可接受
  - <10 = 特征点太少，结果可能不准确

---

## 🔧 配置参数

在 `config/config.yaml` 中调整参数：

```yaml
breathing_detection:
  min_breathing_rate: 12        # 最小呼吸频率（次/分钟）
  max_breathing_rate: 20        # 最大呼吸频率（次/分钟）
  min_motion_amplitude: 2.0     # 最小运动幅度（像素）
  capture_duration: 12          # 捕获时长（秒）
  fps: 30                       # 帧率
  min_keypoints: 10             # 最小关键点数量
```

### 参数调整建议：

**如果经常误报（检测到不存在的呼吸）：**
- 增加 `min_motion_amplitude` 到 3.0-4.0
- 增加 `min_keypoints` 到 15-20

**如果经常漏检（没检测到存在的呼吸）：**
- 减少 `min_motion_amplitude` 到 1.5-2.0
- 减少 `min_keypoints` 到 5-8
- 增加 `capture_duration` 到 15秒

**如果检测太慢：**
- 减少 `capture_duration` 到 10秒
- 减少 `fps` 到 20（但可能影响精度）

---

## 🐛 常见问题排查

### 问题1: "Insufficient keypoints detected"
**原因**: 图像特征太少，SIFT无法检测足够的关键点
**解决方法**:
- 确保胸部区域有足够的纹理（避免纯色衣服）
- 增加光照
- 检查摄像头是否对焦
- 减少 `min_keypoints` 参数

### 问题2: "Insufficient frames"
**原因**: 捕获的帧数太少
**解决方法**:
- 检查摄像头是否正常工作
- 确保捕获时间足够（至少10秒）

### 问题3: 检测结果不稳定
**原因**: 环境干扰或参数设置不当
**解决方法**:
- 确保人员保持静止（除了呼吸）
- 避免背景运动
- 调整 `min_motion_amplitude` 参数
- 增加捕获时长到15秒

### 问题4: "Import cv2 could not be resolved"
**原因**: OpenCV未安装
**解决方法**:
```powershell
pip install opencv-python opencv-contrib-python
```

---

## 🔗 与其他模块集成

### 在跌倒检测后调用呼吸检测：

```python
from src.breathing_detector import BreathingDetector
from src.camera_service import CameraService

# 初始化
detector = BreathingDetector()
camera = CameraService()

# 假设跌倒检测返回了边界框
fall_bbox = (100, 150, 300, 400)  # [x1, y1, x2, y2]

# 从边界框推断胸部位置（通常在上半部分）
x1, y1, x2, y2 = fall_bbox
chest_y1 = y1
chest_y2 = y1 + (y2 - y1) // 2  # 上半身
chest_bbox = (x1, chest_y1, x2, chest_y2)

# 捕获并分析呼吸
result = detector.capture_and_analyze(camera.cap, chest_bbox)

# 根据结果采取行动
if not result['breathing_detected']:
    print("⚠️ 警告: 未检测到呼吸!")
    # 启动紧急流程
else:
    print(f"✓ 检测到呼吸: {result['breathing_rate']:.1f} 次/分钟")
    # 正常状态，可能是误报
```

---

## 📝 测试检查清单

运行测试前确认：
- [ ] OpenCV已安装 (`pip list | findstr opencv`)
- [ ] NumPy已安装 (`pip list | findstr numpy`)
- [ ] PyYAML已安装 (`pip list | findstr yaml`)
- [ ] config.yaml文件存在
- [ ] 如果要测试摄像头，确保摄像头已连接

运行测试后验证：
- [ ] 测试1（模拟呼吸）通过
- [ ] 测试2（静态帧）通过
- [ ] 测试3（随机运动）通过
- [ ] （可选）测试4（真实摄像头）通过

---

## 📞 需要帮助？

如果遇到问题：
1. 检查上面的"常见问题排查"
2. 查看详细日志输出
3. 尝试调整config.yaml中的参数
4. 运行简单测试: `python -c "from src.breathing_detector import BreathingDetector; BreathingDetector()"`

---

## 下一步

完成呼吸检测测试后：
1. ✅ 呼吸检测模块完成
2. ⏭️ 下一步: Phase 6 - 紧急系统 (Emergency Controller)
3. 📚 参考: `IMPLEMENTATION_GUIDE.md` Phase 6

---

**创建日期**: 2025-11-30  
**版本**: 1.0  
**状态**: 就绪测试
