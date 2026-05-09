
import os
import re
from PIL import Image

# 获取当前 py 文件所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据集目录
input_folder = os.path.join(BASE_DIR, "Kohya_train_data", "6_BongardStyle")

# 输出目录
output_root = os.path.join(BASE_DIR, "Kohya_new_dataset")
output_folder = os.path.join(output_root, "5_BongardStyle")

# 自动创建输出目录
os.makedirs(output_folder, exist_ok=True)

print("当前脚本目录:", BASE_DIR)
print("输入目录:", input_folder)
print("输出目录:", output_folder)


def split_images_and_texts():
    count = 0

    # 递归扫描所有文件夹
    for root, dirs, files in os.walk(input_folder):

        for filename in files:

            # 只处理图片
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):

                base_name = os.path.splitext(filename)[0]

                img_path = os.path.join(root, filename)
                txt_path = os.path.join(root, f"{base_name}.txt")

                print(f"\n📂 正在处理: {img_path}")

                # 检查 txt 是否存在
                if not os.path.exists(txt_path):
                    print(f"⚠️ 缺少 txt 文件: {txt_path}")
                    continue

                try:
                    # =========================
                    # 1. 图像裁剪
                    # =========================
                    with Image.open(img_path) as img:

                        width, height = img.size
                        mid = width // 2

                        left_img = img.crop((0, 0, mid, height))
                        right_img = img.crop((mid, 0, width, height))

                        left_img.save(
                            os.path.join(output_folder, f"{base_name}_left.png")
                        )

                        right_img.save(
                            os.path.join(output_folder, f"{base_name}_right.png")
                        )

                    # =========================
                    # 2. 读取文本
                    # =========================
                    with open(txt_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()

                    # =========================
                    # 3. 提取 Left logic
                    # =========================
                    left_logic_match = re.search(
                        r"Left Side \(6 panels\): each panel features a '(.*?)' logic",
                        content
                    )

                    # =========================
                    # 4. 提取 Right logic
                    # =========================
                    right_logic_match = re.search(
                        r"Right Side \(6 panels\): each panel features a '(.*?)' logic",
                        content
                    )

                    if not left_logic_match:
                        print(f"⚠️ 无法提取 Left logic: {base_name}")
                        continue

                    if not right_logic_match:
                        print(f"⚠️ 无法提取 Right logic: {base_name}")
                        continue

                    left_logic = left_logic_match.group(1).strip()
                    right_logic = right_logic_match.group(1).strip()

                    # =========================
                    # 5. 构造 Left prompt
                    # =========================
                    new_left_txt = (
                        f"BongardStyle, a black and white geometric 3x2 grid illustration, "
                        f"white background. "
                        f"Each panel features a '{left_logic}' logic, "
                        f"showing geometric shapes with {left_logic} arrangement. "
                        f"Clear visual logic, stark contrast, minimalist geometric diagram."
                    )

                    # =========================
                    # 6. 构造 Right prompt
                    # =========================
                    new_right_txt = (
                        f"BongardStyle, a black and white geometric 3x2 grid illustration, "
                        f"white background. "
                        f"Each panel features a '{right_logic}' logic, "
                        f"showing geometric shapes with {right_logic} arrangement. "
                        f"Clear visual logic, stark contrast, minimalist geometric diagram."
                    )

                    # =========================
                    # 7. 保存 txt
                    # =========================
                    with open(
                        os.path.join(output_folder, f"{base_name}_left.txt"),
                        'w',
                        encoding='utf-8'
                    ) as f:
                        f.write(new_left_txt)

                    with open(
                        os.path.join(output_folder, f"{base_name}_right.txt"),
                        'w',
                        encoding='utf-8'
                    ) as f:
                        f.write(new_right_txt)

                    print(f"✅ 已完成拆分: {base_name}")

                    count += 1

                except Exception as e:
                    print(f"❌ 处理失败 {base_name}: {e}")

    print(f"\n🚀 任务完成！生成了 {count * 2} 张图片及对应 txt 文件。")
    print(f"📁 输出目录: {output_folder}")


if __name__ == "__main__":
    split_images_and_texts()