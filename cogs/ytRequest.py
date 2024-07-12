import yt_dlp


def audioDownloadYT(
    URL: str, OUTPUT_PATH: str, DURATION: int, START_TIME: int = 0
) -> None:
    if DURATION <= 15:
        options = {
            "format": "bestaudio/best",
            "outtmpl": OUTPUT_PATH,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "postprocessor_args": [
                "-ss",
                str(START_TIME),  # Start time
                "-t",
                str(DURATION),  # Duration of the clip
            ],
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([URL])
    else:
        raise ValueError("Duration must be less than or equal to 30 seconds")
