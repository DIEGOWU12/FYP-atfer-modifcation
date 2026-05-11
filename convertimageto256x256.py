import os
from PIL import Image

def process_images(input_dir, output_dir, size=(256, 256)):
    # 如果输出文件夹不存在则创建
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 支持的图片格式
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')

    for file_name in os.listdir(input_dir):
        if file_name.lower().endswith(valid_extensions):
            img_path = os.path.join(input_dir, file_name)
            try:
                with Image.open(img_path) as img:
                    # 1. 处理透明度（如果是 RGBA 转为 RGB）
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")

                    # 2. 计算中心裁剪（保持正方形）
                    width, height = img.size
                    new_side = min(width, height)
                    left = (width - new_side) / 2
                    top = (height - new_side) / 2
                    right = (width + new_side) / 2
                    bottom = (height + new_side) / 2

                    # 裁剪并缩放
                    img = img.crop((left, top, right, bottom))
                    img = img.resize(size, Image.Resampling.LANCZOS)

                    # 3. 保存图片
                    save_path = os.path.join(output_dir, file_name)
                    img.save(save_path, "JPEG", quality=95)
                    print(f"成功处理: {file_name}")

            except Exception as e:
                print(f"处理 {file_name} 时出错: {e}")

# --- 使用设置 ---
input_folder = r'D:\your_dataset\original'  # 替换为你的原图路径
output_folder = r'D:\your_dataset\256x256'  # 替换为你想保存的路径

process_images(input_folder, output_folder)
print("所有图片处理完成！")