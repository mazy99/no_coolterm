from threading import Thread
import time


class SerialWorker(Thread):

    def __init__(self: SerialWorker, serial_manager: SerialManager) -> None:
        super().__init__(daemon=True)
        self.serial_manager = serial_manager
        self.running = False

    def run(self: 'SerialWorker') -> None:
        self.running = True
        while self.running:
            if self.serial_manager.is_connected():
                try:
                    data = self.serial_manager.read_all()
                    if data:
                        print(f"Received: {data}")
                except Exception as e:
                    print(f"[ERROR] Worker read error: {e}")
            time.sleep(0.05)  

    def stop(self: 'SerialWorker') -> None:
        self.running = False

