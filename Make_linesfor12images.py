import os
from PIL import Image, ImageDraw

# ================= 配置区 =================
# 根目录路径（包含所有 BP 文件夹的父目录）
ROOT_DIR = r'C:\Users\Lenovo\OneDrive\文档\GitHub\FYP-atfer-modifcation\Kohya_data\7_BongardStyle'

# 之前的拼贴参数，保持不变以确保线画在空隙处
UP_SINGLE_SIZE = 230  
UP_PADDING = 25
UP_GROUP_SPACING = 60
TARGET_CANVAS = 1024

# 画线配置
LINE_COLOR = (0, 0, 0)  # 纯黑粗线
THICKNESS = 20          # 强特征线宽
# ==========================================

def get_grid_coordinates():
    """精确计算 12 宫格分割线坐标"""
    left_group_width = (2 * UP_SINGLE_SIZE + 2 * UP_PADDING)
    canvas_side_margin = (TARGET_CANVAS - (2 * left_group_width) - UP_GROUP_SPACING) // 2
    v_mid = canvas_side_margin + left_group_width + (UP_GROUP_SPACING // 2)

    v_left = canvas_side_margin + UP_SINGLE_SIZE + (UP_PADDING // 2)
    v_right = TARGET_CANVAS - canvas_side_margin - UP_SINGLE_SIZE - (UP_PADDING // 2)

    total_group_height = 3 * UP_SINGLE_SIZE + 2 * UP_PADDING
    start_y = (TARGET_CANVAS - total_group_height) // 2
    h1 = start_y + UP_SINGLE_SIZE + (UP_PADDING // 2)
    h2 = start_y + 2 * UP_SINGLE_SIZE + (UP_PADDING * 1.5) 

    return {
        'v_lines': [int(v_mid), int(v_left), int(v_right)],
        'h_lines': [int(h1), int(h2)]
    }

def apply_bold_grid_recursive(root_path):
    if not os.path.exists(root_path):
        print(f"路径错误: {root_path}")
        return

    coords = get_grid_coordinates()
    total_count = 0

    # 使用 os.walk 遍历所有子文件夹
    for root, dirs, files in os.walk(root_path):
        for filename in files:
            # 只处理 1024 尺寸的拼接图，排除掉可能存在的原始小图（如果有的话）
            # 建议你的拼接图文件名包含 "BP" 或者符合你的命名规则
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(root, filename)
                
                try:
                    with Image.open(img_path) as img:
                        # 检查尺寸：只处理 1024x1024 的大图，避免误伤
                        if img.size != (TARGET_CANVAS, TARGET_CANVAS):
                            continue
                            
                        img = img.convert("RGB")
                        draw = ImageDraw.Draw(img)
                        
                        # 画 3 条垂直线
                        for vx in coords['v_lines']:
                            draw.line([vx, 0, vx, TARGET_CANVAS], fill=LINE_COLOR, width=THICKNESS)
                        
                        # 画 2 条水平线
                        for hy in coords['h_lines']:
                            draw.line([0, hy, TARGET_CANVAS, hy], fill=LINE_COLOR, width=THICKNESS)

                        img.save(img_path)
                        total_count += 1
                        print(f"已处理子文件夹 [{os.path.basename(root)}] 中的: {filename}")
                except Exception as e:
                    print(f"处理 {filename} 时出错: {e}")

    print(f"\n🎉 任务完成！共在 {total_count} 张拼接图上应用了强分割线。")

if __name__ == "__main__":
    apply_bold_grid_recursive(ROOT_DIR)