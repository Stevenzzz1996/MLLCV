# SIYI A8 Mini 云台 UDP 控制协议整理

> 适用对象：SIYI A8 Mini 云台相机  
> 当前代码实现范围：UDP 发帧、CRC16 校验、云台速度控制、云台回中、指定角度控制、螺旋扫描  
> 默认通信地址：`192.168.144.25:37260`

---

## 1. 通信方式

| 项目 | 内容 |
|---|---|
| 设备 | SIYI A8 Mini 云台相机 |
| 通信方式 | UDP |
| 默认 IP | `192.168.144.25` |
| 默认端口 | `37260` |
| 字节序 | 小端序，低字节在前 |
| 控制对象 | 云台 yaw / pitch、回中、角度控制、后续可扩展变焦 |

代码中对应配置：

```python
SIYI_IP = "192.168.144.25"
SIYI_PORT = 37260
```

---

## 2. 协议数据帧格式

SIYI 云台 SDK 协议帧整体结构如下：

```text
55 66 | CTRL | LEN_L LEN_H | SEQ_L SEQ_H | CMD_ID | PAYLOAD... | CRC_L CRC_H
```

| 字节偏移 | 长度 | 字段 | 说明 |
|---:|---:|---|---|
| 0 | 2 | STX | 帧头，固定为 `55 66` |
| 2 | 1 | CTRL | 控制位，常用 `0x01` 表示需要 ACK |
| 3 | 2 | Data_len | 数据区长度，即 payload 长度，小端 |
| 5 | 2 | SEQ | 帧序号，`0 ~ 65535`，小端 |
| 7 | 1 | CMD_ID | 命令 ID |
| 8 | N | DATA | 命令数据区 |
| 8+N | 2 | CRC16 | 对前面完整数据包做 CRC16，小端 |

代码中的构帧逻辑：

```python
header = (
    b"\x55\x66"
    + struct.pack("<B", ctrl)
    + struct.pack("<H", data_len)
    + struct.pack("<H", self.seq)
    + struct.pack("<B", cmd_id)
    + payload
)

crc = crc16_ccitt(header)
packet = header + struct.pack("<H", crc)
```

---

## 3. CTRL 控制位

当前代码中：

```python
ctrl = 0x01 if need_ack else 0x00
```

可以理解为：

| CTRL | 含义 |
|---:|---|
| `0x00` | 不要求 ACK |
| `0x01` | 要求设备返回 ACK |

建议实际控制时默认使用 `need_ack=True`，便于判断命令是否被云台正常接收。

---

## 4. CRC16 校验

当前代码使用的是 CRC16-CCITT。

| 项目 | 值 |
|---|---|
| 算法 | CRC16-CCITT |
| 多项式 | `0x1021` |
| 初始值 | `0x0000` |
| 输入数据 | 从 `STX` 到 `DATA`，不包含最后 CRC 本身 |
| 输出字节序 | 小端，即 `CRC_L CRC_H` |

代码实现：

```python
def crc16_ccitt(data: bytes, crc: int = 0) -> int:
    for b in data:
        crc ^= (b << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc
```

---

## 5. 当前代码已实现的命令

### 5.1 云台速度控制

| 项目 | 内容 |
|---|---|
| CMD_ID | `0x07` |
| 功能 | 控制 yaw / pitch 方向转动速度 |
| payload 长度 | 2 字节 |
| 适用场景 | 闭环跟踪、手动控制、目标居中控制 |

函数：

```python
def rotate_speed(self, yaw_speed: int, pitch_speed: int):
    yaw_speed = max(-100, min(100, yaw_speed))
    pitch_speed = max(-100, min(100, pitch_speed))

    payload = struct.pack("<bb", yaw_speed, pitch_speed)
    self.send(0x07, payload)
```

payload 结构：

| 字段 | 类型 | 范围 | 说明 |
|---|---|---:|---|
| yaw_speed | int8_t | `-100 ~ 100` | yaw 方向速度控制 |
| pitch_speed | int8_t | `-100 ~ 100` | pitch 方向速度控制 |

示例：

```python
gimbal.rotate_speed(30, -10)
```

对应 payload：

```text
1E F6
```

含义：

```text
yaw_speed   = 30
pitch_speed = -10
```

停止云台：

```python
gimbal.rotate_speed(0, 0)
```

---

### 5.2 云台停止

当前停止函数：

