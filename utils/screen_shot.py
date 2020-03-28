import cv2


class VideoScreenshot:
    def __init__(self, path):
        # path = path.encode('gbk')
        # path = path.decode('gbk')
        self.path = path
        self.cap = cv2.VideoCapture(path)  ##打开视频文件
        self.frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))  ##视频的帧数
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)  ##视频的帧率
        if self.fps != 0:
            self.dur = self.frames / self.fps  ##视频的时间
        else:
            self.dur = 1

    def __del__(self):
        self.cap.release()

    def __str__(self):
        return "path:%s,dur:%fmin" % (self.path, self.dur / 60)

    def grab(self, percent=None, resize=None):
        """
        :param percent:
        :param resize: Tuple[int, int] (width, height) size of the image to resize
        :return:
        """
        if percent:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, int(self.frames * percent / 100))
        ret, img = self.cap.read()
        if ret and resize:
            height = img.shape[0]
            width = img.shape[1]
            factor1 = 1.0
            factor2 = 1.0
            if width > resize[0]:
                factor1 = resize[0] / width
            if height > resize[1]:
                factor2 = resize[1] / height
            factor = min(factor1, factor2)
            img = cv2.resize(img, (int(width * factor), int(height * factor)))
        return img

