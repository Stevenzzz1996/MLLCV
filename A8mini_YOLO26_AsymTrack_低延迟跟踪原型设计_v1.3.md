# A8 mini 低延迟检测跟踪原型系统设计文档 v1.3

> 检测模型：YOLO26  
> 跟踪模型：AsymTrack  
> 云台平台：思翼 A8 mini 小吊舱  
> 控制方式：A8 mini UDP 速度控制  
> 视频输入：A8 mini RTSP 网口视频流  
> 目标：构建一个可实机验证的低延迟检测、跟踪、预测、云台闭环控制原型系统。  

---

## 1. 原型目标

本原型系统用于验证一条完整的实时闭环链路：

```text
A8 mini RTSP 视频
    ↓
低延迟取最新帧
    ↓
YOLO26 目标检测
    ↓
目标选择 / 人工点击目标
    ↓
AsymTrack 初始化
    ↓
AsymTrack 高频跟踪
    ↓
Kalman 目标位置预测
    ↓
VisualServo / PD 控制
    ↓
A8 mini UDP yaw/pitch 速度控制
    ↓
云台跟随目标
```

核心目标不是先做复杂 GUI，也不是先做数据训练，而是先验证：

```text
检测能发现目标；
跟踪能稳定输出 bbox；
预测能补偿网口视频延迟；
云台能跟上目标；
专家可以随时手动接管；
数据可以被记录下来，为后续 LeRobot 训练准备。
```

---

## 2. 原型必须解决的问题

A8 mini 当前通过网口 RTSP 输出视频，低延迟跟踪会遇到以下问题：

1. RTSP 编码和传输存在延迟；
2. OpenCV / FFmpeg 可能产生视频缓存；
3. YOLO26 检测不能每帧运行，否则控制频率下降；
4. Tracker 如果太慢，会导致云台追旧目标；
5. 云台响应也有物理滞后；
6. GUI 显示和录像不能阻塞控制线程；
7. 目标运动快时，直接追 bbox 中心会慢半拍；
8. 自动跟踪必须能随时被人工停止或接管。

因此，原型设计必须遵守：

```text
只处理最新帧；
旧帧不控制；
YOLO26 低频检测；
AsymTrack 高频跟踪；
Kalman 预测目标位置；
VisualServo 根据预测中心控制云台；
显示和录像异步化；
异常和丢失必须立即 stop。
```

---

## 3. 总体架构

```text
┌──────────────────────────────────────────────┐
│                  A8 mini 吊舱                 │
│       RTSP 视频输出 + UDP yaw/pitch/zoom 控制 │
└──────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────┐
│              LatestFrameRTSP                 │
│  独立线程持续读取 RTSP，只保留最新帧，丢弃旧帧 │
└──────────────────────────────────────────────┘
                     │ latest_frame, frame_ts
                     ▼
┌──────────────────────────────────────────────┐
│              YOLO26 Detector                 │
│  目标检测、目标发现、目标重捕获、低频校验       │
└──────────────────────────────────────────────┘
                     │ detections
                     ▼
┌──────────────────────────────────────────────┐
│              Target Selector                 │
│  人工点击目标 / 自动选择目标 / 目标确认         │
└──────────────────────────────────────────────┘
                     │ selected_bbox
                     ▼
┌──────────────────────────────────────────────┐
│              AsymTrack Tracker               │
│  使用 YOLO26 bbox 初始化，高频输出目标 bbox     │
└──────────────────────────────────────────────┘
                     │ bbox, score
                     ▼
┌──────────────────────────────────────────────┐
│          KalmanTargetPredictor               │
│  对目标中心 [cx, cy, vx, vy] 进行平滑和预测    │
└──────────────────────────────────────────────┘
                     │ predicted_center
                     ▼
┌──────────────────────────────────────────────┐
│              VisualServo Controller          │
│  预测目标中心 → 图像误差 → yaw/pitch 速度       │
└──────────────────────────────────────────────┘
                     │ yaw_speed, pitch_speed
                     ▼
┌──────────────────────────────────────────────┐
│              A8MiniGimbalController          │
│       UDP CMD 0x07 速度控制 + zoom + stop      │
└──────────────────────────────────────────────┘
```

