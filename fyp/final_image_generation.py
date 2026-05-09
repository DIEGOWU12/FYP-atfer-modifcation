import requests
import base64
import io
import os
from PIL import Image

# --- 配置区 ---
URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
# 确保这个路径下有一张参考图，或者改名为你现有的图片
# 必须和文件夹里的名字一模一样
REF_IMAGE_PATH = "fyp/Contronet.jpg"

def encode_file_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def get_image_from_sd(prompt, control_image_base64=None):
    """
    向 SD 发送请求。
    如果提供了 control_image_base64，则开启 ControlNet (Canny)。
    """
    negative_prompt = (
        "color, shading, gradient, 3d, realistic, photo, texture, "
        "grey, blurry, messy, chaotic, merged boxes, distorted lines, "
        "complex background, grey background"
    )
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": 30,
        "width": 384,
        "height": 512,
        "sampler_name": "Euler a",
        "cfg_scale": 9,
        "alwayson_scripts": {}
    }
     
    # 如果有参考图，注入 ControlNet 配置
    if control_image_base64:
        payload["alwayson_scripts"]["ControlNet"] = {
            "args": [
                {
                    "input_image": control_image_base64,
                    "module": "canny",         # 预处理器：边缘检测
                    "model": "diffusion_pytorch_model.fp16 [7b2ce256]",
                    "weight": 1.2,
                    "enabled": True,
                    "control_mode": 2,
                    "threshold_a": 100,   # Canny 低阈值
                    "threshold_b": 200,   # Canny 高阈值
                }
            ]
        }

    print(f"正在生成: [{prompt[:30]}...] (ControlNet: {'开启' if control_image_base64 else '关闭'})")
    response = requests.post(URL, json=payload)
    
    if response.status_code == 200:
        img_base64 = response.json()['images'][0]
        return Image.open(io.BytesIO(base64.b64decode(img_base64)))
    else:
        print(f"生成失败: {response.text}")
        return None

# --- 执行流程 ---

# 1. 检查参考图是否存在
if not os.path.exists(REF_IMAGE_PATH):
    print(f"错误：找不到参考图 {REF_IMAGE_PATH}，请放一张图在脚本目录下并改名。")
else:
    ref_base64 = encode_file_to_base64(REF_IMAGE_PATH)

    # 2. 分别生成
    # 第一张图：使用 ControlNet 控制构图
    p1 = "Bongard style, one large composite image consisting of six individual images arranged in a 3x2 layout. Each of the six images features a 'Is polygon' logic. <lora:sdxltrained4:1>"
    img1 = get_image_from_sd(p1, control_image_base64=ref_base64)

    # 第二张图：普通生成
    p2 = "Bongard style, one large composite image consisting of six individual images arranged in a 3x2 layout. Each of the six images features a 'order is low (high entropy)' logic. <lora:sdxltrained4:1>"
    img2 = get_image_from_sd(p2, control_image_base64=ref_base64)  # 这里也用 ControlNet 来保持风格一致，如果不想要控制，传 None 即可

    if img1 and img2:
        # 3. 左右拼接
        w1, h1 = img1.size
        w2, h2 = img2.size
        new_img = Image.new('RGB', (w1 + w2, max(h1, h2)))
        new_img.paste(img1, (0, 0))
        new_img.paste(img2, (w1, 0))
        
        # 4. 保存
        new_img.save("controlnet_combined.png")
        print("成功！最终图片已保存为: controlnet_combined.png")
        new_img.show()