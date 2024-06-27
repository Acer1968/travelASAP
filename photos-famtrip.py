"""
Skripty pro manipulaci s fotografiemi ze studijních cest.
"""

from tkinter import Label
import os
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from tkinter import Tk, filedialog, Button, Label

SIMULATION = True


def get_date_from_filename(filename):
    try:
        # Předpokládá formát názvu souboru: VIP_20240612_121212.jpg nebo VIPV_20240612_121314.mp4
        parts = filename.split('_')
        if len(parts) > 1:
            date_str = parts[1] + parts[2].split('.')[0]
            return datetime.strptime(date_str, "%Y%m%d%H%M%S")
    except Exception as e:
        print(f"Error extracting date from filename {filename}: {e}")
    return None


def get_date_from_metadata(filepath):
    try:
        img = Image.open(filepath)
        info = img._getexif()
        if info:
            for tag, value in info.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == 'DateTimeOriginal':
                    return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        print(f"Error extracting date from metadata {filepath}: {e}")
    return None


def get_folder_data(folder_path):
    min_date = None
    max_date = None
    file_names = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('jpg', 'jpeg', 'png', 'tiff', 'mp4')):
                filepath = os.path.join(root, file)
                date_from_metadata = get_date_from_metadata(filepath)
                date_from_filename = get_date_from_filename(file)
                if date_from_metadata or date_from_filename:
                    if not min_date or (date_from_metadata and date_from_metadata < min_date) or (date_from_filename and date_from_filename < min_date):
                        min_date = date_from_metadata if date_from_metadata else date_from_filename
                    if not max_date or (date_from_metadata and date_from_metadata > max_date) or (date_from_filename and date_from_filename > max_date):
                        max_date = date_from_metadata if date_from_metadata else date_from_filename
                    file_names.append(
                        (file, date_from_metadata, date_from_filename, date_from_metadata == date_from_filename))
    return min_date, max_date, file_names


def check_intervals(folder_ranges):
    problematic_folders = set()
    folders = list(folder_ranges.keys())

    for i in range(len(folders)):
        for j in range(len(folders)):
            if i != j:
                start_i, end_i = folder_ranges[folders[i]][:2]
                start_j, end_j = folder_ranges[folders[j]][:2]
                if start_i and end_i and start_j and end_j:
                    if start_i <= start_j and end_j <= end_i:
                        problematic_folders.add(folders[i])

    return problematic_folders


def create_virtual_tree(folder_ranges):
    virtual_tree = {}
    for folder, (min_date, max_date, file_names) in folder_ranges.items():
        virtual_tree[folder] = {
            'interval': (min_date, max_date),
            'files': file_names
        }
    return virtual_tree


def create_gui():
    root = Tk()
    root.title("Správce fotografií ze studijních cest")

    last_report_label = Label(root, text="")
    last_report_label.pack()

    def update_report_info(report_file, creation_time):
        last_report_label.config(
            text=f"Naposledy vytvořený report: {report_file}\nVytvořen: {creation_time}")

    def on_create_virtual_tree():
        folder_path = filedialog.askdirectory(title="Vyber kořenovou složku")
        if folder_path:
            report_file, creation_time = main_process(folder_path)
            update_report_info(report_file, creation_time)
        else:
            print("Nebyla vybrána žádná složka.")

    def on_sort_unassigned_photos():
        folder_path = filedialog.askdirectory(
            title="Vyber kořenovou složku pro třídění fotografií")
        if folder_path:
            sort_unassigned_photos(folder_path)

    btn_create_virtual_tree = Button(
        root, text="Vytvoř virtuální strom složky", command=on_create_virtual_tree)
    btn_create_virtual_tree.pack()

    btn_sort_unassigned_photos = Button(
        root, text="Zařaď nezařazené fotografie", command=on_sort_unassigned_photos)
    btn_sort_unassigned_photos.pack()

    root.mainloop()


def count_files_with_prefixes(files_info, prefixes):
    prefix_counts = {prefix: 0 for prefix in prefixes}
    for file_info in files_info:
        file_name = file_info[0]
        for prefix in prefixes:
            if file_name.startswith(prefix):
                prefix_counts[prefix] += 1
    return prefix_counts


def main_process(root_folder):
    folder_ranges = {}
    for root, dirs, _ in os.walk(root_folder):
        for dir_name in dirs:
            folder_path = os.path.join(root, dir_name)
            min_date, max_date, file_names = get_folder_data(folder_path)
            folder_ranges[folder_path] = (min_date, max_date, file_names)

    problematic_folders = check_intervals(folder_ranges)
    virtual_tree = create_virtual_tree(folder_ranges)

    prefixes = ["IMG_", "VID_"]
    output_file = os.path.join(root_folder, "report.txt")
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(f"Report vytvořen: {current_time}\n")
        for folder, data in virtual_tree.items():
            status = "Problémový" if folder in problematic_folders else "Bezpečný"
            file.write(f"Složka: {folder}\n")
            file.write(f"Nejčasnější snímek: {data['interval'][0]}\n")
            file.write(f"Nejpozdější snímek: {data['interval'][1]}\n")
            file.write(f"Status: {status}\n")

            files_info = data['files']
            video_files = [
                f for f in files_info if f[0].lower().endswith('.mp4')]
            photo_files = [
                f for f in files_info if not f[0].lower().endswith('.mp4')]

            file.write(f"Počet videí: {len(video_files)}\n")
            file.write(f"Počet fotografií: {len(photo_files)}\n")

            prefix_counts = count_files_with_prefixes(files_info, prefixes)
            for prefix, count in prefix_counts.items():
                file.write(f"Počet souborů s prefixem {prefix}: {count}\n")

            file.write("Soubory:\n")
            for file_info in files_info:
                file_name, date_meta, date_name, match = file_info
                match_status = "shodné" if match else "neshodné"
                file.write(
                    f"  {file_name}: Metadata - {date_meta}, Název - {date_name}, Shoda - {match_status}\n")
            file.write("\n")

    print(f"Výsledky byly uloženy do souboru: {output_file}")
    return output_file, current_time


def main():
    create_gui()


if __name__ == "__main__":
    main()
