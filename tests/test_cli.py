"""CLI integration tests."""

from pathlib import Path

from PIL import Image

from image_compressor.cli import main


def test_cli_writes_all_requested_outputs(tmp_path: Path) -> None:
    source = tmp_path / "input.png"
    output = tmp_path / "output.png"
    boundaries = tmp_path / "boundaries.png"
    animation = tmp_path / "animation.gif"
    Image.new("RGB", (8, 8), "blue").save(source)

    assert main(
        [
            str(source),
            "--output",
            str(output),
            "--boundaries",
            str(boundaries),
            "--gif",
            str(animation),
            "--workers",
            "2",
        ]
    ) == 0
    assert output.exists()
    assert boundaries.exists()
    assert animation.exists()
