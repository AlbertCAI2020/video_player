import os
import cv2
import threading
import queue
import PySimpleGUI as sg
from utils.face_detect import FaceDetect
from video_file import *


class MediaFinder:
    def __init__(self, folder, suffixes=None):
        if suffixes is None:
            suffixes = ['.mp4', '.avi', '.wmv', '.rmvb']
        self.root = folder
        self.suffixes = suffixes
        self.files = []

    def find_all(self):
        for root, dirs, files in os.walk(self.root):
            for file in files:
                for suffix in self.suffixes:
                    if file.endswith(suffix):
                        path = os.path.join(root, file)
                        path = path.replace('/', '\\')
                        self.files.append(path)
        return self.files


class VideoProcess(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, name='video_process')
        self._que = queue.Queue()
        self._is_stopped = False

    def run(self):
        while not self._is_stopped:
            msg = self._que.get(True)
            if msg is None:
                print('process thread quit')
                break
            path = msg['path']
            print('process ' + path)
            video = VideoFile(path=path)
            if not video.is_cache_exist():
                video.grab_small_frames()
                video.save_cache()

    def process(self, path):
        self._que.put({
            'path': path
        })

    def stop(self):
        self._que.put(None)
        self._is_stopped = True
        self.join()


_thread = VideoProcess()


class MarkWindow:
    def __init__(self, score=0):
        layout = [[sg.Text('Give a mark for current video <0-100>')],
                  [sg.InputText(default_text=str(score), size=(20, 1), do_not_clear=False, key='_INPUT_'),
                   sg.Button('Ok', size=(5, 1), bind_return_key=True)]
                  ]
        self.window = sg.Window(title='Mark', layout=layout, keep_on_top=True)

    def read(self):
        while True:
            button, values = self.window.Read()
            if button != 'Ok':
                return None
            value = values['_INPUT_']
            if not value.isdecimal():
                sg.popup_error('invalid score', keep_on_top=True)
            else:
                break
        return int(value)

    def __del__(self):
        self.window.close()
        del self.window


class SelectWindow:
    def __init__(self):
        layout = [[sg.Text('score range')],
                  [sg.InputText(default_text='60', size=(10, 1), key='_lower_'),
                   sg.Text('-'),
                   sg.InputText(default_text='100', size=(10, 1), key='_upper_'),
                   sg.Button('Ok', size=(5, 1), bind_return_key=True)]
                  ]
        self.window = sg.Window(title='Select', layout=layout, keep_on_top=True)

    def read(self):
        while True:
            button, values = self.window.Read()
            if button != 'Ok':
                return None, None
            lower = values['_lower_']
            upper = values['_upper_']
            if not lower.isdecimal() or not upper.isdecimal():
                sg.popup_error('invalid score', keep_on_top=True)
            else:
                break
        return int(lower), int(upper)

    def __del__(self):
        self.window.close()
        del self.window


