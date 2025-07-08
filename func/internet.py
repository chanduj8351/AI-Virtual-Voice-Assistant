import os
import speedtest
import socket
import subprocess


class Internet:
    @staticmethod
    def is_connected() -> bool:
        """Check if the device is connected to the internet."""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)  # Google's DNS
            return True
        except OSError:
            return False
        

    @staticmethod
    def connect_to_wifi(ssid: str = "Hello", password: str = "12345678"):
        """
        Connect to a specified Wi-Fi network.

        :param ssid: The SSID of the Wi-Fi network.
        :param password: The password of the Wi-Fi network.
        """
        try:
            if not ssid or not password:
                print("❌ SSID and Password are required.")
                return False

            # Define profile path
            profile_path = os.path.join(os.getcwd(), f"{ssid}.xml")

            subprocess.run(['netsh', 'wlan', 'add', 'profile', f'filename={profile_path}'], capture_output=True, text=True)

            # Connect to Wi-Fi
            result = subprocess.run(['netsh', 'wlan', 'connect', f'name={ssid}'], capture_output=True, text=True, encoding='utf-8')

            if "completed successfully" in result.stdout.lower():
                print(f"✅ Successfully connected to {ssid}")
                return True
            else:
                print(f"❌ Failed to connect to {ssid}: {result.stdout}")
                return False

        except Exception as e:
            print(f"❌ Error connecting to Wi-Fi: {e}")
            return False

    @staticmethod
    def disconnect_wifi():
        """
        Disconnect from the current Wi-Fi network.
        """
        try:
            result = subprocess.run(['netsh', 'wlan', 'disconnect'], capture_output=True, text=True, encoding='utf-8')
            
            if "disconnected" in result.stdout.lower():
                print("❌ Failed to disconnect: {result.stdout}")
                return True
            else:
                print(f"✅ Disconnected from Wi-Fi")
                return False

        except Exception as e:
            print(f"❌ Error disconnecting from Wi-Fi: {e}")
            return False


    @staticmethod
    def check_internet_speed():
        """
        Check the internet speed (download, upload, and ping).
        """
        try:
            st = speedtest.Sp()
            st.get_best_server()

            print("Testing download speed...")
            download_speed = st.download() / 1_000_000  # Convert to Mbps

            print("Testing upload speed...")
            upload_speed = st.upload() / 1_000_000  # Convert to Mbps

            ping = st.results.ping

            print("\n--- Internet Speed Results ---")
            print(f"Download Speed: {download_speed:.2f} Mbps")
            print(f"Upload Speed: {upload_speed:.2f} Mbps")
            print(f"Ping: {ping:.2f} ms")

            return {
                "download_speed": round(download_speed, 2),
                "upload_speed": round(upload_speed, 2),
                "ping": round(ping, 2),
            }
        
        except Exception as e:
            return f"❌ Unexpected error: {e}"

    @staticmethod
    def list_available_networks():
        """
        List all available Wi-Fi networks.
        """
        try:
            result = subprocess.run(['netsh', 'wlan', 'show', 'networks'], capture_output=True, text=True, encoding='utf-8')
            return result.stdout
        except Exception as e:
            return f"❌ Error listing networks: {e}"
             

    @staticmethod
    def get_current_network():
        """
        Get the currently connected Wi-Fi network.
        """
        try:
            result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True, encoding='utf-8')
            lines = result.stdout.split('\n')
            for line in lines:
                if "SSID" in line and "BSSID" not in line:
                    return line.split(":")[1].strip()
            return None
        except Exception as e:
            return f"❌ Error retrieving current network: {e}"
            

    

if __name__ == "__main__":
    Internet.connect_to_wifi()

