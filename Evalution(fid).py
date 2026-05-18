from pytorch_fid import fid_score

def calculate_fid():
    real_path = "FinalLora_dataset/test/5_BongardStyle"
    fake_path = "Datasets for evaluation/BongardStyle_LoRA"

    print("正在计算 FID (folder vs folder)...")

    score = fid_score.calculate_fid_given_paths(
        [real_path, fake_path],
        batch_size=50,
        device='cuda' if __name__ == "__main__" else 'cpu',
        dims=2048
    )

    print("\n==============================")
    print(f"FID Score: {score}")
    print("==============================")

    return score


if __name__ == "__main__":
    calculate_fid()