```python
def stop(self):
    self.rotate_speed(0, 0)
```

实际发送：

```text
CMD_ID  = 0x07
payload = 00 00
```

说明：

```text
yaw_speed   = 0
pitch_speed = 0
```

在检测/跟踪系统中，停止命令非常重要。比如：

1. 目标丢失；
2. 切换模式；
3. 手动接管；
4. 程序异常退出；
5. 扫描结束。

这些场景下都应该立即发送 `rotate_speed(0, 0)`。

---

### 5.3 一键回中

| 项目 | 内容 |
|---|---|
| CMD_ID | `0x08` |
| 功能 | 云台回中 |
| payload 长度 | 1 字节 |
| 适用场景 | 初始化、异常恢复、搜索开始前归零 |

函数：

```python
def center(self):
    payload = struct.pack("<B", 1)
    self.send(0x08, payload)
```

payload：

| center_pos | 含义 |
|---:|---|
| `1` | 一键回中 |
| `2` | 回中并向下 |
| `3` | 回中 |
| `4` | 向下 |

当前代码发送：

```text
CMD_ID  = 0x08
payload = 01
```

即：

```text
云台一键回中
```

---

### 5.4 指定角度控制

| 项目 | 内容 |
|---|---|
| CMD_ID | `0x0E` |
| 功能 | 设置云台 yaw / pitch 目标角度 |
| payload 长度 | 4 字节 |
| 适用场景 | 区域搜索、固定角度观察、螺旋扫描、预置点控制 |

函数：

```python
def set_angle(self, yaw_deg: float, pitch_deg: float):
    yaw = int(yaw_deg * 10)
    pitch = int(pitch_deg * 10)

    yaw = max(-1350, min(1350, yaw))
    pitch = max(-900, min(250, pitch))

    payload = struct.pack("<hh", yaw, pitch)
    self.send(0x0E, payload)
```

payload 结构：

| 字段 | 类型 | 单位 | A8 Mini 范围 |
|---|---|---|---|
| yaw | int16_t | `0.1°` | `-135.0° ~ 135.0°` |
| pitch | int16_t | `0.1°` | `-90.0° ~ 25.0°` |

例如：

```python
gimbal.set_angle(0, -90)
```

计算结果：

```text
yaw   = 0°    -> 0
pitch = -90°  -> -900
```

小端 payload：

```text
00 00 7C FC
```

---

## 6. ACK 返回帧解析

当前代码只是打印 ACK：

```python
try:
    data, _ = self.sock.recvfrom(1024)
    print("ACK:", " ".join(f"{b:02x}" for b in data))
except socket.timeout:
    pass
```

建议后续改成标准解析：

```python
def parse_packet(data: bytes):
    if len(data) < 10:
        return None

    if data[0:2] != b"\x55\x66":
        return None

    recv_crc = struct.unpack("<H", data[-2:])[0]
    calc_crc = crc16_ccitt(data[:-2])

    if recv_crc != calc_crc:
        print("CRC error")
        return None

    ctrl = data[2]
    data_len = struct.unpack("<H", data[3:5])[0]
    seq = struct.unpack("<H", data[5:7])[0]
    cmd_id = data[7]
    payload = data[8:8 + data_len]

    return {
        "ctrl": ctrl,
        "data_len": data_len,
        "seq": seq,
        "cmd_id": cmd_id,
        "payload": payload,
    }
```

建议解析字段：

| 字段 | 作用 |
|---|---|
| STX | 判断是否为 `55 66` |
| CTRL | 判断是否为 ACK 包 |
| Data_len | 获取返回 payload 长度 |
| SEQ | 对应发送序号 |
| CMD_ID | 对应哪个命令 |
| DATA | 状态或角度信息 |
| CRC16 | 判断返回帧是否有效 |

---

## 7. 当前螺旋扫描逻辑

当前扫描函数核心逻辑：

```python
yaw = center_yaw + yaw_amp * r * math.cos(theta)
pitch = center_pitch + pitch_amp * r * math.sin(theta)
```

完整流程：

```text
时间 t
  ↓
半径 r 从 0 增大到 1，再从 1 缩回 0
  ↓
theta = omega * t
  ↓
yaw   = center_yaw   + yaw_amp   * r * cos(theta)
pitch = center_pitch + pitch_amp * r * sin(theta)
  ↓
限幅
  ↓
发送 set_angle(yaw, pitch)
```

因此该扫描属于：

