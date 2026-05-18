import requests
import base64
import io
import os
from PIL import Image
from pathlib import Path

# --- 配置区 ---
URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"

INPUT_FOLDER = "FinalLora_dataset/test/5_BongardStyle"
OUTPUT_FOLDER = "Datasets for evaluation/BongardStyle_LoRA"

# ⭐ LoRA 配置（新增）
LORA_NAME = "sdxltrained8"
LORA_WEIGHT = 1

# 确保输出文件夹存在
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def get_image_from_sd(prompt):
    """向 SD API 发送请求（不使用 ControlNet 和 negative prompt）"""

    # ⭐ 只改这里：把 LoRA 插入 prompt
    prompt = f"{prompt}, <lora:{LORA_NAME}:{LORA_WEIGHT}>"
    payload = {
        "prompt": prompt,
        "steps": 20,
        "width": 256,
        "height": 256,
        "sampler_name": "Euler a",
        "cfg_scale": 9
    }

    try:
        response = requests.post(URL, json=payload, timeout=60)

        if response.status_code == 200:
            img_base64 = response.json()['images'][0]
            return Image.open(io.BytesIO(base64.b64decode(img_base64)))
        else:
            print(f"生成失败: {response.text}")
            return None

    except Exception as e:
        print(f"请求出错: {e}")
        return None


# --- 执行流程 ---

def main():

    input_path = Path(INPUT_FOLDER)

    if not input_path.exists():
        print(f"错误：找不到输入文件夹 '{INPUT_FOLDER}'")
        return

    txt_files = list(input_path.glob("*.txt"))

    if not txt_files:
        print("文件夹内没有找到 .txt 文件。")
        return

    print(f"共发现 {len(txt_files)} 个任务，准备开始生成...")

    for txt_file in txt_files:

        with open(txt_file, "r", encoding="utf-8") as f:
            prompt_content = f.read().strip()

        if not prompt_content:
            print(f"跳过空文件: {txt_file.name}")
            continue

        print(f"正在处理: {txt_file.name} ...")

        image = get_image_from_sd(prompt_content)

        if image:
            save_path = os.path.join(
                OUTPUT_FOLDER,
                f"{txt_file.stem}.png"
            )

            image.save(save_path)
            print(f"已保存: {save_path}")

        else:
            print(f"文件 {txt_file.name} 生成失败。")

    print("\n所有任务处理完毕！")


if __name__ == "__main__":
    main()