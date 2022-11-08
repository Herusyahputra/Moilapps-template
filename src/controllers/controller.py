# import necessary library you used here
from PyQt6 import QtGui, QtCore
from .resource_icon import *
from src.views.ui_template import Ui_MainWindow
from src.models.moilutils import mutils
from src.models.model import Model


class Controller(Ui_MainWindow):
    def __init__(self, parent):
        """
        The controllers class is The brains of the application that controls how data is displayed.
        The controller's responsibility is to pull, modify, and provide data to the user.
        Essentially, the controllers is the link between the view and model.

        Args:
            model: The backend that contains all the data logic
        """
        super().__init__()
        self.setupUi(parent)
        self.model = Model()
        self.maps_x, self.maps_y = None, None
        self.cap = None
        self.moildev = None

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.reload_to_ui)
        self.camera = False

        self.hide_ui()
        self.set_icon_video_controller()
        self.set_icon_anypoint_controller()
        self.set_icon_play_pause()

        self.connect_action()

    def connect_action(self):
        """
            This function is for connect button to the logic application
        Returns:
            None
        """
        self.btn_open_sources.clicked.connect(self.open_sources)
        self.btn_open_camera.clicked.connect(self.open_sources_camera)

        self.btn_fisheye.clicked.connect(lambda: self.change_mode_view("Fisheye"))
        self.btn_anypoint.clicked.connect(lambda: self.change_mode_view("Anypoint"))
        self.btn_panorama.clicked.connect(lambda: self.change_mode_view("Panorama"))

        self.btn_center_anypoint.clicked.connect(lambda: self.set_anypoint_value(0, 0, 0, 0, 0))
        self.btn_up_anypoint.clicked.connect(lambda: self.set_anypoint_value(75, 0, 50, 0, 0))
        self.btn_left_anypoint.clicked.connect(lambda: self.set_anypoint_value(65, -90, 0, -75, 0))
        self.btn_right_anypoint.clicked.connect(lambda: self.set_anypoint_value(65, 90, 0, 65, 0))
        self.btn_down_anypoint.clicked.connect(lambda: self.set_anypoint_value(65, 180, -65, 0, 0))

        self.btn_play_pause.clicked.connect(self.onclick_play_pause_video)
        self.btn_stop.clicked.connect(self.onclick_stop_video)
        self.btn_rewind.clicked.connect(self.onclick_rewind_video)
        self.btn_forward.clicked.connect(self.onclick_forward_video)
        self.slider_video.valueChanged.connect(self.onclick_slider_video)

        self.radioButton_mode_1.toggled.connect(lambda: self.change_mode_anypoint(1))
        self.radioButton_mode_2.toggled.connect(lambda: self.change_mode_anypoint(2))
        self.spinBox_alpha.valueChanged.connect(self.change_properties_anypoint_from_ui)
        self.spinBox_beta.valueChanged.connect(self.change_properties_anypoint_from_ui)
        self.spinBox_roll.valueChanged.connect(self.change_properties_anypoint_from_ui)
        self.doubleSpinBox_zoom.valueChanged.connect(self.change_properties_anypoint_from_ui)

        self.spinBox_alpha_max.valueChanged.connect(self.change_properties_panorama_from_ui)
        self.spinBox_alpha_min.valueChanged.connect(self.change_properties_panorama_from_ui)

        self.btn_save_image.clicked.connect(self.save_image)
        self.btn_change_param.clicked.connect(self.change_camera_type)

        self.btn_parameter_config.clicked.connect(self.parameter_configuration)

    def open_sources(self):
        """
            This function is for open sources image or video from directory
        Returns:
            None
        """
        file_path = self.model.mutils.select_file(None, "Open Sources", "../", "*.jpg *.png *.avi *.mp4")
        if file_path:
            self.camera = False
            self.model.sources_path = file_path
            self.model.load_media(file_path)
            print(self.model.data_properties.properties_video["video"])
            if self.model.data_properties.properties_video["video"]:
                self.frame_video_controller.show()
                self.model.running_video()
                self.initial_open_media()
                self.reload_to_ui()
            else:

                self.frame_video_controller.hide()
                self.show_to_ui()

    def open_sources_camera(self):
        """
            This function is for streaming camera from USB or streaming camera
        Returns:
            None
        """
        camera = self.model.mutils.select_source_camera()
        if camera is not None:
            self.camera = True
            self.model.load_media_camera(camera)
            self.frame_video_controller.show()
            self.show_to_ui()

    def change_mode_view(self, value):
        """
            This function is for change mode of view (fisheye (original image), anypoint or panorama)
        Returns:
            None
        """
        if self.model.data_properties.image_original is not None:
            self.model.data_properties.mode_view = value
            if value == "Fisheye":
                self.frame_anypoint.hide()
                self.frame_panorama.hide()
                self.frame_anyoint_button.hide()
            elif value == "Anypoint":
                self.frame_anypoint.show()
                self.frame_panorama.hide()
                self.frame_anyoint_button.show()
                if self.radioButton_mode_1.isChecked():
                    self.spinBox_roll.hide()
                    self.label_3.hide()
                else:
                    self.spinBox_roll.show()
                    self.label_3.show()
            elif value == "Panorama":
                self.frame_anypoint.hide()
                self.frame_panorama.show()
                self.frame_anyoint_button.hide()
            self.model.create_maps()
            self.show_to_ui()

    def change_mode_anypoint(self, mode):
        """
            This function is for change mode anypoint (mode 1 or mode 2)
        Args:
            mode: input mode 1 or mode 2
        Returns:
            None
        """
        self.model.data_properties.properties_anypoint["mode"] = mode
        self.model.reset_anypoint_properties()
        self.change_ui_from_properties_anypoint()
        self.change_properties_anypoint_from_ui()

    def set_anypoint_value(self, alpha1, beta1, alpha2, beta2, roll):
        """
            This function is for fast anypoint action
        Args:
            alpha1: alpha mode 1
            beta1: beta mode 1
            alpha2: alpha mode 2
            beta2: beta mode 2
            roll: roll for mode 2
        Returns:
            None
        """
        if self.model.data_properties.properties_anypoint["mode"] == 1:
            self.model.data_properties.properties_anypoint["alpha"] = alpha1
            self.model.data_properties.properties_anypoint["beta"] = beta1
        else:
            self.model.data_properties.properties_anypoint["alpha"] = alpha2
            self.model.data_properties.properties_anypoint["beta"] = beta2
            self.model.data_properties.properties_anypoint["roll"] = roll
        self.change_ui_from_properties_anypoint()
        self.model.create_maps()
        self.show_to_ui()

    def change_properties_anypoint_from_ui(self):
        """
            this function is for change properties anypoint from value in user interface
        Returns:
            None
        """
        self.model.data_properties.properties_anypoint["alpha"] = self.spinBox_alpha.value()
        self.model.data_properties.properties_anypoint["beta"] = self.spinBox_beta.value()
        self.model.data_properties.properties_anypoint["roll"] = self.spinBox_roll.value()
        self.model.data_properties.properties_anypoint["zoom"] = self.doubleSpinBox_zoom.value()
        self.change_mode_view("Anypoint")
        if self.model.data_properties.properties_video["video"]:
            self.btn_play_pause.setChecked(False)
            self.timer.stop()
        self.show_to_ui()

    def change_properties_panorama_from_ui(self):
        """
            this function is for change properties panorama from value in user interface
        Returns:
            None
        """
        self.model.data_properties.properties_panorama["alpha_max"] = self.spinBox_alpha_max.value()
        self.model.data_properties.properties_panorama["alpha_min"] = self.spinBox_alpha_min.value()
        self.change_mode_view("Panorama")
        if self.model.data_properties.properties_video["video"]:
            self.btn_play_pause.setChecked(False)
            self.timer.stop()
        self.show_to_ui()

    def change_ui_from_properties_anypoint(self):
        """
            This function is for change user interface ui from properties anypoint but with block unblock signal
        Returns:
            None
        """
        self.spinBox_alpha.blockSignals(True)
        self.spinBox_beta.blockSignals(True)
        self.spinBox_roll.blockSignals(True)
        self.doubleSpinBox_zoom.blockSignals(True)
        self.spinBox_alpha.setValue(self.model.data_properties.properties_anypoint["alpha"])
        self.spinBox_beta.setValue(self.model.data_properties.properties_anypoint["beta"])
        self.spinBox_roll.setValue(self.model.data_properties.properties_anypoint["roll"])
        self.doubleSpinBox_zoom.setValue(self.model.data_properties.properties_anypoint["zoom"])
        self.spinBox_alpha.blockSignals(False)
        self.spinBox_beta.blockSignals(False)
        self.spinBox_roll.blockSignals(False)
        self.doubleSpinBox_zoom.blockSignals(False)

    def change_ui_from_properties_panorama(self):
        """
            This function is for change user interface ui from properties panorama but with block unblock signal
        Returns:
            None
        """
        self.spinBox_alpha_max.blockSignals(True)
        self.spinBox_alpha_min.blockSignals(True)
        self.spinBox_alpha_max.setValue(self.model.data_properties.properties_panorama["alpha_max"])
        self.spinBox_alpha_min.setValue(self.model.data_properties.properties_panorama["alpha_min"])
        self.spinBox_alpha_max.blockSignals(False)
        self.spinBox_alpha_min.blockSignals(False)

    def show_to_ui(self):
        """
            This function is for show image in user interface
        Returns:
            None
        """
        self.set_icon_play_pause()
        if self.model.data_properties.mode_view != "Fisheye":
            image = self.model.data_properties.image_drawing
        else:
            image = self.model.data_properties.image_original

        image2 = self.model.data_properties.image_result
        if image is not None:
            self.model.mutils.show_image_to_label(self.lbl_original, image, 320)
        if image2 is not None:
            self.model.mutils.show_image_to_label(self.lbl_result, image2, 1000)

    def reload_to_ui(self):
        """
            This function is for video only and can update view depend on length of the video
        Returns:
            None
        """
        self.model.next_frame()
        self.show_to_ui()
        self.set_value_slider_video()
        if self.camera:
            self.model.set_total_video_time_O()
        else:
            if self.model.data_properties.properties_video["frame_count"] == \
                    self.model.data_properties.properties_video["pos_frame"]:
                self.timer.stop()
        self.set_time_video()

    def onclick_play_pause_video(self):
        """
            This function is for action play pause video and icon
        Returns:
            None
        """
        if self.model.data_properties.image_result is not None:
            if self.btn_play_pause.isChecked():
                self.timer.start()
            else:
                self.timer.stop()
            self.set_icon_play_pause()

    def onclick_stop_video(self):
        """
            This function is for get action stop video
        Returns:
            None
        """
        self.btn_play_pause.setChecked(False)
        self.model.stop_video()
        self.timer.stop()
        self.reload_to_ui()

    def onclick_rewind_video(self):
        """
            This function is for get action rewind video
        Returns:

        """
        self.btn_play_pause.setChecked(False)
        self.model.rewind_video()
        self.timer.stop()
        self.reload_to_ui()

    def onclick_forward_video(self):
        """
            This function is get action for forward video
        Returns:

        """
        self.btn_play_pause.setChecked(False)
        self.model.forward_video()
        self.timer.stop()
        self.reload_to_ui()

    def onclick_slider_video(self, value):
        """
            This function is to get value input from slider user interface
        Args:
            value: position of slider

        Returns:
            None
        """
        value_max = self.slider_video.maximum()
        self.model.slider_controller(value, value_max)
        self.reload_to_ui()

    def hide_ui(self):
        """
            Hide some frame in user interface for first running
        Returns:

        """
        self.frame_anypoint.hide()
        self.frame_panorama.hide()
        self.frame_anyoint_button.hide()

    def save_image(self):
        """
            This function is for get action for saving image
        Returns:
            None
        """
        self.timer.stop()
        self.btn_play_pause.setChecked(False)
        path = self.model.mutils.select_directory(None, ".")
        if path:
            self.model.save_image(path)

    def parameter_configuration(self):
        """
            This function is for get action and do the form camera parameter
        Returns:
            None
        """
        self.model.mutils.form_camera_parameter()

    def change_camera_type(self):
        """
            This function is for get action to change parameter or camera type
        Returns:
            None
        """
        self.timer.stop()
        self.btn_play_pause.setChecked(False)
        self.model.change_camera_type()
        self.show_to_ui()

    def initial_open_media(self):
        """
            This video is for set label and slider video controller to none
        Returns:
            None
        """
        self.lbl_current_time.setText("--:--")
        self.lbl_total_time.setText("--:--")
        self.slider_video.setValue(0)

    def set_value_slider_video(self):
        """
            set slider position base on length video
        Returns:
            None
        """
        value = self.slider_video.maximum()
        current_position = self.model.get_value_slider_video(value)
        self.slider_video.blockSignals(True)
        self.slider_video.setValue(current_position)
        self.slider_video.blockSignals(False)

    def set_time_video(self):
        """
            set time of video in label
        Returns:
            None
        """
        total_minute = self.model.data_properties.properties_video["total_minute"]
        total_second = self.model.data_properties.properties_video["total_second"]
        current_minute = self.model.data_properties.properties_video["current_minute"]
        current_second = self.model.data_properties.properties_video["current_second"]
        self.lbl_current_time.setText("%02d:%02d" % (current_minute, current_second))
        self.lbl_total_time.setText("%02d:%02d" % (total_minute, total_second))

    def set_icon_video_controller(self):
        """
            Set icon vidio controller
        Returns:
            None
        """
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons:rewind.svg"), QtGui.QIcon.Mode.Normal,
                       QtGui.QIcon.State.Off)
        self.btn_rewind.setIcon(icon)

        icon.addPixmap(QtGui.QPixmap("icons:square.svg"), QtGui.QIcon.Mode.Normal,
                       QtGui.QIcon.State.Off)
        self.btn_stop.setIcon(icon)

        icon.addPixmap(QtGui.QPixmap("icons:fast-forward.svg"), QtGui.QIcon.Mode.Normal,
                       QtGui.QIcon.State.Off)
        self.btn_forward.setIcon(icon)

    def set_icon_anypoint_controller(self):
        """
            set icon for button anypoint
        Returns:
            None
        """
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons:arrow-up.svg"), QtGui.QIcon.Mode.Normal,
                        QtGui.QIcon.State.Off)
        self.btn_up_anypoint.setIconSize(QtCore.QSize(26, 26))
        self.btn_up_anypoint.setIcon(icon1)

        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons:square.svg"), QtGui.QIcon.Mode.Normal,
                        QtGui.QIcon.State.Off)
        self.btn_center_anypoint.setIconSize(QtCore.QSize(26, 26))
        self.btn_center_anypoint.setIcon(icon1)

        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons:arrow-left.svg"), QtGui.QIcon.Mode.Normal,
                        QtGui.QIcon.State.Off)
        self.btn_left_anypoint.setIconSize(QtCore.QSize(26, 26))
        self.btn_left_anypoint.setIcon(icon1)

        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons:arrow-right.svg"), QtGui.QIcon.Mode.Normal,
                        QtGui.QIcon.State.Off)
        self.btn_right_anypoint.setIconSize(QtCore.QSize(26, 26))
        self.btn_right_anypoint.setIcon(icon1)

        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons:arrow-down.svg"), QtGui.QIcon.Mode.Normal,
                        QtGui.QIcon.State.Off)
        self.btn_down_anypoint.setIconSize(QtCore.QSize(26, 26))
        self.btn_down_anypoint.setIcon(icon1)

    def set_icon_play_pause(self):
        """
            Set icon for button play and pause video
        Returns:
            None
        """
        icon = QtGui.QIcon()
        if self.btn_play_pause.isChecked():
            icon.addPixmap(QtGui.QPixmap("icons:pause.svg"), QtGui.QIcon.Mode.Normal,
                           QtGui.QIcon.State.Off)
        else:
            icon.addPixmap(QtGui.QPixmap("icons:play.svg"), QtGui.QIcon.Mode.Normal,
                           QtGui.QIcon.State.Off)
        self.btn_play_pause.setIcon(icon)
