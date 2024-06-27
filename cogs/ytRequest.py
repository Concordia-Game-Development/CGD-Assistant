import yt_dlp


def audioDownloadYT(URL: str, OUTPUT_PATH: str):
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
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([URL])
