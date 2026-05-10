import os
import random
import shutil
from PIL import Image

# =========================================================
# 路径配置
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 源目录：包含 BP10, BP100 等子文件夹的目录
SOURCE_ROOT = os.path.join(BASE_DIR, "Kohya_data", "7_BongardStyle")

# 目标目录
TRAIN_DIR = os.path.join(BASE_DIR, "Lora_dataset2", "train", "5_BongardStyle")
TEST_DIR  = os.path.join(BASE_DIR, "Lora_dataset2", "test", "5_BongardStyle")

os.makedirs(TRAIN_DIR, exist_ok=True)
os.makedirs(TEST_DIR, exist_ok=True)

# =========================================================
# 参数
# =========================================================
TEST_NUM = 200  # 测试集数量
SEED = 42
TARGET_SIZE = (1024, 1024) # SDXL 最佳分辨率

random.seed(SEED)

# =========================================================
# 1. 收集所有数据对 (Image + Text)
# =========================================================
def collect_data_pairs():
    pairs = []
    
    # 遍历所有子文件夹
    for root, dirs, files in os.walk(SOURCE_ROOT):
        # 过滤掉不需要的文件夹
        if "Lora_dataset" in root or "Testdataset" in root:
            continue
            
        # 寻找 png 和 txt
        png_files = [f for f in files if f.lower().endswith('.png')]
        
        for png_file in png_files:
            base_name = os.path.splitext(png_file)[0]
            png_path = os.path.join(root, png_file)
            txt_path = os.path.join(root, f"{base_name}.txt")
            
            # 确保 txt 存在
            if os.path.exists(txt_path):
                pairs.append({
                    "id": base_name,
                    "png": png_path,
                    "txt": txt_path
                })
            else:
                print(f"⚠️ 跳过 {base_name}: 缺少对应的 .txt 文件")
                
    return pairs

# =========================================================
# 2. 处理单个文件 (Resize + Copy + Format Text)
# =========================================================
def process_and_save(pair, dst_dir):
    base_name = pair["id"]
    src_png = pair["png"]
    src_txt = pair["txt"]
    
    dst_png = os.path.join(dst_dir, f"{base_name}.png")
    dst_txt = os.path.join(dst_dir, f"{base_name}.txt")
    
    try:
        # --- 图像处理：确保 1024x1024 ---
        with Image.open(src_png) as img:
            # 转换为 RGB (防止 PNG 透明度问题)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 缩放并裁剪/填充到 1024x1024
            # 使用 Image.Resampling.LANCZOS 保证质量
            img_resized = img.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
            img_resized.save(dst_png)
            
        # --- 文本处理：格式化 Caption ---
        with open(src_txt, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        # 模板：BongardStyle + 描述 + 风格词
        # 注意：这里是 3x4 grid，因为是一整张图
        final_caption = f"BongardStyle, {content}."
        
        with open(dst_txt, 'w', encoding='utf-8') as f:
            f.write(final_caption)
            
        return True
        
    except Exception as e:
        print(f"❌ 处理失败 {base_name}: {e}")
        return False

# =========================================================
# 3. 主流程
# =========================================================
def main():
    print("🔍 正在扫描数据...")
    data_pairs = collect_data_pairs()
    
    if not data_pairs:
        print("❌ 未找到任何有效数据对 (png + txt)。")
        return
        
    print(f"📦 共找到 {len(data_pairs)} 组有效数据。")
    
    # 随机打乱
    random.shuffle(data_pairs)
    
    # 划分
    test_set = data_pairs[:TEST_NUM]
    train_set = data_pairs[TEST_NUM:]
    
    print(f"🧪 准备 Test 集: {len(test_set)} 组")
    print(f"🚂 准备 Train 集: {len(train_set)} 组")
    
    # 处理 Test
    print("\n📤 正在处理并保存 Test 集...")
    test_ok = 0
    for pair in test_set:
        if process_and_save(pair, TEST_DIR):
            test_ok += 1
    print(f"✅ Test 集完成: {test_ok}/{len(test_set)}")
    
    # 处理 Train
    print("\n📤 正在处理并保存 Train 集...")
    train_ok = 0
    for pair in train_set:
        if process_and_save(pair, TRAIN_DIR):
            train_ok += 1
    print(f"✅ Train 集完成: {train_ok}/{len(train_set)}")
    
    print(f"\n 全部完成！")
    print(f"📂 Train 路径: {TRAIN_DIR}")
    print(f"📂 Test  路径: {TEST_DIR}")

if __name__ == "__main__":
    main()
