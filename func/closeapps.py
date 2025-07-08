import psutil
from AppOpener import close_app

class CloseApps:
    @staticmethod
    def is_app_running(app_name: str) -> bool:
        """Check if the app is currently running."""
        try:
            for process in psutil.process_iter(attrs=['name']):
                if process.info['name'] and app_name.lower() in process.info['name'].lower():
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        return False

    @staticmethod
    def close_app(app_name: str) -> bool:
        """Close the app if it's running, otherwise notify that it's not running."""
        if CloseApps.is_app_running(app_name):
            try:
                close_app(app_name, output=True, match_closest=True, throw_error=True)
                #print(f"{name} app closed successfully.")
                #return f"{app_name} app closed successfully."
                return True
            except Exception as e:
                print(f"Failed to close {app_name} app: {str(e)}")
                return False
        else:
            return f"{app_name} app is not running in the background."
            

    @staticmethod
    def close_all_apps() -> bool:
        """
        Closes all running applications while ensuring system processes are not affected.
        """
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() not in ["explorer.exe", "system", "idle"]:
                    proc.terminate()  # Graceful termination
                    print(f"Terminated process: {proc.info['name']} (PID: {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return True

if __name__ == "__main__":
    o = CloseApps.close_app('whatsapp')
    print(o)