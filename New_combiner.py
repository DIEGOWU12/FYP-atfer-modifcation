import os
import shutil
import itertools
from PIL import Image, ImageDraw
#这个跟上一个combiner的区别就是这个是1024x1024的。
# ====================================================================
# 1. 路径与全局配置
# ====================================================================
SOURCE_DIR = "Bongard_Dataset_v3"
FINAL_TARGET_DIR = "Kohya_data/7_BongardStyle"

RIGHT_7 = [284, 344, 351, 529, 533, 809, 917, 1003, 1008, 1065, 1115, 1122, 1184, 1202, 1283, 559]
LEFT_7 = [352, 356, 523, 524, 860, 869, 935, 1093, 1116, 1261, 1262, 1275]
LEFT_8 = [379, 802, 998, 1012, 1258, 1268]
BOTH_7 = [966, 1033, 1274]
RIGHT_8 = [997, 1118, 1187, 1200, 1252]
AUGMENT_LIST = RIGHT_7 + LEFT_7 + LEFT_8 + BOTH_7 + RIGHT_8

SINGLE_IMG_SIZE, IMG_PADDING, GROUP_SPACING = 100, 10, 30
SINGLE_GROUP_WIDTH = 2 * SINGLE_IMG_SIZE + 3 * IMG_PADDING
SINGLE_GROUP_HEIGHT = 3 * SINGLE_IMG_SIZE + 4 * IMG_PADDING
IMG_AREA_WIDTH = (SINGLE_GROUP_WIDTH * 2) + GROUP_SPACING
IMG_AREA_HEIGHT = SINGLE_GROUP_HEIGHT

def create_combined_image(left_imgs, right_imgs, save_path):
    # 1. 调整参数以适应 1024x1024 整体画布
    # 设置单张小图为 230px 左右，加上间距刚好填满
    UP_SINGLE_SIZE = 230  
    UP_PADDING = 25
    UP_GROUP_SPACING = 60
    TARGET_CANVAS = 1024

    # 创建白色画布
    combined_img = Image.new("RGB", (TARGET_CANVAS, TARGET_CANVAS), "white")
    draw = ImageDraw.Draw(combined_img)
    
    all_imgs = list(left_imgs) + list(right_imgs)
    
    for i, img_path in enumerate(all_imgs):
        try:
            with Image.open(img_path) as img:
                # 核心改进：使用 LANCZOS 进行高质量放大
                img_res = img.convert("L").resize((UP_SINGLE_SIZE, UP_SINGLE_SIZE), resample=Image.LANCZOS)
                
                # 核心改进：二值化处理，确保单张小图是纯黑白，消除放大产生的虚边
                img_res = img_res.point(lambda p: 255 if p > 127 else 0, mode='1').convert("RGB")

            # 计算坐标
            offset_x = 0 if i < 6 else (UP_SINGLE_SIZE * 2 + UP_PADDING * 3 + UP_GROUP_SPACING)
            idx = i if i < 6 else i - 6
            
            x = UP_PADDING + (idx % 2) * (UP_SINGLE_SIZE + UP_PADDING)
            # 如果 offset_x 较大，需要根据右侧组调整 x
            if i >= 6:
                x = (TARGET_CANVAS // 2) + (UP_GROUP_SPACING // 2) + (idx % 2) * (UP_SINGLE_SIZE + UP_PADDING)
            else:
                x = (TARGET_CANVAS // 2) - (UP_GROUP_SPACING // 2) - (2 * UP_SINGLE_SIZE + UP_PADDING) + (idx % 2) * (UP_SINGLE_SIZE + UP_PADDING)
            
            # 居中对齐 y 轴坐标
            total_group_height = 3 * UP_SINGLE_SIZE + 2 * UP_PADDING
            start_y = (TARGET_CANVAS - total_group_height) // 2
            y = start_y + (idx // 2) * (UP_SINGLE_SIZE + UP_PADDING)

            # 粘贴图片
            combined_img.paste(img_res, (int(x), int(y)))
            
            # 画小框（可选，建议颜色深一点方便模型识别边界）
            draw.rectangle([x - 1, y - 1, x + UP_SINGLE_SIZE, y + UP_SINGLE_SIZE], outline=(180, 180, 180))
            
        except Exception as e:
            print(f"Error pasting {img_path}: {e}")
            continue

    # 画中间的分隔线
    center_x = TARGET_CANVAS // 2
    draw.line([(center_x, 100), (center_x, TARGET_CANVAS - 100)], fill=(200, 200, 200), width=2)
    
    # 最终保存
    combined_img.save(save_path, "PNG")

# ====================================================================
# 3. 整合处理函数
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

    # 增强逻辑
    if bp_id in AUGMENT_LIST:
        if bp_id in RIGHT_7: lp, rp = imgs[:6], imgs[6:13]
        elif bp_id in LEFT_7: lp, rp = imgs[:7], imgs[7:13]
        elif bp_id in LEFT_8: lp, rp = imgs[:8], imgs[8:14]
        elif bp_id in BOTH_7: lp, rp = imgs[:7], imgs[7:14]
        elif bp_id in RIGHT_8: lp, rp = imgs[:6], imgs[6:14]
        
        count = 0
        for l_set, r_set in itertools.product(itertools.combinations(lp, 6), itertools.combinations(rp, 6)):
            count += 1
            v_name = f"{bp_folder_name}_c{count}"
            v_folder = os.path.join(FINAL_TARGET_DIR, v_name)
            os.makedirs(v_folder, exist_ok=True)
            create_combined_image(l_set, r_set, os.path.join(v_folder, f"{v_name}.png"))
            if solution_content:
                with open(os.path.join(v_folder, f"{v_name}.txt"), "w", encoding="utf-8") as f:
                    f.write(solution_content)
        print(f"📦 {bp_folder_name}: 生成 {count} 个增强变体")

    # 标准逻辑
    elif len(imgs) == 12:
        v_folder = os.path.join(FINAL_TARGET_DIR, bp_folder_name)
        os.makedirs(v_folder, exist_ok=True)
        create_combined_image(imgs[:6], imgs[6:12], os.path.join(v_folder, f"{bp_folder_name}.png"))
        if solution_content:
            with open(os.path.join(v_folder, f"{bp_folder_name}.txt"), "w", encoding="utf-8") as f:
                f.write(solution_content)
        print(f"✅ {bp_folder_name}: 标准处理完成")

if __name__ == "__main__":
    os.makedirs(FINAL_TARGET_DIR, exist_ok=True)
    all_folders = [d for d in os.listdir(SOURCE_DIR) if d.startswith("BP") and os.path.isdir(os.path.join(SOURCE_DIR, d))]
    for folder in sorted(all_folders, key=lambda x: int(x[2:]) if x[2:].isdigit() else 0):
        process_bp_folder(folder)
    print(f"\n🎉 完成！输出路径: {FINAL_TARGET_DIR}")