# Push-up Counter - Code Documentation

A computer vision application that automatically counts push-ups using MediaPipe pose estimation and Phoenix tracing for performance monitoring.

## Code Architecture Overview

The application follows a pipeline architecture with three main components:
1. **Pose Detection Pipeline** - MediaPipe pose estimation
2. **Angle Calculation Engine** - Geometric analysis of joint positions
3. **Counting State Machine** - Push-up detection logic
4. **Tracing System** - Phoenix observability integration

## Core Components

### 1. Dependencies and Initialization

```python
import mediapipe as mp
import cv2
import numpy as np
import phoenix as px
from opentelemetry import trace
from phoenix.otel import register
```

**MediaPipe Setup:**
```python
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
```
- `mp_pose.Pose()` creates the pose estimation model
- `mp_drawing` handles visualization of pose landmarks
- The pose model detects 33 body landmarks in 3D space

**Phoenix Tracing Setup:**
```python
px.launch_app(port=6006)
tracer_provider = register(
    project_name="pushup-app",
    endpoint="http://localhost:6006/v1/traces",
    batch=False
)
```
- Launches Phoenix dashboard on port 6006
- `batch=False` sends traces immediately for real-time monitoring
- Creates a tracer for instrumenting the pipeline

### 2. Angle Calculation Function

```python
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b) 
    c = np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle
```

**Mathematical Explanation:**
- Takes three points: `a` (shoulder), `b` (elbow), `c` (wrist)
- Calculates vectors: `ba` and `bc`
- Uses `arctan2` to find angles of both vectors relative to horizontal
- Subtracts angles to get the angle between vectors
- Converts from radians to degrees
- Ensures angle is between 0-180° (acute/obtuse only)

**Vector Math:**
- `arctan2(y, x)` returns angle in radians from positive x-axis
- The difference gives the interior angle at point `b` (elbow)
- `np.abs()` ensures positive angle measurement

### 3. Frame Processing Pipeline

```python
def process_frame_pipeline(frame):
    global counter, stage
    
    # Color space conversion
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image_rgb.flags.writeable = False
    
    # Pose detection
    results = pose.process(image_rgb)
```

**Color Space Handling:**
- OpenCV uses BGR, MediaPipe expects RGB
- `writeable = False` optimizes performance by preventing array copying
- `results.pose_landmarks` contains 33 landmark points if detection succeeds

**Landmark Extraction:**
```python
if results.pose_landmarks:
    landmarks = results.pose_landmarks.landmark
    shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
    elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
             landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
    wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
             landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
```

**Coordinate System:**
- Landmarks are normalized: x,y values between 0-1
- Origin (0,0) is top-left corner
- Right side landmarks used for consistency
- Each landmark has `.x`, `.y`, `.z` coordinates plus visibility score

### 4. Push-up Detection State Machine

```python
# Push-up counter logic
if angle > 160:
    stage = "up"
if angle < 70 and stage == "up":
    stage = "down"
    counter += 1
    print(f"Push-up Count: {counter}")
```

**State Machine Logic:**
- **"up" state**: Arms extended, elbow angle > 160°
- **"down" state**: Arms bent, elbow angle < 70°
- **Counting trigger**: Transition from "up" → "down"
- **Prevents double counting**: Requires "up" state before counting "down"

**Threshold Selection:**
- `160°`: Near-straight arm position (allows slight bend)
- `70°`: Significantly bent arm (proper push-up depth)
- Hysteresis prevents noise from causing false counts

### 5. Visualization and UI

```python
# Angle display
cv2.putText(image_bgr, str(int(angle)),
            tuple(np.multiply(elbow, [640, 480]).astype(int)),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

# Counter UI
cv2.rectangle(image_bgr, (0, 0), (225, 73), (245, 117, 16), -1)
cv2.putText(image_bgr, 'Push-ups', (15, 12),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
cv2.putText(image_bgr, str(counter), (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

# Pose skeleton
mp_drawing.draw_landmarks(image_bgr, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
```

**Coordinate Transformation:**
- `np.multiply(elbow, [640, 480])`: Converts normalized coordinates to pixel coordinates
- Assumes video resolution of 640x480 (adjust as needed)
- `astype(int)`: OpenCV requires integer pixel coordinates

**UI Elements:**
- **Rectangle**: Colored background for counter display
- **Text overlay**: Shows current count and label
- **Pose skeleton**: Connects landmarks with lines to show body pose

### 6. Phoenix Tracing Integration

```python
pipeline_attrs = {
    "landmarks_detected": False,
    "shoulder": None,
    "elbow": None, 
    "wrist": None,
    "angle": None,
    "counter": counter,
    "stage": stage,
}

# Later in the pipeline...
with tracer.start_as_current_span("pushup_pipeline") as span:
    image, attrs = process_frame_pipeline(frame)
    for key, val in attrs.items():
        if isinstance(val, list):
            val = [float(x) for x in val]
        span.set_attribute(key, val)
```

**Tracing Data Collection:**
- **Structured attributes**: Each frame creates a span with metadata
- **Performance metrics**: Track processing time per frame
- **Debug information**: Joint coordinates, angles, detection success
- **State tracking**: Monitor counter and stage transitions

**Data Flattening:**
- Lists converted to float arrays for OpenTelemetry compatibility
- Attributes stored as key-value pairs for analysis

### 7. Main Execution Loop

```python
def main(video_path):
    cap = cv2.VideoCapture(video_path)
    global counter, stage
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        with tracer.start_as_current_span("pushup_pipeline") as span:
            image, attrs = process_frame_pipeline(frame)
            # ... tracing code ...
            
        cv2.imshow('Push-up Counter', image)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
```

**Video Processing Flow:**
1. **Frame capture**: `cap.read()` gets next frame
2. **Processing**: Run through pose detection pipeline  
3. **Tracing**: Wrap processing in OpenTelemetry span
4. **Display**: Show processed frame with overlays
5. **Control**: Check for 'q' key to exit

**Frame Rate Control:**
- `cv2.waitKey(10)`: 10ms delay between frames (~100 FPS max)
- Adjust delay to match video frame rate or processing capability

## Algorithm Flow

1. **Input**: Video frame (BGR format)
2. **Preprocessing**: Convert BGR → RGB, set read-only flag
3. **Pose Detection**: MediaPipe extracts 33 body landmarks
4. **Joint Extraction**: Get shoulder, elbow, wrist coordinates
5. **Angle Calculation**: Compute elbow angle using vector math
6. **State Machine**: Update "up"/"down" state based on angle
7. **Counting**: Increment counter on state transitions
8. **Visualization**: Draw UI elements and pose skeleton
9. **Tracing**: Record metrics and debug information
10. **Output**: Processed frame with annotations

## Performance Considerations

**Optimization Techniques:**
- `image_rgb.flags.writeable = False`: Prevents unnecessary memory copying
- Global variables for counter/stage: Avoids parameter passing overhead
- Normalized coordinates: Reduces computation in coordinate transforms
- Single span per frame: Minimizes tracing overhead

**Bottlenecks:**
- **Pose detection**: Most computationally expensive step
- **Video I/O**: Reading/displaying frames
- **Memory allocation**: Array conversions and copying

## Error Handling

```python
try:
    if results.pose_landmarks:
        # ... pose processing ...
except Exception as e:
    pipeline_attrs["error.message"] = str(e)
```

The code includes basic exception handling that captures errors in the pose processing pipeline and records them in tracing attributes for debugging.