---

## 4. 原型状态机

### 4.1 状态定义

```python
IDLE
DETECTING
CLICK_TO_TRACK
MANUAL_TRACK
AUTO_TRACK
LOST
REACQUIRE
STOPPED
SAFE_STOP
```

---

### 4.2 IDLE

含义：

```text
视频流正常，YOLO26 可以检测，但没有选中目标。
```

动作：

1. 显示 RTSP 实时画面；
2. 低频运行 YOLO26；
3. 显示检测框；
4. 云台停止；
5. 等待专家点击目标或自动选择目标。

转移：

```text
鼠标点击检测框 → CLICK_TO_TRACK
按 T 且有检测目标 → 自动选择目标并进入 CLICK_TO_TRACK
按 W/A/S/D → 手动移动云台，但不进入跟踪
按 Space → STOPPED
按 ESC → SAFE_STOP
```

---

### 4.3 CLICK_TO_TRACK

含义：

```text
根据专家点击位置或自动选择结果，初始化 AsymTrack。
```

逻辑：

1. 接收点击点 `(click_x, click_y)`；
2. 判断点击点是否落入 YOLO26 检测框；
3. 如果命中检测框，选择该 bbox；
4. 如果未命中检测框，可采用点击点附近默认框或要求重新点击；
5. 使用 selected_bbox 初始化 AsymTrack；
6. 初始化成功后进入 MANUAL_TRACK 或 AUTO_TRACK；
7. 初始化失败则回到 IDLE。

默认策略：

```text
专家点击目标后，默认进入 MANUAL_TRACK；
专家按 T 或点击 AUTO_TRACK 后，进入 AUTO_TRACK。
```

---

### 4.4 MANUAL_TRACK

含义：

```text
AsymTrack 持续跟踪目标，但云台控制权在人手里。
```

运行内容：

1. AsymTrack 每帧更新 bbox；
2. KalmanPredictor 持续更新和平滑目标中心；
3. VisualServo 计算误差，但不执行自动控制；
4. GUI 显示检测框、跟踪框、预测中心、误差向量；
5. 专家用 W/A/S/D 控制 yaw/pitch；
6. 专家用 Q/E 控制 zoom；
7. 所有专家动作被记录为 action。

转移：

```text
按 T → AUTO_TRACK
按 Space → STOPPED
按 R → REACQUIRE
tracker 连续失败 → LOST
鼠标重新点击 → CLICK_TO_TRACK
按 ESC → SAFE_STOP
```

---

### 4.5 AUTO_TRACK

含义：

```text
AsymTrack + Kalman + VisualServo 自动闭环控制云台。
```

运行内容：

1. AsymTrack 每帧输出 bbox；
2. KalmanPredictor 更新目标中心和速度；
3. KalmanPredictor 预测 `predict_ms` 后的位置；
4. VisualServo 根据预测中心计算 yaw_speed / pitch_speed；
5. A8MiniGimbalController 发送 UDP 速度控制；
6. YOLO26 低频校验跟踪结果；
7. GUI 显示 tracker bbox、预测中心、控制速度、延迟信息；
8. DataRecorder 记录 observation/action。

转移：

```text
按 M → MANUAL_TRACK
按 Space → STOPPED
按 R → REACQUIRE
tracker 连续失败 → LOST
YOLO26 校验连续失败 → LOST
按 ESC → SAFE_STOP
```

---

### 4.6 LOST

含义：

```text
当前跟踪目标丢失。
```

动作：

1. 立即 `gimbal.stop()`；
2. `tracker.reset()`；
3. `predictor.reset()`；
4. GUI 提示目标丢失；
5. YOLO26 提高检测频率；
6. 等待人工点击或进入 REACQUIRE。

转移：

