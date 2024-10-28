import os
# Set the environment variable to allow duplicate OpenMP runtime libraries
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from Components.YoutubeDL import download_youtube_video

url = input("Enter YouTube video URL: ")
Vid = download_youtube_video(url)
if Vid:
    Vid = Vid.replace(".webm", ".mp4")
    print(f"Downloaded video and audio files successfully! at {Vid}")

else:
    print("Unable to Download the video")
