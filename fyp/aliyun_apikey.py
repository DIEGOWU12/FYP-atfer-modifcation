import os
import time
import dashscope
from dashscope import MultiModalConversation

# ================= 配置区 =================
API_KEY = "sk-e03f2df5f8ed44e2bb77a9bae5ff5121"  # 🔑 替换为你的真实 Key
IMAGE_DIR = r"C:\Users\Lenovo\OneDrive\文档\GitHub\FYP-atfer-modifcation\fyp\Kohya_new_dataset\5_BongardStyle"

MODEL = "qwen-vl-plus"
DELAY_SECONDS = 1.5
MAX_RETRIES = 3  # 新增：网络抖动/限流自动重试次数
# ==========================================

dashscope.api_key = API_KEY

PROMPT_TEMPLATE = """BongardStyle,Please help me to describe the figure using a similar style as follows in a brief way:
"The image shows a 3x2 grid of six black geometric shapes:

Top-left: [Shape description]
Top-right: [Shape description]
Middle-left: [Shape description]
Middle-right: [Shape description]
Bottom-left: [Shape description]
Bottom-right: [Shape description]

Minimalist black-and-white style."

Please output ONLY the description in this exact format. Replace the bracketed parts with accurate shape descriptions based on the image. Do not add any extra text, explanations, or markdown formatting."""

def safe_extract_text(response):
    """适配 DashScope 返回结构的稳健解析"""
    try:
        if response.status_code == 200 and response.output:
            content = response.output.choices[0].message.content
            # DashScope 可能返回 str 或 list[dict]
            if isinstance(content, list):
                return content[0].get("text", "").strip()
            return str(content).strip()
        return None
    except Exception:
        return None

def call_model_with_retry(image_path, prompt, max_retries=3):
    """带重试机制的 API 调用"""
    for attempt in range(1, max_retries + 1):
        try:
            response = MultiModalConversation.call(
                model=MODEL,
                messages=[{
                    "role": "user",
                    "content": [
                        {"image": image_path},  # ✅ 直接传本地路径，SDK 会自动上传
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
                print(f"⚠️ 请求失败 (HTTP {response.status_code}): {response.message}")
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

    print(f"📂 共找到 {len(png_files)} 张图片，开始处理...\n")

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
            print(f"⚠️ 跳过保存（无有效响应或请求失败）。")

        if i < len(png_files):
            time.sleep(DELAY_SECONDS)

    print("\n🎉 所有图片处理完成！")

if __name__ == "__main__":
    # 确保 SDK 为最新版（支持本地路径自动上传）
    print("💡 提示：首次运行请确保已执行 pip install -U dashscope")
    process_bongard_images()
