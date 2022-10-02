import json
import pathlib
import textwrap


def pytest_generate_tests(metafunc):
    if "config_data" not in metafunc.fixturenames:
        return
    test_file_path = pathlib.Path(metafunc.module.__file__)
    test_config = (
        test_file_path.parent
        / "resources"
        / test_file_path.with_suffix("").name
        / metafunc.function.__name__
    ).with_suffix(".json")
    test_config_content = json.loads(test_config.read_text())
    if not isinstance(test_config_content, list):
        raise Exception(
            f"config_data for {metafunc.function.__name__} in {metafunc.module.__file__} isn't a list"
        )
    metafunc.parametrize(
        "config_data",
        test_config_content,
        ids=(
            textwrap.shorten(config_data.__str__(), 100, placeholder="...")
            for config_data in test_config_content
        ),
    )
