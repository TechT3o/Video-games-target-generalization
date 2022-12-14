import os.path
from data_recording.mouse_input import MouseLogger
from environment_extracting.environment_extraction import EnvironmentExtractor
import time
import csv
from cv2 import imwrite
from statics import check_and_create_directory
import win32api
from typing import Tuple


class DataRecorder:
    """
    Class that records the user input and the image frames and saves that information in csv files
    """
    def __init__(self, window_coordinates: Tuple[int, int, int, int], reset_cursor_flag: bool, save_path: str = ''):
        """
        class constructor
        :param save_path: path where the data should be saved
        """
        self.mouse_logger = MouseLogger(window_coordinates=window_coordinates, reset_cursor_flag=reset_cursor_flag)
        self.environment = EnvironmentExtractor(window_coordinates)
        self.fps = 15

        self.data_path = os.path.join(save_path, 'data')
        self.frames_path = os.path.join(self.data_path, 'frames')
        self.csv_path = os.path.join(self.data_path, 'csvs')
        self.create_saving_dirs()

    def create_saving_dirs(self) -> None:
        """
        Creates saving directories
        :return: None
        """

        check_and_create_directory(self.data_path)
        check_and_create_directory(self.frames_path)
        check_and_create_directory(self.csv_path)

    def run(self) -> None:
        """
        main function that runs to record the data
        :return: None
        """
        ltime = time.localtime(time.time())
        timestamp = f'{ltime.tm_year}_{ltime.tm_mon}_{ltime.tm_mday}_{ltime.tm_hour}_{ltime.tm_min}_{ltime.tm_sec}'
        file_path = os.path.join(self.csv_path, f'data_{timestamp}.csv')
        current_frames_path = os.path.join(self.frames_path, f'recording_{timestamp}')
        check_and_create_directory(current_frames_path)

        with open(file_path, 'w', newline='') as csv_file:
            data_writer = csv.writer(csv_file)
            # data_writer.writerow(["Image Path", "Start X", "Start Y", "End X", "End Y", "Shot", "Hit Edge Flag"])
            data_writer.writerow(["Image Path", "Delta X", "Delta Y", "Shot", "Hit Edge Flag"])
            frame_index = 1
            while True:
                loop_start_time = time.time()
                self.mouse_logger.get_mouse_states()
                # print(self.mouse_logger.d_x, self.mouse_logger.d_y)
                image_save_path = os.path.join(current_frames_path, f'Frame_{timestamp}_{frame_index}.jpg')
                imwrite(image_save_path, self.environment.get_image())
                data_writer.writerow([os.path.join(os.path.join('../data', 'frames'),
                                                   os.path.join(f'recording_{timestamp}',
                                                                f'Frame_{timestamp}_{frame_index}.jpg')),
                                      self.mouse_logger.d_x, self.mouse_logger.d_y, self.mouse_logger.l_click,
                                      self.mouse_logger.hit_edge()])
                frame_index += 1
                while time.time() < loop_start_time + 1/self.fps:
                    pass
                print(1 / (time.time() - loop_start_time))

                if win32api.GetAsyncKeyState(ord('Q'))&0x0001 > 0:
                    print('Quit')
                    break

