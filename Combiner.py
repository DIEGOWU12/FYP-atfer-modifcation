import os
import itertools
from PIL import Image

# ====================================================================
# 1. 路径与全局配置
# ====================================================================
SOURCE_DIR = "Bongard_Dataset_v3"
FINAL_TARGET_DIR = "Kohya_data/8_BongardStyle"

# 最终组合图的总尺寸
FINAL_WIDTH = 256
FINAL_HEIGHT = 256

# 每张子图在这个总尺寸下的计算大小 (2列 x 3行)
# 宽度 256/2 = 128, 高度 256/3 = 85 (留1像素余量或全填充)
SUB_IMG_W = 128
SUB_IMG_H = 85

RIGHT_7 = [284, 344, 351, 529, 533, 809, 917, 1003, 1008, 1065, 1115, 1122, 1184, 1202, 1283, 559]
LEFT_7 = [352, 356, 523, 524, 860, 869, 935, 1093, 1116, 1261, 1262, 1275]
LEFT_8 = [379, 802, 998, 1012, 1258, 1268]
BOTH_7 = [966, 1033, 1274]
RIGHT_8 = [997, 1118, 1187, 1200, 1252]
AUGMENT_LIST = RIGHT_7 + LEFT_7 + LEFT_8 + BOTH_7 + RIGHT_8

def create_combined_256_image(img_list, save_path):
    """
    将6张图强制缩放并拼接成一张标准的 256x256 图片
    布局为 2列 x 3行
    """
    # 创建 256x256 白色底图
    combined_img = Image.new("RGB", (FINAL_WIDTH, FINAL_HEIGHT), "white")
    
    for i, img_path in enumerate(img_list[:6]):
        try:
            with Image.open(img_path) as img:
                # 关键：先将每一张子图强制 resize 到 (128, 85)
                # 这样 2x3 拼接起来正好铺满 256x256
                img_res = img.convert("RGB").resize((SUB_IMG_W, SUB_IMG_H), Image.Resampling.LANCZOS)
                
                # 计算坐标
                x = (i % 2) * SUB_IMG_W
                y = (i // 2) * SUB_IMG_H
                
                combined_img.paste(img_res, (x, y))
        except Exception as e:
            print(f"无法处理 {img_path}: {e}")
            continue
            
    # 保存最终结果
    combined_img.save(save_path, "PNG")

# ====================================================================
# 3. 整合处理逻辑 (针对你的 6-image 需求)
# ====================================================================
def process_bp_folder(bp_folder_name):
    src_folder = os.path.join(SOURCE_DIR, bp_folder_name)
    if not os.path.exists(src_folder): return
    try: bp_id = int(bp_folder_name.replace("BP", ""))
    except: return

    imgs = sorted([os.path.join(src_folder, f) for f in os.listdir(src_folder) 
                   if f.lower().endswith((".png", ".jpg")) and "combined" not in f.lower()])
    
    sol_src = os.path.join(src_folder, "solution.txt")
    solution_content = open(sol_src, "r", encoding="utf-8").read() if os.path.exists(sol_src) else ""

    # 逻辑核心：提取目标图片池
    if bp_id in AUGMENT_LIST:
        if bp_id in RIGHT_7: target_pool = imgs[6:13]
        elif bp_id in LEFT_7: target_pool = imgs[:7]
        elif bp_id in LEFT_8: target_pool = imgs[:8]
        elif bp_id in BOTH_7: target_pool = imgs[:7]
        elif bp_id in RIGHT_8: target_pool = imgs[6:14]
        else: target_pool = imgs[:6]

        count = 0
        # 从池子里选 6 张图的所有排列组合
        for combo in itertools.combinations(target_pool, 6):
            count += 1
            v_name = f"{bp_folder_name}_v{count}"
            save_path = os.path.join(FINAL_TARGET_DIR, f"{v_name}.png")
            txt_path = os.path.join(FINAL_TARGET_DIR, f"{v_name}.txt")
            
            create_combined_256_image(combo, save_path)
            
            if solution_content:
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(solution_content)
    
    elif len(imgs) >= 6:
        # 标准处理：直接取前6张
        save_path = os.path.join(FINAL_TARGET_DIR, f"{bp_folder_name}.png")
        txt_path = os.path.join(FINAL_TARGET_DIR, f"{bp_folder_name}.txt")
        create_combined_256_image(imgs[:6], save_path)
        if solution_content:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(solution_content)

if __name__ == "__main__":
    os.makedirs(FINAL_TARGET_DIR, exist_ok=True)
    all_folders = [d for d in os.listdir(SOURCE_DIR) if d.startswith("BP") and os.path.isdir(os.path.join(SOURCE_DIR, d))]
    for folder in sorted(all_folders, key=lambda x: int(x[2:]) if x[2:].isdigit() else 0):
        process_bp_folder(folder)
    print(f"\n🎉 任务完成！所有组合图均为标准的 256x256 尺寸。")