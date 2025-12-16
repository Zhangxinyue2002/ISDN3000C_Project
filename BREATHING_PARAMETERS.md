# 呼吸检测参数调优指南

## 📊 核心参数说明

### 1. **min_motion_amplitude** (最小运动振幅)
**位置**: `config/config.yaml` → `breathing_detection.min_motion_amplitude`  
**当前值**: `2.0` 像素  
**含义**: 胸部运动的最小像素位移，低于此值视为静止

#### 🔧 何时调整：
- **调高** (2.5-3.0px)：
  - 假阳性太多（憋气也检测到呼吸）
  - 摄像头抖动/噪声严重
  - 高分辨率摄像头
  
- **调低** (1.5-1.8px)：
  - 假阴性太多（真实呼吸检测不到）
  - 低像素摄像头
  - 呼吸很浅/微弱

#### ⚡ 效果：
- **提高**: 更严格，减少假阳性，但可能漏检微弱呼吸
- **降低**: 更敏感，捕捉微弱呼吸，但易受噪声干扰

---

### 2. **min_breathing_rate / max_breathing_rate** (呼吸率范围)
**位置**: `config/config.yaml`  
**当前值**: `6-30` BPM (每分钟呼吸次数)  
**含义**: 正常人类呼吸速率范围

#### 🔧 何时调整：
- **缩小范围** (8-20 BPM)：
  - 减少高频噪声误判
  - 只检测正常平静呼吸
  
- **扩大范围** (4-35 BPM)：
  - 包含极慢呼吸（深度睡眠）
  - 包含快速呼吸（紧张/运动后）

#### ⚡ 效果：
- **正常成人静息**: 12-20 BPM
- **放松/睡眠**: 6-12 BPM
- **紧张/运动**: 20-30 BPM

---

### 3. **MIN_CONFIDENCE_THRESHOLD** (最低置信度)
**位置**: `src/breathing_detector.py` Line ~160  
**当前值**: `0.4`  
**含义**: 综合置信度分数，低于此值拒绝检测结果

#### 🔧 何时调整：
- **调高** (0.5-0.6)：
  - 假阳性太多
  - 要求高可靠性
  - 可接受偶尔漏检
  
- **调低** (0.3-0.35)：
  - 假阴性太多
  - 低像素摄像头
  - 优先避免漏检

#### ⚡ 置信度计算：
```python
confidence = (rate_confidence + amplitude_confidence) / 2.0
# rate_confidence: 呼吸率匹配度 (0-1)
# amplitude_confidence: min(1.0, motion_amplitude / 5.0)
```

---

### 4. **strong_amplitude** (宽松模式振幅)
**位置**: `src/breathing_detector.py` Line ~376  
**当前值**: `2.8` 像素  
**含义**: 宽松模式下的高振幅阈值，用于呼吸率稍偏离时的检测

#### 🔧 何时调整：
- **调高** (3.5-4.0px)：
  - 只接受明显的深呼吸
  - 减少边缘情况误判
  
- **调低** (2.5-2.8px)：
  - 接受较浅的呼吸
  - 提高宽松模式容忍度

#### ⚡ 宽松模式逻辑：
```python
# 如果呼吸率稍偏离(4-35 BPM)，但振幅够强，仍可通过
relaxed_mode = (4 <= rate <= 35) AND (amplitude >= 2.8)
```

---

### 5. **capture_duration** (捕获时长)
**位置**: `config/config.yaml`  
**当前值**: `8` 秒  
**含义**: 录制视频的时长

#### 🔧 何时调整：
- **延长** (10-12秒)：
  - 呼吸频率分析不稳定
  - 捕捉更多呼吸周期
  - 牺牲速度换准确性
  
- **缩短** (6-7秒)：
  - 加快应急响应
  - 呼吸检测已足够准确

#### ⚡ 权衡：
- **8秒**: 能捕获1-2个完整呼吸周期（12 BPM）
- **更长**: 更准确，但紧急响应变慢
- **更短**: 更快，但FFT分析不够稳定