```text
人工点击目标 → CLICK_TO_TRACK
按 R → REACQUIRE
超时 → IDLE
按 ESC → SAFE_STOP
```

---

### 4.7 REACQUIRE

含义：

```text
局部重捕获目标。
```

第一版建议：

```text
云台先停止；
YOLO26 高频检测；
专家手动小范围搜索；
检测到目标后点击重新初始化 AsymTrack。
```

第二版可加入：

```text
局部螺旋搜索；
最后目标位置附近搜索；
自动选择与原目标类别/外观最相似的目标。
```

---

### 4.8 STOPPED

含义：

```text
普通停止，云台停止但系统继续运行。
```

动作：

1. `yaw_speed = 0`；
2. `pitch_speed = 0`；
3. zoom 停止；
4. 视频继续显示；
5. YOLO26 可继续检测；
6. tracker 可保留或暂停，取决于配置。

---

### 4.9 SAFE_STOP

含义：

```text
安全急停状态。
```

动作：

1. `gimbal.stop()`；
2. `tracker.reset()`；
3. `predictor.reset()`；
4. 清除 selected_target；
5. 禁止自动控制；
6. 只能人工恢复到 IDLE。

---

## 5. 低延迟视频采集模块

### 5.1 模块名称

```text
modules/latest_frame_rtsp.py
```

### 5.2 职责

```text
独立线程读取 RTSP；
只保留最新帧；
旧帧直接丢弃；
提供 frame_ts；
支持断线重连。
```

### 5.3 接口

```python
class LatestFrameRTSP:
    def start(self) -> None:
        pass

    def read_latest(self):
        # return ok, frame, frame_ts
        pass

    def stop(self) -> None:
        pass
```

### 5.4 帧新鲜度控制

每次控制前检查：

```python
frame_age_ms = (time.time() - frame_ts) * 1000

if frame_age_ms > max_frame_age_ms:
    gimbal.stop()
    skip_control()
```

推荐配置：

```yaml
latency:
  max_frame_age_ms: 150
  drop_stale_frame: true
```

---

## 6. YOLO26 检测模块

### 6.1 模块名称

```text
modules/yolo26_detector.py
```

### 6.2 职责

YOLO26 负责：

```text
目标发现；
目标初始化；
目标重捕获；
跟踪期间低频校验。
```

YOLO26 不负责每帧闭环跟踪，否则推理耗时可能拉低控制频率。

---

### 6.3 接口

```python
class YOLO26Detector:
    def __init__(self, model_path, backend, imgsz, conf, classes):
        pass

    def detect(self, frame) -> list[Detection]:
        pass
```

### 6.4 输出格式

```python
@dataclass
class Detection:
    cls_id: int
    cls_name: str
    conf: float
    bbox_xyxy: tuple[float, float, float, float]
    center: tuple[float, float]
    area: float
```

### 6.5 运行频率

```text
IDLE / DETECTING：5~10 FPS
CLICK_TO_TRACK：当前帧检测结果直接使用
MANUAL_TRACK：2~5 FPS 辅助校验
AUTO_TRACK：1~2 FPS 低频校验
LOST / REACQUIRE：5~10 FPS
```

### 6.6 后端设计

优先支持：

```text
backend = ultralytics
model = models/yolo26/best.pt
```

后续支持：

```text
backend = onnxruntime
model = models/yolo26/best.onnx

backend = tensorrt
model = models/yolo26/best.engine
```

---

## 7. AsymTrack 跟踪模块

### 7.1 模块名称

```text
modules/asymtrack_tracker.py
```

### 7.2 职责

AsymTrack 负责：

```text
接收 YOLO26 初始化框；
裁剪 template；
每帧生成 search region；
执行 AsymTrack 推理；
输出 bbox 和跟踪分数；
为 KalmanPredictor 提供目标测量。
```

---

### 7.3 接口

```python
class AsymTrackTracker:
    def init(self, frame, bbox_xyxy) -> bool:
        pass

    def update(self, frame):
        # return bbox_xyxy, score, ok
        pass

    def reset(self) -> None:
        pass
```

