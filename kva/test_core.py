import pytest
from kva import kva, File, Folder
import os
import pandas as pd
import shutil

# Fixture to create and clean up a test environment
@pytest.fixture(scope="module", autouse=True)
def setup_env():
    os.environ['KVA_STORAGE'] = '/tmp/kva_test'
    if os.path.exists('/tmp/kva_test'):
        shutil.rmtree('/tmp/kva_test')
    os.makedirs('/tmp/kva_test')
    yield
    shutil.rmtree('/tmp/kva_test')

def test_basic_logging():
    kva.init(run_id="test-run")
    kva.log(config={'foo': 'bar'})
    kva.log(config={'hello': 'world'})
    kva.log(step=1, loss=42)
    kva.log(step=2)
    kva.log(loss=4.2)
    result = kva.get(run_id="test-run").latest('config')
    assert result == {'foo': 'bar', 'hello': 'world'}

def test_deep_merge_false():
    kva.init(run_id="test-run")
    kva.log(config={'foo': 'bar'})
    kva.log(config={'hello': 'world'})
    result = kva.get(run_id="test-run").latest('config', deep_merge=False)
    assert result == {'hello': 'world'}

def test_latest_single_column():
    kva.init(run_id="test-run")
    kva.log(step=1, loss=42)
    kva.log(step=2)
    kva.log(loss=4.2)
    result = kva.get(run_id="test-run").latest('loss')
    assert result == 4.2

def test_latest_multiple_columns():
    kva.init(run_id="test-run")
    kva.log(step=1, loss=42)
    kva.log(step=2)
    kva.log(loss=4.2)
    result = kva.get(run_id="test-run").latest(['loss', 'step'])
    assert result == {'loss': 4.2, 'step': 2}

def test_latest_with_index():
    kva.init(run_id="test_latest_with_index")
    kva.log(step=1, loss=42)
    kva.log(step=2)
    kva.log(loss=4.2)
    result = kva.get(run_id="test_latest_with_index").latest('loss', index='step')
    expected_df = pd.DataFrame({'step': [1, 2], 'loss': [42.0, 4.2]})
    pd.testing.assert_frame_equal(result.reset_index(), expected_df)


def test_folder_logging():
    kva.init(run_id="folder-run")
    os.makedirs('/tmp/kva_test/test_folder', exist_ok=True)
    with open('/tmp/kva_test/test_folder/file1.txt', 'w') as f:
        f.write("File 1")
    with open('/tmp/kva_test/test_folder/file2.txt', 'w') as f:
        f.write("File 2")
    kva.log(cwd=Folder('/tmp/kva_test/test_folder'))
    result = kva.get(run_id="folder-run").latest('cwd')
    assert 'file1.txt' in result
    assert 'file2.txt' in result

def test_mandelbrot_example():
    from examples.mandelbrot import generate_mandelbrot_image
    kva.init(run_id="mandelbrot-run")
    for step in range(10, 101, 10):
        generate_mandelbrot_image(step)
        kva.log(step=step, image=File('mandelbrot.png'))
    result = kva.get(run_id="mandelbrot-run").latest('image')
    assert os.path.exists(os.path.join(kva.storage, result['path']))

def test_llm_sampling():
    from examples.llm_sampling import model
    kva.init(run_id="llm-sampling-run")
    inputs = ['Hello', 'What is your name?', 'How are you doing?']
    for step in range(10, 101, 10):
        for input in inputs:
            response = model(input, step)
            kva.log(step=step, input=input, output=response)
    result = kva.get(run_id="llm-sampling-run").latest('output', index='input')
    assert not result.empty
    assert 'input' in result.index.names
    assert 'output' in result.columns

def test_tables():
    from examples.tables import get_dummy_df
    kva.init(run_id="tables-run")
    kva.log(step=1)
    kva.log({'dummy_table': get_dummy_df('dummy text')})
    kva.log(step=2)
    kva.log({'dummy_table': get_dummy_df('updated text')})
    result = kva.get(run_id="tables-run").latest('dummy_table', index='step')
    assert not result.empty
    assert 'step' in result.index.names
    assert 'dummy_table' in result.columns

def test_as_df_method():
    kva.init(run_id="test-as-df")
    data = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data)
    kva.log(step=1, df=df)
    retrieved_df = kva.get(run_id="test-as-df").latest('df').as_df()
    pd.testing.assert_frame_equal(retrieved_df, df)

if __name__ == "__main__":
    pytest.main()
