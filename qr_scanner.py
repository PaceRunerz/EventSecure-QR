import cv2
from pyzbar.pyzbar import decode
import hashlib
import csv
import os
from datetime import datetime

class QRScanner:
    def __init__(self):
        # Configuration - User should modify these
        self.SECRET_KEY = "your_secret_key_here"  # Must match generator's key
        self.PARTICIPANTS_FILE = "participants.csv"
        self.ATTENDANCE_FILE = f"attendance_{datetime.now().strftime('%Y%m%d')}.csv"
        self.processed_codes = set()
        
        # Initialize participants database
        self.participants = self._load_participants()
        
    def _load_participants(self):
        """Load participant data from CSV"""
        try:
            with open(self.PARTICIPANTS_FILE, "r") as csvfile:
                return {row["reg_no"]: row for row in csv.DictReader(csvfile)}
        except FileNotFoundError:
            print(f"⚠️ Error: {self.PARTICIPANTS_FILE} not found!")
            return {}
        except Exception as e:
            print(f"⚠️ Error loading participants: {e}")
            return {}

    def _validate_qr(self, data):
        """Validate QR code authenticity"""
        try:
            participant_data, received_hash = data.rsplit("|", 1)
            expected_hash = hashlib.sha256(
                (participant_data + self.SECRET_KEY).encode()
            ).hexdigest()
            return received_hash == expected_hash, participant_data
        except Exception as e:
            print(f"⚠️ Validation error: {e}")
            return False, None

    def _record_attendance(self, reg_no, name):
        """Record attendance with timestamp"""
        try:
            file_exists = os.path.isfile(self.ATTENDANCE_FILE)
            with open(self.ATTENDANCE_FILE, "a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    writer.writerow(["Registration No", "Name", "Timestamp"])
                writer.writerow([
                    reg_no,
                    name,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ])
            return True
        except Exception as e:
            print(f"⚠️ Failed to record attendance: {e}")
            return False

    def start_scanning(self):
        """Main scanning loop"""
        if not self.participants:
            print("❌ Cannot start scanning - No participants loaded")
            return

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Error: Could not access camera")
            return

        print("\n" + "="*40)
        print("QR Attendance Scanner Active")
        print(f"Loaded {len(self.participants)} participants")
        print("Press 'q' to quit")
        print("="*40 + "\n")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Camera feed error")
                break

            for barcode in decode(frame):
                qr_data = barcode.data.decode("utf-8")
                
                if qr_data in self.processed_codes:
                    continue

                is_valid, participant_data = self._validate_qr(qr_data)
                
                if is_valid:
                    try:
                        name, reg_no = participant_data.split(",")
                        if reg_no in self.participants:
                            if self._record_attendance(reg_no, name):
                                self.processed_codes.add(qr_data)
                                print(f"✅ {name} ({reg_no}) - Attendance recorded")
                            else:
                                print(f"⚠️ Failed to record {name}")
                        else:
                            print(f"❌ Unknown participant: {reg_no}")
                    except Exception as e:
                        print(f"⚠️ Processing error: {e}")
                else:
                    print("❌ Invalid QR Code - Not recognized")

            cv2.imshow("QR Scanner", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()
        print(f"\nScanning stopped. Attendance saved to '{self.ATTENDANCE_FILE}'")

if __name__ == "__main__":
    scanner = QRScanner()
    scanner.start_scanning()
