from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
import onnxruntime as ort

from .common import Detection


@dataclass
class LetterboxMeta:
    scale: float
    pad_x: float
    pad_y: float
    input_w: int
    input_h: int
    orig_w: int
    orig_h: int


def nms_xyxy(boxes: np.ndarray, scores: np.ndarray, iou_thr: float) -> list[int]:
    if len(boxes) == 0:
        return []
    x1, y1, x2, y2 = boxes.T
    areas = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)
    order = scores.argsort()[::-1]
    keep: list[int] = []
    while order.size:
        i = int(order[0])
        keep.append(i)
        if order.size == 1:
            break
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])
        inter = np.maximum(0, xx2 - xx1) * np.maximum(0, yy2 - yy1)
        union = areas[i] + areas[order[1:]] - inter
        iou = inter / np.maximum(union, 1e-6)
        order = order[1:][iou <= iou_thr]
    return keep


class ISRONNXDetector:
    def __init__(
        self,
        model_path: str,
        conf: float = 0.25,
        iou: float = 0.45,
        classes: list[int] | None = None,
        providers: list[str] | None = None,
    ) -> None:
        providers = providers or ["CUDAExecutionProvider", "CPUExecutionProvider"]
        available = ort.get_available_providers()
        providers = [p for p in providers if p in available] or ["CPUExecutionProvider"]
        self.session = ort.InferenceSession(model_path, providers=providers)
        self.input = self.session.get_inputs()[0]
        shape = self.input.shape
        self.input_h = int(shape[2])
        self.input_w = int(shape[3])
        self.conf = conf
        self.iou = iou
        self.classes = set(classes) if classes is not None else None

    def detect(self, frame) -> list[Detection]:
        x, meta = self._preprocess(frame)
        out = self.session.run(None, {self.input.name: x})[0]
        pred = out[0].T
        return self._postprocess(pred, meta)

    def _preprocess(self, frame):
        orig_h, orig_w = frame.shape[:2]
        scale = min(self.input_w / orig_w, self.input_h / orig_h)
        new_w, new_h = int(round(orig_w * scale)), int(round(orig_h * scale))
        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        canvas = np.full((self.input_h, self.input_w, 3), 114, dtype=np.uint8)
        pad_x = (self.input_w - new_w) // 2
        pad_y = (self.input_h - new_h) // 2
        canvas[pad_y : pad_y + new_h, pad_x : pad_x + new_w] = resized
        rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        chw = np.transpose(rgb, (2, 0, 1))[None]
        return np.ascontiguousarray(chw), LetterboxMeta(scale, pad_x, pad_y, self.input_w, self.input_h, orig_w, orig_h)

    def _postprocess(self, pred: np.ndarray, meta: LetterboxMeta) -> list[Detection]:
        if pred.shape[1] < 6:
            return []
        # Supports both YOLOv8-style [xywh, cls...] and YOLOv5-style [xywh, obj, cls...].
        cls_scores_v8 = pred[:, 4:]
        best_v8 = cls_scores_v8.max(axis=1)
        obj = pred[:, 4:5]
        cls_scores_v5 = pred[:, 5:] * obj if pred.shape[1] > 6 else cls_scores_v8
        best_v5 = cls_scores_v5.max(axis=1)
        use_v5 = float(np.nanmax(best_v5)) > float(np.nanmax(best_v8)) * 1.2
        scores_mat = cls_scores_v5 if use_v5 else cls_scores_v8
        scores = scores_mat.max(axis=1)
        cls_ids = scores_mat.argmax(axis=1)
        mask = scores >= self.conf
        if self.classes is not None:
            mask &= np.isin(cls_ids, list(self.classes))
        if not np.any(mask):
            return []

        rows = pred[mask]
        scores = scores[mask]
        cls_ids = cls_ids[mask]
        cx, cy, w, h = rows[:, 0], rows[:, 1], rows[:, 2], rows[:, 3]
        x1 = (cx - w * 0.5 - meta.pad_x) / meta.scale
        y1 = (cy - h * 0.5 - meta.pad_y) / meta.scale
        x2 = (cx + w * 0.5 - meta.pad_x) / meta.scale
        y2 = (cy + h * 0.5 - meta.pad_y) / meta.scale
        boxes = np.stack(
            [
                np.clip(x1, 0, meta.orig_w - 1),
                np.clip(y1, 0, meta.orig_h - 1),
                np.clip(x2, 0, meta.orig_w - 1),
                np.clip(y2, 0, meta.orig_h - 1),
            ],
            axis=1,
        )
        keep_all: list[int] = []
        for cls_id in sorted(set(int(c) for c in cls_ids.tolist())):
            idx = np.where(cls_ids == cls_id)[0]
            keep_all.extend(idx[i] for i in nms_xyxy(boxes[idx], scores[idx], self.iou))
        keep_all = sorted(keep_all, key=lambda i: float(scores[i]), reverse=True)
        return [
            Detection(
                cls_id=int(cls_ids[i]),
                cls_name=str(int(cls_ids[i])),
                conf=float(scores[i]),
                bbox_xyxy=tuple(float(v) for v in boxes[i]),
            )
            for i in keep_all
        ]
