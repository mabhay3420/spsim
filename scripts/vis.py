from typing import Final
from pathlib import Path
import flask

ROOT: Final[Path] = Path(__file__).resolve().parents[1]
DATA_RAW: Final[Path] = ROOT / "data" / "raw"
DATA_PROCESSED: Final[Path] = ROOT / "data" / "processed"
GRAPH_JSON_FOLDER = DATA_PROCESSED / "force"
GRAPH_JSON: Final[Path] = GRAPH_JSON_FOLDER / "force.json"

app = flask.Flask(__name__, static_folder=str(GRAPH_JSON_FOLDER))

@app.route("/")
def static_proxy():
    return app.send_static_file("force.html")


print("\nGo to http://localhost:8000 to see the example\n")
app.run(port=8000)