import os
from pytubefix import YouTube
import ffmpeg  # Ensure that this is the 'ffmpeg-python' package

def get_video_size(stream):
    return stream.filesize / (1024 * 1024)

def download_youtube_video(url):
    try:
        yt = YouTube(url)

        # Filter only video streams and list them, sorted by resolution
        video_streams = yt.streams.filter(type="video").order_by('resolution').desc()
        audio_stream = yt.streams.filter(only_audio=True).first()  # Get the first available audio stream

        print("Available video streams:")
        for i, stream in enumerate(video_streams):
            size = get_video_size(stream)
            stream_type = "Progressive" if stream.is_progressive else "Adaptive"
            print(f"{i}. Resolution: {stream.resolution}, Size: {size:.2f} MB, Type: {stream_type}")

        # Input validation loop to ensure correct selection
        while True:
            try:
                choice = int(input("Enter the number of the video stream to download: "))
                if 0 <= choice < len(video_streams):
                    break
                else:
                    print("Please enter a valid number corresponding to the video streams listed.")
            except ValueError:
                print("Please enter a valid integer.")

        selected_stream = video_streams[choice]

        # Create 'videos' directory if it doesn't exist
        if not os.path.exists('videos'):
            os.makedirs('videos')

        print(f"Downloading video: {yt.title}")
        video_file = selected_stream.download(output_path='videos', filename_prefix="video_")
        print(f"Downloaded video file: {video_file}")

        # If the stream is Adaptive (video-only), download the audio separately and merge them
        if not selected_stream.is_progressive:
            print("Selected stream is adaptive (video-only). Downloading audio separately and merging.")
            audio_file = audio_stream.download(output_path='videos', filename_prefix="audio_")
            print(f"Downloaded audio file: {audio_file}")

            # Convert the video file to .mp4 format if needed
            video_file_mp4 = video_file.replace('.webm', '.mp4')
            if video_file != video_file_mp4:
                try:
                    # Debug: Print FFmpeg command and paths
                    print(f"Converting video: {video_file} to {video_file_mp4}")
                    ffmpeg.input(video_file).output(video_file_mp4, vcodec='libx264').run(overwrite_output=True)
                    print(f"Conversion successful: {video_file_mp4}")
                    os.remove(video_file)  # Remove the original .webm file
                except Exception as e:
                    print(f"Error converting video to MP4: {e}")
                    return None

            # Merge video and audio
            output_file = os.path.join('videos', f"{yt.title}.mp4")
            try:
                print(f"Merging video: {video_file_mp4} and audio: {audio_file} into {output_file}")
                ffmpeg.input(video_file_mp4).input(audio_file).output(
                    output_file, vcodec='libx264', acodec='aac', strict='experimental'
                ).run(overwrite_output=True)
                print(f"Merged video and audio successfully: {output_file}")

                # Check if the merged file was created successfully
                if os.path.exists(output_file):
                    # Clean up the temporary files
                    os.remove(video_file_mp4)
                    os.remove(audio_file)
                else:
                    print("Error: Merged file was not created.")
            except Exception as e:
                print(f"Error merging video and audio: {e}")
                return None
        else:
            print(f"Downloaded: {yt.title} to 'videos' folder")
            print(f"File path: {video_file}")
            return video_file

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Please make sure you have the latest version of pytube and ffmpeg-python installed.")
        print("You can update them by running:")
        print("pip install --upgrade pytube ffmpeg-python")
        print("Also, ensure that ffmpeg is installed on your system and available in your PATH.")

if __name__ == "__main__":
    youtube_url = input("Enter YouTube video URL: ")
    download_youtube_video(youtube_url)
