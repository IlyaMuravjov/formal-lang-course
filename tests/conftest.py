import json
import pathlib
import textwrap


def pytest_generate_tests(metafunc):
    if "config_data" not in metafunc.fixturenames:
        return
    test_file_path = pathlib.Path(metafunc.module.__file__)
    test_file_config = (
        test_file_path.parent / "resources" / test_file_path.name
    ).with_suffix(".json")
    test_file_data = json.loads(test_file_config.read_text())
    test_function_data = test_file_data.get(metafunc.function.__name__)
    if not isinstance(test_function_data, list):
        raise Exception(
            f"config_data for {metafunc.function.__name__} in {metafunc.module.__file__} isn't a list"
        )
    metafunc.parametrize(
        "config_data",
        test_function_data,
        ids=(
            textwrap.shorten(config_data.__str__(), 100, placeholder="...")
            for config_data in test_function_data
        ),
    )
