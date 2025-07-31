# mac_parallel_video_gui.py

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog
)
from Sources.VideoColumnProcessor import VideoColumnPlayer


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
