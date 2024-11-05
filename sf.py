import os
import sys
import shutil
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
from pathlib import Path

def get_exif_datetime(file_path):
    try:
        image = Image.open(file_path)
        exif_data = image._getexif()
        if exif_data:
            for tag_id, value in exif_data.items():

                tag = TAGS.get(tag_id, tag_id)

                if tag == 'DateTimeOriginal':
                    date_str = value

                    # Vervang de eerste twee dubbele punten door streepjes
                    date_str = date_str.replace(':', '-', 2)
                    date_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    return date_time
    except Exception as e:
        pass
    return None

def get_file_mod_datetime(file_path):
    timestamp = os.path.getmtime(file_path)
    return datetime.fromtimestamp(timestamp)

def process_files(source_dir, dest_dir):
    source_path = Path(source_dir)
    dest_path = Path(dest_dir)

    for file_path in source_path.rglob('*'):
        if file_path.is_file():
            sys.stdout.write(".")
            sys.stdout.flush()
            # Probeer eerst de datum uit de EXIF-data te halen
            date_time = get_exif_datetime(file_path)
            if date_time is None:
                # Als dat niet lukt, gebruik de bestandsmodificatiedatum
                date_time = get_file_mod_datetime(file_path)

            # Stel de nieuwe bestandsnaam en pad samen
            year = date_time.strftime('%Y')
            month = date_time.strftime('%m')
            day = date_time.strftime('%d')
            base_filename = date_time.strftime('%Y-%m-%d %H.%M.%S')
            extension = file_path.suffix
            new_filename = base_filename + extension

            # Maak de doelmap aan als deze nog niet bestaat
            dest_subdir = dest_path / year / month / day
            dest_subdir.mkdir(parents=True, exist_ok=True)

            dest_file_path = dest_subdir / new_filename

            # Voorkom naamconflicten door een teller toe te voegen
            counter = 1
            while dest_file_path.exists():
                new_filename = f"{base_filename} ({counter}){extension}"
                dest_file_path = dest_subdir / new_filename
                counter += 1

            # Verplaats het bestand naar de nieuwe locatie
            shutil.move(str(file_path), str(dest_file_path))

if __name__ == '__main__':
    source_directory = '/Volumes/Untitled/bronmap'
    destination_directory = '/Volumes/Untitled/doelmap'
    process_files(source_directory, destination_directory)
