# mac_parallel_video_gui.py

import sys
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton, QFileDialog
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPixmap, QImage


class VideoColumnProcessor:
    """멀티스레드로 각 영상에서 컬럼 추출"""
    def __init__(self, step_list):
        self.steps = step_list
        self.executor = ThreadPoolExecutor(max_workers=len(step_list))

    def extract_columns_parallel(self, frames):
        futures = [
            self.executor.submit(self.extract_columns, frames[i], self.steps[i])
            if frames[i] is not None else None
            for i in range(len(frames))
        ]
        return [f.result() if f else None for f in futures]

    @staticmethod
    def extract_columns(frame, step):
        return frame[:, ::step, :]  # 컬럼 추출 (1,2,3,4 배수)


class VideoColumnPlayer(QWidget):
    """영상 재생기: 4개의 영상을 병렬로 컬럼 추출 및 표시"""
    def __init__(self, video_paths, step_list, parent=None):
        super().__init__(parent)
        self.video_caps = [cv2.VideoCapture(p) for p in video_paths]
        self.processor = VideoColumnProcessor(step_list)
        self.labels = [QLabel() for _ in video_paths]

        layout = QVBoxLayout()
        for lbl in self.labels:
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(33)  # 30fps

    def next_frame(self):
        frames = []
        for cap in self.video_caps:
            ret, frame = cap.read()
            if not ret:
                frames.append(None)
                continue
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(rgb)

        processed_frames = self.processor.extract_columns_parallel(frames)

        for i, proc in enumerate(processed_frames):
            if proc is None:
                continue
            resized = cv2.resize(proc, (640, 360))  # GUI 표시용 축소
            qimg = QImage(resized.data, resized.shape[1], resized.shape[0], QImage.Format.Format_RGB888)
            pix = QPixmap.fromImage(qimg)
            self.labels[i].setPixmap(pix)

    def closeEvent(self, event):
        for cap in self.video_caps:
            cap.release()


class MainWindow(QMainWindow):
    """메인 윈도우: 영상 선택 및 플레이어 로드"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎬 Mac용 고성능 병렬 영상 처리")
        self.setGeometry(100, 100, 800, 1000)

        self.load_button = QPushButton("📂 Load 4 Videos")
        self.load_button.clicked.connect(self.load_videos)

        self.central_widget = QWidget()
        self.vbox = QVBoxLayout(self.central_widget)
        self.vbox.addWidget(self.load_button)
        self.setCentralWidget(self.central_widget)

        self.player = None

    def load_videos(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Select 4 Videos", "", "Video Files (*.mp4 *.avi *.mov)")
        if len(paths) != 4:
            return

        if self.player:
            self.player.setParent(None)
            self.player.deleteLater()

        self.player = VideoColumnPlayer(paths, [1, 2, 3, 4])
        self.vbox.addWidget(self.player)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
