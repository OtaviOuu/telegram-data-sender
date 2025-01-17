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

path = Path("./testes/Pikuma")


async def add_tag_to_folder_title(folder_title):
    return f"#A{folder_title}"


async def create_progress_bar(file):
    with tqdm(
        total=file.stat().st_size,
        unit="B",
        unit_scale=True,
        desc=file.name,
    ) as progress_bar:

        def progress_callback(current, total):
            progress_bar.n = current
            progress_bar.total = total
            progress_bar.refresh()

        return progress_callback, progress_bar


async def send_doc(doc):

    progress_bar, progress_callback = create_progress_bar(doc)

    with progress_bar:
        await client.send_file(
            target_channel_id,
            file=doc,
            caption=doc.name,
            progress_callback=progress_callback,
        )


async def send_video(video):
    progress_bar, progress_callback = create_progress_bar(video)

    with progress_bar:
        await client.send_file(
            target_channel_id,
            video,
            caption=video.name,
            supports_streaming=True,
            progress_callback=progress_callback,
        )


async def manage_content(content_file):
    file_suffix = content_file.suffix.lower()

    video_extensions = [
        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
    ]
    document_extensions = [
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".ppt",
        ".pptx",
        ".xls",
        ".xlsx",
    ]

    for video_extension in video_extensions:
        if file_suffix == video_extension:
            await send_video(content_file)

    for document_extension in document_extensions:
        if file_suffix == document_extension:
            await send_doc(content_file)


async def send():
    sorted_files = sorted(path.iterdir(), key=lambda x: x.name.lower())
    for file in sorted_files:
        if file.is_dir():
            dir_name = await add_tag_to_folder_title(file.name)
            await client.send_message(target_channel_id, dir_name)

            sorted_videos = sorted(file.iterdir(), key=lambda x: x.name.lower())
            for content_file in sorted_videos:
                await manage_content(content_file)

        elif file.is_file():
            await manage_content(file)


with client:
    client.loop.run_until_complete(send())
