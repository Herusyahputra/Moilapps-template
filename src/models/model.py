import datetime

import cv2

from .moilutils import mutils
from .data_properties import DataProperties


class Model(object):
    def __init__(self):
        """
        The backend that contains all the data logic.
        The model's job is to simply manage the data. Whether the data is from a database,
        API, or a JSON object, the model is responsible for managing it.

        """
        super(Model, self).__init__()
        self.data_properties = DataProperties()
        self.mutils = mutils
        self.maps_x, self.maps_y = None, None
        self.cap = None
        self.moildev = None

    def load_media(self, file_path):
        """
            This function is for process input image or video
        Returns:
            none
        """
        self.data_properties.source_path = file_path
        if self.data_properties.source_path.endswith((".png", ".jpg", ".jpeg", ".gif", ".bmg")):
            self.data_properties.properties_video["video"] = False
            # camera_type = mutils.read_camera_type(self.model.source_path)
            camera_type = None
            if camera_type is None:
                camera_type = mutils.select_type_camera()
                # mutils.write_camera_type(self.model.source_path, camera_type)
            self.moildev = mutils.connect_to_moildev(type_camera=camera_type)
            self.set_initial_image(mutils.read_image(self.data_properties.source_path))
        elif self.data_properties.source_path.endswith((".avi", ".mp4")):
            self.data_properties.properties_video["video"] = True
            camera_type = mutils.select_type_camera()
            self.moildev = mutils.connect_to_moildev(type_camera=camera_type)
            self.running_video()
        self.create_maps()

    def load_media_camera(self, camera):
        """
            This function is for load camera for streaming video
        Args:
            camera: input address camera
        Returns:
            None
        """
        if camera == int:
            self.data_properties.source_path = int(camera)
        else:
            self.data_properties.source_path = camera
        self.data_properties.properties_video["video"] = True
        camera_type = mutils.select_type_camera()
        self.moildev = mutils.connect_to_moildev(type_camera=camera_type)
        self.running_video()
        self.create_maps()

    def running_video(self):
        """
            read camera address
        Returns:
            None
        """
        self.cap = cv2.VideoCapture(self.data_properties.source_path)
        self.next_frame()

    def next_frame(self):
        """
            This function is for do lopping video for user interface
        Returns:
            None
        """
        success, self.data_properties.image_original = self.cap.read()
        if success:
            self.data_properties.properties_video["video"] = True
            if self.data_properties.mode_view == "Fisheye":
                self.data_properties.image_result = self.data_properties.image_original
            elif self.data_properties.mode_view == "Anypoint":
                self.data_properties.image_result = self.generate_result_image()
            elif self.data_properties.mode_view == "Panorama":
                self.data_properties.image_result = self.generate_result_image()
            self.video_duration()

    def video_duration(self):
        """
            This function is for get time of video
        Returns:
            None
        """
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.data_properties.properties_video["pos_frame"] = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        self.data_properties.properties_video["frame_count"] = float(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_sec = int(self.data_properties.properties_video["frame_count"] / fps)

        self.data_properties.properties_video["total_minute"] = int(duration_sec // 60)
        duration_sec %= 60
        self.data_properties.properties_video["total_second"] = duration_sec
        sec_pos = int(self.data_properties.properties_video["pos_frame"] / fps)
        self.data_properties.properties_video["current_minute"] = int(sec_pos // 60)
        sec_pos %= 60
        self.data_properties.properties_video["current_second"] = sec_pos

    def set_total_video_time_O(self):
        """
            This function is for set properties video total length is 0
        Returns:
            None
        """
        self.data_properties.properties_video["total_minute"] = 0
        self.data_properties.properties_video["total_second"] = 0

    def create_maps(self):
        """
            This function is for create image maps_x and maps_y base on mode view
        Returns:
            None
        """
        if self.data_properties.mode_view == "Fisheye":
            self.data_properties.image_result = self.data_properties.image_original
        elif self.data_properties.mode_view == "Anypoint":
            if self.data_properties.properties_anypoint["mode"] == 1:
                self.maps_x, self.maps_y = self.moildev.maps_anypoint(
                    self.data_properties.properties_anypoint["alpha"],
                    self.data_properties.properties_anypoint["beta"],
                    self.data_properties.properties_anypoint["zoom"],
                    self.data_properties.properties_anypoint["mode"])
            else:
                self.maps_x, self.maps_y = self.moildev.maps_anypoint_car(
                    self.data_properties.properties_anypoint["alpha"],
                    self.data_properties.properties_anypoint["beta"],
                    self.data_properties.properties_anypoint["roll"],
                    self.data_properties.properties_anypoint["zoom"])
            self.data_properties.image_result = self.generate_result_image()

        elif self.data_properties.mode_view == "Panorama":
            self.maps_x, self.maps_y = self.moildev.maps_panorama(
                self.data_properties.properties_panorama["alpha_min"],
                self.data_properties.properties_panorama["alpha_max"])
            self.data_properties.image_result = self.generate_result_image()

    def generate_result_image(self):
        """
            This function is for generate image base map_x, map_y
        Returns:
            None
        """
        self.data_properties.image_drawing = mutils.draw_polygon(self.data_properties.image_original.copy(), self.maps_x, self.maps_y)
        return mutils.remap_image(self.data_properties.image_original, self.maps_x, self.maps_y)

    def set_initial_image(self, image):
        """
        This function is will be used to set original image (get image result) in the user interface frame

        Args:
            image: set up value original image
        Returns:
            This function is None
        """
        self.data_properties.image_original = image
        self.data_properties.image_result = image
        self.data_properties.image_drawing = image

    def reset_anypoint_properties(self):
        """
            This function is to set alpha, beta and roll to 0
        Returns:
            None
        """
        self.data_properties.properties_anypoint["alpha"] = 0
        self.data_properties.properties_anypoint["beta"] = 0
        self.data_properties.properties_anypoint["roll"] = 0
        self.data_properties.properties_anypoint["zoom"] = 2

    def reset_panorama_properties(self):
        """
            This function is to set alpha min 110 and alpha max 10
        Returns:
            None
        """
        self.data_properties.properties_panorama["alpha_min"] = 110
        self.data_properties.properties_panorama["alpha_max"] = 10

    def save_image(self, path):
        """
            this function is for save image
        Args:
            path: path image save
        Returns:
            None
        """
        x = datetime.datetime.now()
        time = x.strftime("%Y_%m_%d_%H_%M_%S")
        if self.data_properties.image_original is not None:
            cv2.imwrite(path + "/image_result_" + time + ".jpg", self.data_properties.image_result)
            cv2.imwrite(path + "/image_result_" + time + ".jpg", self.data_properties.image_original)

    def change_camera_type(self):
        """
            This function is for change parameter of image input
        Returns:
            None
        """
        if self.data_properties.image_original is not None:
            if self.data_properties.properties_video["video"]:
                camera_type = mutils.select_type_camera()
                self.moildev = mutils.connect_to_moildev(type_camera=camera_type)
                self.running_video()
            else:
                camera_type = mutils.select_type_camera()
                mutils.write_camera_type(self.data_properties.source_path, camera_type)
                self.moildev = mutils.connect_to_moildev(type_camera=camera_type)
                self.set_initial_image(mutils.read_image(self.data_properties.source_path))
            self.create_maps()

    def stop_video(self):
        """
            This function is set video in to frame 0
        Returns:
            None
        """
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.next_frame()

    def forward_video(self):
        """
            This function is for forward video frame for 5 seconds
        Returns:
            None
        """
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        position = self.data_properties.properties_video["pos_frame"] + 5 * fps
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)
        self.next_frame()

    def rewind_video(self):
        """
            This function is for rewind video frame for 5 seconds
        Returns:
            None
        """
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        position = self.data_properties.properties_video["pos_frame"] - 5 * fps
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)
        self.next_frame()

    def slider_controller(self, value, slider_maximum):
        """
            This function is for change video position base on input slider
        Args:
            value: current slider position
            slider_maximum: value maximum slider video
        Returns:
            None
        """
        dst = self.data_properties.properties_video["frame_count"] * value / slider_maximum
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, dst)
        self.next_frame()

    def get_value_slider_video(self, value):
        """
            This function is for get current position slider time base on position slider maximum
        Args:
            value: value slider maximum
        Returns:
            None
        """
        current_position = self.data_properties.properties_video["pos_frame"] * (value + 1) / \
                           self.data_properties.properties_video["frame_count"]
        return current_position



