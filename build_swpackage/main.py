import time
import subprocess
import shutil
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver
from datetime import datetime
from pathlib import Path

g_current_dir = Path(__file__).resolve().parent
print(f"main.py_dir: {g_current_dir}")

folder_path = '/media/sf_C_DRIVE/Users/ppa2hc/etas_ota/fota'

g_dreamkit_id = None

if len(sys.argv) < 2:
    print("Usage: python3 main.py <dreamKIT-ID>")
    sys.exit(1)
    
g_dreamkit_id = sys.argv[1]
print("dreamKIT ID:", g_dreamkit_id)

class DebouncedEventHandler(FileSystemEventHandler):
    def __init__(self, debounce_interval=0.5):
        super().__init__()
        self.debounce_interval = debounce_interval
        self.last_events = {}  # {(path, event_type): last_event_time}

    def should_process(self, event_type, path):
        now = time.time()
        key = (path, event_type)
        last_time = self.last_events.get(key, 0)

        if now - last_time > self.debounce_interval:
            self.last_events[key] = now
            return True
        return False

    def deployPackageToTarget(self, src_path):
        print(f"deployPackageToTarget: {src_path}")

        # Check if file extension is .hex
        if not src_path.endswith(".hex"):
            print("Only .hex files are supported. Exiting.")
            return

        target_fota_json = f"{g_current_dir}/swpackage/fota/fota.json"
        if "ambient" in src_path:
            print("Deploying ambient package...")
            target_fota_json = f"{g_current_dir}/swpackage/fota/fota_ambient.json"
        elif "motor" in src_path:
            print("Deploying motor package...")
            target_fota_json = f"{g_current_dir}/swpackage/fota/fota_motor.json"
        else:
            print("src type not supported. Exiting.")
            return
        cmd = f"cp {target_fota_json} {g_current_dir}/swpackage/fota/fota.json"
        result = subprocess.run(cmd, shell=True)
        if result.returncode == 0:
            print(f"Script executed successfully. cmd: {cmd}")
        else:
            print(f"Script execution failed with return code: {result.returncode}. cmd: {cmd}")

        hex2bin_script = f"{g_current_dir}/hex2bin.py"
        bin_path = f"{g_current_dir}/swpackage/fota/tc375/app.bin"
        cmd = f"python3 {hex2bin_script} {src_path} 0x80100000 0x80200000 {bin_path}"
        result = subprocess.run(cmd, shell=True)
        if result.returncode == 0:
            print(f"Script executed successfully. cmd: {cmd}")
        else:
            print(f"Script execution failed with return code: {result.returncode}. cmd: {cmd}")

        # Path to swpackage folder
        swpackage_folder = f"{g_current_dir}/swpackage"
        # Path to output zip file (will be created in the same directory as swpackage)
        zip_output = f"{g_current_dir}/swpackage.zip"
        print(f"remove old package: {zip_output}")
        cmd = f"rm {zip_output}"
        subprocess.run(cmd, shell=True)
        # # Create zip archive including the 'swpackage' folder as root inside the zip
        _current_dir = Path(g_current_dir)
        _zip_output = _current_dir / "swpackage.zip"
        shutil.make_archive(
           base_name=str(_zip_output.with_suffix('')),
           format='zip',
           root_dir=str(_current_dir),
           base_dir='swpackage'
        )

        print(f"Created zip archive: {zip_output}")

        deploy2kit_script = f"{g_current_dir}/deployToKit.py"
        cmd = f"python3 {deploy2kit_script} {g_dreamkit_id}"
        subprocess.run(cmd, shell=True)

    def on_created(self, event):
        # Ignore directory modifications to reduce noise
        if event.is_directory:
            return

        # Check if the file has .hex extension (case-insensitive)
        if not event.src_path.lower().endswith('.hex'):
            print(f"on_modified: not the hex file. Failed.")
            return  # Skip non-hex files

        if self.should_process('created', event.src_path):
            now_str = datetime.now().strftime('%H:%M:%S')
            print(f"{now_str} - Created: {event.src_path}")
            self.deployPackageToTarget(event.src_path)

    def on_modified(self, event):
        # Ignore directory modifications to reduce noise
        if event.is_directory:
            return

        # Check if the file has .hex extension (case-insensitive)
        if not event.src_path.lower().endswith('.hex'):
            print(f"on_modified: not the hex file. Failed.")
            return  # Skip non-hex files

        if self.should_process('modified', event.src_path):
            now_str = datetime.now().strftime('%H:%M:%S')
            print(f"{now_str} - Modified: {event.src_path}")
            self.deployPackageToTarget(event.src_path)
            
    def on_deleted(self, event):
        if self.should_process('deleted', event.src_path):
            now_str = datetime.now().strftime('%H:%M:%S')
            print(f"{now_str} - Deleted: {event.src_path}")

    def on_moved(self, event):
        if self.should_process('moved_from', event.src_path):
            now_str = datetime.now().strftime('%H:%M:%S')
            print(f"{now_str} - Moved from: {event.src_path}")
        if self.should_process('moved_to', event.dest_path):
            now_str = datetime.now().strftime('%H:%M:%S')
            print(f"{now_str} - Moved to: {event.dest_path}")


def main():
    event_handler = DebouncedEventHandler(debounce_interval=0.5)

    # observer = Observer()
    # observer.schedule(event_handler, folder_path, recursive=True)
    # observer.start()

    observer = PollingObserver()
    observer.schedule(event_handler, folder_path, recursive=True)
    observer.start()

    print(f"Monitoring folder: {folder_path}")
    print("Press Ctrl+C to exit.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping observer...")
        observer.stop()
    observer.join()


if __name__ == '__main__':
    main()
