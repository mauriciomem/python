import random
import csv
from pathlib import Path

ITERATIONS = 51
ROUND = 3
NAMESPACE = 'default'
FILE = Path("./kubeapitest.csv")

def create_random_ns() -> dict:
    test_ns_name = f'testns{random.randint(1,9999)}'
    test_ns_resource = {
        "apiVersion": "v1",
        "kind": "Namespace",
        "metadata": {
            "name" : test_ns_name
        }
    }
    return {'ns_resource': test_ns_resource, 'ns_name': test_ns_name}

def to_csv(filename: Path, accessmode: str, data: dict) -> None:
    with open(filename, accessmode) as f:
        header = data.keys()
        writer = csv.DictWriter(f, fieldnames=header)
        if filename.stat().st_size == 0:
            writer.writeheader()
        writer.writerow(data)