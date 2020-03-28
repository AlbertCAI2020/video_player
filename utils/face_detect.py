import cv2


class FaceDetect:
    face_cascade = None

    def __init__(self):
        if FaceDetect.face_cascade is None:
            print('init CascadeClassifier')
            FaceDetect.face_cascade = cv2.CascadeClassifier('data\\haarcascade_frontalface_default.xml')

    def detect(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = FaceDetect.face_cascade.detectMultiScale(img_gray, 1.1, 5)
        for (x, y, w, h) in faces:
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 2)
        return len(faces)

