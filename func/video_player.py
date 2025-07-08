import os
import subprocess
import platform
from pyauto import execute_hotkey
from time import sleep
from app_status import get_app_name


class VideoPlayer:
    def __init__(self, player_settings=None):
        """
        Initialize the VideoPlayer with optional settings.
        :param player_settings: Dictionary for custom player settings.
        """
        self.player_settings = player_settings if player_settings else {}

    @staticmethod
    def play_video(video_path):
        """
        Play a video file using the default system player.
        :param video_path: Path to the video file.
        """
        video_path = os.path.normpath(video_path)

        if not os.path.isfile(video_path):
            print(f"Error: File not found at '{video_path}'")
            return

        try:
            system_platform = platform.system()
            if system_platform == "Windows":
                os.startfile(video_path)
            elif system_platform == "Darwin":  # macOS
                subprocess.run(["open", video_path], check=True)
            elif system_platform == "Linux":
                subprocess.run(["xdg-open", video_path], check=True)
            else:
                print(f"Error: Unsupported operating system '{system_platform}'.")
                return

            print(f"Playing video: '{video_path}'")
        except FileNotFoundError:
            print(f"Error: Unable to locate the required program to open the video on {system_platform}.")
        except subprocess.SubprocessError as e:
            print(f"Error: A subprocess error occurred: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def commands(self, command):
        """
        Execute a video player command (e.g., fullscreen, zoom, play, pause).
        :param command: The command to execute (e.g., 'fullscreen', 'zoom').
        """
        valid_commands = {
            "fullscreen": lambda: execute_hotkey('alt', 'enter'),
            "zoom": lambda: execute_hotkey('ctrl', 'shift', 'z'),
            "play": lambda: execute_hotkey('space'),
            "pause": lambda: execute_hotkey('space'),
        }

        if get_app_name() == "Media Player":

            if command in valid_commands:
                try:
                    valid_commands[command]()
                    print(f"Executed command: '{command}'")
                except Exception as e:
                    print(f"Unexpected error executing '{command}': {e}")
            else:
                print(f"Error: Invalid command '{command}'. Valid commands are: {', '.join(valid_commands.keys())}")

        else:
            print(f"Error: This function is only available in the Media Player app.")


# Example Usage
if __name__ == "__main__":
    player = VideoPlayer()

    
    
    video_path = "hotword.mp4"
    player.play_video(video_path)

    sleep(2)
    # Execute commands
    player.commands("fullscreen")
    # player.commands("play")
    # player.commands("pause")
    # player.commands("zoom")
