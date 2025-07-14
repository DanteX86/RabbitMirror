from pathlib import Path
from typing import Optional

import qrcode


class QRGenerator:
    def __init__(
        self,
        output_dir: str = "qr_codes",
        size: int = 10,
        error_correction: str = "M",
        color: str = "black",
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.size = size
        self.error_correction = error_correction
        self.color = color

        # Map error correction string to constant
        self.error_correction_map = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H,
        }

    def generate_qr(self, data: str, filename: Optional[str] = None) -> str:
        """Generate a QR code for the given data and save it to a file."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=self.error_correction_map.get(
                self.error_correction, qrcode.constants.ERROR_CORRECT_M
            ),
            box_size=self.size,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        image = qr.make_image(fill_color=self.color, back_color="white")

        if filename is None:
            filename = f"qr_{hash(data)}.png"

        output_path = self.output_dir / filename
        image.save(output_path)

        return str(output_path)
