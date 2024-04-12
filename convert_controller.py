# :coding: utf-8

# convert_controller.py

import sys
import os
import re
import importlib
import subprocess
import logging as logger

from PySide2 import QtWidgets

import convert_model
import convert_view

importlib.reload(convert_model)
importlib.reload(convert_view)


# make log file
logfile_path = os.path.join(os.path.dirname(sys.argv[0]), "log")
if not os.path.exists(logfile_path):
    os.mkdir(logfile_path)
LOGFILE = os.path.join(logfile_path, "ami_handler.log")


class ConvertController(convert_view.ConverterView):
    def __init__(self) -> None:
        super().__init__()
        self._logger = self.__init_log(LOGFILE)
        self._custom_filedialog = convert_view.CustomFileDialog()
        self._custom_messagebox = CustomMessageBox()
        self._model = convert_model.ShotgunAction(sys.argv[1])
        self.__set_data()
        self.__set_flags()
        self._show_path = "/RAPA/test_juno"  # 파일탐색기 경로(벗어날 시 에러 발생)
        self.__connections()
    
    def __set_flags(self) -> None:
        self._is_converted = False
    
    def __set_data(self) -> None:
        """
        파싱된 url 정보를 클래스 변수로 저장
        """
        self._protocol, self._action, self._params = self._model.parse_url(self._logger)
        
        self._selected_ids = []
        if len(self._params["selected_ids"]) > 1:
            sids = self._params["selected_ids"].split(",")
            self._selected_ids = [int(id) for id in sids]
        else:
            self._selected_ids = self._params["selected_ids"]
        
        self._entity_type = self._params["entity_type"]
        
    def __connections(self) -> None:
        """
        view 클래스의 시그널과 슬롯 연결
        """
        self.btn_browse.clicked.connect(self.__slot_btn_browse_clicked)
        self.btn_start.clicked.connect(self.__slot_btn_start_clicked)
        self.btn_cancel.clicked.connect(self.__slot_btn_cancel_clicked)
    
    def __slot_btn_browse_clicked(self) -> None:
        """
        browse 버튼 클릭 시 파일 탐색기에서 저장 경로 지정
        """
        self._dir_path = self._custom_filedialog.getExistingDirectory(None, "Save Path", self._show_path)
        
        # 경로가 지정되지 않은 경우
        if self._dir_path == "":
            return
        
        # 경로가 존재하지 않는 경우
        if not os.path.exists(self._dir_path):
            self._custom_messagebox.warning(self, "Invalid Path", f"Path not found: '{self._dir_path}'")
            return
        
        # 경로가 show_path를 벗어날 경우
        if not self._dir_path.startswith(self._show_path):
            self._custom_messagebox.warning(self, "Invalid Path", f"Please select directory within '{self._show_path}'")
            return
        
        self.line_path.setText(self._dir_path)

    def __slot_btn_start_clicked(self) -> None:
        """
        start 버튼 클릭 시 예외 검증 후 convert 시작
        """
        # 경로가 존재하지 않는 경우
        if not os.path.exists(self.line_path.text()):
            self._custom_messagebox.warning(self, "Invalid Path", f"Path not found: '{self.line_path.text()}'")
            return

        if self._custom_messagebox.question(self, "Confirm", "Are you sure to Convert?") == QtWidgets.QMessageBox.No:
            return
        
        self._out_ext = self.comboBox.currentText()
        self.__check_action()

    def __slot_btn_cancel_clicked(self) -> None:
        """
        cancel 버튼 클릭 시 프로세스 종료
        """
        self.close()
    
    def __check_action(self) -> None:
        """
        url의 액션을 확인하여 특정 작업 수행
        """
        if self._action == 'convert_seq2mov':
            self.__convert(self._dir_path, self._out_ext)
        else:
            self._custom_messagebox.warning(self, "Action Error", f"Invalid Action: {self.action}")
            return
        
    def __convert(self, dir_path: str, output_ext: str) -> None:
        """
        선택된 레코드의 정보를 파싱하여 로컬 경로에 있는 시퀀스 이미지를 지정된 디렉토리에 영상으로 변환하여 출력.

        Args:
            dir_path (str): 저장될 경로
            output_ext (str): 콤보박스에서 선택된 확장자
        """
        for selected_id in self._selected_ids:
            
            # 가져오고자 하는 필드값
            fields = ["code", "sg_local_path", "sg_fps"]
            entity = self._model.get_entity_info(self._entity_type, selected_id, fields)
            
            # Local path 정보가 존재하지 않을 경우
            if entity is None:
                self._custom_messagebox.warning(self, "Entity Error", f"Entity not found for entity ID: {selected_id}")
                continue
            
            if not entity and entity['sg_local_path']:
                self._custom_messagebox.warning(self, "Field Error", f"Local Path not found for entity ID: {selected_id}")
                continue
            
            sequence_name = entity['code']
            local_file_path = entity['sg_local_path']
            sequence_fps = round(entity['sg_fps'], 3)
            
            # 경로가 존재하지 않을 경우
            if not os.path.exists(local_file_path):
                self._custom_messagebox.warning(self, "Invalid Path", f"Path not found: {local_file_path}")
                continue
            
            print(f"Start Converting: '{sequence_name}' to {sequence_fps} mov")
            try:
                self.__images_to_video(local_file_path, dir_path, output_ext, sequence_fps)
            except Exception as err:
                print(f"\033]31m{err}\033]0m")
        
        # 컨버팅이 진행된 경우 알림
        if self._is_converted:
            self._custom_messagebox.infromation(self, "Complete", "Converted Successfully")
    
    def __images_to_video(self, images_dir: str, output_dir: str, output_ext:str, fps=24) -> None:
        """
        시퀀스로 이미지를 영상으로 변환하여 출력

        Args:
            images_dir (str): 이미지 시퀀스가 존재하는 경로
            output_dir (str): 출력본이 저장될 경로
            output_ext (str): 출력본의 확장자명
            fps (int, optional): 출력본의 fps. Defaults to 24.
        """
        # validate directory
        if not os.path.exists(images_dir) or not os.path.exists(output_dir):
            self._custom_messagebox.warning(self, "Path Error", "Current Path doesn't Exists")
            return
        
        file_lst = []
        for filename in os.listdir(images_dir):
            file_lst.append(filename)
            
        file_lst = sorted(file_lst)
        if not file_lst:
            self._custom_messagebox.warning(self, "Not Found Error", "No Files in Local Path")
            return
        
        # validate image sequence
        if not self.__validate_sequence(file_lst):
            return

        # set variants
        basename = os.path.basename(file_lst[0])                                          # fire.0001.jpg
        sequence_name = basename.split(".")[0]                                            # fire
        ext = basename.split(".")[-1]                                                                # jpg
        first_frame = basename.split(".")[1]                                                     # 0001
        last_frame = (os.path.basename(file_lst[-1])).split(".")[1]                  # 0100
        output_name = sequence_name + f".[{first_frame}-{last_frame}]"    # fire.[0001-0100]
        
        # avoid duplication
        final_output_path = os.path.join(output_dir, f"{output_name}{output_ext}")
        counter = 1
        while os.path.exists(final_output_path):
            final_output_path = os.path.join(output_dir, f"{output_name}_{counter}{output_ext}")
            counter += 1
            
        self._is_converted = True

        cmd = [            
            'ffmpeg',
            "-y",
            '-f', 'image2',
            '-i', f'{images_dir}/{sequence_name}.%04d.{ext}',
            '-pix_fmt',  'yuv420p',
            '-b:v',  '10M',
            '-r',  f'{fps}',
            final_output_path
        ]
        subprocess.Popen(cmd)
    
    def __validate_sequence(self, file_name_list: list) -> bool:
        """
        이미지 넘버에 비어있는 부분이 있는지 확인,
        비어있는 이미지가 있을 경우 False, 그렇지 않은 경우 True를 반환
        """
        exist_num = set()
        pattern = re.compile("r'\4d")

        for filename in file_name_list:
            match = pattern.search(filename)
            if match:
                file_num = int(match.group)
                exist_num.add(file_num)

        if exist_num:
            min_num = min(exist_num)
            max_num = max(exist_num)
        else:
            return True
        
        missing_nums = [
            num for num in range(min_num, max_num + 1)
            if num not in exist_num
                        ]
        
        if missing_nums:
            self._custom_messagebox.warning(
                self, 
                "Sequence Error", 
                f"Images doesn't exists in directory: {missing_nums}"
                )
            return False
        
    def __init_log(self, filename: str="ami_handler.log") -> logger:
        """
        로그 파일을 초기화하고 로그 형식을 지정

        Args:
            filename (str, optional): 로그 파일의 이름 지정, Defaults to "ami_handler.log".

        Raises:
            ShotgunActionException: 로그 파일 작성 실패 시 에러발생

        Returns:
            logger: logging 객체 return
        """
        try:
            logger.basicConfig(
                level=logger.DEBUG,
                format="%(asctime)s %(levelname)-8s %(message)s",
                datefmt="%Y-%b-%d %H:%M:%S",
                filename=filename,
                filemode="w+",
            )
        except IOError as e:
            raise LogException("Unable to open LOGFILE for writing: %s" % e)
        logger.info("ami_handler logging started.")
        return logger


class LogException(Exception):
    pass


class CustomMessageBox(QtWidgets.QMessageBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    @staticmethod
    def warning(parent=None, title="", text=""):
        QtWidgets.QMessageBox.warning(parent, title, text)
        
    @staticmethod
    def infromation(parent=None, title="", text=""):
        QtWidgets.QMessageBox.information(parent, title, text)
        
    @staticmethod
    def question(parent=None, title="", text=""):
        return QtWidgets.QMessageBox.question(parent, title, text)


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    dc = ConvertController()
    sys.exit(app.exec_())
    # test = python3 "/path/to/convert_controller.py" "foo://convert_seq2mov?selected_ids={ids}&entity_type=PublishedFile"