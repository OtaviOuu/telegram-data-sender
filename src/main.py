from telethon import TelegramClient
from pathlib import Path
from tqdm import tqdm
import dotenv
import os
import socket

video_index = 0

dotenv.load_dotenv(dotenv_path=".env", override=True)

credentials = {
    "api_id": os.getenv("API_ID"),
    "api_hash": os.getenv("API_HASH"),
    "phone_number": os.getenv("PHONE_NUMBER"),
    "folder": os.getenv("FOLDER"),
    "channel_id": int(os.getenv("CHANNEL_ID")),
}

client = TelegramClient("session_name", credentials["api_id"], credentials["api_hash"])

folder_path = Path(str(credentials["folder"]))
content_map = {}


async def send_doc(doc, video_tag):
    doc_name = doc.name

    with tqdm(
        total=doc.stat().st_size,
        unit="B",
        unit_scale=True,
        desc=doc_name,
    ) as progress_bar:

        def progress_callback(current, total):
            progress_bar.n = current
            progress_bar.total = total
            progress_bar.refresh()

        await client.send_file(
            credentials["channel_id"],
            file=doc,
            caption=doc_name,
            progress_callback=progress_callback,
        )


async def send_video(video, video_tag):
    video_name = f"{video_tag} - {video.name}"

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
            credentials["channel_id"],
            video,
            caption=video_name,
            supports_streaming=True,
            progress_callback=progress_callback,
        )


async def manage_content(content_file, video_tag):
    file_suffix = content_file.suffix.lower()

    extension_handlers = {
        "video": {
            "extensions": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
            "handler": send_video,
        },
        "document": {
            "extensions": [".pdf", ".txt", ".xls"],
            "handler": send_doc,
        },
    }

    for _, extension_data in extension_handlers.items():
        if file_suffix in extension_data["extensions"]:
            await extension_data["handler"](content_file, video_tag)


async def process_folder(folder_path: Path):
    global video_index
    dir_name = folder_path.name

    if dir_name not in content_map:
        content_map[dir_name] = []

    for file in sorted(folder_path.iterdir(), key=lambda x: x.name.lower()):
        if file.is_dir():
            await process_folder(file)
        else:
            video_tag = f"#V{str(video_index).zfill(3)}"
            content_map[dir_name].append(video_tag)
            video_index += 1
            await manage_content(file, video_tag)


async def send_large_message(channel_id, message, chunk_size=4096):
    for i in range(0, len(message), chunk_size):
        await client.send_message(channel_id, message[i : i + chunk_size])


async def main():
    for file in sorted(folder_path.iterdir(), key=lambda x: x.name.lower()):
        if file.is_dir():
            await process_folder(file)
        elif file.is_file():
            pass

    guide_message = f"Feito com ♥ por {socket.gethostname()}:\n\n\n"
    for folder, tags in sorted(content_map.items()):
        guide_message += f"= {folder}\n{' '.join(tags)}\n\n"

    await send_large_message(credentials["channel_id"], guide_message)


with client:
    client.loop.run_until_complete(main())
