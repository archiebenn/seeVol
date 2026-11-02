import numpy as np
import pytest

from seevol.cli import main


def test_cli_saves_visibility_results(tmp_path):
    volume_path = tmp_path / "volume.npy"
    output_path = tmp_path / "visibility.npz"
    np.save(volume_path, np.ones((2, 2, 2), dtype=np.uint8))

    assert main([str(volume_path), "--output", str(output_path)]) == 0

    with np.load(output_path) as result:
        assert result["coords"].shape == (8, 3)
        assert result["edges"].shape == (28, 2)
        np.testing.assert_array_equal(result["scores"], np.ones(8))


def test_cli_scores_single_open_voxel_as_zero(tmp_path):
    volume_path = tmp_path / "volume.npy"
    output_path = tmp_path / "visibility.npz"
    np.save(volume_path, np.ones((1, 1, 1), dtype=np.uint8))

    main([str(volume_path), "--output", str(output_path)])

    with np.load(output_path) as result:
        np.testing.assert_array_equal(result["scores"], np.zeros(1))


def test_cli_rejects_non_binary_input(tmp_path):
    volume_path = tmp_path / "volume.npy"
    np.save(volume_path, np.full((2, 2, 2), 2, dtype=np.uint8))

    with pytest.raises(SystemExit) as error:
        main([str(volume_path), "--output", str(tmp_path / "visibility.npz")])
    assert error.value.code == 2
