import random
from unittest.mock import patch
from uuid import uuid4

import pandas as pd
import pytest
from splight_lib.models import Number

from splight_cli.engine.manager import DatalakeManager

ASSET_ID = str(uuid4())
ATTR_ID = str(uuid4())

DATAFRAME = pd.DataFrame(
    data={
        "instance_id": [str(uuid4()) for _ in range(5)],
        "instance_type": ["Component" for _ in range(5)],
        "asset": [ASSET_ID for _ in range(5)],
        "attribute": [ATTR_ID for _ in range(5)],
        "output_format": ["Number" for _ in range(5)],
        "value": [random.random() for _ in range(5)],
    },
    index=pd.date_range(
        start="2020-01-01 00:00:00+00:00",
        end="2020-01-01 04:00:00+00:00",
        freq="H",
    ),
)


@pytest.mark.parametrize("model", [Number])
@patch.object(pd.DataFrame, "to_csv", return_value=None)
def test_dump(mock_df, model):
    manager = DatalakeManager(model)
    with patch.object(model, "get_dataframe", return_value=DATAFRAME) as mock:
        manager.dump(
            path="./test_dump.csv",
            filters={"asset": ASSET_ID, "attribute": ATTR_ID},
        )
        mock.assert_called_with(asset=ASSET_ID, attribute=ATTR_ID)
