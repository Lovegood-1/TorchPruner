from datetime import datetime
import numpy as np
import os
import csv
import torch
import pickle
from thop import profile


current_dir = os.path.dirname(__file__)


def now():
    return datetime.now().strftime("%Y%m%dT%H%M%S")


def _save_pruner_state(state, path):
    with open(path, "wb") as handle:
        pickle.dump(state, handle, protocol=pickle.HIGHEST_PROTOCOL)


def _load_pruner_state(path):
    with open(f"{path}", "rb") as handle:
        state = pickle.load(handle)
        print(state)
    return state


def save_model_state(state, model_name, timestamp):
    if not os.path.exists(f"{current_dir}/weights/"):
        os.makedirs(f"{current_dir}/weights/")
    torch.save(state, f"{current_dir}/weights/{model_name}_{timestamp}.pt")
    # Saving also without timestamp suffix makes it easier to just load the "last"
    torch.save(state, f"{current_dir}/weights/{model_name}.pt")


def load_model_state(model, model_name, timestamp):
    print(f"Loading {model_name}_{timestamp}")
    load_path = model_name
    if isinstance(timestamp, str) and len(timestamp) > 0 and timestamp != "last":
        load_path += f"_{timestamp}"
    model.load_state_dict(torch.load(f"{current_dir}/weights/{load_path}.pt"))


def log_dict(filename, dict):
    with open(f"{current_dir}/results/{filename}.csv", "a", newline="") as csvfile:
        fieldnames = list(dict.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerow(dict)


def get_layer_sizes(model):
    summary = []
    for m, _ in model.get_pruning_graph():
        summary.append(m.weight.shape[0])
    return str(summary).replace(", ", "-").replace("[", "").replace("]", "")


def get_parameter_count_and_flops(model, input_size, device):
    # Notice that, because of BathNorm, the sample dim must be >= 2
    x = torch.randn((2,) + tuple(input_size))
    x = x.to(device)
    print(x.shape)
    macs, params = profile(model, inputs=(x,))
    return 2 * macs, params
