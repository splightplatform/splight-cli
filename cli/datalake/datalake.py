from cli.utils import *
from splight_lib.datalake import DatalakeClient
import splight_models as models
from datetime import datetime
import pandas as pd

class Datalake():

    def __init__(self, context, namespace):
        self.context = context
        self.namespace = namespace
        self.datalake_client = DatalakeClient(namespace)
        self.remote_datalake_handler = RemoteDatalakeHandler(self.context)

    def list(self, remote):
        if remote:
            collections = self.remote_datalake_handler.list_source()
        else:
            collections = [{"source": col, "algo": "-"} for col in self.datalake_client.list_collection_names()]

        click.secho("{:<50} {:<15}".format('COLLECTION', 'ALGORITHM'))
        for collection in collections:
            click.secho("{:<50} {:<15}".format(collection['source'], collection['algo']))

    def dump(self, collection, path, filter, remote, example):
        if os.path.isdir(path):
            path = os.path.join(path, 'splight_dump.csv')
        elif not path.endswith(".csv"):
            raise Exception("Only CSV files are supported")

        if example:
            with open(f"{BASE_DIR}/cli/datalake/dump_example.csv", 'rb') as f:
                ff = open(path, 'wb+')
                ff.write(f.read())
                ff.close()
                return
        filters = {f.split('=')[0]: f.split('=')[1] for f in filter}

        if 'limit_' not in filters:
            filters['limit_'] = 0
        if remote:
            filters['source'] = collection
            self.remote_datalake_handler.dump(path, filters)   
        else:
            client = DatalakeClient(self.namespace)
            client.get_dataframe(resource_type=models.Variable,
                             collection=collection,
                             **self._get_filters(filters)).to_csv(path, index=False)

    def load(self, collection, path):
        if not os.path.isfile(path):
            raise Exception("File not found")
        if not path.endswith(".csv"):
            raise Exception("Only CSV files are supported")
        self.datalake_client.save_dataframe(pd.read_csv(path), collection=collection)

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