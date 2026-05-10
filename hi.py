import os
from PIL import Image

# 1. 路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_ROOT = os.path.join(BASE_DIR, "Kohya_data")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "Testdataset", "5_BongardStyle")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def split_images_and_texts():
    count = 0
    
    for root, dirs, files in os.walk(INPUT_ROOT):
        # 这里的判断是为了防止扫描到输出文件夹
        if "Testdataset" in root or "Kohya_new_dataset" in root:
            continue

        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                base_name = os.path.splitext(filename)[0]
                img_path = os.path.join(root, filename)
                txt_path = os.path.join(root, f"{base_name}.txt")
                sub_folder_name = os.path.basename(root)

                if not os.path.exists(txt_path):
                    continue

                try:
                    # --- 1. 图像裁剪 ---
                    with Image.open(img_path) as img:
                        width, height = img.size
                        mid = width // 2
                        left_img = img.crop((0, 0, mid, height))
                        right_img = img.crop((mid, 0, width, height))

                        save_prefix = f"{sub_folder_name}_{base_name}"
                        left_img.save(os.path.join(OUTPUT_FOLDER, f"{save_prefix}_left.png"))
                        right_img.save(os.path.join(OUTPUT_FOLDER, f"{save_prefix}_right.png"))

                    # --- 2. 文本处理 (基于 "vs." 定位) ---
                    with open(txt_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()

                    # 核心逻辑：用 "vs." 拆分字符串
                    if "vs." in content:
                        # 假设格式是 "A vs. B."
                        # parts[0] = "Hollow outline", parts[1] = "filled in solid."
                        parts = content.split("vs.")
                        l_logic = parts[0].strip()
                        r_logic = parts[1].replace(".", "").strip() # 去掉结尾的句号
                    else:
                        # 如果没找到 vs.，就用全文
                        l_logic = r_logic = content
                        print(f"🔎 提示：{filename} 没找到 'vs.'，已使用全文描述。")

                    # 3. 构造并保存新的 TXT
                    template = "BongardStyle, {}, black and white geometric 3x2 grid, white background, minimalist."
                    
                    with open(os.path.join(OUTPUT_FOLDER, f"{save_prefix}_left.txt"), 'w', encoding='utf-8') as f:
                        f.write(template.format(l_logic))
                    
                    with open(os.path.join(OUTPUT_FOLDER, f"{save_prefix}_right.txt"), 'w', encoding='utf-8') as f:
                        f.write(template.format(r_logic))

                    count += 1
                    print(f"✅ 处理成功: {save_prefix}")

                except Exception as e:
                    print(f"❌ 失败 {filename}: {e}")

    print(f"\n🎉 完成！共生成 {count*2} 对文件。")

if __name__ == "__main__":
    split_images_and_texts()