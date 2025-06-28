import qrcode
from typing import Optional
from pathlib import Path

class QRGenerator:
    def __init__(self, output_dir: str = 'qr_codes'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_qr(self, data: str, filename: Optional[str] = None) -> str:
        """Generate a QR code for the given data and save it to a file."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        image = qr.make_image(fill_color="black", back_color="white")
        
        if filename is None:
            filename = f'qr_{hash(data)}.png'
        
        output_path = self.output_dir / filename
        image.save(output_path)
        
        return str(output_path)
