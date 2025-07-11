from pathlib import Path

import pytest

from rabbitmirror.qr_generator import QRGenerator


@pytest.fixture
def temp_qr_dir(tmp_path):
    """Fixture providing a temporary QR code directory."""
    qr_dir = tmp_path / "qr_codes"
    qr_dir.mkdir()
    return qr_dir


class TestQRGenerator:
    """Test suite for the QRGenerator class."""

    def test_initialization_default(self):
        """Test QRGenerator initialization with default parameters."""
        qr_gen = QRGenerator()
        assert qr_gen.output_dir == Path("qr_codes")

    def test_initialization_custom_dir(self, temp_qr_dir):
        """Test QRGenerator initialization with custom directory."""
        qr_gen = QRGenerator(output_dir=temp_qr_dir)
        assert qr_gen.output_dir == temp_qr_dir

    def test_generate_qr_basic(self, temp_qr_dir):
        """Test basic QR code generation."""
        qr_gen = QRGenerator(output_dir=temp_qr_dir)
        data = "https://example.com"
        output_path = qr_gen.generate_qr(data)

        assert Path(output_path).exists()
        assert Path(output_path).suffix == ".png"
        assert Path(output_path).parent == temp_qr_dir

    def test_generate_qr_custom_filename(self, temp_qr_dir):
        """Test QR code generation with custom filename."""
        qr_gen = QRGenerator(output_dir=temp_qr_dir)
        data = "Custom data for QR code"
        filename = "custom_qr.png"
        output_path = qr_gen.generate_qr(data, filename)

        assert Path(output_path).exists()
        assert Path(output_path).name == filename
        assert Path(output_path).parent == temp_qr_dir

    def test_generate_qr_auto_filename(self, temp_qr_dir):
        """Test QR code generation with automatic filename."""
        qr_gen = QRGenerator(output_dir=temp_qr_dir)
        data = "Test data"
        output_path = qr_gen.generate_qr(data)

        assert Path(output_path).exists()
        # Should contain hash of the data
        expected_hash = str(hash(data))
        assert (
            expected_hash in Path(output_path).stem or "qr_" in Path(output_path).stem
        )

    def test_generate_qr_different_data(self, temp_qr_dir):
        """Test QR code generation with different types of data."""
        qr_gen = QRGenerator(output_dir=temp_qr_dir)

        test_cases = [
            "https://github.com/romulusaugustus/RabbitMirror",
            "Simple text message",
            "Email: test@example.com",
            "Phone: +1-555-123-4567",
            'JSON data: {"key": "value", "number": 42}',
            "Multi-line\ntext\nwith\nlinebreaks",
        ]

        for i, data in enumerate(test_cases):
            filename = f"test_{i}.png"
            output_path = qr_gen.generate_qr(data, filename)

            assert Path(output_path).exists()
            assert Path(output_path).name == filename

    def test_generate_qr_empty_data(self, temp_qr_dir):
        """Test QR code generation with empty data."""
        qr_gen = QRGenerator(output_dir=temp_qr_dir)
        data = ""
        output_path = qr_gen.generate_qr(data)

        assert Path(output_path).exists()
        assert Path(output_path).suffix == ".png"

    def test_generate_qr_large_data(self, temp_qr_dir):
        """Test QR code generation with large data."""
        qr_gen = QRGenerator(output_dir=temp_qr_dir)
        # Create a reasonably large string
        data = "Large data: " + "A" * 1000
        output_path = qr_gen.generate_qr(data)

        assert Path(output_path).exists()
        assert Path(output_path).suffix == ".png"

    def test_generate_multiple_qr_codes(self, temp_qr_dir):
        """Test generating multiple QR codes."""
        qr_gen = QRGenerator(output_dir=temp_qr_dir)

        data_list = [
            ("Data 1", "qr1.png"),
            ("Data 2", "qr2.png"),
            ("Data 3", "qr3.png"),
        ]

        output_paths = []
        for data, filename in data_list:
            output_path = qr_gen.generate_qr(data, filename)
            output_paths.append(output_path)
            assert Path(output_path).exists()

        # Verify all files exist
        for path in output_paths:
            assert Path(path).exists()

    def test_output_directory_creation(self, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        non_existent_dir = tmp_path / "new_qr_dir"
        assert not non_existent_dir.exists()

        qr_gen = QRGenerator(output_dir=non_existent_dir)  # noqa: F841
        assert non_existent_dir.exists()
        assert non_existent_dir.is_dir()

    def test_hash_consistency(self, temp_qr_dir):
        """Test that same data produces same hash-based filename."""
        qr_gen = QRGenerator(output_dir=temp_qr_dir)
        data = "Consistent data"

        path1 = qr_gen.generate_qr(data)
        path2 = qr_gen.generate_qr(data)

        # Same data should produce same filename (will overwrite)
        assert Path(path1).name == Path(path2).name

    def test_unicode_data(self, temp_qr_dir):
        """Test QR code generation with Unicode data."""
        qr_gen = QRGenerator(output_dir=temp_qr_dir)
        unicode_data = "Unicode: 🐰 🔍 📊 Testing émojis and açcénts"
        output_path = qr_gen.generate_qr(unicode_data, "unicode_test.png")

        assert Path(output_path).exists()
        assert Path(output_path).suffix == ".png"
