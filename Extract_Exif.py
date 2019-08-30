import os
import re
import csv
import PIL.Image
from PIL.ExifTags import TAGS, GPSTAGS
from tqdm import tqdm

class Extract_Exif:

    def __init__(self, img_dir, save_type=""):
        """
        2019.08.08 This code is for extracting GPSInfo, Yaw, Roll, Pitch from Exif.
        2019.08.14 Upgrade the code for Phantom4RTK, Mavic images to be processed.
                   Warn : Before using, please check images are separated according to type of drone.
                          If images are mixed regardless of drone type, the processing will be failed
                          because of difference of exif format.
        This code supports only jpg, jpeg, png, if you want to add file format, please check img_
        absdir_extract function().
        :param img_dir: folder directory including image files.
        :param save_type: default ""
        """
        self.img_dir = img_dir
        self.img_absdir, self.img_base = self.img_absdir_extract()
        self.gpsinfo_list_tmp, self.xmlinfo_list, self.xmpinfo_list, self.TypeError_list = self.get_exifmeta()
        self.gpsinfo_list = self.gpsinfo_tag_decode()
        self.num = len(self.gpsinfo_list)
        gps_info = self.Extract_data()

        if save_type == "txt":
            self.save_txt(gps_info)
        elif save_type == "csv":
            self.save_csv(gps_info)
        else:
            self.save_txt(gps_info)
            self.save_csv(gps_info)

    def img_absdir_extract(self):
        ext = [".jpg", ".jpg".upper(), ".png", ".png".upper(), ".jpeg", ".jpeg".upper()]
        file_dirlist = os.listdir(self.img_dir)
        img_absdir = []
        img_base = []
        for file in file_dirlist:
            absdir = os.path.join(self.img_dir, file)
            if os.path.isfile(absdir):
                name, extension = os.path.splitext(file)
                if extension in ext:
                    img_absdir.append(os.path.join(self.img_dir, file))
                    img_base.append(file)
        return img_absdir, img_base

    def get_exifmeta(self):
        gpsinfo_list = []
        xmlinfo_list = []
        xmpinfo_list = []
        TypeError_list = []
        print("Exif data are extracting....")
        for dir in self.img_absdir:
            img_obj = PIL.Image.open(dir)
            try:
                exifmeta = img_obj._getexif()
                # 34853 : GPSInfo TagID, 700 : XmlPack TagID
                gpsinfo_list.append(exifmeta[34853])
                xmlinfo_list.append(exifmeta[700])
            except TypeError:
                print("TypeError : {0} has no EXIF. {0} name will be removed from processing ".format(
                    os.path.basename(dir)))
                TypeError_list.append(os.path.basename(dir))
                self.img_absdir.remove(dir)
            except KeyError:
                f_object = open(dir, 'rb')
                object = f_object.read()
                xmp_start = object.find(b'<x:xmpmeta')
                xmp_end = object.find(b'</x:xmpmeta')
                xmp_str = object[xmp_start:xmp_end + 12]
                xmpinfo_list.append(str(xmp_str))

        print("If TypeError warned, check TypeErrorlist : classobject.TypeError_list")
        return gpsinfo_list, xmlinfo_list, xmpinfo_list, TypeError_list

    def gpsinfo_tag_decode(self):
        gpsinfo_list = []
        # gpsinfo decode
        for gps_dict in self.gpsinfo_list_tmp:
            gpsinfo_dict = {}
            for tag, val in gps_dict.items():
                decode = GPSTAGS.get(tag, tag)
                gpsinfo_dict[decode] = val
            gpsinfo_list.append(gpsinfo_dict)

        return gpsinfo_list

    def Extract_data(self):
        gps_info = {}
        print("Data Extraction from {0} image file starts. Please Wait.".format(self.num))

        if len(self.xmpinfo_list)==0:
            xm_list = self.xmlinfo_list
        else:
            xm_list = self.xmpinfo_list

        for filename, gps_dict_elem, xm_elem in tqdm(zip(self.img_base, self.gpsinfo_list, xm_list)):

            if len(self.xmpinfo_list)==0:
                # Yaw, Roll, Pitch Extraction
                for yrp in ["Yaw", "Roll", "Pitch"]:
                    target = "<Camera:" + yrp + ">(.*?)/100"
                    m = re.search(target, str(xm_elem))
                    if yrp == "Yaw":
                        Yaw = eval(m.group()[12:])
                    elif yrp == "Roll":
                        Roll = eval(m.group()[13:])
                    elif yrp == "Pitch":
                        Pitch = eval(m.group()[14:])
            else:
                target_yaw = 'FlightYawDegree="(.*?)"'
                target_pitch = 'FlightPitchDegree="(.*?)"'
                target_roll = 'FlightRollDegree="(.*?)"'
                yaw_part = re.search(target_yaw, str(xm_elem))
                pitch_part = re.search(target_pitch, str(xm_elem))
                roll_part = re.search(target_roll, str(xm_elem))
                Yaw = float(yaw_part.group()[17:-1])
                Pitch = float(pitch_part.group()[19:-1])
                Roll = float(roll_part.group()[18:-1])

            # Lat, Lon, Altitude Extraction
            lat = gps_dict_elem["GPSLatitude"][0][0] / gps_dict_elem["GPSLatitude"][0][1] + \
                  gps_dict_elem["GPSLatitude"][1][0] / gps_dict_elem["GPSLatitude"][1][1] / 60 + \
                  gps_dict_elem["GPSLatitude"][2][0] / gps_dict_elem["GPSLatitude"][2][1] / 3600

            lon = gps_dict_elem["GPSLongitude"][0][0] / gps_dict_elem["GPSLongitude"][0][1] + \
                  gps_dict_elem["GPSLongitude"][1][0] / gps_dict_elem["GPSLongitude"][1][1] / 60 + \
                  gps_dict_elem["GPSLongitude"][2][0] / gps_dict_elem["GPSLongitude"][2][1] / 3600

            alt = gps_dict_elem["GPSAltitude"][0] / gps_dict_elem["GPSAltitude"][1]

            gps_info[filename] = {"GPSLongitude": lon, "GPSLatitude": lat, "GPSAltitude": alt, "Yaw": Yaw,
                                  "Pitch": Pitch, "Roll": Roll}

        print("GPSInfo(Lat, Lon, Alt), DronePosition Data Extraction completed.\n")
        return gps_info

    def save_txt(self, gps_info):
        for img_nm, gps_data in gps_info.items():
            with open(os.path.join(self.img_dir, os.path.splitext(img_nm)[0] + ".txt"), 'w') as f:
                f.write(str(img_nm)+"\t")
                for gps_tag, gps_val in gps_data.items():
                    f.write(str(gps_val)+"\t")
        print("Data saved as txt file.")
        return

    def save_csv(self, gps_info):
        with open(os.path.join(self.img_dir, "Exif_gpsinfo.csv"), 'w', newline='') as f:
            header = ["Filename", "GPSLatitude", "GPSLongitude", "GPSAltitude", "Yaw", "Row", "Pitch"]
            writer = csv.writer(f)
            writer.writerow(header)

            for file, gps_data in gps_info.items():
                gps_list = list(gps_data.values())
                gps_list.insert(0, file)
                writer.writerow(gps_list)
        print("Data saved as csv file.")
        return


if __name__ == "__main__":
    #Flur Dud
    #a = Extract_Exif("C:\\LSM\\190800_ShipDetection\\EXIF\Photo_sort\\Flurduopro")
    #Mavic
    #a = Extract_Exif("C:\\LSM\\190800_ShipDetection\\EXIF\\Photo_sort\\Mavicpro")
    #Phantom4RTK
    #a = Extract_Exif("C:\LSM\\190800_ShipDetection\EXIF\Photo_sort\Phantom4RTK")
    #Mix - need to be improved
    a = Extract_Exif("C:\LSM\\190800_ShipDetection\EXIF\Photo_sort\mix")
