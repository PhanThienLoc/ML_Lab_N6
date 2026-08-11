from src.logger import get_log_path


def test_log_path():
    path = get_log_path()

    assert str(path).endswith(
        "experiments.csv"
    )
