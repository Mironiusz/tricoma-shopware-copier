import os

def save_files_content_to_txt(root_folder, output_file, ignore_dirs=None):
    """Rekurencyjnie odczytuje pliki .py w folderach, z pominięciem katalogów z ignore_dirs,
    i zapisuje ich treść do pliku tekstowego."""
    ignore_dirs = set(ignore_dirs or [])

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(root_folder):
            # Usuń z listy dirs te katalogi, których nazwy są na liście ignore_dirs
            dirs[:] = [d for d in dirs if d not in ignore_dirs]

            for file in files:
                if file.endswith('.py') or file.endswith('.txt') or file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(f"==== {file_path} ====\n")
                            outfile.write(infile.read())
                            outfile.write("\n\n")
                    except Exception as e:
                        print(f"Nie udało się odczytać pliku {file_path}: {e}")

if __name__ == "__main__":
    # Ścieżka, którą chcesz przeszukać
    input_folder = "./"
    output_file = "output.txt"
    # Tutaj wpisz nazwy folderów (tylko nazwa, nie ścieżka), które chcesz pominąć
    ignore_list = ['venv', '__pycache__', 'build']

    save_files_content_to_txt(input_folder, output_file, ignore_dirs=ignore_list)
    print(f"Zawartość plików została zapisana do {output_file}, z pominięciem katalogów: {ignore_list}")