```text
基于角度指令的椭圆螺旋扫描
```

适合：

```text
搜索 / 巡扫 / 预设区域扫描 / 数据采集
```

不太适合：

```text
高速闭环跟踪
```

因为高速闭环跟踪更需要根据图像中心误差实时调节速度。

---

## 8. 扫描参数说明

函数定义：

```python
def spiral_scan(
    gimbal,
    center_yaw=0.0,
    center_pitch=-25.0,
    yaw_amp=80.0,
    pitch_amp=35.0,
    yaw_limit=120.0,
    pitch_min=-80.0,
    pitch_max=15.0,
    step_time=0.1,
    omega=0.8,
    grow_time=15.0,
):
```

参数表：

| 参数 | 默认值 | 含义 |
|---|---:|---|
| center_yaw | `0.0` | 扫描中心 yaw 角 |
| center_pitch | `-25.0` | 扫描中心 pitch 角 |
| yaw_amp | `80.0` | yaw 最大扫描幅度 |
| pitch_amp | `35.0` | pitch 最大扫描幅度 |
| yaw_limit | `120.0` | yaw 最大限幅 |
| pitch_min | `-80.0` | pitch 最小角度 |
| pitch_max | `15.0` | pitch 最大角度 |
| step_time | `0.1` | 每次发送控制指令的间隔 |
| omega | `0.8` | 角速度，控制扫描快慢 |
| grow_time | `15.0` | 半径从 0 增长到最大所需时间 |

建议：

| 场景 | step_time | omega | grow_time |
|---|---:|---:|---:|
| 慢速观察 | `0.15 ~ 0.3` | `0.3 ~ 0.6` | `20 ~ 40` |
| 常规搜索 | `0.08 ~ 0.15` | `0.6 ~ 1.0` | `10 ~ 20` |
| 快速搜索 | `0.05 ~ 0.1` | `1.0 ~ 1.5` | `5 ~ 10` |

---

## 9. 推荐的控制模式划分

后续如果要接入 YOLO26 + AsymTrack，建议把控制模式分成以下几类：

| 模式 | 输入 | 输出 | 推荐命令 |
|---|---|---|---|
| 初始化 | 程序启动 | 云台回中 | `0x08` |
| 搜索扫描 | 时间轨迹 | 目标角度 | `0x0E` |
| 检测接管 | YOLO 检测框 | 云台速度 | `0x07` |
| 跟踪控制 | AsymTrack 目标框 | 云台速度 | `0x07` |
| 跟踪丢失 | lost 状态 | 停止 / 重新搜索 | `0x07` + `0x0E` |
| 人工接管 | GUI 指令 | 速度或角度 | `0x07` / `0x0E` |
| 数据录制 | 图像 + 状态 | 训练样本 | 记录日志 |

---

## 10. YOLO / AsymTrack 闭环控制建议

图像坐标误差：

```text
err_x = target_cx - image_w / 2
err_y = target_cy - image_h / 2
```

归一化：

```text
norm_x = err_x / (image_w / 2)
norm_y = err_y / (image_h / 2)
```

映射为速度：

```python
yaw_speed = int(k_yaw * norm_x)
pitch_speed = int(k_pitch * norm_y)
```

限幅：

```python
yaw_speed = clamp(yaw_speed, -100, 100)
pitch_speed = clamp(pitch_speed, -100, 100)
```

发送：

```python
gimbal.rotate_speed(yaw_speed, pitch_speed)
```

建议加入死区，避免目标接近中心时云台抖动：

```python
if abs(norm_x) < 0.03:
    yaw_speed = 0

if abs(norm_y) < 0.03:
    pitch_speed = 0
```

---

## 11. 后续建议补充的协议接口

目前代码已经实现了最小可用控制链路，后续建议继续补充：

| 功能 | 建议函数 | 说明 |
|---|---|---|
| ACK 解析 | `parse_packet()` | 校验返回帧 |
| 查询姿态 | `get_attitude()` | 获取 yaw / pitch / roll |
| 光学变焦 | `zoom_in()` / `zoom_out()` | 用于目标细节观察 |
| 停止变焦 | `zoom_stop()` | 防止持续变焦 |
| 绝对变焦 | `set_zoom()` | 适合自动跟踪阶段 |
| 数据记录 | `log_state()` | 记录图像、bbox、云台角度、动作 |
| 异常保护 | `safe_stop()` | 程序退出时强制停止云台 |

