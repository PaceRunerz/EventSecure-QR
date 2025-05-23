import qrcode
import hashlib
import csv
import cv2
import os
from pyzbar.pyzbar import decode

class QRAttendanceSystem:
    def __init__(self):
        # Configuration - User should modify these
        self.SECRET_KEY = "your_secret_key_here"  # Change before deployment
        self.QR_OUTPUT_DIR = "generated_qrcodes"
        self.PARTICIPANTS_FILE = "participants.csv"
        self.ATTENDANCE_FILE = "attendance.csv"
        
        # Create output directory if not exists
        os.makedirs(self.QR_OUTPUT_DIR, exist_ok=True)

    def generate_qr(self, data):
        """Generate QR code with encrypted data"""
        secure_data = f"{data}|{hashlib.sha256((data + self.SECRET_KEY).encode()).hexdigest()}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(secure_data)
        qr.make(fit=True)
        return qr.make_image(fill="black", back_color="white")

    def validate_qr(self, data):
        """Validate scanned QR code"""
        try:
            participant_data, received_hash = data.rsplit("|", 1)
            expected_hash = hashlib.sha256(
                (participant_data + self.SECRET_KEY).encode()
            ).hexdigest()
            return received_hash == expected_hash, participant_data
        except Exception:
            return False, None

    def generate_participant_qrs(self, participants):
        """Generate QR codes for all participants"""
        # Save participant data
        with open(self.PARTICIPANTS_FILE, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["name", "reg_no"])
            writer.writeheader()
            writer.writerows(participants)
        
        # Generate QR codes
        for participant in participants:
            data = f"{participant['name']},{participant['reg_no']}"
            img = self.generate_qr(data)
            img.save(os.path.join(self.QR_OUTPUT_DIR, f"{participant['reg_no']}.png"))
        
        print(f"Generated {len(participants)} QR codes in '{self.QR_OUTPUT_DIR}' folder")
        print(f"Participant data saved to '{self.PARTICIPANTS_FILE}'")

    def scan_attendance(self):
        """Scan QR codes and mark attendance"""
        processed = set()
        cap = cv2.VideoCapture(0)
        
        print("\nQR Scanner Active - Press 'q' to quit")
        print("Waiting for QR codes...")

        while True:
            _, frame = cap.read()
            
            for barcode in decode(frame):
                qr_data = barcode.data.decode("utf-8")
                
                if qr_data not in processed:
                    is_valid, participant_data = self.validate_qr(qr_data)
                    
                    if is_valid:
                        name, reg_no = participant_data.split(",")
                        self._record_attendance(reg_no)
                        processed.add(qr_data)
                        print(f"✅ {name} ({reg_no}) - Attendance recorded")
                    else:
                        print("❌ Invalid QR Code - Not recognized")

            cv2.imshow("QR Scanner", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()
        print(f"\nAttendance records saved to '{self.ATTENDANCE_FILE}'")

    def _record_attendance(self, reg_no):
        """Internal method to record attendance"""
        with open(self.ATTENDANCE_FILE, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([reg_no])

# Sample Usage
if __name__ == "__main__":
    system = QRAttendanceSystem()
    
    # Sample data - Replace with your actual participants
    sample_participants = [
        {"name": "John Doe", "reg_no": "23ABC1001"},
        {"name": "Jane Smith", "reg_no": "23XYZ2002"}
    ]
    
    # Generate QR Codes (run once)
    system.generate_participant_qrs(sample_participants)
    
    # Scan attendance (run during event)
    # system.scan_attendance()
