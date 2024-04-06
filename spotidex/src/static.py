FFMPEG_URLS = {
    "windows": {
        "amd64": "https://github.com/eugeneware/ffmpeg-static/releases/download/b4.4/win32-x64",
        "i686": "https://github.com/eugeneware/ffmpeg-static/releases/download/b4.4/win32-ia32",
    },
    "linux": {
        "x86_64": "https://github.com/eugeneware/ffmpeg-static/releases/download/b4.4/linux-x64",
        "x86": "https://github.com/eugeneware/ffmpeg-static/releases/download/b4.4/linux-ia32",
        "arm32": "https://github.com/eugeneware/ffmpeg-static/releases/download/b4.4/linux-arm",
        "aarch64": "https://github.com/eugeneware/ffmpeg-static/releases/download/b4.4/linux-arm64",
    },
    "darwin": {
        "x86_64": "https://github.com/eugeneware/ffmpeg-static/releases/download/b4.4/darwin-x64",
        "arm": "https://github.com/eugeneware/ffmpeg-static/releases/download/b4.4/darwin-arm64",
    },
}

client_id     = "df3b20346d3a47a49295015021776d5d"
client_secret = "69047630688b498fa601fc311ef19577"
bitrate       = {"low":'24','medium':'128','high':'320'} 