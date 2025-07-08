import psutil
import win32gui
import win32process
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AppInfo:
    @staticmethod
    def get_active_window_info():
        """Returns the title and process name of the currently active window."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid > 0:
                window_title = win32gui.GetWindowText(hwnd)
                process_name = psutil.Process(pid).name()
                return window_title, process_name
            return None, None
        except Exception as e:
            logging.error(f"Error in get_active_window_info: {e}")
            return None, None

    @staticmethod
    def get_app_name():
        """Extracts the app name from the active window title."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid > 0:
                window_title = win32gui.GetWindowText(hwnd)
                if " - " in window_title:
                    return window_title.split(" - ")[-1].strip()
                return window_title.strip()
            return None
        except Exception as e:
            logging.error(f"Error in get_app_name: {e}")
            return None

    @staticmethod
    def app_status_check(duration=10):
        """
        Continuously prints active window info for a given duration in seconds.
        """
        try:
            end_time = time.time() + duration
            while time.time() < end_time:
                title, process = AppInfo.get_active_window_info()
                if title and process:
                    print(f"🪟 Active Window: {title} | 🧠 Process: {process}")
                else:
                    print("⚠️ No active window detected.")
                time.sleep(1)
        except KeyboardInterrupt:
            print("🛑 Monitoring stopped by user.")
        except Exception as e:
            logging.error(f"Error in app_status_check: {e}")

    @staticmethod
    def is_app_running(app_name):
        """Returns True if app with 'app_name' is running; otherwise False."""
        try:
            for proc in psutil.process_iter(['name']):
                if app_name.lower() in proc.info['name'].lower():
                    return True
            return False
        except Exception as e:
            logging.error(f"Error checking if app is running: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    app_to_check = "WhatsApp"
    if AppInfo.is_app_running(app_to_check):
        print(f"✅ {app_to_check} is running in the background.")
    else:
        print(f"❌ {app_to_check} is NOT running.")
    
    print("\n🔍 Monitoring active window for 5 seconds:")
    AppInfo.app_status_check(duration=5)
