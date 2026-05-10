import requests
import base64
import io
import os
from PIL import Image
from pathlib import Path

# --- 配置区 ---
URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
REF_IMAGE_PATH = "fyp/Contronet.jpg"  # ControlNet 参考图路径
INPUT_FOLDER = "Kohya_new_dataset/test/5_BongardStyle"       # 存放 txt 文件的文件夹
OUTPUT_FOLDER = "FID_results"   # 结果输出文件夹

# 确保输出文件夹存在
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def encode_file_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def get_image_from_sd(prompt, control_image_base64=None):
    """向 SD API 发送请求"""
    negative_prompt = (
        "color, shading, gradient, 3d, realistic, photo, texture, "
        "grey, blurry, messy, chaotic, merged boxes, distorted lines, "
        "complex background, grey background"
    )
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": 25,
        "width": 384,
        "height": 512,
        "sampler_name": "Euler a",
        "cfg_scale": 9,
        "alwayson_scripts": {}
    }
     
    if control_image_base64:
        payload["alwayson_scripts"]["ControlNet"] = {
            "args": [
                {
                    "input_image": control_image_base64,
                    "module": "canny",
                    "model": "diffusion_pytorch_model.fp16 [7b2ce256]", # 确保模型名称正确
                    "weight": 1.2,
                    "enabled": True,
                }
            ]
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
    # 1. 准备 ControlNet 参考图
    ref_base64 = None
    if os.path.exists(REF_IMAGE_PATH):
        ref_base64 = encode_file_to_base64(REF_IMAGE_PATH)
        print(f"已加载参考图: {REF_IMAGE_PATH}")
    else:
        print(f"提示：未找到参考图 {REF_IMAGE_PATH}，将不使用 ControlNet 生成。")

    # 2. 检查输入文件夹
    input_path = Path(INPUT_FOLDER)
    if not input_path.exists():
        print(f"错误：找不到输入文件夹 '{INPUT_FOLDER}'")
        return

    # 3. 遍历所有的 .txt 文件
    txt_files = list(input_path.glob("*.txt"))
    if not txt_files:
        print("文件夹内没有找到 .txt 文件。")
        return

    print(f"共发现 {len(txt_files)} 个任务，准备开始生成...")

    for txt_file in txt_files:
        # 读取 txt 内容作为 prompt
        with open(txt_file, "r", encoding="utf-8") as f:
            prompt_content = f.read().strip()
        
        if not prompt_content:
            print(f"跳过空文件: {txt_file.name}")
            continue

        # 调用 API 生图
        print(f"正在处理: {txt_file.name} ...")
        image = get_image_from_sd(prompt_content, control_image_base64=ref_base64)

        if image:
            # 保存图片，文件名和 txt 文件名保持一致，后缀改为 .png
            save_path = os.path.join(OUTPUT_FOLDER, f"{txt_file.stem}.png")
            image.save(save_path)
            print(f"已保存: {save_path}")
        else:
            print(f"文件 {txt_file.name} 生成失败。")

    print("\n所有任务处理完毕！")

if __name__ == "__main__":
    main()