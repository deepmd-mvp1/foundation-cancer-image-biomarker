import numpy as np
import pandas as pd
import torch
from loguru import logger
from tqdm import tqdm

from .models import resnet50
from .preprocessing import get_dataloader


def get_features(
    csv_path,
    weights_path=None,
    download_url="https://www.dropbox.com/s/bd7azdsvx1jhalp/fmcib.torch?dl=1",
    spatial_size=(50, 50, 50),
    precropped=False,
):
    logger.info("Loading CSV file ...")
    df = pd.read_csv(csv_path)
    dataloader = get_dataloader(csv_path, spatial_size=spatial_size, precropped=precropped)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = resnet50(device=device, weights_path=weights_path, download_url=download_url)

    feature_list = []
    logger.info("Running inference over batches ...")

    model.eval()
    for batch in tqdm(dataloader, total=len(dataloader)):
        feature = model(batch.to(device)).detach().cpu().numpy()
        feature_list.append(feature)

    features = np.concatenate(feature_list, axis=0)
    # Flatten features into a list
    features = features.reshape(-1, 4096)

    # Add the features to the dataframe
    df = pd.concat([df, pd.DataFrame(features, columns=[f"pred_{idx}" for idx in range(4096)])], axis=1)
    return df
