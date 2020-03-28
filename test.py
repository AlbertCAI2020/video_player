import unittest
from video_file import *
import re


class VideoFileTest(unittest.TestCase):
    def test_load_cache(self):
        video = VideoFile(path='test.mp4')
        ret = video.load_cache()
        self.assertEqual(True, ret)


class RepositoryTest(unittest.TestCase):
    def test_insert(self):
        repo = Repository('test.db')
        uid = str(uuid.uuid1())
        repo.insert(uid, 'aaaaaa')
        value = repo.find_by_path('aaaaaa')
        self.assertEqual('aaaaaa', value['path'])

        values = repo.find_all()
        print(values)

    def test_insert2(self):
        repo = Repository('test.db')
        uid = '12ad6264-6655-11ea-977a-ac9e17f0444c'
        repo.insert(uid, 'aaaaaa')
        value = repo.find_by_path('aaaaaa')
        self.assertEqual('aaaaaa', value['path'])

        values = repo.find_all()
        print(values)


if __name__ == '__main__':
    unittest.main()
