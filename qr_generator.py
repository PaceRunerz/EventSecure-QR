import qrcode
import hashlib
import csv

SECRET_KEY = "your_secret_key"  # Change this in production!

def generate_qr(data):
    """Generate QR code with encrypted data"""
    secure_data = f"{data}|{hashlib.sha256((data + SECRET_KEY).encode()).hexdigest()}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(secure_data)
    qr.make(fit=True)
    return qr.make_image(fill="black", back_color="white")

def generate_participant_qrs(participants_file, output_dir="qrcodes"):
    """Generate QR codes for all participants"""
    import os
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(participants_file, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data = f"{row['name']},{row['reg_no']}"
            img = generate_qr(data)
            img.save(f"{output_dir}/{row['reg_no']}_qr.png")

if __name__ == "__main__":
    # Example usage
    generate_participant_qrs("sample_data/participants.csv")