class VideoPlayer:
    def __init__(self):
        graph_col = [
            [sg.Graph((960, 500), (0, 0), (960, 500), background_color='black', key='graph', pad=(0, 0))],
            [sg.Slider((1, 100), size=(110, 20), pad=(0, 0), orientation='h', disable_number_display=True,
                       enable_events=True, key='slider'), sg.Button('Play', size=(8, 1))]
        ]
        files_col = [
            [sg.Listbox(values=[], size=(30, 30), enable_events=True, select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED,
                        key='listbox', pad=(0, 0))],
            [sg.Text('Total:', pad=(0, 0)), sg.Text('0', size=(10, 1), key='total_count', pad=(0, 0))]
        ]
        layout = [
            [
                sg.Menu([
                    ['&File', ['Open Folder', 'Close all']],
                    ['&Edit', ['&Detect face', '&Mark', 'Open container folder']],
                    ['&History', ['All::load_all', 'Marked::load_marked', '&Remove']],
                    ['&Settings', ['Face detect']]
                ])
            ],
            [
                sg.Column(files_col, pad=(0, 0)),
                sg.Column(graph_col)
            ]
        ]
        self.window = sg.Window('Video Player', layout, return_keyboard_events=True,
                                use_default_focus=False, resizable=False)
        self.graph = self.window['graph']
        self.event_dispatch = {
            'Open Folder': self._handle_open_folder,
            'Open container folder': self._handle_open_container_folder,
            'Close all': self._handle_close_all,
            'All::load_all': self._handle_load_all,
            'Marked::load_marked': self._handle_load_marked,
            'Mark': self._handle_mark,
            'listbox': self._handle_file_selected,
            'Play': self._handle_play_video,
            'Detect face': self._handle_detect_face,
            'Remove': self._handle_file_remove,
            'slider': self._handle_slider_move
        }
        self.selected_video = None

    def run(self):
        while True:
            event, values = self.window.read()
            # print(event, values)
            if event is None:
                break
            elif event in self.event_dispatch:
                if event in values:
                    self.event_dispatch[event](values[event])
                else:
                    self.event_dispatch[event]()

        self.window.close()

    def _handle_open_folder(self):
        items = self.window['listbox'].GetListValues()
        folder = sg.popup_get_folder('Folder to open', default_path='')
        if folder:
            files = MediaFinder(folder).find_all()
            for file in files:
                if file not in items:
                    items.append(file)
                    _thread.process(file)
        self.window['listbox'].update(items)
        self.window['total_count'].Update(str(len(items)))

    def _handle_open_container_folder(self):
        if self.selected_video is not None:
            path = self.selected_video.path
            path = os.path.dirname(path)
            if not os.path.isdir(path):
                sg.popup_error('file not exists', keep_on_top=True)
                return
            os.startfile(path)

    def _handle_close_all(self):
        self.window['listbox'].Update([])
        self.window['slider'].Update(1)
        self.window['graph'].Erase()
        self.selected_video = None
        self.window['total_count'].Update('0')

    def _handle_load_all(self):
        repo = Repository(cache_repo)
        files = repo.find_all()
        self.window['listbox'].Update(values=[file['path'] for file in files])
        self.window['total_count'].Update(str(len(files)))

    def _handle_load_marked(self):
        lower, upper = SelectWindow().read()
        repo = Repository(cache_repo)
        files = repo.find_with_score(lower, upper)
        self.window['listbox'].Update(values=[file['path'] for file in files])
        self.window['total_count'].Update(str(len(files)))

    def _handle_mark(self):
        if self.selected_video is not None:
            score = MarkWindow(self.selected_video.score).read()
            if score is not None:
                self.selected_video.set_score(score)

    def _handle_file_selected(self, files):
        if len(files) is 0:
            return
        path = files[0]
        if self.selected_video is None or self.selected_video.path is not path:
            self.selected_video = VideoFile(path)
            if self.selected_video.is_cache_exist():
                self.selected_video.load_cache()
        self._display_small_graphs()

    def _handle_file_remove(self):
        listbox = self.window['listbox']
        files = listbox.GetListValues()
        selected = listbox.get()
        for file in selected:
            VideoFile(file).delete_cache()
            files.remove(file)
        listbox.Update(files)
        self.window['total_count'].Update(str(len(files)))

    def _handle_play_video(self):
        if self.selected_video is None or not self.selected_video.is_file_exist():
            sg.popup_error('file not exists', keep_on_top=True)
            return
        os.startfile(self.selected_video.path)

    def _display_video(self, pos=None):
        if self.selected_video is None or not self.selected_video.is_file_exist():
            sg.popup_error('file not exists', keep_on_top=True)
            return
        self.graph.Erase()
        frame = self.selected_video.grab_frame(pos)
        if frame is not None:
            self.graph.DrawImage(data=frame, location=(0, 480), color='black', font=None, angle=0)
        self.graph.DrawText(self.selected_video.path, location=(0, 500), color='white',
                            text_location=sg.TEXT_LOCATION_TOP_LEFT)

    def _display_small_graphs(self):
        if self.selected_video is None:
            return
        frames = self.selected_video.get_small_frames()
        if len(frames) is not 12:
            return
        self.graph.Erase()
        size = small_frame_size
        for j in range(0, 3):
            for i in range(0, 4):
                frame = self.selected_video.get_small_frames()[j * 4 + i]
                if frame is not None:
                    width = size[0]
                    height = size[1]
                    self.graph.DrawImage(data=frame,
                                         location=(i * width + 10, 480 - j * (height + 10)),
                                         color='black',
                                         font=None, angle=0)

        self.graph.DrawText(self.selected_video.path, location=(0, 500), color='white',
                            text_location=sg.TEXT_LOCATION_TOP_LEFT)

    def _handle_slider_move(self, pos):
        self._display_video(pos)

    def _handle_detect_face(self):
        if self.selected_video is None or self.selected_video.get_cur_cv_frame() is None:
            return
        frame = self.selected_video.get_cur_cv_frame()
        fd = FaceDetect()
        num = fd.detect(frame)
        if num > 0:
            img_bytes = cv2.imencode('.png', frame)[1].tobytes()
            self.graph.DrawImage(data=img_bytes, location=(10, 480), color='black', font=None, angle=0)


if __name__ == '__main__':
    _thread.start()
    VideoPlayer().run()
    _thread.stop()
