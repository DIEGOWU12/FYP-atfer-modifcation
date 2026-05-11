import os
from PIL import Image, ImageDraw

def process_images_inplace(target_folder, line_color=(0, 0, 0), thickness=25):
    """
    直接在目标文件夹内的图片上画线并覆盖保存
    """
    # 检查路径是否存在
    if not os.path.exists(target_folder):
        print(f"错误: 找不到路径 {target_folder}")
        return

    count = 0
    for filename in os.listdir(target_folder):
        # 筛选图片格式
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            img_path = os.path.join(target_folder, filename)
            
            try:
                with Image.open(img_path) as img:
                    # 必须转为 RGB 才能画彩色线（防止有的图是黑白模式）
                    img = img.convert("RGB")
                    draw = ImageDraw.Draw(img)
                    width, height = img.size

                    # 1. 垂直中轴线
                    v_x = width // 2
                    draw.line([v_x, 0, v_x, height], fill=line_color, width=thickness)

                    # 2. 水平三等分线
                    h_y1 = height // 3
                    h_y2 = (height // 3) * 2
                    draw.line([0, h_y1, width, h_y1], fill=line_color, width=thickness)
                    draw.line([0, h_y2, width, h_y2], fill=line_color, width=thickness)

                    # 直接覆盖原文件保存
                    img.save(img_path)
                    count += 1
                    print(f"已处理并覆盖: {filename}")
            except Exception as e:
                print(f"处理 {filename} 时出错: {e}")

    print(f"\n任务完成！共处理了 {count} 张图片。")

# --- 你的特定路径 ---
path = r'C:\Users\Lenovo\OneDrive\文档\GitHub\FYP-atfer-modifcation\FinalKohya_data\5_BongardStyle'

# 执行（线宽设为 25 像素，适合模型学习边界特征）
process_images_inplace(path, thickness=25)