---

### 7.4 输入输出

输入：

```text
init:
    frame
    bbox_xyxy from YOLO26 or manual click

update:
    current frame
```

输出：

```text
bbox_xyxy
score
ok
```

---

### 7.5 第一版实现策略

如果真实 AsymTrack ONNX / TensorRT 尚未接入，可分两步：

```text
第一步：
    先用 OpenCV KCF/CSRT 模拟 tracker 接口，跑通完整闭环；

第二步：
    替换为真实 AsymTrackTracker，实现 ONNX/TensorRT 推理。
```

但工程接口必须命名清楚：

```text
OpenCVTrackerWrapper
AsymTrackTracker
```

不要把 OpenCV tracker 伪装成 AsymTrack。

---

## 8. TargetSelector 设计

### 8.1 职责

TargetSelector 负责：

```text
从 YOLO26 检测结果中选择目标；
处理鼠标点击；
处理拖框；
自动选择目标；
生成 tracker 初始化框。
```

### 8.2 点击选择逻辑

```python
def select_by_click(detections, click_x, click_y):
    # 1. 优先选择包含点击点的 bbox
    # 2. 如果多个 bbox 包含，选 conf 最高或面积最合适的
    # 3. 如果没有 bbox 包含，可返回 None 或创建默认框
```

### 8.3 自动选择逻辑

综合评分：

```text
score = 0.5 * conf + 0.3 * area_score + 0.2 * center_score
```

其中：

```text
conf：YOLO26 置信度
area_score：目标框面积得分
center_score：距离画面中心越近得分越高
```

---

## 9. KalmanTargetPredictor 设计

### 9.1 模块名称

```text
modules/target_predictor.py
```

### 9.2 为什么需要

A8 mini 网口跟踪存在链路延迟：

```text
成像
编码
RTSP 传输
解码
算法处理
云台响应
```

Tracker 输出的是旧时刻的目标位置。Kalman 预测用于补偿延迟。

---

### 9.3 状态量

二维匀速模型：

```text
x = [cx, cy, vx, vy]
```

含义：

```text
cx：目标中心 x
cy：目标中心 y
vx：x 方向像素速度
vy：y 方向像素速度
```

观测量：

```text
z = [cx_meas, cy_meas]
```

---

### 9.4 接口

```python
class KalmanTargetPredictor:
    def update(self, bbox_xyxy, timestamp) -> None:
        pass

    def predict_future(self, future_dt: float):
        # return pred_cx, pred_cy
        pass

    def get_velocity(self):
        # return vx, vy
        pass

    def reset(self) -> None:
        pass
```

---

### 9.5 预测时间

配置：

```yaml
prediction:
  enable: true
  predict_ms: 100
  max_predict_ms: 200
```

调参顺序：

```text
50ms → 80ms → 100ms → 150ms
```

---

## 10. VisualServo 控制模块

### 10.1 模块名称

```text
modules/visual_servo.py
```

### 10.2 输入

```text
frame_shape
predicted_center
target_velocity 可选
```

### 10.3 误差

```python
err_x = (pred_cx - frame_w / 2) / (frame_w / 2)
err_y = (pred_cy - frame_h / 2) / (frame_h / 2)
```

### 10.4 P 控制

```python
yaw_speed   = kp_yaw   * err_x
pitch_speed = kp_pitch * err_y
```

### 10.5 PD 控制可选

```python
yaw_speed = kp_yaw * err_x + kd_yaw * (vx / frame_w)
pitch_speed = kp_pitch * err_y + kd_pitch * (vy / frame_h)
```

第一版建议：

```text
先用 Kalman 预测中心 + P 控制；
确认稳定后再加 D 项。
```

### 10.6 保护

必须加入：

```text
deadzone
clamp
smooth
stale frame guard
tracker lost guard
```

---

## 11. A8 mini 云台控制模块

### 11.1 模块名称

```text
modules/gimbal_controller.py
```

