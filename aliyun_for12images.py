import os
import time
import base64
import dashscope
from dashscope import MultiModalConversation

# ================= 配置区 =================
API_KEY = "sk-e03f2df5f8ed44e2bb77a9bae5ff5121"  # 🔑 替换为你的真实 Key
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 修改为相对路径定位
IMAGE_DIR = os.path.join(BASE_DIR, "Kohya_data", "7_BongardStyle")
MODEL = "qwen-vl-plus"
DELAY_SECONDS = 1.5
MAX_RETRIES = 3 
# ==========================================

dashscope.api_key = API_KEY

# 修复了末尾多余的引号，并将内部引号统一为直引号以免混淆
PROMPT_TEMPLATE = """BongardStyle,Please help me to describe the figure using a similar style as follows in a brief way: "The image shows a 3x4 grid of twelve black figures: Row 1, Left: [Shape description] Row 1, Mid-Left: [Shape description] Row 1, Mid-Right: [Shape description] Row 1, Right: [Shape description] Row 2, Left: [Shape description] Row 2, Mid-Left: [Shape description] Row 2, Mid-Right: [Shape description] Row 2, Right: [Shape description] Row 3, Left: [Shape description] Row 3, Mid-Left: [Shape description] Row 3, Mid-Right: [Shape description] Row 3, Right: [Shape description] Minimalist black-and-white style with rough, hand-drawn or pixelated edges." Please output ONLY the description in this exact format. Replace the bracketed parts with accurate shape descriptions based on the image. Do not add any extra text, explanations, or markdown formatting."""

def image_to_base64(image_path):
    """将本地图片转换为 Base64 字符串，确保 API 兼容"""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    # 添加前缀，告诉模型这是 jpg/png 图片
    # 这里简单判断后缀，如果是 png 就用 png，否则默认 jpg
    suffix = "png" if image_path.lower().endswith('.png') else "jpeg"
    return f"data:image/{suffix};base64,{encoded_string}"

def safe_extract_text(response):
    """适配 DashScope 返回结构的稳健解析，并清洗 Markdown"""
    try:
        if response.status_code == 200 and response.output:
            content = response.output.choices[0].message.content
            text = ""
            if isinstance(content, list):
                text = content[0].get("text", "")
            else:
                text = str(content)
            
            # 简单清洗：去除可能存在的 markdown 代码块标记 ```text ... ```
            text = text.strip()
            if text.startswith("```"):
                lines = text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:] # 去掉第一行
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1] # 去掉最后一行
                text = "\n".join(lines).strip()
            return text
        return None
    except Exception:
        return None

def call_model_with_retry(image_path, prompt, max_retries=3):
    """带重试机制的 API 调用"""
    # 将本地路径转换为 Base64，这是最稳妥的方式
    image_content = image_to_base64(image_path)
    
    for attempt in range(1, max_retries + 1):
        try:
            response = MultiModalConversation.call(
                model=MODEL,
                messages=[{
                    "role": "user",
                    "content": [
                        {"image": image_content},  # ✅ 使用 Base64
                        {"text": prompt}
                    ]
                }]
            )
            if response.status_code == 200:
                return response
            elif response.status_code == 429 or response.status_code >= 500:
                wait = DELAY_SECONDS * attempt
                print(f"⚠️ 状态码 {response.status_code}，{wait}s 后重试 ({attempt}/{max_retries})...")
                time.sleep(wait)
            else:
                print(f"️ 请求失败 (HTTP {response.status_code}): {response.message}")
                return response
        except Exception as e:
            print(f"❌ 请求异常: {str(e)}，{attempt}/{max_retries} 次重试...")
            time.sleep(DELAY_SECONDS * attempt)
    return None

def process_bongard_images():
    if not os.path.isdir(IMAGE_DIR):
        print(f"❌ 目录不存在: {IMAGE_DIR}")
        return

    png_files = sorted([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith('.png')])
    if not png_files:
        print("⚠️ 未找到任何 .png 文件")
        return

    print(f" 共找到 {len(png_files)} 张图片，开始处理...\n")

    for i, png_file in enumerate(png_files, 1):
        png_path = os.path.abspath(os.path.join(IMAGE_DIR, png_file))
        txt_path = os.path.join(IMAGE_DIR, os.path.splitext(png_file)[0] + '.txt')

        print(f"[{i}/{len(png_files)}] 正在处理: {png_file} ...")

        response = call_model_with_retry(png_path, PROMPT_TEMPLATE, MAX_RETRIES)
        
        description = safe_extract_text(response) if response else None
        if description:
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(description)
            print(f"✅ 已保存描述至: {os.path.basename(txt_path)}")
        else:
            print(f"️ 跳过保存（无有效响应或请求失败）。")

        if i < len(png_files):
            time.sleep(DELAY_SECONDS)

    print("\n🎉 所有图片处理完成！")

if __name__ == "__main__":
    print(f"🚀 脚本所在目录: {BASE_DIR}")
    print(f"📂 目标图片目录: {IMAGE_DIR}")
    print("💡 提示：首次运行请确保已执行 pip install -U dashscope")
    process_bongard_images()
