import os
from pathlib import Path
from typing import Any, cast

import ruamel.yaml


def convert_to_commented_map(
    data: dict[str, Any], comment_dict: dict[str, str] | None
) -> ruamel.yaml.CommentedMap:
    """Converts a dictionary to CommentedMap and adds comments.

    Args:
      data: The dictionary to convert.
      comment_dict: The dictionary of comments to be added.

    Returns:
      ruamel.yaml.CommentedMap.
    """
    commented_map = ruamel.yaml.CommentedMap(data)

    # Add comments
    if comment_dict:
        for key, comment in comment_dict.items():
            if key in commented_map:
                commented_map.yaml_set_comment_before_after_key(key, before=comment)
            else:
                print(
                    f"Warning: Comment key '{key}' not found at top level for adding comment."
                )

    return commented_map


def save_data_to_yaml_with_comments(
    data: dict[str, Any],
    output_yaml_file: Path,
    *,
    comment_dict: dict[str, str] | None = None,
    indent: int = 2,
    file_permission: int = 0o644,
    dir_permission: int = 0o755,
    encoding: str = "utf-8",
) -> None:
    """Saves a data dictionary to a YAML file with comments.

    Args:
      data: Input data dictionary to be saved.
      output_yaml_file: Path to the output YAML file.
      comment_dict: The dictionary of comments to be added.
      indent: The indentation level for the JSON output. Defaults to 2.
      permission: The file permissions for the created file. Defaults to 0o644.
      encoding: The character encoding to use for writing the file. Defaults to "utf-8".

    Raises:
      - ValueError: If a YAML-related issue occurs during saving.
      - OSError: If a file system-related issue occurs during writing.
    """
    yaml = ruamel.yaml.YAML()
    yaml.allow_unicode = True
    yaml.indent(mapping=indent, sequence=indent + 2, offset=0)

    data = convert_to_commented_map(data, comment_dict=comment_dict)

    try:
        # make a parent directory
        output_yaml_file.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(output_yaml_file.parent, dir_permission)

        # save a yaml file
        with open(output_yaml_file, "w", encoding=encoding) as f:
            yaml.dump(data, f)
        os.chmod(output_yaml_file, file_permission)
    except ruamel.yaml.YAMLError as e:
        raise ValueError(
            f"YAML encoding/serialization issue occurs when saving to {output_yaml_file}."
        ) from e
    except OSError as e:
        raise OSError(f"Failed to write the file: {output_yaml_file}.") from e


def load_data_from_yaml(
    input_yaml_file: Path, *, encoding: str = "utf-8"
) -> dict[str, Any]:
    """Loads a YAML file and returns a data dictionary.

    Args:
      input_yaml_file: Path to the input YAML file.
      encoding: The character encoding to use for loading the file. Defaults to "utf-8".

    Returns:
      A dictionary parsed from the YAML file.

    Raises:
        - FileNotFoundError: If the input file is not found.
        - ValueError: If a YAML parsing issue, or a Unicode decoding error occurs.
        - OSError: If a file system-related issue occurs during loading.
    """
    yaml = ruamel.yaml.YAML(typ="safe")

    try:
        with open(input_yaml_file, encoding=encoding) as f:
            data = cast(dict[str, Any], yaml.load(f))
        return data if data is not None else {}
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Input file not found: {input_yaml_file}.") from e
    except ruamel.yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file: {input_yaml_file}") from e
    except UnicodeDecodeError as e:
        raise ValueError(
            f"file {input_yaml_file} is not encoded in {encoding.upper()}. Save it again in {encoding.upper()}."
        ) from e
    except OSError as e:
        raise OSError(f"Failed to load the file: {input_yaml_file}.") from e
