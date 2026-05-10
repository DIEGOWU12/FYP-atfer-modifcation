import os
import time
import base64
import dashscope
from dashscope import MultiModalConversation

# ================= 配置区 =================
API_KEY = "sk-e03f2df5f8ed44e2bb77a9bae5ff5121"  # 🔑 替换为你的真实 Key
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 目标根目录
ROOT_IMAGE_DIR = os.path.join(BASE_DIR, "Kohya_data", "7_BongardStyle")
MODEL = "qwen-vl-plus"
DELAY_SECONDS = 1.5
MAX_RETRIES = 3 
# ==========================================

dashscope.api_key = API_KEY

PROMPT_TEMPLATE = """BongardStyle,Please help me to describe the figure using a similar style as follows in a brief way: "The image shows a 3x4 grid of twelve black figures: Row 1, Left: [Shape description] Row 1, Mid-Left: [Shape description] Row 1, Mid-Right: [Shape description] Row 1, Right: [Shape description] Row 2, Left: [Shape description] Row 2, Mid-Left: [Shape description] Row 2, Mid-Right: [Shape description] Row 2, Right: [Shape description] Row 3, Left: [Shape description] Row 3, Mid-Left: [Shape description] Row 3, Mid-Right: [Shape description] Row 3, Right: [Shape description] Minimalist black-and-white style with rough, hand-drawn or pixelated edges." Please output ONLY the description in this exact format. Replace the bracketed parts with accurate shape descriptions based on the image. Do not add any extra text, explanations, or markdown formatting."""

def image_to_base64(image_path):
    """将本地图片转换为 Base64 字符串"""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    suffix = "png" if image_path.lower().endswith('.png') else "jpeg"
    return f"data:image/{suffix};base64,{encoded_string}"

def safe_extract_text(response):
    """解析并清洗返回文本"""
    try:
        if response.status_code == 200 and response.output:
            content = response.output.choices[0].message.content
            text = ""
            if isinstance(content, list):
                text = content[0].get("text", "")
            else:
                text = str(content)
            
            text = text.strip()
            if text.startswith("```"):
                lines = text.splitlines()
                if lines[0].startswith("```"): lines = lines[1:]
                if lines and lines[-1].startswith("```"): lines = lines[:-1]
                text = "\n".join(lines).strip()
            return text
        return None
    except Exception:
        return None

def call_model_with_retry(image_path, prompt, max_retries=3):
    """带重试的 API 调用"""
    image_content = image_to_base64(image_path)
    for attempt in range(1, max_retries + 1):
        try:
            response = MultiModalConversation.call(
                model=MODEL,
                messages=[{
                    "role": "user",
                    "content": [{"image": image_content}, {"text": prompt}]
                }]
            )
            if response.status_code == 200: return response
            elif response.status_code == 429 or response.status_code >= 500:
                wait = DELAY_SECONDS * attempt
                print(f"⚠️ 状态码 {response.status_code}，{wait}s 后重试...")
                time.sleep(wait)
            else:
                print(f"❌ 请求失败: {response.message}")
                return response
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            time.sleep(DELAY_SECONDS * attempt)
    return None

def process_all_images():
    # 使用 os.walk 遍历所有子文件夹
    if not os.path.isdir(ROOT_IMAGE_DIR):
        print(f"❌ 目录不存在: {ROOT_IMAGE_DIR}")
        return

    all_image_paths = []
    
    # 遍历目录树
    for root, dirs, files in os.walk(ROOT_IMAGE_DIR):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                full_path = os.path.join(root, file)
                all_image_paths.append(full_path)
    
    # 排序，保证处理顺序一致
    all_image_paths.sort()

    if not all_image_paths:
        print("⚠️ 未找到任何图片文件")
        return

    print(f"✅ 共找到 {len(all_image_paths)} 张图片，开始处理...\n")

    for i, img_path in enumerate(all_image_paths, 1):
        # 生成对应的 txt 保存路径 (保存在图片同级目录)
        txt_path = os.path.splitext(img_path)[0] + '.txt'
        img_name = os.path.basename(img_path)
        
        print(f"[{i}/{len(all_image_paths)}] 正在处理: {img_path} ...")

        response = call_model_with_retry(img_path, PROMPT_TEMPLATE, MAX_RETRIES)
        description = safe_extract_text(response) if response else None
        
        if description:
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(description)
            print(f"✅ 已保存: {txt_path}")
        else:
            print(f"️ 处理失败，跳过保存。")

        if i < len(all_image_paths):
            time.sleep(DELAY_SECONDS)

    print("\n🎉 全部完成！")

if __name__ == "__main__":
    print(f"🚀 脚本目录: {BASE_DIR}")
    print(f"📂 扫描目录: {ROOT_IMAGE_DIR}")
    process_all_images()