### 11.2 职责

```text
UDP 速度控制；
stop；
center；
zoom in/out；
dry_run；
方向符号修正。
```

### 11.3 接口

```python
class A8MiniGimbal:
    def set_speed(self, yaw_speed, pitch_speed):
        pass

    def zoom_in(self):
        pass

    def zoom_out(self):
        pass

    def center(self):
        pass

    def stop(self):
        pass

    def close(self):
        pass
```

### 11.4 安全要求

```text
1. set_speed 内部限幅；
2. stop 必须发送 0,0；
3. 异常退出必须 stop；
4. tracker 丢失必须 stop；
5. stale frame 必须 stop；
6. SAFE_STOP 状态禁止自动控制。
```

---

## 12. Expert GUI 设计

### 12.1 显示内容

GUI 必须显示：

```text
RTSP 实时画面；
YOLO26 检测框；
当前选中目标；
AsymTrack 跟踪框；
Kalman 预测中心；
画面中心十字线；
目标中心误差；
yaw_speed / pitch_speed；
frame_age_ms；
track_fps；
control_hz；
当前状态；
是否录制。
```

---

### 12.2 键盘操作

```text
W / ↑：pitch 上
S / ↓：pitch 下
A / ←：yaw 左
D / →：yaw 右

Q：zoom -
E：zoom +

M：MANUAL_TRACK
T：AUTO_TRACK
R：REACQUIRE
C：CENTER
V：RECORD

Space：STOP
ESC：SAFE_STOP
```

---

### 12.3 鼠标操作

```text
左键点击检测框：
    选择目标并初始化 AsymTrack

左键点击空白处：
    可提示没有检测目标，或以点击点创建默认 bbox

左键拖框：
    手动指定 AsymTrack 初始化框

右键：
    取消目标 / 停止跟踪
```

---

## 13. 数据录制设计

### 13.1 录制内容

每帧记录：

```python
{
    "timestamp": float,
    "frame_index": int,
    "frame_age_ms": float,

    "state": str,

    "detections": list,
    "selected_target": dict,
    "tracker_bbox": list,
    "tracker_score": float,

    "kalman_center": [cx, cy],
    "predicted_center": [pred_cx, pred_cy],
    "target_velocity": [vx, vy],

    "err_x": float,
    "err_y": float,

    "action": {
        "mode_action": int,
        "yaw_speed": float,
        "pitch_speed": float,
        "zoom_cmd": int,
        "track_enable": int,
        "manual_track_enable": int,
        "auto_track_enable": int,
        "stop_enable": int
    }
}
```

---

### 13.2 Episode 文件结构

```text
recordings/
└── episode_000001/
    ├── meta.json
    ├── video.mp4
    ├── data.jsonl
    ├── events.jsonl
    └── latency.jsonl
```

---

## 14. 主循环设计

```python
while True:
    ok, frame, frame_ts = capture.read_latest()

    if not ok:
        gimbal.stop()
        state = SAFE_STOP
        continue

    now = time.time()
    frame_age_ms = (now - frame_ts) * 1000

    if frame_age_ms > cfg.latency.max_frame_age_ms:
        gimbal.stop()
        continue

    # YOLO26 低频检测
    if should_run_yolo(state, frame_id):
        detections = yolo26.detect(frame)

    # AsymTrack 高频跟踪
    if tracker.initialized:
        bbox, track_score, track_ok = tracker.update(frame)
    else:
        bbox, track_score, track_ok = None, 0.0, False

    # GUI 事件
    events = gui.poll_events()

    # 点击目标初始化 AsymTrack
    if has_click_event(events):
        selected_bbox = target_selector.select_by_click(detections, click_x, click_y)
        if selected_bbox is not None:
            tracker.init(frame, selected_bbox)
            predictor.reset()
            state = MANUAL_TRACK

    # MANUAL_TRACK
    if state == MANUAL_TRACK:
        if track_ok:
            predictor.update(bbox, frame_ts)
            pred_center = predictor.predict_future(cfg.prediction.predict_ms / 1000.0)
        # 云台由专家按键控制，不执行 VisualServo

    # AUTO_TRACK
    if state == AUTO_TRACK:
        if track_ok:
            predictor.update(bbox, frame_ts)
            pred_center = predictor.predict_future(cfg.prediction.predict_ms / 1000.0)
            yaw_speed, pitch_speed = visual_servo.compute(frame.shape, pred_center)
            gimbal.set_speed(yaw_speed, pitch_speed)
        else:
            gimbal.stop()
            state = LOST

    # STOP / SAFE_STOP
    if has_stop_event(events):
        gimbal.stop()
        state = STOPPED

    if has_safe_stop_event(events):
        gimbal.stop()
        tracker.reset()
        predictor.reset()
        state = SAFE_STOP

    gui.draw(...)
    recorder.record_step(...)
```

