import pytest
from PIL import Image
import pillow_heif

from heic_to_jpeg import convert_heic_to_jpeg, find_jobs


def make_heic(path, mode="RGB"):
    path.parent.mkdir(parents=True, exist_ok=True)
    pillow_heif.from_pillow(Image.new(mode, (8, 8), "red")).save(str(path))


def test_preserves_structure_and_extension_case(tmp_path):
    src, out = tmp_path / "in", tmp_path / "out"
    make_heic(src / "a.heic")
    make_heic(src / "sub" / "b.HEIC")
    counts = convert_heic_to_jpeg(str(src), str(out))
    assert counts == {"converted": 2, "skipped": 0, "failed": 0}
    assert (out / "a.jpg").exists()
    assert (out / "sub" / "b.jpg").exists()


def test_name_collisions_get_unique_names(tmp_path):
    src = tmp_path / "in"
    make_heic(src / "a.heic")
    make_heic(src / "a.HEIC")
    names = {out for _, out in find_jobs(str(src), str(tmp_path / "out"))}
    assert len(names) == 2


def test_skip_then_overwrite(tmp_path):
    src, out = tmp_path / "in", tmp_path / "out"
    make_heic(src / "a.heic")
    convert_heic_to_jpeg(str(src), str(out))
    assert convert_heic_to_jpeg(str(src), str(out))["skipped"] == 1
    assert convert_heic_to_jpeg(str(src), str(out), overwrite=True)["converted"] == 1


def test_alpha_image_converts(tmp_path):
    src, out = tmp_path / "in", tmp_path / "out"
    make_heic(src / "a.heic", mode="RGBA")
    assert convert_heic_to_jpeg(str(src), str(out))["converted"] == 1


def test_corrupt_file_counts_as_failed(tmp_path):
    src, out = tmp_path / "in", tmp_path / "out"
    src.mkdir()
    (src / "bad.heic").write_bytes(b"not an image")
    assert convert_heic_to_jpeg(str(src), str(out))["failed"] == 1


@pytest.mark.parametrize("workers", [1, 3])
def test_workers(tmp_path, workers):
    src, out = tmp_path / "in", tmp_path / "out"
    for i in range(4):
        make_heic(src / f"{i}.heic")
    assert convert_heic_to_jpeg(str(src), str(out), workers=workers)["converted"] == 4
