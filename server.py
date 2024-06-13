import os
import yaml
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import Dict, Any, List, Union
from pydantic import BaseModel
import pandas as pd
from kva import kva, File
from fastapi.responses import FileResponse


app = FastAPI()

# Add CORS middleware
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


config_path = None

class ViewConfig(BaseModel):
    index: List[str]
    panels: List[Dict[str, Any]]

def load_config(config_path: str) -> ViewConfig:
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return ViewConfig(**config)

def get_run_data(keys: Dict[str, Any], columns: List[str], index: str = None):
    db = kva.get(**keys)
    return db.latest(columns, index=index)

def replace_nan_with_none(data: Any) -> Any:
    if isinstance(data, float) and (pd.isna(data) or data == float('inf') or data == float('-inf')):
        return None
    elif isinstance(data, dict):
        return {k: replace_nan_with_none(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_nan_with_none(item) for item in data]
    return data

def jsonable_encoder(data: Any) -> Any:
    if isinstance(data, pd.DataFrame):
        data = data.where(pd.notnull(data), None).to_dict(orient='records')
    return replace_nan_with_none(data)

@app.get("/view/{path:path}")
async def view_run(path: str):
    global config_path
    config = load_config(config_path)
    keys = dict(zip(config.index, path.split('/')))
    run_data = {}
    
    for panel in config.panels:
        columns = panel['columns']
        index = panel.get('index')
        data = get_run_data(keys, columns, index)
        run_data[panel['name']] = {
            'data': jsonable_encoder(data),
            'type': panel['type'],
            'index': panel.get('index')
        }
    print(run_data)
    return JSONResponse(content=run_data)
    
@app.get("/runs")
async def list_runs():
    global config_path
    config = load_config(config_path)
    df = pd.DataFrame(kva.data)
    if not all(col in df.columns for col in config.index):
        raise HTTPException(status_code=400, detail="Invalid index columns in config")
    
    runs = df[config.index].drop_duplicates().to_dict(orient='records')
    run_paths = ['/'.join(str(run[key]) for key in config.index) for run in runs]
    return JSONResponse(content={"runs": run_paths})

@app.get("/store/artifacts/{file_path:path}")
async def serve_image(file_path: str):
    file_location = os.path.join(os.getenv('KVA_STORAGE', '~/.kva'), "artifacts", file_path)
    if not os.path.exists(file_location):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_location)


app.mount("/", StaticFiles(directory="frontend/build", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    import sys
    
    if len(sys.argv) != 3 or sys.argv[1] != '--view':
        print("Usage: python server.py --view path/to/view/config.yaml")
        sys.exit(1)
    
    config_path = sys.argv[2]
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        sys.exit(1)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
