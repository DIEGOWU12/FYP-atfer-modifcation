import os
import re
from PIL import Image

# 1. 自动获取脚本所在的绝对路径 (fyp 文件夹)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 核心路径配置
# 输入：脚本旁边的 Kohya_data 文件夹
INPUT_ROOT = os.path.join(BASE_DIR, "Kohya_data")
# 输出：脚本旁边的 Kohya_new_dataset/5_BongardStyle
OUTPUT_FOLDER = os.path.join(BASE_DIR, "Kohya_new_dataset", "5_BongardStyle")

# 自动创建输出目录
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

print(f"🚀 启动扫描...")
print(f"📂 正在进入: {INPUT_ROOT}")
print(f"📁 结果将存入: {OUTPUT_FOLDER}\n")

def split_images_and_texts():
    count = 0

    # 检查输入文件夹是否存在
    if not os.path.exists(INPUT_ROOT):
        print(f"❌ 错误：找不到输入文件夹 {INPUT_ROOT}")
        return

    # 3. 递归遍历 Kohya_data 下的所有文件夹和文件
    for root, dirs, files in os.walk(INPUT_ROOT):
        # 排除输出文件夹，防止自己扫自己（如果输出文件夹不小心建在了输入文件夹里面）
        if "Kohya_new_dataset" in root:
            continue

        for filename in files:
            # 只处理图片文件
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                base_name = os.path.splitext(filename)[0]
                img_path = os.path.join(root, filename)
                txt_path = os.path.join(root, f"{base_name}.txt")

                # 获取当前图片所在的子文件夹名称（用于重命名防止冲突）
                sub_folder_name = os.path.basename(root)

                # 检查对应的 txt 描述文件是否存在
                if not os.path.exists(txt_path):
                    continue

                try:
                    # --- 图像裁剪 ---
                    with Image.open(img_path) as img:
                        width, height = img.size
                        mid = width // 2
                        left_img = img.crop((0, 0, mid, height))
                        right_img = img.crop((mid, 0, width, height))

                        # 保存文件名：[子文件夹名]_[原文件名]_left.png
                        # 这样做是为了防止不同文件夹下的 001.png 互相覆盖
                        save_prefix = f"{sub_folder_name}_{base_name}"
                        
                        left_img.save(os.path.join(OUTPUT_FOLDER, f"{save_prefix}_left.png"))
                        right_img.save(os.path.join(OUTPUT_FOLDER, f"{save_prefix}_right.png"))

                    # --- 文本逻辑提取 ---
                    with open(txt_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()

                    # 使用正则匹配原有的 Left/Right logic
                    left_match = re.search(r"Left Side \(6 panels\): each panel features a '(.*?)' logic", content)
                    right_match = re.search(r"Right Side \(6 panels\): each panel features a '(.*?)' logic", content)

                    if left_match and right_match:
                        l_logic = left_match.group(1).strip()
                        r_logic = right_match.group(1).strip()

                        # 构造新的训练 Prompt
                        prompt_template = (
                            "BongardStyle, a black and white geometric 3x2 grid illustration, white background. "
                            "Each panel features a '{}' logic, showing geometric shapes with {} arrangement. "
                            "Clear visual logic, stark contrast, minimalist geometric diagram."
                        )

                        with open(os.path.join(OUTPUT_FOLDER, f"{save_prefix}_left.txt"), 'w', encoding='utf-8') as f:
                            f.write(prompt_template.format(l_logic, l_logic))
                        
                        with open(os.path.join(OUTPUT_FOLDER, f"{save_prefix}_right.txt"), 'w', encoding='utf-8') as f:
                            f.write(prompt_template.format(r_logic, r_logic))

                    count += 1
                    print(f"✅ 处理成功: {sub_folder_name}/{filename}")

                except Exception as e:
                    print(f"❌ 处理异常 {filename}: {e}")

    print(f"\n🎉 任务完成！总计处理了 {count} 组数据。")

if __name__ == "__main__":
    split_images_and_texts()