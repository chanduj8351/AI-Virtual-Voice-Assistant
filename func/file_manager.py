import os
import json
import shutil


with open(os.getcwd() + "\\assets\\json\\extensions.json", "r") as json_file:
    data = json.load(json_file)
    extensions = data["extensions"] 


class FileManager:
    def __init__(self):
        self.folders = {
            'desktop': os.path.join(os.path.expanduser('~'), 'Desktop'),
            'documents': os.path.join(os.path.expanduser('~'), 'Documents'),
            'downloads': os.path.join(os.path.expanduser('~'), 'Downloads'),
            'music': os.path.join(os.path.expanduser('~'), 'Music'),
            'pictures': os.path.join(os.path.expanduser('~'), 'Pictures'),
            'videos': os.path.join(os.path.expanduser('~'), 'Videos'),
        }

    def copyfile_object(self, src_file, dst_file):
        with open(src_file, 'rb') as src, open(dst_file, 'wb') as dst:
            shutil.copyfileobj(src, dst)
            return True

    def copy_file(self, src_file, dst_file):
        shutil.copyfile(src_file, dst_file)
        return True


    def move_file(self, src_dir, dst_dir):
        shutil.move(src_dir, dst_dir)
        return True


    def disk_space_available(self):
        usage = shutil.disk_usage('/')
        return f"Total: {usage.total / 1024 ** 3:.2f} GB, Used: {usage.used / 1024 ** 3:.2f} GB, Free: {usage.free / 1024 ** 3:.2f} GB"


    def directory_paths(self):
        """Returns a list of directory paths"""
        for folder_name, folder_path in self.folders.items():
            return f"{folder_name}: {folder_path}"
            

    def list_of_folders_files(self):
        """get list of folders in each directory"""
        for folder_name, folder_path in self.folders.items():
            print(f"\nContents of {folder_name} ({folder_path}):")
            if os.path.exists(folder_path):
                items = os.listdir(folder_path)
                if items:
                    for item in items:
                        return f"- {item}"
                else:
                    return "  (Folder is empty)"
            else:
                return "  (Folder path does not exist)"


    def get_file_paths(self):
        """
        Retrieves the full paths of all files and subdirectories in the predefined folders,
        excluding specified files, extensions, folders, and .venv paths, and saves them to a JSON file.
        """
        excluded_extensions = {'.conf', '.ie', '.int', '.fst', '.dubm', '.md'}
        excluded_names = {'__pycache__', '.cpython-311.pyc'}
        all_paths = {}

        for folder_name, folder_path in self.folders.items():
            print(f"\nFull paths of contents in {folder_name} ({folder_path}):")
            folder_paths = []

            if os.path.exists(folder_path):
                for root, dirs, files in os.walk(folder_path):
                    # Skip .venv directories entirely
                    if '.venv' in root:
                        continue

                    # Remove unwanted directories from traversal
                    dirs[:] = [d for d in dirs if d not in excluded_names and '.venv' not in d]

                    for name in dirs + files:
                        full_path = os.path.join(root, name)
                        _, ext = os.path.splitext(name)

                        if (
                            ext in excluded_extensions or
                            name in excluded_names or
                            '.venv' in full_path
                        ):
                            continue  # Skip excluded file or path

                        folder_paths.append(full_path)
                        #print(full_path)
            else:
                print("  (Folder path does not exist)")

            all_paths[folder_name] = folder_paths

        # Save collected paths to JSON
        try:
            json_path = os.path.join(os.getcwd(), "func", "assets", "files_paths.json")
            os.makedirs(os.path.dirname(json_path), exist_ok=True)

            with open(json_path, 'w') as path_file:
                json.dump(all_paths, path_file, indent=4)
            print(f"\nAll file paths written to: {json_path}")
        except Exception as e:
            print(f"Error writing to JSON file: {e}")


    def get_folder_contents(self, folder_name: str):
        """
        Retrieves and prints the contents of the specified folder, including subfolders.

        :param folder_dest: The key name of the folder in self.folders whose contents you want to retrieve.
        """
        if folder_name not in self.folders:
            print(f"Invalid folder destination: '{folder_name}'.")
            print("Available folders are:")
            for key in self.folders.keys():
                print(f"- {key}")
            raise ValueError(f"Folder destination '{folder_name}' is not valid.")

        folder_path = self.folders[folder_name]
        
        if os.path.exists(folder_path):
            print(f"\nContents of {folder_name} ({folder_path}):")
            for root, dirs, files in os.walk(folder_path):
                level = root.replace(folder_path, '').count(os.sep)
                indent = ' ' * 4 * level
                print(f"{indent}{os.path.basename(root)}/")
                sub_indent = ' ' * 4 * (level + 1)
                for f in files:
                    print(f"{sub_indent}{f}")
        else:
            print(f"The folder path '{folder_path}' does not exist.")


    def create_folder(self,
                    folder_name: str = None,
                    folder_dest: str = None,
                    file_name: str = None,
                    create_file: bool = True) -> bool:
        """
        Creates a folder inside one of the predefined folders (e.g., Desktop, Documents, etc.)
        and optionally creates a file within that folder.

        :param folder_name: Name of the new folder to create.
        :param folder_dest: Destination folder name from self.folders where the folder should be created.
        :param file_name: Name of the file to create in the new folder (if create_file is True).
        :param create_file: Boolean flag to indicate if a file should be created in the new folder.
        """
        if folder_dest and folder_dest in self.folders:
            parent_folder_path = self.folders[folder_dest]
            new_folder_path = os.path.join(parent_folder_path, folder_name)

            try:
                os.makedirs(new_folder_path, exist_ok=True)
                print(f"Folder '{folder_name}' created in '{folder_dest}'.")

                if create_file and file_name:
                    file_path = os.path.join(new_folder_path, file_name)
                    with open(file_path, 'w') as file:
                        file.write("")
                    print(f"File '{file_name}' created in folder '{folder_name}'.")
                    return True
            except Exception as e:
                print(f"An error occurred while creating the folder or file: {e}")
            return False
        else:
            print(f"Invalid folder destination: '{folder_dest}'. Choose from {list(self.folders.keys())}")

    def create_file(self,
                    folder_dest: str = "desktop",
                    folder_name: str = None,
                    file_name: str = None,
                    file_type: str = None,
                    create_file: bool = True):
        """
        Creates a file with the specified type in the given folder.

        :param file_name: Name of the file to create.
        :param file_type: Type of file (e.g., 'json', 'text') to determine file extension.
        :param folder_name: Name of the folder where the file should be created.
        :param folder_dest: Destination folder name from self.folders where the file should be created.
        :param create_file: Boolean flag to indicate if the file should be created.
        """
        if folder_dest and folder_dest in self.folders:
            if file_type in extensions:
                extension = extensions[file_type]
                if file_name:
                    if folder_name is None:
                        folder_name = ""

                    folder_path = os.path.join(self.folders[folder_dest], folder_name)

                    if not os.path.exists(folder_path):
                        print(f"Folder '{folder_name}' does not exist. Creating it.")
                        os.makedirs(folder_path, exist_ok=True)

                    file_name_with_extension = f"{file_name}{extension}"
                    file_path = os.path.join(folder_path, file_name_with_extension)

                    if create_file:
                        try:
                            with open(file_path, 'w') as file:
                                file.write("")
                            #print(f"File '{file_name_with_extension}' created in folder '{folder_name}'.")
                            return f"C:/Users/chand/{folder_dest}/{folder_name}/{file_name_with_extension}"
                        except Exception as e:
                            print(f"An error occurred while creating the file: {e}")
                    else:
                        print(f"File creation skipped for '{file_name_with_extension}'.")
                else:
                    print("File name must be provided.")
            else:
                print(f"Invalid file type: '{file_type}'. Choose from {list(extensions.keys())}")
        else:
            print(f"Invalid folder destination: '{folder_dest}'. Choose from {list(self.folders.keys())}")


    def open_file(self, file_path: str) -> bool:
        """
        Opens a file using the default associated application.

        :param file_name: Name of the file to open.
        :return: True if the file was opened successfully, False otherwise.
        """
        os.startfile(file_path)
        return True

    def rename(self, old_file_name: str, new_file_name: str):
        """rename only current directory files"""
        FileManager().open_file(file_name=old_file_name)
        if self.open_file(file_name=old_file_name):
            os.rename(old_file_name, new_file_name)
            print(f"File '{old_file_name}' renamed to '{new_file_name}'.")
            return True
        return False
    
    def delete_file(self, file_path: str):
        """
        Deletes a file from the current directory.
        :param file_name: Name of the file to delete.
        """
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"File '{file_path}' deleted.")
            return True
        else:
            print(f"File '{file_path}' does not exist.")
            return False

    def list_files(self, folder_dest: str):
        """
        Lists all files in the specified folder.
        """
        if folder_dest not in self.folders:
            print(f"Invalid folder destination: '{folder_dest}'. Available: {list(self.folders.keys())}")
            return
        
        folder_path = self.folders[folder_dest]
        if os.path.exists(folder_path):
            files = os.listdir(folder_path)
            print(f"Files in {folder_dest}:")
            for file in files:
                print(f"- {file}")
        else:
            print(f"Folder '{folder_dest}' does not exist.")

    def delete_file_from_folder(self, folder_dest: str, file_name: str):
        """
        Deletes a file from the specified folder.
        """
        if folder_dest not in self.folders:
            print(f"Invalid folder destination: '{folder_dest}'. Available: {list(self.folders.keys())}")
            return
        
        file_path = os.path.join(self.folders[folder_dest], file_name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"File '{file_name}' deleted from '{folder_dest}'.")
            except Exception as e:
                print(f"Error deleting file: {e}")
        else:
            print(f"File '{file_name}' does not exist in '{folder_dest}'.")

    def move_file(self, src_folder: str, dest_folder: str, file_name: str):
        """
        Moves a file from one folder to another.
        """
        if src_folder not in self.folders or dest_folder not in self.folders:
            print("Invalid source or destination folder.")
            return
        
        src_path = os.path.join(self.folders[src_folder], file_name)
        dest_path = os.path.join(self.folders[dest_folder], file_name)
        
        if os.path.exists(src_path):
            try:
                shutil.move(src_path, dest_path)
                print(f"Moved '{file_name}' from '{src_folder}' to '{dest_folder}'.")
            except Exception as e:
                print(f"Error moving file: {e}")
        else:
            print(f"File '{file_name}' not found in '{src_folder}'.")

    def rename_file(self, folder_dest: str, old_name: str, new_name: str):
        """
        Renames a file in the specified folder.
        """
        if folder_dest not in self.folders:
            print("Invalid folder destination.")
            return
        
        old_path = os.path.join(self.folders[folder_dest], old_name)
        new_path = os.path.join(self.folders[folder_dest], new_name)
        
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            print(f"Renamed '{old_name}' to '{new_name}' in '{folder_dest}'.")
        else:
            print(f"File '{old_name}' not found in '{folder_dest}'.")

    def search_file(self, file_name: str):
        """
        Searches for a file in all predefined folders.
        """
        found = False
        for folder_name, folder_path in self.folders.items():
            for root, _, files in os.walk(folder_path):
                if file_name in files:
                    print(f"File '{file_name}' found in: {root}")
                    found = True
        if not found:
            print(f"File '{file_name}' not found in any predefined folders.")

if __name__ == "__main__":
    manager = FileManager()
    #manager.create_file(folder_name='Siri17', file_name='chandu', file_type='python')
    #manager.create_folder(folder_name="test", folder_dest="desktop")
    #manager.search_file("scrap.txt")
    # manager.list_files(folder_dest='Desktop')
    # manager.rename_file(folder_dest='Desktop', old_name='chandu.py', new_name='new_chandu.py')
    # manager.move_file(src_folder='Desktop', dest_folder='Documents', file_name='new_chandu.py')
    # manager.delete_file(folder_dest='Documents', file_name='new_chandu.py')
    #manager.search_file(file_name='.venv')

    #print(manager.disk_space_available())
    #print(manager.open_file('C:\\Users\\chand\\Desktop\\Siri17\\siri.py'))
    print(manager.open_file('C:\\Users\\chand\\Desktop\\Siri17\\siri.py'))
