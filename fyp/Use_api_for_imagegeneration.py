import requests
import base64
import json

# WebUI 的 API 地址
url = "http://127.0.0.1:7860/sdapi/v1/txt2img"

# 构造生图参数
payload = {
    "prompt": "a beautiful cat, high quality, masterpiece, cinematic lighting", # 提示词
    "negative_prompt": "easynegative, low quality", # 负面词
    "steps": 20,          # 采样步数
    "width": 512,         # 宽度
    "height": 512,        # 高度
    "cfg_scale": 7,       # 提示词引导系数
    "sampler_name": "Euler a", # 采样器
    "batch_size": 1       # 生成张数
}

# 发送 POST 请求
response = requests.post(url, json=payload)

# 处理返回结果
if response.status_code == 200:
    r = response.json()
    # 返回的是 base64 编码的图片数据
    for i, img_data in enumerate(r['images']):
        with open(f"output_{i}.png", 'wb') as f:
            f.write(base64.b64decode(img_data))
    print("图片生成成功，已保存为 output_0.png")
else:
    print(f"出错啦: {response.text}")