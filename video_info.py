import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as bpdf

import cv2
import torch

from pathlib import Path


PERIOD = 5000 # msec
MODEL = torch.hub.load('yolov5-master', 'custom', path='model3/weights/best.pt', source='local')


def smoothing(series):
    ln = len(series)
    series = pd.Series([0, 0, 0]).add(series.groupby(series).count(),  fill_value=0)
    if series[2]/ln >= 0.2:
        return 2
    if series[2] > 0:
        return 1
    if series[0]/ln >= 0.6:
        return 0
    return 1


def smooth_data(data):
    return data[["left_state", "right_state"]].rolling(window=9, min_periods=0, center=True).apply(smoothing).astype("int8")


def to_periods(data):
    def shorter(data):
        d = {}
        d['time_start'] = data.iloc[:, 0].min()
        d['state'] = data.iloc[:, 1].min()
        return pd.Series(d, index=['time_start', 'state'])

    grouped =  data.groupby(data.iloc[:, 1].diff().ne(0).cumsum())
    grouped = grouped.apply(shorter)
    grouped = grouped.drop(grouped[(-grouped["time_start"].diff(-1)).fillna(10**6) < 30].index).reset_index(drop=True)
    grouped = grouped.groupby(grouped.iloc[:, 1].diff().ne(0).cumsum())
    grouped = grouped.apply(shorter)
    return grouped.reset_index(drop=True)


def get_frame_info(frame):
    def df_to_state(pd):
        if (pd["class"] == 0).any():
            return 2
        if (pd["class"] == 1).any():
            return 1
        return 0

    width = frame.shape[1]
    left, right = frame[:, :width // 2], frame[:, width // 2:]
    result = MODEL([left, right])
    left_res, right_res = result.pandas().xyxy
    return df_to_state(left_res), df_to_state(right_res)


def get_video_info(path):
    vd = cv2.VideoCapture(path)

    fps = vd.get(cv2.CAP_PROP_FPS)
    frame_count = int(vd.get(cv2.CAP_PROP_FRAME_COUNT))
    final_len = int(frame_count / fps) * 1000 // PERIOD + 10

    frames_data = pd.DataFrame(data=np.full((final_len, 3), -1), columns=["time", "left_state", "right_state"])
    last = -1
    while True:
        frame_pos = int(vd.get(cv2.CAP_PROP_POS_FRAMES))
        frame_time = int(vd.get(cv2.CAP_PROP_POS_MSEC))
        ret, frame = vd.read()

        if not ret:
            break
        if frame_time // PERIOD <= last:
            continue

        last += 1
        left_info, right_info = get_frame_info(frame)
        frames_data.loc[last] = [int(frame_time), left_info, right_info]
    vd.release()

    frames_data.dropna(inplace=True)
    frame_data.drop(b[b["time"] == -1])
    frame_data[["left_state", "right_state"]] = smooth_data(frame_data)

    left_part = frame_data[["time", "left_state"]]
    right_part = frame_data[["time", "right_state"]]

    left_part = to_periods(left_part)
    right_part = to_periods(right_part)

    left_part["time_start"] = pd.to_datetime(left_part["time_start"], unit="s").dt.time
    right_part["time_start"] = pd.to_datetime(right_part["time_start"], unit="s").dt.time

    path = Path(path)
    save_path = path.parent / (path.stem + ' info')
    save_path.mkdir()

    left_part["state"] = left_part["state"].apply(apply_labels)
    right_part["state"] = right_part["state"].apply(apply_labels)
    with pd.ExcelWriter(str(save_path / 'periods info.xlsx')) as writer:
        left_part.to_excel(writer, sheet_name='Left cam', index=False)
        right_part.to_excel(writer, sheet_name='Right cam', index=False)
