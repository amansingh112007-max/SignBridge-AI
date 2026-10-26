"""
Turns a Kaggle dataset (class folders of images or videos) into keypoint
sequences our LSTM can learn from. Uses the SAME tracker as the live
backend -> zero train/serve skew. v2: writes used_files.json manifest
so evaluate.py can build a clean held-out test set.
"""
import argparse
import json
import os
import random
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.tracker import KeypointTracker

IMG_EXT = ('.jpg', '.jpeg', '.png')
VID_EXT = ('.mp4', '.avi', '.mov')
SEQ_LEN = 30   # must match GestureModel.sequence_length


def find_class_folders(root):
    classes = {}
    for dirpath, _, filenames in os.walk(root):
        if any(f.lower().endswith(IMG_EXT + VID_EXT) for f in filenames):
            classes[os.path.basename(dirpath)] = dirpath
    return classes


def seq_from_image(tracker, path):
    img = cv2.imread(path)
    if img is None:
        return None
    kp, _ = tracker.process_frame(img)
    if kp is None:
        return None
    jitter = np.random.normal(0, 0.003, (SEQ_LEN, kp.shape[0]))
    return kp[None, :] + jitter


def seq_from_video(tracker, path):
    cap = cv2.VideoCapture(path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total < SEQ_LEN:
        cap.release()
        return None
    targets = np.linspace(0, total - 1, SEQ_LEN).astype(int)
    seq, fi, ptr = [], 0, 0
    while ptr < SEQ_LEN:
        ret, frame = cap.read()
        if not ret:
            break
        if fi == targets[ptr]:
            kp, _ = tracker.process_frame(frame)
            if kp is None:
                cap.release()
                return None
            seq.append(kp)
            ptr += 1
        fi += 1
    cap.release()
    return np.array(seq) if len(seq) == SEQ_LEN else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--per-class', type=int, default=100)
    args = ap.parse_args()

    random.seed(42)
    tracker = KeypointTracker()
    folders = find_class_folders(args.data)
    classes = sorted(folders.keys())
    print(f'Found {len(classes)} classes: {classes}')

    X, y, used = [], [], []
    for ci, name in enumerate(classes):
        files = os.listdir(folders[name])
        imgs = [f for f in files if f.lower().endswith(IMG_EXT)]
        vids = [f for f in files if f.lower().endswith(VID_EXT)]
        random.shuffle(imgs)
        random.shuffle(vids)
        taken = 0
        for v in vids:
            if taken >= args.per_class:
                break
            s = seq_from_video(tracker, os.path.join(folders[name], v))
            if s is not None:
                X.append(s); y.append(ci); taken += 1
                used.append(os.path.normpath(os.path.join(folders[name], v)))
        for p in imgs:
            if taken >= args.per_class:
                break
            s = seq_from_image(tracker, os.path.join(folders[name], p))
            if s is not None:
                X.append(s); y.append(ci); taken += 1
                used.append(os.path.normpath(os.path.join(folders[name], p)))
        print(f'  class {name:>6}: {taken} samples')

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int64)
    os.makedirs(args.out, exist_ok=True)
    np.save(os.path.join(args.out, 'keypoints.npy'), X)
    np.save(os.path.join(args.out, 'labels.npy'), y)
    with open(os.path.join(args.out, 'classes.json'), 'w') as f:
        json.dump(classes, f)
    with open(os.path.join(args.out, 'used_files.json'), 'w') as f:
        json.dump(used, f)
    print(f'✅ Dataset saved: {X.shape[0]} samples, shape {X.shape}')
    print(f'📜 Manifest saved: {len(used)} files listed in used_files.json')


if __name__ == '__main__':
    main()