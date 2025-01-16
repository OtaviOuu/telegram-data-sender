from telethon import TelegramClient
from telethon.sync import TelegramClient
from pathlib import Path
from tqdm import tqdm
import dotenv
import os

dotenv.load_dotenv()

credentials = {
    "api_id": os.getenv("API_ID"),
    "api_hash": os.getenv("API_HASH"),
    "phone_number": os.getenv("PHONE_NUMBER"),
}


client = TelegramClient("session_name", credentials["api_id"], credentials["api_hash"])

target_channel_id = -1002480588574

path = Path("./Dominando o calc")


async def add_tag_to_video_title(video_tile):
    return f"#A{video_tile}"


async def send_video(video):
    video_name = video.name
    with tqdm(
        total=video.stat().st_size,
        unit="B",
        unit_scale=True,
        desc=video_name,
    ) as progress_bar:

        def progress_callback(current, total):
            progress_bar.n = current
            progress_bar.total = total
            progress_bar.refresh()

        await client.send_file(
            target_channel_id,
            video,
            caption=video_name,
            supports_streaming=True,
            progress_callback=progress_callback,
        )

        """ 
        #F513 001 - aula

        073 - Séries de Taylor
        =011 - ( ) Identidade de Euler
        """


async def main():
    sorted_files = sorted(path.iterdir(), key=lambda x: x.name.lower())
    for file in sorted_files:
        if file.is_dir():
            dir_name = file.name
            await client.send_message(target_channel_id, dir_name)

            sorted_videos = sorted(file.iterdir(), key=lambda x: x.name.lower())
            for video in sorted_videos:
                if video.suffix.lower() == ".mp4":
                    await send_video(video)


with client:
    client.loop.run_until_complete(main())