---

## 15. 配置文件设计

```yaml
runtime:
  dry_run_gimbal: false
  show_gui: true
  record_enable: true

video:
  source: "rtsp://192.168.144.25:8554/main.264"
  backend: "opencv_ffmpeg"
  rtsp_transport: "udp"
  latest_frame_only: true
  buffer_size: 1

latency:
  max_frame_age_ms: 150
  max_control_gap_ms: 120
  drop_stale_frame: true
  show_latency: true

yolo26:
  enable: true
  backend: "ultralytics"
  model: "models/yolo26/best.pt"
  onnx_model: "models/yolo26/best.onnx"
  engine: "models/yolo26/best.engine"
  imgsz: 640
  conf: 0.35
  iou: 0.45
  classes: [0]
  detect_interval_idle: 3
  detect_interval_track: 20
  detect_interval_lost: 3

asymtrack:
  enable: true
  backend: "onnxruntime"
  model: "models/asymtrack/asymtrack.onnx"
  engine: "models/asymtrack/asymtrack.engine"
  template_size: 128
  search_size: 256
  score_thr: 0.35
  max_lost_count: 10

prediction:
  enable: true
  method: "kalman_cv"
  predict_ms: 100
  max_predict_ms: 200
  process_noise: 50.0
  measurement_noise: 25.0
  reset_on_lost: true

servo:
  mode: "p"
  kp_yaw: 30
  kp_pitch: 22
  kd_yaw: 0
  kd_pitch: 0
  deadzone_x: 0.04
  deadzone_y: 0.04
  smooth_alpha: 0.5
  max_yaw_speed: 35
  max_pitch_speed: 25

gimbal:
  ip: "192.168.144.25"
  port: 37260
  yaw_sign: 1
  pitch_sign: 1
  zoom_enable: true

control:
  command_hz: 25
  stop_on_stale_frame: true
  stop_on_tracker_lost: true

display:
  fps_limit: 15
  show_yolo: true
  show_tracker: true
  show_prediction: true
  show_latency: true

record:
  enable: true
  root: "recordings"
  async_record: true
  block_control_loop: false
  save_video: true
  save_jsonl: true
```

---

## 16. 原型测试步骤

### 16.1 RTSP 延迟测试

```bash
ffplay -rtsp_transport udp -fflags nobuffer -flags low_delay -framedrop -analyzeduration 0 -probesize 32 rtsp://192.168.144.25:8554/main.264
```

再测试 TCP：

```bash
ffplay -rtsp_transport tcp -fflags nobuffer -flags low_delay -framedrop -analyzeduration 0 -probesize 32 rtsp://192.168.144.25:8554/main.264
```

选择更低延迟且稳定的方式。

---

### 16.2 YOLO26 检测测试

```bash
python3 scripts/test_yolo26_rtsp.py --config config_low_latency.yaml
```

要求：

```text
RTSP 画面显示；
YOLO26 检测框正常；
检测 FPS 满足需求。
```

---

### 16.3 AsymTrack 初始化测试

```bash
python3 scripts/test_asymtrack_click.py --config config_low_latency.yaml
```

要求：

