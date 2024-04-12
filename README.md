# Shotgrid_AMI_converter

Shotgrid에 추가된 AMI를 통해 로컬에 존재하는 이미지 시퀀스를 비디오로 변환하여 저장하는 프로그램.
<br>
로직을 응용하여 추가적인 기능 구현 가능

## 필요 모듈 및 프레임워크

- PySide2
- shotgun_api3
- ffmpeg 4.2.4

```bash
pip install PySide2
```
```bash
pip install shotgun_api3
```
```bash
wget https://ffmpeg.org/releases/ffmpeg-4.2.4.tar.xz
```


## 사용 방법

1. shotgrid에 커스텀 AMI 추가<br>(https://help.autodesk.com/view/SGDEV/ENU/?guid=SGD_ami_action_menu_items_create_html)
2. 코드 수정 (script_key, 경로, 설정값 등)
3. 커스텀 프로토콜 추가<br>(https://stackoverflow.com/questions/32064229값custom-protocol-handlers-linux-centos-7-for-chrome)
4. AMI 실행


## 제작자
email: td.junopark@gmail.com
github: https://github.com/junopark00
requests: https://github.com/junopark00/ShotGrid_AMI_convert/pulls
