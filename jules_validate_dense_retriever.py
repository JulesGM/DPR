import cerberus
import fire
import rich
import yaml
from pathlib import Path


SCHEMA_PATH_DEFAULT = "conf/dense_retriever_schema.yaml"
DATA_PATH_DEFAULT = "conf/dense_retriever.yaml"


def load_file(path):
    with open(path) as fin:
        return fin.read()


def load_yaml(path):
    return yaml.safe_load(load_file(path))


class ValidatorWithPaths(cerberus.Validator):
    path_type = cerberus.TypeDefinition("path", (Path,), ())
    types_mapping = cerberus.Validator.types_mapping.copy()
    types_mapping["path"] = path_type

    def _check_with_exists(self, field, value):
        if value is None:
            # self._errors(field, "Got None")
            pass
        elif not Path(value).exists():
            self._error(
                field, 
                f"[check_with: exists] "
                f"Doesn't exist: \"{value}\""
            )

    def _check_with_parent_exists(self, field, value):
        if value is None:
            # self._errors(field, "Got None")
            pass
        elif not Path(value).parent.exists():
            self._error(
                field, 
                f"[check_with: parent_exists] "
                f"Parent of following doesn't exist: \"{value}\""
            )

    def _normalize_coerce_path(self, value):
        if value is None:
            return value
        return Path(value)


def validate(arguments_dict, schema_path, verbose=True):
    assert arguments_dict, "argument_dict"

    schema = load_yaml(schema_path)
    validator = ValidatorWithPaths(schema)

    output = validator.validate(arguments_dict)

    if not output:
        print("Failed validation.")
        print("Errors:")
        rich.print(validator.errors)
        print("Value:")
        rich.print(arguments_dict)
        raise ValueError("Failed validation.")
    else:
        if verbose:
            rich.print("[bold]Passed validation.")
            rich.print(arguments_dict)


def main(schema_path=SCHEMA_PATH_DEFAULT, data_path=DATA_PATH_DEFAULT):
    data = load_yaml(data_path)
    validate(data, schema_path)


if __name__ == "__main__":
    fire.Fire(main)