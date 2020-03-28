# Video Player

To be honest, this is not a real video player, at least the current version is not. This program is designed to manage
local video files. It has features list below:

1. Run in background when opening folders that contains video files, grab screenshots of the video files and save them
into cache files.
2. List video files in a listbox and show small screenshots of the video in the graph area when it is been selected.
Thanks for the cached files, this procedure is fast.
3. Videos can be marked with a score and thus can be filtered by score range from history records. The filtered video 
files are listed in the listbox by descending order of scores.
4. Drag the slider to show video frames. 
5. Click the play button to play the selected video by calling an external video player on your system.
6. Detect faces on the video frame that currently showed.

#### _Depends on third party programs_

opencv-python https://pypi.org/project/opencv-python/

PySimpeGui https://github.com/PySimpleGUI/PySimpleGUI