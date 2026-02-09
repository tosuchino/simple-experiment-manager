import json
import os
from pathlib import Path
from typing import Any, cast


def save_data_to_json(
    data: dict[str, Any],
    output_json_file: Path,
    *,
    indent: int = 2,
    file_permission: int = 0o644,
    dir_permission: int = 0o755,
    encoding: str = "utf-8",
) -> None:
    """Saves a data dictionary to a JSON file.

    Args:
        data: Input data dictionary to be saved.
        output_json_file: Path to the output JSON file.
        indent: The indentation level for the JSON output. Defaults to 2.
        permission: The file permissions for the created file. Defaults to 0o644.
        encoding: The character encoding to use for writing the file. Defaults to "utf-8".

    Raises:
      - ValueError: If a JSON encoding issue occurs during saving.
      - OSError: If a file system-related issue occurs during writing (e.g., permission denied, disk full)
    """
    try:
        # make a parent directory
        output_json_file.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(output_json_file.parent, dir_permission)

        # save a json file
        with open(output_json_file, "w", encoding=encoding) as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        os.chmod(output_json_file, file_permission)
    except TypeError as e:
        raise ValueError(
            f"JSON encoding issue occurs when saving to {output_json_file}."
        ) from e
    except OSError as e:
        raise OSError(f"Failed to write the file: {output_json_file}.") from e


def load_data_from_json(
    input_json_file: Path, *, encoding: str = "utf-8"
) -> dict[str, Any]:
    """Loads a JSON file and returns a data dictionary.

    Args:
        input_json_file: Path to the input JSON file.
        encoding: The character encoding to use for loading the file. Defaults to "utf-8".

    Returns:
        A dictionary parsed from the JSON file.

    Raises:
      - FileNotFoundError: If the input file is not found or if a JSON decoding error occurs.
      - ValueError: If a JSON decoding error occurs.
      - OSError: If a file system-related issue occurs during loading.
    """
    try:
        with open(input_json_file, encoding=encoding) as f:
            data = cast(dict[str, Any], json.load(f))
        return data if data is not None else {}
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Input file not found: {input_json_file}.") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing JSON file: {input_json_file}.") from e
    except UnicodeDecodeError as e:
        raise ValueError(
            f"""File {input_json_file} is not encoded in {encoding.upper()}.
                Please save it again in {encoding.upper()}."""
        ) from e
    except OSError as e:
        raise OSError(f"Failed to read file: {input_json_file}.") from e
