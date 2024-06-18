import os
import pickle
import shutil
import uuid
from dataclasses import dataclass
from datetime import datetime

import hydra
import numpy as np
import pandas as pd
import pytest
import torch
from hydra import compose, initialize
from hydra.core.config_store import ConfigStore
from omegaconf import OmegaConf

from kva import File, Folder, kva, set_default_storage


# Fixture to create and clean up a test environment
@pytest.fixture(scope="module", autouse=True)
def setup_env():
    set_default_storage(kva, "/tmp/kva_test_encoder")
    if os.path.exists('/tmp/kva_test_encoder'):
        shutil.rmtree('/tmp/kva_test_encoder')
    
    yield
    shutil.rmtree('/tmp/kva_test_encoder')


@dataclass
class Config:
    foo: str = "bar"
    num: int = 42


cs = ConfigStore.instance()
cs.store(name="config", node=Config)


def test_datetime_serialization(setup_env):
    kva.init(run_id="datetime-run")
    now = datetime.now()
    kva.log(datetime=now)
    result = kva.get(run_id="datetime-run").latest("datetime")
    assert result == now.isoformat(), "Datetime not serialized correctly"


def test_torch_tensor_serialization(setup_env):
    kva.init(run_id="tensor-run")
    tensor = torch.tensor([1, 2, 3])
    kva.log(tensor=tensor)
    result = kva.get(run_id="tensor-run").latest("tensor")
    expected = tensor.numpy().tolist()
    assert result == expected, "Torch tensor not serialized correctly"


def test_numpy_array_serialization(setup_env):
    kva.init(run_id="numpy-run")
    array = np.array([1, 2, 3])
    kva.log(array=array)
    result = kva.get(run_id="numpy-run").latest("array")
    expected = array.tolist()
    assert result == expected, "Numpy array not serialized correctly"


def test_hydra_config_serialization(setup_env):
    with initialize(config_path=None):
        config = compose(config_name="config")
        kva.init(run_id="hydra-run")
        kva.log(config=OmegaConf.to_container(config))
        result = kva.get(run_id="hydra-run").latest("config")
        assert isinstance(result, dict), "Hydra config not serialized correctly"


def test_custom_object_serialization(setup_env):
    kva.init(run_id="custom-object-run")
    custom_obj = {"key": "value"}
    kva.log(custom=custom_obj)
    result = kva.get(run_id="custom-object-run").latest("custom")
    assert isinstance(result, dict), "Custom object not serialized correctly"


class CustomClass:
    def __init__(self, name):
        self.name = name


def test_pickle_serialization(setup_env):
    obj = CustomClass("test")
    kva.init(run_id="pickle-run")
    kva.log(custom_object=obj)
    result = kva.get(run_id="pickle-run").latest("custom_object")
    assert isinstance(result, File), "Pickle object not serialized as a file"


def test_log_local_class_object(setup_env):
    class LocalClass:
        def __init__(self, name):
            self.name = name

    kva.init(run_id="local-class-run")
    obj = LocalClass("test")
    kva.log(local_object=obj)
    result = kva.get(run_id="local-class-run").latest("local_object")
    assert result["name"] == "test", "Local class object not serialized correctly"


def test_basic_logging(setup_env):
    kva.init(run_id="test-run")
    kva.log(config={"foo": "bar"})
    kva.log(config={"hello": "world"})
    kva.log(step=1, loss=42)
    kva.log(step=2)
    kva.log(loss=4.2)
    result = kva.get(run_id="test-run").latest("config")
    assert result == {"foo": "bar", "hello": "world"}


def test_deep_merge_false(setup_env):
    kva.init(run_id="test-run")
    kva.log(config={"foo": "bar"})
    kva.log(config={"hello": "world"})
    result = kva.get(run_id="test-run").latest("config", deep_merge=False)
    assert result == {"hello": "world"}


def test_latest_single_column(setup_env):
    kva.init(run_id="test-run")
    kva.log(step=1, loss=42)
    kva.log(step=2)
    kva.log(loss=4.2)
    result = kva.get(run_id="test-run").latest("loss")
    assert result == 4.2


def test_latest_multiple_columns(setup_env):
    kva.init(run_id="test-run")
    kva.log(step=1, loss=42)
    kva.log(step=2)
    kva.log(loss=4.2)
    result = kva.get(run_id="test-run").latest(["loss", "step"])
    assert result == {"loss": 4.2, "step": 2}


def test_latest_with_index(setup_env):
    kva.init(run_id="test_latest_with_index")
    kva.log(step=1, loss=42)
    kva.log(step=2)
    kva.log(loss=4.2)
    result = kva.get(run_id="test_latest_with_index").latest("loss", index="step")
    expected_df = pd.DataFrame({"step": [1, 2], "loss": [42.0, 4.2]})
    pd.testing.assert_frame_equal(result.reset_index(), expected_df)


def test_folder_logging(setup_env):
    kva.init(run_id="folder-run")
    os.makedirs("/tmp/kva_test/test_folder", exist_ok=True)
    with open("/tmp/kva_test/test_folder/file1.txt", "w") as f:
        f.write("File 1")
    with open("/tmp/kva_test/test_folder/file2.txt", "w") as f:
        f.write("File 2")
    kva.log(cwd=Folder("/tmp/kva_test/test_folder"))
    result = kva.get(run_id="folder-run").latest("cwd")
    assert "file1.txt" in result
    assert "file2.txt" in result


def test_mandelbrot_example(setup_env):
    from examples.mandelbrot import generate_mandelbrot_image

    kva.init(run_id="mandelbrot-run")
    for step in range(10, 101, 10):
        generate_mandelbrot_image(step)
        kva.log(step=step, image=File("mandelbrot.png"))
    result = kva.get(run_id="mandelbrot-run").latest("image")
    assert os.path.exists(os.path.join(kva.storage, result["path"]))


def test_llm_sampling(setup_env):
    from examples.llm_sampling import model

    kva.init(run_id="llm-sampling-run")
    inputs = ["Hello", "What is your name?", "How are you doing?"]
    for step in range(10, 101, 10):
        for input in inputs:
            response = model(input, step)
            kva.log(step=step, input=input, output=response)
    result = kva.get(run_id="llm-sampling-run").latest("output", index="input")
    assert not result.empty
    assert "input" in result.index.names
    assert "output" in result.columns


def test_tables(setup_env):
    from examples.tables import get_dummy_df

    kva.init(run_id="tables-run")
    kva.log(step=1)
    kva.log({"dummy_table": get_dummy_df("dummy text")})
    kva.log(step=2)
    kva.log({"dummy_table": get_dummy_df("updated text")})
    result = kva.get(run_id="tables-run").latest("dummy_table", index="step")
    assert not result.empty
    assert "step" in result.index.names
    assert "dummy_table" in result.columns


def test_as_df_method(setup_env):
    kva.init(run_id="test-as-df")
    data = {"col1": [1, 2], "col2": [3, 4]}
    df = pd.DataFrame(data)
    kva.log(step=1, df=df)
    retrieved_df = kva.get(run_id="test-as-df").latest("df").as_df()
    pd.testing.assert_frame_equal(retrieved_df, df)


if __name__ == "__main__":
    pytest.main()
