import cv2
from pyzbar.pyzbar import decode
import hashlib
import csv

SECRET_KEY = "your_secret_key"  # Must match generator's key

def validate_qr(data):
    """Validate QR code authenticity"""
    try:
        participant_data, received_hash = data.rsplit("|", 1)
        expected_hash = hashlib.sha256((participant_data + SECRET_KEY).encode()).hexdigest()
        return received_hash == expected_hash, participant_data
    except Exception as e:
        print(f"Validation error: {e}")
        return False, None

def mark_attendance(reg_no, output_file="sample_data/attendance.csv"):
    """Record attendance in CSV"""
    with open(output_file, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([reg_no])

def scan_qr_codes(participants_file):
    """Main scanning function"""
    processed_codes = set()
    cap = cv2.VideoCapture(0)
    
    while True:
        _, frame = cap.read()
        for barcode in decode(frame):
            qr_data = barcode.data.decode("utf-8")
            
            if qr_data not in processed_codes:
                is_valid, participant_data = validate_qr(qr_data)
                if is_valid:
                    reg_no = participant_data.split(",")[1]
                    mark_attendance(reg_no)
                    processed_codes.add(qr_data)
                    print(f"Attendance marked for: {participant_data}")
        
        cv2.imshow("QR Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    scan_qr_codes("sample_data/participants.csv")
