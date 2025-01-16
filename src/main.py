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

path = Path("./testes/teste")


async def add_tag_to_folder_title(folder_title):
    return f"#A{folder_title}"


async def send_pdf(pdf):
    pdf_name = pdf.name
    with tqdm(
        total=pdf.stat().st_size,
        unit="B",
        unit_scale=True,
        desc=pdf_name,
    ) as progress_bar:

        def progress_callback(current, total):
            progress_bar.n = current
            progress_bar.total = total
            progress_bar.refresh()

        await client.send_file(
            target_channel_id,
            pdf,
            caption=pdf_name,
            progress_callback=progress_callback,
        )


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


async def manage_content(content_file):
    file_name = content_file.name
    file_suffix = content_file.suffix.lower()

    if file_suffix == ".mp4":
        # await send_video(content_file)
        await client.send_message(target_channel_id, file_name)
    if file_suffix == ".pdf":
        await send_pdf(content_file)


async def main():
    sorted_files = sorted(path.iterdir(), key=lambda x: x.name.lower())
    for file in sorted_files:
        if file.is_dir():
            dir_name = await add_tag_to_folder_title(file.name)
            await client.send_message(target_channel_id, dir_name)

            sorted_videos = sorted(file.iterdir(), key=lambda x: x.name.lower())
            for content_file in sorted_videos:
                await manage_content(content_file)

        if file.is_file():
            await manage_content(file)


with client:
    client.loop.run_until_complete(main())
