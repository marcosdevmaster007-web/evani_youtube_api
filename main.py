from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
import subprocess
import os
import re

app = FastAPI()

DOWNLOADS = "downloads"
os.makedirs(DOWNLOADS, exist_ok=True)

# ================= MODELS =================


class DownloadRequest(BaseModel):
    url: str
    tipo: str = "video"  # video | audio


# ================= HELPERS =================


def clean_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()


# ================= ROOT =================


@app.get("/")
def root():
    return {"status": "API online"}


# ================= DOWNLOAD =================


@app.post("/download")
def download(data: DownloadRequest):

    if not data.url.startswith("http"):
        raise HTTPException(status_code=400, detail="URL inválida")

    try:
        # pegar info para o título
        with YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
            info = ydl.extract_info(data.url, download=False)

        title = clean_filename(info.get("title", "media"))

        if data.tipo == "audio":
            filename = f"{title}.mp3"
            cmd = [
                "yt-dlp",
                "-f",
                "bestaudio/best",
                "-x",
                "--audio-format",
                "mp3",
                "--audio-quality",
                "0",
                "--force-overwrites",
                "-o",
                f"{DOWNLOADS}/{filename}",
                data.url,
            ]
        else:
            filename = f"{title}.mp4"
            cmd = [
                "yt-dlp",
                "-f",
                "bestvideo+bestaudio/best",
                "--merge-output-format",
                "mp4",
                "--force-overwrites",
                "-o",
                f"{DOWNLOADS}/{filename}",
                data.url,
            ]

        subprocess.run(cmd, check=True)

        file_path = os.path.join(DOWNLOADS, filename)

        return FileResponse(
            file_path,
            media_type="application/octet-stream",
            filename=filename,
        )

    except DownloadError:
        raise HTTPException(status_code=500, detail="Erro ao baixar mídia")

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Falha no download")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
