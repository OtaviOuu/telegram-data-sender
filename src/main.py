from telethon import TelegramClient
from telethon.sync import TelegramClient
from pathlib import Path
from tqdm import tqdm
import dotenv
import os
import json

dotenv.load_dotenv()

credentials = {
    "api_id": os.getenv("API_ID"),
    "api_hash": os.getenv("API_HASH"),
    "phone_number": os.getenv("PHONE_NUMBER"),
}


client = TelegramClient("session_name", credentials["api_id"], credentials["api_hash"])

target_channel_id = -1002480588574

path = Path("./testes/Dominando o calc")

content_map = {}


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
            target_channel_id,
            file=doc,
            caption=doc_name,
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


async def manage_content(content_file):
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
            await extension_data["handler"](content_file)


async def main():
    video_index = 0
    sorted_files = sorted(path.iterdir(), key=lambda x: x.name.lower())
    for file in sorted_files:
        if file.is_dir():
            dir_name = file.name
            # aaaaaaaaaaaaaaaaa
            content_map[dir_name] = []
            # await client.send_message(target_channel_id, dir_name)

            sorted_videos = sorted(file.iterdir(), key=lambda x: x.name.lower())
            for content_file in sorted_videos:
                video_tag = f"#V{video_index}"
                content_map[dir_name].append(video_tag)

                with open("content_map.txt", "w") as f:
                    json.dump(content_map, f, indent=4, ensure_ascii=False)
                # await manage_content(content_file)
                video_index += 1
        elif file.is_file():
            await manage_content(file)

    guide_message = ""
    for folder, tags in content_map.items():
        guide_message += f"""
        {folder}
        {', '.join(tags)}
        """
    with open("final.txt", "w") as f:
        f.write(guide_message)
    await client.send_message(target_channel_id, guide_message)


with client:
    client.loop.run_until_complete(main())