---

### 6. **光流参数** (Optical Flow)
**位置**: `src/breathing_detector.py` Line ~258  
**当前值**: `winSize=(31,31), maxLevel=4`

#### 🔧 winSize (窗口大小):
- **更大** (41,41)：
  - 低分辨率摄像头
  - 更稳定，抗噪声
  - 更慢
  
- **更小** (21,21)：
  - 高分辨率摄像头
  - 更精确
  - 更快

#### 🔧 maxLevel (金字塔层级):
- **更高** (5-6)：
  - 低分辨率
  - 捕捉更大位移
  
- **更低** (2-3)：
  - 高分辨率
  - 减少计算量

---

### 7. **跟踪网格** (Tracking Grid)
**位置**: `src/breathing_detector.py` Line ~269  
**当前值**: `4x4` = 16个跟踪点

#### 🔧 何时调整：
- **增加点数** (5x5 = 25点)：
  - 更准确
  - 更多冗余
  - 计算量增加
  
- **减少点数** (3x3 = 9点)：
  - 更快
  - 低像素摄像头（太多点可能失效）

---

## 🎯 典型调整场景

### 场景1: 假阳性（憋气也检测到呼吸）
```yaml
# 提高阈值
min_motion_amplitude: 2.5 → 3.0
MIN_CONFIDENCE_THRESHOLD: 0.4 → 0.5
strong_amplitude: 2.8 → 3.5
```

### 场景2: 假阴性（呼吸检测不到）
```yaml
# 降低阈值
min_motion_amplitude: 2.0 → 1.5
MIN_CONFIDENCE_THRESHOLD: 0.4 → 0.3
strong_amplitude: 2.8 → 2.5
```

### 场景3: 高分辨率摄像头
```yaml
min_motion_amplitude: 3.0-5.0  # 像素位移更大
winSize: (21, 21)              # 更小窗口
maxLevel: 3                     # 更少层级
grid: 5x5                       # 更多跟踪点
```

### 场景4: 极低分辨率摄像头
```yaml
min_motion_amplitude: 1.5-2.0  # 像素位移很小
winSize: (41, 41)              # 更大窗口
maxLevel: 5                     # 更多层级
grid: 3x3                       # 更少跟踪点
MIN_CONFIDENCE_THRESHOLD: 0.3  # 更宽容
```

---

## 📈 调试流程

1. **查看日志中的实际值**：
   ```
   📊 FFT analysis: rate=13.19 bpm, amplitude=1.74 px
   🔍 Detection logic: Standard(True & False=False)
   ```

2. **分析问题**：
   - 呼吸率正常(13.19)但振幅不足(1.74<2.0) → 假阴性

3. **调整参数**：
   - 降低 `min_motion_amplitude` 到 1.5

4. **重新测试**：
   ```bash
   sudo ./scripts/run.sh
   ```

5. **观察结果并迭代**

---

## ⚠️ 注意事项

- **不要过度优化单一场景**: 可能导致其他场景失效
- **保持平衡**: 假阳性vs假阴性的权衡
- **分批调整**: 一次只改一个参数，观察效果
- **记录测试结果**: 不同参数组合的表现

---

## 🔍 当前配置摘要

```yaml
# 适配低像素摄像头的平衡配置
min_motion_amplitude: 2.0 px      # 标准振幅
strong_amplitude: 2.8 px          # 宽松振幅
breathing_rate: 6-30 BPM          # 呼吸率范围
MIN_CONFIDENCE_THRESHOLD: 0.4     # 置信度
capture_duration: 8 秒            # 捕获时长
winSize: (31, 31)                 # 光流窗口
maxLevel: 4                       # 金字塔层级
grid: 4x4 = 16 跟踪点             # 跟踪网格
```

**优化方向**: 针对低像素摄像头，优先避免假阴性
