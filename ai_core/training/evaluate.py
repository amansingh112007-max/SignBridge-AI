"""Held-out evaluation on images the model NEVER trained on.
The extractor's used_files.json manifest defines what is 'seen';
everything else in the train pool is a legitimate unseen test image.
(Caveat, stated honestly: same signer as training data.)"""
import argparse
import json
import os
import sys
import random
import cv2
import numpy as np
import torch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.tracker import KeypointTracker
from app.services.model import LSTMModel

SEQ_LEN = 30
IMG_EXT = ('.jpg', '.jpeg', '.png')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--train', default='dataset/asl_alphabet_train/asl_alphabet_train')
    ap.add_argument('--exclude', default='dataset/processed/used_files.json')
    ap.add_argument('--per-class', type=int, default=50)
    args = ap.parse_args()

    models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    with open(os.path.join(models_dir, 'classes.json')) as f:
        classes = json.load(f)

    model = LSTMModel(260, 64, 2, len(classes))
    model.load_state_dict(torch.load(os.path.join(models_dir, 'signbridge_lstm.pth'),
                                     map_location='cpu'))
    model.eval()

    used = set()
    if os.path.exists(args.exclude):
        with open(args.exclude) as f:
            used = {os.path.normpath(p) for p in json.load(f)}
    else:
        print('⚠️ No manifest found - run extract_dataset.py v2 first!')
        return

    tracker = KeypointTracker()

    # collect UNSEEN images per class
    files_per_class = {name: [] for name in classes}
    for dirpath, _, filenames in os.walk(args.train):
        folder_name = os.path.basename(dirpath)
        if folder_name not in files_per_class:
            continue
        for fn in filenames:
            if not fn.lower().endswith(IMG_EXT):
                continue
            p = os.path.normpath(os.path.join(dirpath, fn))
            if p not in used:
                files_per_class[folder_name].append(p)

        random.seed(7)                      # reproducible, unbiased test slice
    y_true, y_pred = [], []
    for ci, name in enumerate(classes):
        pool = files_per_class[name]
        random.shuffle(pool)
        imgs = pool[:args.per_class] 
        taken = 0
        for path in imgs:
            img = cv2.imread(path)
            if img is None:
                continue
            kp, _ = tracker.process_frame(img)
            if kp is None:
                continue
            seq = np.repeat(kp[None, :], SEQ_LEN, axis=0).astype(np.float32)
            with torch.no_grad():
                out = model(torch.tensor(seq).unsqueeze(0))
            y_true.append(ci)
            y_pred.append(int(out.argmax(1)))
            taken += 1
        print(f'  evaluated {name:>8}: {taken} unseen test samples')

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    if len(y_true) == 0:
        print('❌ No unseen samples found - check --train / --exclude paths')
        return

    acc = float((y_true == y_pred).mean())
    cm = np.zeros((len(classes), len(classes)), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1

    lines = [
        f'Held-out TEST accuracy (unseen images, same signer): {acc:.1%}',
        f'Test samples: {len(y_true)}',
        '',
        'Per-class recall:',
    ]
    for ci, name in enumerate(classes):
        tot = int(cm[ci].sum())
        rec = cm[ci, ci] / tot if tot else 0.0
        lines.append(f'  {name:>8}: {rec:6.1%}  ({cm[ci, ci]}/{tot})')
    lines += ['', 'Confusion matrix (rows=true, cols=predicted):']
    lines.append(' ' * 10 + ' '.join(f'{c[:4]:>5}' for c in classes))
    for ci, name in enumerate(classes):
        lines.append(f'{name:>10}' + ' '.join(f'{v:5d}' for v in cm[ci]))

    report = '\n'.join(lines)
    print('\n' + report)

    reports = os.path.join(os.path.dirname(__file__), '..', 'reports')
    os.makedirs(reports, exist_ok=True)
    with open(os.path.join(reports, 'eval_report.txt'), 'w') as f:
        f.write(report + '\n')
    np.save(os.path.join(reports, 'confusion_matrix.npy'), cm)
    print('\n💾 Saved reports/eval_report.txt and reports/confusion_matrix.npy')


if __name__ == '__main__':
    main()