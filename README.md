# EXIF_extractor
Python code for extracting Roll, Pitch, Yaw and longitude, latitude, altitude from exif of dji, flur drone images.


1. 해당 코드를 실행하시기 전에(Before running the code)
   
해당 코드 실행을 위해서는 두 개의 라이브러리가 필요합니다. pillow, tqdm을 설치해주세요.
Before running the code, You should install two python libraries: pillow, tqdm.
   
2. 코드에 대하여(About the code)
   
DJI, Flur 드론영상의 EXIF에서 Roll, Pitch, Yaw 그리고 Longitude, Latitude, Altitude를 추출하는 코드입니다. 추출된 정보는 csv 또는 txt로 저장됩니다.
This code is for extracting Roll, Pitch, Yaw and Longitude, Latitude, Altitude from EXIF of DJI, FLUR drone images. The extracted information will be saved as csv or txt format.
   
3. 사용방법(How to use)

영상이 담긴 폴더의 경로를 초기값으로 받는 클래스 객체를 생성하시면 됩니다.
make an instance of the class that needs directory of file that contains images as an initial argument.

4. 주의점(Precaution)

드론 제조사 별 영상을 구분해주세요. 
Before using, please check images are separated according to type of drone.
