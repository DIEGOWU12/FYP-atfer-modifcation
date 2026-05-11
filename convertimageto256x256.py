import os
from PIL import Image

def process_bongard_images_pure_resize(input_dir, output_dir, size=(256, 256)):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
    files = os.listdir(input_dir)
    print(f"正在直接缩放 {len(files)} 个文件至 {size}...")

    for file_name in files:
        if file_name.lower().endswith(valid_extensions):
            img_path = os.path.join(input_dir, file_name)
            save_path = os.path.join(output_dir, file_name)

            try:
                with Image.open(img_path) as img:
                    # 确保是 RGB 模式
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    
                    # 直接强制缩放 (忽略原图比例)
                    # 使用 Image.Resampling.LANCZOS 保证线条清晰
                    img_resized = img.resize(size, Image.Resampling.LANCZOS)
                    
                    # 保存为 PNG
                    img_resized.save(save_path, "PNG")
                    print(f"Resize完成: {file_name}")

            except Exception as e:
                print(f"处理 {file_name} 出错: {e}")

# --- 路径设置 ---
input_folder = r'C:\Users\Lenovo\OneDrive\文档\GitHub\FYP-atfer-modifcation\Kohya_new_dataset\train\5_BongardStyle'
output_folder = r'C:\Users\Lenovo\OneDrive\文档\GitHub\FYP-atfer-modifcation\256x256imgaes\6_BongardStyle'

process_bongard_images_pure_resize(input_folder, output_folder)
print("\n--- 任务结束，已完成强制缩放处理 ---")