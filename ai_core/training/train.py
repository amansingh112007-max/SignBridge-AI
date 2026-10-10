"""Trains the LSTM on extracted keypoint sequences and saves the best weights.
v2: longer training + class-weighted loss + online jitter augmentation + LR scheduler."""
import argparse
import json
import os
import sys

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.model import LSTMModel   # MUST match production architecture


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True)
    ap.add_argument('--epochs', type=int, default=40)
    ap.add_argument('--batch', type=int, default=32)
    ap.add_argument('--noise', type=float, default=0.01,
                    help='online jitter augmentation strength')
    args = ap.parse_args()

    X = np.load(os.path.join(args.data, 'keypoints.npy'))
    y = np.load(os.path.join(args.data, 'labels.npy'))
    with open(os.path.join(args.data, 'classes.json')) as f:
        classes = json.load(f)
    print(f'Loaded {X.shape[0]} samples, {len(classes)} classes')

    # ---- class weights: rare letters matter as much as common ones ----
    counts = np.bincount(y, minlength=len(classes)).astype(np.float64)
    counts[counts == 0] = 1.0
    w = (1.0 / counts)
    w = w / w.sum() * len(classes)
    class_w = torch.tensor(w, dtype=torch.float32)
    print('Class weights:', {classes[i]: round(float(w[i]), 2) for i in range(len(classes))})

    # 80/20 train/validation split
    idx = np.random.permutation(len(X))
    cut = int(0.8 * len(X))
    tr, va = idx[:cut], idx[cut:]

    tr_loader = DataLoader(TensorDataset(torch.tensor(X[tr]), torch.tensor(y[tr])),
                           batch_size=args.batch, shuffle=True)
    va_loader = DataLoader(TensorDataset(torch.tensor(X[va]), torch.tensor(y[va])),
                           batch_size=args.batch)

    # SAME architecture as production: input 258, hidden 64, 2 layers
    model = LSTMModel(X.shape[2], 64, 2, len(classes))
    crit = nn.CrossEntropyLoss(weight=class_w)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    sched = torch.optim.lr_scheduler.StepLR(opt, step_size=15, gamma=0.5)

    out_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    os.makedirs(out_dir, exist_ok=True)
    best = 0.0

    for epoch in range(args.epochs):
        # ---- training pass (with online jitter augmentation) ----
        model.train()
        loss_sum = correct = total = 0
        for xb, yb in tr_loader:
            if args.noise > 0:
                xb = xb + torch.randn_like(xb) * args.noise   # fresh jitter every epoch
            opt.zero_grad()
            out = model(xb)
            loss = crit(out, yb)
            loss.backward()
            opt.step()
            loss_sum += loss.item() * len(xb)
            correct += (out.argmax(1) == yb).sum().item()
            total += len(xb)
        tr_acc = correct / total
        sched.step()

        # ---- validation pass ----
        model.eval()
        vc = vt = 0
        with torch.no_grad():
            for xb, yb in va_loader:
                vc += (model(xb).argmax(1) == yb).sum().item()
                vt += len(xb)
        va_acc = vc / vt

        print(f'epoch {epoch+1:02d} | loss {loss_sum/total:.3f} | '
              f'train acc {tr_acc:.1%} | val acc {va_acc:.1%}')

        if va_acc > best:
            best = va_acc
            torch.save(model.state_dict(), os.path.join(out_dir, 'signbridge_lstm.pth'))
            with open(os.path.join(out_dir, 'classes.json'), 'w') as f:
                json.dump(classes, f)
            print('   💾 saved new best weights')

    print(f'🎉 Done. Best validation accuracy: {best:.1%}')


if __name__ == '__main__':
    main()