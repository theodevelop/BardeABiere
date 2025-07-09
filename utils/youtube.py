import yt_dlp

def get_audio_url(youtube_url: str) -> str:
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
    return info["url"]