---

## 12. 建议工程结构

后续可以整理成如下工程结构：

```text
siyi_a8mini_control/
├── siyi_protocol.py          # 协议封包、CRC、ACK解析
├── siyi_gimbal.py            # 云台控制接口
├── scan_policy.py            # 螺旋扫描、网格扫描、扇区扫描
├── visual_servo.py           # 视觉闭环控制
├── tracker_node.py           # YOLO + AsymTrack 对接
├── recorder.py               # 数据录制
├── gui_control.py            # GUI 控制
└── main.py                   # 主程序入口
```

---

## 13. 推荐主循环伪代码

```python
while True:
    frame = camera.read()

    if mode == "SCAN":
        yaw, pitch = scan_policy.next_angle()
        gimbal.set_angle(yaw, pitch)

        det = yolo.detect(frame)
        if det is not None:
            tracker.init(frame, det.bbox)
            mode = "TRACK"

    elif mode == "TRACK":
        ok, bbox = tracker.track(frame)

        if ok:
            cx, cy = bbox_center(bbox)
            yaw_speed, pitch_speed = visual_servo(cx, cy, frame.shape)
            gimbal.rotate_speed(yaw_speed, pitch_speed)
        else:
            gimbal.stop()
            mode = "SCAN"

    recorder.write(
        frame=frame,
        mode=mode,
        bbox=bbox,
        yaw_speed=yaw_speed,
        pitch_speed=pitch_speed,
    )
```

---

## 14. 当前代码的核心结论

当前代码已经完成：

```text
1. SIYI UDP 控制链路
2. 协议帧构建
3. CRC16 校验
4. 云台速度控制
5. 云台停止
6. 云台回中
7. 云台指定角度控制
8. 基于角度控制的螺旋扫描
```

后续要做专家系统、YOLO26 检测、AsymTrack 跟踪、LeRobot 数据录制，建议以当前协议层为基础继续扩展：

```text
图像输入
  ↓
YOLO26 检测
  ↓
目标选择 / 专家规则
  ↓
AsymTrack 跟踪
  ↓
目标中心误差
  ↓
yaw / pitch 速度控制
  ↓
SIYI UDP 协议发送
  ↓
云台运动
  ↓
同步记录图像、bbox、云台角度、控制动作
```

---

## 15. 参考命令速查表

| 功能 | CMD_ID | Payload | 推荐用途 |
|---|---:|---|---|
| 云台速度控制 | `0x07` | `int8 yaw_speed + int8 pitch_speed` | 跟踪闭环 |
| 云台停止 | `0x07` | `00 00` | 安全停止 |
| 一键回中 | `0x08` | `01` | 初始化 |
| 指定角度 | `0x0E` | `int16 yaw + int16 pitch` | 搜索扫描 |
| 查询姿态 | `0x0D` | 待补充 | 状态反馈 |
| 光学变焦 | 待补充 | 待补充 | 自动观察 / 跟踪增强 |

---

# 附录：当前代码中的关键点

## A. 为什么 angle 要乘以 10？

因为 SIYI 协议中角度单位是 `0.1°`。

所以：

```text
1.0°   -> 10
10.0°  -> 100
-90.0° -> -900
```

代码：

```python
yaw = int(yaw_deg * 10)
pitch = int(pitch_deg * 10)
```

---

## B. 为什么 payload 用 `<hh>`？

```python
payload = struct.pack("<hh", yaw, pitch)
```

含义：

| 符号 | 含义 |
|---|---|
| `<` | 小端序 |
| `h` | int16_t |
| `h` | int16_t |

即：

```text
yaw   -> int16_t
pitch -> int16_t
```

---

## C. 为什么速度控制用 `<bb>`？

```python
payload = struct.pack("<bb", yaw_speed, pitch_speed)
```

含义：

| 符号 | 含义 |
|---|---|
| `<` | 小端序 |
| `b` | int8_t |
| `b` | int8_t |

即：

```text
yaw_speed   -> int8_t
pitch_speed -> int8_t
```

---

## D. 为什么程序退出时要 stop + center？

当前代码中：

```python
except KeyboardInterrupt:
    print("\n停止螺旋扫描")
    gimbal.stop()
    time.sleep(0.2)
    gimbal.center()
```

这是合理的安全策略：

```text
1. 先 stop，避免云台继续转；
2. 等待一小段时间；
3. 再 center，回到安全初始姿态。
```
