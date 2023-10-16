import requests
import config
import pathlib
import shutil
import json

local_dir = pathlib.Path(pathlib.os.getcwd())
data_dir = local_dir.joinpath("data")
data_dir.mkdir(exist_ok=True, parents=True)


def download_data():
    archive_path = data_dir.joinpath(config.ARCHIVE_NAME)
    response = requests.get(config.DATA_URL)
    with open(archive_path, "wb") as file:
        file.write(response.content)
    shutil.unpack_archive(archive_path, data_dir)


def preprocess_data():
    with open(data_dir.joinpath("iris.data"), "r") as iris_data:
        iris_data = iris_data.read().strip()
        iris_data = iris_data.split("\n")
    
    documents = []
    for idx, iris in enumerate(iris_data):
        # Note from Elasticsearch error message : The bulk request must be terminated by a newline [\\n]
        document = '{"index": {"_index": "datasets", "_type": "iris", "_id": "%s"}}\n' % idx
        documents.append(document)

        sl, sw, pl, pw, iris_type = iris.split(",")
        document = '{"sepal_length": %f, "sepal_width": %f, "petal_length": %f, "petal_width": %f, "class": "%s"}\n' % \
        (float(sl), float(sw), float(pl), float(pw), iris_type.split("-")[1])
        documents.append(document)

    with open(data_dir.joinpath("iris_data.json"), "w") as file:
        file.writelines("".join(documents))
     
    with open(data_dir.joinpath("iris_mapping.json"), "w") as file:
        mapping = {
            "iris": {
                "properties": {
                    "sepal_length": {"type": "float"},
                    "sepal_width": {"type": "float"},
                    "petal_length": {"type": "float"},
                    "petal_width": {"type": "float"},
                    "class": {"type": "string"},
                }
            } 
        }
        file.write(json.dumps(mapping))