```text
鼠标点击目标；
AsymTrack 初始化成功；
bbox 能跟随目标移动。
```

---

### 16.4 Kalman 预测测试

```bash
python3 scripts/test_kalman_predictor.py
```

显示：

```text
测量中心；
滤波中心；
预测中心；
速度向量。
```

---

### 16.5 自动跟踪低速测试

初始配置：

```yaml
servo:
  max_yaw_speed: 15
  max_pitch_speed: 10
  kp_yaw: 18
  kp_pitch: 12

prediction:
  predict_ms: 80
```

运行：

```bash
python3 main_low_latency_track.py --config config_low_latency.yaml
```

确认：

```text
方向正确；
没有振荡；
Space 可以停止；
ESC 可以急停；
tracker lost 会 stop。
```

---

## 17. 调参策略

### 17.1 跟踪慢半拍

处理顺序：

```text
1. 检查 frame_age_ms；
2. 去掉视频缓存；
3. 降低 YOLO26 运行频率；
4. 提高 AsymTrack FPS；
5. 增大 predict_ms；
6. 适当增大 Kp。
```

---

### 17.2 云台来回振荡

处理顺序：

```text
1. 减小 predict_ms；
2. 减小 Kp；
3. 增大 deadzone；
4. 增大 smooth_alpha；
5. 降低 max_speed。
```

---

### 17.3 bbox 抖动

处理顺序：

```text
1. 增大 Kalman measurement_noise；
2. 增大 deadzone；
3. 增大 smooth_alpha；
4. 使用 YOLO26 低频校验纠偏。
```

---

### 17.4 目标快速运动跟不上

处理顺序：

```text
1. 确认没有旧帧；
2. 增大 process_noise；
3. 适当增加 predict_ms；
4. 增大 max_speed；
5. 后续启用 PD 控制。
```

---

## 18. 给 Codex 的实现提示词

```text
请实现 A8 mini 低延迟检测跟踪原型系统。

检测模型使用 YOLO26，跟踪模型使用 AsymTrack。

核心要求：
1. 使用 RTSP 视频输入；
2. 新增 LatestFrameRTSP，独立线程读取视频，只保留最新帧；
3. 若 frame_age_ms 超过阈值，必须 gimbal.stop()；
4. YOLO26 负责目标检测、初始化目标和低频校验；
5. AsymTrack 负责高频跟踪；
6. 鼠标点击 YOLO26 检测框后初始化 AsymTrack；
7. 新增 KalmanTargetPredictor，状态为 [cx, cy, vx, vy]；
8. VisualServo 使用 Kalman 预测中心输出 yaw_speed/pitch_speed；
9. MANUAL_TRACK 下 AsymTrack 和 Kalman 运行，但云台由专家控制；
10. AUTO_TRACK 下 AsymTrack + Kalman + VisualServo 自动控制云台；
11. GUI 必须显示 YOLO26 检测框、AsymTrack 跟踪框、Kalman 预测中心、frame_age_ms、track_fps、control_hz；
12. 数据录制记录每帧 observation/action；
13. 所有退出路径必须 gimbal.stop()；
14. 第一版可先用 OpenCV Tracker 模拟 AsymTrack 接口，但模块必须预留真实 AsymTrack ONNX/TensorRT 后端；
15. 显示和录像不能阻塞控制线程。
```

---

## 19. 总结

本原型的核心闭环是：

```text
LatestFrameRTSP
    ↓
YOLO26 检测初始化
    ↓
AsymTrack 高频跟踪
    ↓
Kalman 预测位置
    ↓
VisualServo 生成速度
    ↓
A8 mini UDP 控制
```

相比普通跟踪方案，本设计额外强调：

```text
低延迟；
只用最新帧；
YOLO26 低频；
AsymTrack 高频；
Kalman 预测；
旧帧不控云台；
人工随时接管；
数据同步记录。
```

这套原型跑通后，就可以继续扩展为完整专家 GUI 系统和 LeRobot 数据采集训练系统。
