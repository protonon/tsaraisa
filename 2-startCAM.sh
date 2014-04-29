# This is camera module startup script for raspberry pi
sudo pkill uv4l
#sudo uv4l --driver raspicam --auto-video_nr --encoding mjpeg --framerate 2 --nopreview --exposure sports --awb cloudy
sudo uv4l --driver raspicam --auto-video_nr --encoding mjpeg --framerate 2 --nopreview --exposure sports

