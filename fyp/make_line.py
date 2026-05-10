import os
from PIL import Image, ImageDraw

def process_images(input_folder, output_folder, line_color=(255, 0, 0), thickness=15):
    """
    在图片上绘制 3x2 的红色分割粗线
    :param input_folder: 原始图片文件夹
    :param output_folder: 处理后图片的保存路径
    :param line_color: 线条颜色，默认红色 (R, G, B)
    :param thickness: 线条粗细
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(input_folder, filename)
            
            # 打开图片并转为 RGB
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                draw = ImageDraw.Draw(img)
                width, height = img.size

                # 1. 绘制垂直分割线 (居中)
                # 线条坐标格式: [x0, y0, x1, y1]
                v_x = width // 2
                draw.line([v_x, 0, v_x, height], fill=line_color, width=thickness)

                # 2. 绘制两条水平分割线 (三等分)
                h_y1 = height // 3
                h_y2 = (height // 3) * 2
                draw.line([0, h_y1, width, h_y1], fill=line_color, width=thickness)
                draw.line([0, h_y2, width, h_y2], fill=line_color, width=thickness)

                # 保存结果
                img.save(os.path.join(output_folder, f"marked_{filename}"))
                print(f"已处理: {filename}")

# --- 使用设置 ---
input_dir = 'your_images_folder'  # 替换为你的存放图片的文件夹名
output_dir = 'marked_results'      # 处理后图片存放的位置
line_width = 20                   # 训练用建议线宽设大一点，比如 20-30 像素

# 运行处理
# process_images(input_dir, output_dir, thickness=line_width)