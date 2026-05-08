import os
import shutil
from PIL import Image, ImageDraw
#2
# --- 路径配置 (根据你的实际路径修改) ---
SOURCE_DIR = "Bongard_Dataset_v3"
TARGET_DIR = "Bongard_Dataset_v3_new_struct"

# --- 布局常量 (保持你之前的 2x6 逻辑) ---
SUB_GRID_ROWS = 3
SUB_GRID_COLS = 2
NUM_IMAGES_PER_GROUP = 6
SINGLE_IMG_SIZE = 100 # 稍微调大一点，12宫格更清晰
IMG_PADDING = 10
GROUP_SPACING = 30

# 计算拼图的总尺寸
SINGLE_GROUP_WIDTH = SUB_GRID_COLS * SINGLE_IMG_SIZE + (SUB_GRID_COLS + 1) * IMG_PADDING
SINGLE_GROUP_HEIGHT = SUB_GRID_ROWS * SINGLE_IMG_SIZE + (SUB_GRID_ROWS + 1) * IMG_PADDING
IMG_AREA_WIDTH = (SINGLE_GROUP_WIDTH * 2) + GROUP_SPACING
IMG_AREA_HEIGHT = SINGLE_GROUP_HEIGHT

def process_to_new_struct(bp_id):
    bp_folder_name = f"BP{bp_id}"
    src_folder = os.path.join(SOURCE_DIR, bp_folder_name)
    
    if not os.path.exists(src_folder):
        return

    # 1. Create corresponding BP folder in target directory
    dst_folder = os.path.join(TARGET_DIR, bp_folder_name)
    os.makedirs(dst_folder, exist_ok=True)

    # 2. Process images: select 12 valid images
    valid_exts = (".png", ".jpg", ".jpeg")
    img_files = sorted([
        f for f in os.listdir(src_folder) 
        if f.lower().endswith(valid_exts) and f != "combined.png"
    ])

    if len(img_files) == 12:
        # Create a blank canvas
        combined_img = Image.new("RGB", (IMG_AREA_WIDTH, IMG_AREA_HEIGHT), "white")
        draw = ImageDraw.Draw(combined_img)

        for i in range(12):
            img_path = os.path.join(src_folder, img_files[i])
            with Image.open(img_path) as img:
                img_res = img.convert("RGB").resize((SINGLE_IMG_SIZE, SINGLE_IMG_SIZE))
            
            # Compute position (2x6 layout: left group + right group)
            group_offset_x = 0 if i < 6 else (SINGLE_GROUP_WIDTH + GROUP_SPACING)
            idx = i if i < 6 else i - 6
            x = group_offset_x + IMG_PADDING + (idx % SUB_GRID_COLS) * (SINGLE_IMG_SIZE + IMG_PADDING)
            y = IMG_PADDING + (idx // SUB_GRID_COLS) * (SINGLE_IMG_SIZE + IMG_PADDING)

            # Draw light border
            draw.rectangle(
                [x - 1, y - 1, x + SINGLE_IMG_SIZE, y + SINGLE_IMG_SIZE],
                outline=(200, 200, 200)
            )
            combined_img.paste(img_res, (x, y))

        # Draw a vertical separator line between two groups
        center_x = SINGLE_GROUP_WIDTH + GROUP_SPACING // 2
        draw.line(
            [(center_x, 20), (center_x, IMG_AREA_HEIGHT - 20)],
            fill="lightgray",
            width=1
        )

        # Save combined image to target folder
        combined_img.save(os.path.join(dst_folder, f"{bp_folder_name}.png"))
        print(f"✅ {bp_folder_name}: combined image generated successfully")

    else:
        print(f"⚠ {bp_folder_name}: invalid image count ({len(img_files)}), skipping combination")

    # 3. Copy solution.txt to target folder
    src_txt = os.path.join(src_folder, "solution.txt")
    if os.path.exists(src_txt):
        shutil.copy(src_txt, os.path.join(dst_folder, "solution.txt"))
        print(f"✅ {bp_folder_name}: solution file copied")
    else:
        print(f"❌ {bp_folder_name}: solution.txt not found")

if __name__ == "__main__":
    os.makedirs(TARGET_DIR, exist_ok=True)
    
    # 获取所有 BP 文件夹并排序
    all_folders = [d for d in os.listdir(SOURCE_DIR) if d.startswith("BP") and os.path.isdir(os.path.join(SOURCE_DIR, d))]
    
    for folder in sorted(all_folders, key=lambda x: int(x[2:]) if x[2:].isdigit() else 0):
        bp_num = folder[2:]
        if bp_num.isdigit():
            process_to_new_struct(int(bp_num))

    print(f"\n🚀 任务完成！新结构已保存在: {TARGET_DIR}")