# :coding: utf-8

# convert_view.py

import sys

from PySide2.QtWidgets import *


class ConverterView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.__setup_ui()

    def __setup_ui(self) -> None:
        """
        UI 생성 및 시각화
        """
        self.setWindowTitle("Convert Sequence to Video")
        self.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(70, 70, 70);")
        self.setMinimumWidth(500)
        self.__set_center()

        # create widgets
        _vbox = QVBoxLayout()
        _hbox_1 = QHBoxLayout()
        _hbox_2 = QHBoxLayout()
        
        ## hbox_1
        self.line_path = QLineEdit()
        self.line_path.setPlaceholderText("/path/to/save/file")
        self.line_path.setEnabled(False)
        self.comboBox = QComboBox()
        self.comboBox.addItem(".mov")
        self.comboBox.addItem(".mp4")
        self.btn_browse = QPushButton("Browse")
        
        _hbox_1.addWidget(self.line_path)
        _hbox_1.addWidget(self.comboBox)
        _hbox_1.addWidget(self.btn_browse)
        
        vspacer = QSpacerItem(200, 20, QSizePolicy.Expanding, QSizePolicy.Fixed)

        ## hbox_2
        hspacer = QSpacerItem(200, 5, QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_start = QPushButton("OK")
        self.btn_cancel = QPushButton("Cancel")
        
        _hbox_2.addItem(hspacer)
        _hbox_2.addWidget(self.btn_start)
        _hbox_2.addWidget(self.btn_cancel)

        # set layouts
        _vbox.addLayout(_hbox_1)
        _vbox.addItem(vspacer)
        _vbox.addLayout(_hbox_2)
        self.setLayout(_vbox)

        self.show()

    def __set_center(self) -> None:
        """
        UI를 화면 중앙에 배치
        """
        res = QDesktopWidget().screenGeometry()
        self.move(
            (res.width() / 2) - (self.frameSize().width() / 2),
            (res.height() / 2) - (self.frameSize().height() / 2),
        )
        

class CustomFileDialog(QFileDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def getExistingDirectory(parent=None, caption='', directory='', options=None):
        options = options or QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        dir_path = QFileDialog.getExistingDirectory(parent, caption, directory, options)
        return dir_path
    

if __name__ == '__main__':
    app = QApplication()
    cv = ConverterView()
    sys.exit(app.exec_())
