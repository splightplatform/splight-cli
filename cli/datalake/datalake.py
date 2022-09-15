import pandas as pd
import splight_models as models
from datetime import datetime
from cli.utils import *
from cli.constants import DEFAULT_NAMESPACE


class Datalake:

    def __init__(self, context):
        self.context = context
        self.namespace = DEFAULT_NAMESPACE

    @property
    def client(self):
        return self.context.framework.setup.DATALAKE_CLIENT(self.namespace)

    @property
    def sample_dataframe(self):
        return pd.read_csv(f"{BASE_DIR}/cli/datalake/dump_example.csv")

    def list(self):
        return self.client.list_collection_names()

    def dump(self, collection, path, filter, example):
        if os.path.exists(path):
            raise Exception(f"File {path} already exists")
        if os.path.isdir(path):
            path = os.path.join(path, 'splight_dump.csv')
        elif not path.endswith(".csv"):
            raise Exception("Only CSV files are supported")

        if example:
            dataframe = self.sample_dataframe
        else:
            filters = {
                f.split('=')[0]: f.split('=')[1] for f in filter
            }

            dataframe = self.client.get_dataframe(
                resource_type=models.Variable,
                collection=collection,
                **self._get_filters()
            )
        dataframe.to_csv(path, index=False)
        click.secho(f"Succesfully dumpped {collection} in {path}", fg="green")

    def load(self, collection, path, example):
        if not os.path.isfile(path):
            raise Exception("File not found")
        if not path.endswith(".csv"):
            raise Exception("Only CSV files are supported")

        if example:
            dataframe = self.sample_dataframe
        else:
            dataframe = pd.read_csv(path)
        self.client.save_dataframe(dataframe, collection=collection)
        click.secho(f"Succesfully loaded {path} in {collection}", fg="green")

    @staticmethod
    def _to_list(key: str, elem: str):
        if ',' not in elem and '__in' not in key:
            raise ValueError
        return list(elem.split(","))

    @staticmethod
    def _to_int(key: str, elem: str):
        if elem[0] == '-':
            can = elem[1:].isdigit()
        else:
            can = elem.isdigit()
        if not can:
            raise ValueError
        return int(elem)

    @staticmethod
    def _to_float(key: str, elem: str):
        try:
            return float(elem)
        except Exception:
            raise ValueError

    @staticmethod
    def _to_bool(key: str, elem: str):
        if elem == "True":
            return True
        elif elem == "False":
            return False
        else:
            raise ValueError

    @staticmethod
    def _to_date(key: str, elem: str):
        return datetime.strptime(elem, "%Y-%m-%dT%H:%M:%S%z")

    def _get_filters(self, filters):
        to_cast = [
            self._to_list,
            self._to_int,
            self._to_float,
            self._to_bool,
            self._to_date
        ]
        parsed_filters = {}
        for key, value in filters.items():
            if key == 'limit_':
                parsed_filters[key] = value
                continue
            for cast in to_cast:
                try:
                    value = cast(key, value)
                    break
                except ValueError:
                    pass

            parsed_filters[key] = value
        return parsed_filters
