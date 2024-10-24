# kva/server.py
import json
import os
from typing import Any, Dict, List, Union

import pandas as pd
import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from kva import File, kva, storage_path

app = FastAPI()

# Add CORS middleware
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://0.0.0.0:8000",
    # Just allow all origins for now
    "*",
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
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return ViewConfig(**config)


def get_run_data(keys: Dict[str, Any], columns: List[str], index: str = None):
    # kva.reload()
    db = kva.get(**keys)
    return db.latest(columns, index=index)


def replace_nan_with_none(data: Any) -> Any:
    if isinstance(data, float) and (
        pd.isna(data) or data == float("inf") or data == float("-inf")
    ):
        return None
    elif isinstance(data, dict):
        return {k: replace_nan_with_none(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_nan_with_none(item) for item in data]
    return data


def jsonable_encoder(data: Any) -> Any:
    if isinstance(data, pd.DataFrame):
        # data = data.where(pd.notnull(data), None).to_dict(orient='records')
        data = data.dropna(how="all")
        data = data.reset_index().to_dict(orient="records")
    return replace_nan_with_none(data)


@app.get("/data/{path:path}")
async def view_run(path: str):
    global config_path
    config = load_config(config_path)
    keys = dict(zip(config.index, path.split("/")))
    run_data = {}

    for panel in config.panels:
        columns = panel["columns"]
        index = panel.get("index")
        if slider := panel.get("slider"):
            if index is None:
                index = slider
            elif isinstance(index, list):
                index = [slider] + index
            else:
                index = [slider, index]
        data = get_run_data(keys, columns, index)
        if len(data) == 0:
            continue
        run_data[panel["name"]] = {
            "data": jsonable_encoder(data),
            "type": panel["type"],
            "index": panel.get("index"),
            "slider": panel.get("slider"),
        }
    print(json.dumps(run_data, indent=2))
    return JSONResponse(content=run_data)

@app.get("/reload")
async def reload_data():
    global kva_instance
    kva_instance.reload()

@app.get("/runs")
async def list_runs():
    config = load_config(config_path)
    df = pd.DataFrame(kva.data)
    if not all(col in df.columns for col in config.index):
        raise HTTPException(status_code=400, detail="Invalid index columns in config")

    runs = df[config.index].drop_duplicates().to_dict(orient="records")
    run_paths = ["/".join(str(run[key]) for key in config.index) for run in runs]
    print(run_paths)
    return JSONResponse(content={"runs": run_paths})


@app.get("/artifacts/logfiles/{run_id}/{filename}")
async def serve_log_file(run_id: str, filename: str):
    values = kva.get(run_id=run_id).latest("*")
    for k, v in values.items():
        try:
            assert v['filename'] == filename
            log_file_path = v['src']
            break
        except:
            pass
    if not os.path.exists(log_file_path):
        print(f"Log file not found: {log_file_path}")
        raise HTTPException(status_code=404, detail="Log file not found")
    return FileResponse(log_file_path)


@app.get("/artifacts/{file_path:path}")
async def serve_file(file_path: str):
    file_location = os.path.join(storage_path(), "artifacts", file_path)
    file_location = os.path.expanduser(file_location)
    if not os.path.exists(file_location):
        print(f"File not found: {file_location}")
        raise HTTPException(status_code=404, detail="File not found")
    if file_path.endswith(".csv"):
        return FileResponse(file_location, media_type="text/csv")
    return FileResponse(file_location)


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    static_path = os.path.join(
        os.path.dirname(__file__), "../frontend/build", full_path
    )
    if os.path.exists(static_path) and os.path.isfile(static_path):
        return FileResponse(static_path)
    frontend_path = os.path.join(
        os.path.dirname(__file__), "../frontend/build", "index.html"
    )
    if os.path.exists(frontend_path):
        return HTMLResponse(content=open(frontend_path).read(), status_code=200)
    else:
        raise HTTPException(status_code=404, detail="Frontend not found")


def make_config():
    config = {
        "index": ["run_id"],
        "panels": [{"name": "Summary", "columns": "*", "type": "data"}],
    }
    df = pd.DataFrame(kva.data)
    for col in df.columns:
        if col in ["timestamp", "run_id"]:
            continue
        # For all scalars, add a line plot
        if pd.api.types.is_numeric_dtype(df[col]):
            index = "step" if "step" in df.columns else "timestamp"
            if col == "step":
                index = "timestamp"
            config["panels"].append(
                {"name": col, "columns": [col], "type": "lineplot", "index": index}
            )

    config_path = os.path.join(storage_path(), "default.yaml")
    with open(config_path, "w") as file:
        yaml.dump(config, file)
    return config_path


def main():
    import sys

    import uvicorn

    global config_path

    if len(sys.argv) == 3:
        config_path = sys.argv[2]
        if not os.path.exists(config_path):
            print(f"Config file not found: {config_path}")
            sys.exit(1)
    else:
        config_path = make_config()

    uvicorn.run(app, host="0.0.0.0", port=9998)


if __name__ == "__main__":
    main()
