import os
from moviepy.editor import VideoFileClip
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import yt_dlp

# Prompt for channel URL
channel_url = input("Enter the YouTube channel URL: ")

# Folder to save downloads temporarily
download_folder = "YT_Shorts_Downloads"
os.makedirs(download_folder, exist_ok=True)

# YT-DLP options to download Shorts
ydl_opts = {
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
    'ignoreerrors': True,
    'quiet': False,
    'match_filter': yt_dlp.utils.match_filter_func("duration < 61")  # Shorts < 60s
}

# Download Shorts
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([channel_url])

# Function to crop to 16:9 (auto-crop if video is not 16:9)
def crop_to_16_9(video_path):
    clip = VideoFileClip(video_path)
    w, h = clip.size
    target_ratio = 16/9
    current_ratio = w/h

    if current_ratio > target_ratio:
        # Video is too wide → crop width
        new_w = int(h * target_ratio)
        x1 = (w - new_w)//2
        clip = clip.crop(x1=x1, x2=x1+new_w)
    elif current_ratio < target_ratio:
        # Video is too tall → crop height
        new_h = int(w / target_ratio)
        y1 = (h - new_h)//2
        clip = clip.crop(y1=y1, y2=y1+new_h)

    output_path = video_path.replace(".mp4", "_16_9.mp4")
    clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    clip.close()
    return output_path

# Crop all downloaded videos
cropped_videos = []
for file in os.listdir(download_folder):
    if file.endswith(".mp4"):
        path = os.path.join(download_folder, file)
        cropped_path = crop_to_16_9(path)
        cropped_videos.append(cropped_path)

# Google Drive upload
gauth = GoogleAuth()
gauth.LocalWebserverAuth()  # Opens browser for authentication
drive = GoogleDrive(gauth)

for video in cropped_videos:
    file_drive = drive.CreateFile({'title': os.path.basename(video)})
    file_drive.SetContentFile(video)
    file_drive.Upload()
    print(f"Uploaded {video} to Google Drive successfully!")

print("All videos processed and uploaded!")
