import os
import torch
import pandas as pd
from PIL import Image
from torchvision import transforms
from torchvision.models import inception_v3
import torch.nn.functional as F


# -------------------------
# model
# -------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"

model = inception_v3(pretrained=True, transform_input=False)
model.fc = torch.nn.Identity()
model.eval()
model.to(device)


# -------------------------
# transform
# -------------------------
transform = transforms.Compose([
    transforms.Resize((299, 299)),
    transforms.ToTensor(),
])


def get_feature(img_path):
    img = Image.open(img_path).convert("RGB")
    img = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        feat = model(img)

    return feat.squeeze(0)


# -------------------------
# main eval
# -------------------------
def compare_folders(real_path, fake_path, save_csv="fid_report.csv"):

    real_files = sorted([f for f in os.listdir(real_path) if f.endswith(".png")])
    fake_files = set(os.listdir(fake_path))

    results = []
    distances = []

    for name in real_files:

        if name not in fake_files:
            print(f"跳过（缺失 image）：{name}")
            continue

        real_img = os.path.join(real_path, name)
        fake_img = os.path.join(fake_path, name)

        real_feat = get_feature(real_img)
        fake_feat = get_feature(fake_img)

        dist = F.mse_loss(real_feat, fake_feat).item()
        distances.append(dist)

        results.append([name, dist])

    # -------------------------
    # table
    # -------------------------
    df = pd.DataFrame(results, columns=["Image", "Distance"])

    print("\n==============================")
    print("Pairwise Distance Table")
    print("==============================")
    print(df.to_string(index=False))

    # -------------------------
    # mean
    # -------------------------
    mean_dist = sum(distances) / len(distances)

    print("\n==============================")
    print(f"Mean Distance: {mean_dist:.6f}")
    print("==============================")

    # -------------------------
    # save CSV (for paper)
    # -------------------------
    df.loc[len(df)] = ["MEAN", mean_dist]
    df.to_csv(save_csv, index=False)

    print(f"\nCSV saved to: {save_csv}")

    return df, mean_dist


# -------------------------
# run
# -------------------------
if __name__ == "__main__":

   real_path = "FinalLora_dataset/test/5_BongardStyle"
   fake_path = "Datasets for evaluation/BongardStyle_LoRA"

compare_folders(real_path, fake_path)