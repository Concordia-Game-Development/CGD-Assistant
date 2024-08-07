import yt_dlp, os


class InvalidURLException(Exception):
    pass


def audioDownloadYT(
    URL: str, OUTPUT_PATH: str, DURATION: int, START_TIME: int = 0
) -> None:
    try:
        # Validate if the URL is a YouTube link
        isYoutubeURL(URL)

        if DURATION <= 0 or DURATION > 15:
            raise ValueError(
                "Duration must be a positive integer and less than or equal to 15 seconds."
            )

        # Check if the CUSTOM.mp3 file exists and delete it if it does
        if os.path.exists(OUTPUT_PATH):
            os.remove(OUTPUT_PATH)

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

    except InvalidURLException as e:
        raise RuntimeError(f"Error: {str(e)}")
    except yt_dlp.utils.DownloadError as e:
        # Handle errors related to downloading the video (e.g., invalid URL)
        raise RuntimeError(f"Download failed: {str(e)}.\nMake sure the URL is valid.")
    except Exception as e:
        # Handle other unforeseen errors
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")


def isYoutubeURL(url):
    youtube_domains = ["youtube.com", "youtu.be", "youtube.ca"]
    if not any(domain in url for domain in youtube_domains):
        raise InvalidURLException("The URL provided is not a valid YouTube link.")
    return True
