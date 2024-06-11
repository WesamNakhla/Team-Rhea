import os

class FileHandler:
    def __init__(self):
        self.loaded_files = []
        self.selected_file = None  # Changed to None for clarity
        print(f"\nInitialized FileHandler with loaded_files: {self.loaded_files} and selected_file: {self.selected_file}\n")


    def remove_path(self, file_path, remove_extension=False):
        file_name = os.path.basename(file_path)
        if remove_extension:
            file_name = os.path.splitext(file_name)[0]
        print(f"\nremove_path called with file_path: {file_path}, remove_extension: {remove_extension}. Result: {file_name}\n")
        return file_name

    def remove_file(self, index):
        if 0 <= index < len(self.loaded_files):
            removed_file = self.loaded_files[index]
            del self.loaded_files[index]
            print(f"\nRemoved file at index {index}: {removed_file}. Updated loaded_files: {self.loaded_files}\n")
            if self.selected_file is not None and self.selected_file >= len(self.loaded_files):
                self.selected_file = max(0, len(self.loaded_files) - 1)
                print(f"\nUpdated selected_file index to {self.selected_file}\n")
        else:
            print(f"\nAttempted to remove file at index {index}, which is out of range.\n")
            raise IndexError("Index out of range")

    def load_files(self, file_path):
        self.loaded_files.append(file_path)
        if self.loaded_files:
            self.selected_file = len(self.loaded_files) - 1  # Ensure selected_file is set to the last loaded file
        print(f"\nLoaded files: {self.loaded_files}. Updated loaded_files: {self.loaded_files}. Selected file: {self.get_selected_file()}\n")

    def get_selected_file(self):
        #return the path the selected file
        #selected_file is displaying the index of the loaded_files list that is selected
        if self.selected_file is not None and 0 <= self.selected_file < len(self.loaded_files):
            print(f"\nget_selected_file called. Result: {self.loaded_files[self.selected_file]}\n")
            return self.loaded_files[self.selected_file]
        else:
            print(f"\nget_selected_file called. Result: None\n")
            return None

    def get_loaded_files(self):
        print(f"\nget_loaded_files called. Result: {self.loaded_files}\n")
        return self.loaded_files

# Example usage
if __name__ == "__main__":
    fh = FileHandler()
    fh.load_file("c:/files/somefile.png")
    fh.load_file("c:/files/anotherfile.png")
    print("\nLoaded files:", fh.get_loaded_files())
    print("\nSelected file:", fh.get_selected_file())
    print("\nRemoving path:", fh.remove_path(fh.get_selected_file()))
    fh.remove_file(0)
    print("\nLoaded files after removal:", fh.get_loaded_files())
    print("\nSelected file after removal:", fh.get_selected_file())
