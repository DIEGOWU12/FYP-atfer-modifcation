import os
import random
import shutil
from PIL import Image

# =========================================================
# 路径配置
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 修改为你现在的 256x256 数据源路径
SOURCE_ROOT = os.path.join(BASE_DIR, "FinalKohya_data", "5_BongardStyle")

# 目标目录
TRAIN_DIR = os.path.join(BASE_DIR, "FinalLora_dataset", "train", "5_BongardStyle")
TEST_DIR  = os.path.join(BASE_DIR, "FinalLora_dataset", "test", "5_BongardStyle")

os.makedirs(TRAIN_DIR, exist_ok=True)
os.makedirs(TEST_DIR, exist_ok=True)

# =========================================================
# 参数
# =========================================================
TEST_NUM = 200  # 测试集数量
SEED = 42
# 注意：这里不再定义 TARGET_SIZE，因为我们直接用原图尺寸

random.seed(SEED)

# =========================================================
# 1. 收集所有数据对 (Image + Text)
# =========================================================
def collect_data_pairs():
    pairs = []
    
    # 直接在源目录下寻找 png 和 txt
    # 假设你的数据都在 5_BongardStyle 这一级目录下
    files = os.listdir(SOURCE_ROOT)
    png_files = [f for f in files if f.lower().endswith('.png')]
    
    for png_file in png_files:
        base_name = os.path.splitext(png_file)[0]
        png_path = os.path.join(SOURCE_ROOT, png_file)
        txt_path = os.path.join(SOURCE_ROOT, f"{base_name}.txt")
        
        if os.path.exists(txt_path):
            pairs.append({
                "id": base_name,
                "png": png_path,
                "txt": txt_path
            })
    return pairs

# =========================================================
# 2. 处理并移动文件 (保持 256x256)
# =========================================================
def process_and_save(pair, dst_dir):
    base_name = pair["id"]
    src_png = pair["png"]
    src_txt = pair["txt"]
    
    dst_png = os.path.join(dst_dir, f"{base_name}.png")
    dst_txt = os.path.join(dst_dir, f"{base_name}.txt")
    
    try:
        # --- 图像处理：仅确保 RGB 模式 ---
        with Image.open(src_png) as img:
            # 转换为 RGB 模式（去掉透明度通道）
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 直接保存，不再进行 resize
            # 这样会保留你之前 Combiner 处理好的 256x256 原始像素
            img.save(dst_png)
            
        # --- 文本处理：格式化 Caption ---
        with open(src_txt, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        # 你的触发词：BongardStyle
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
    print(f"🔍 正在扫描: {SOURCE_ROOT}")
    data_pairs = collect_data_pairs()
    
    if not data_pairs:
        print("❌ 未找到有效数据对。请检查路径。")
        return
        
    print(f"📦 共找到 {len(data_pairs)} 组有效数据。")
    
    random.shuffle(data_pairs)
    
    test_set = data_pairs[:TEST_NUM]
    train_set = data_pairs[TEST_NUM:]
    
    # 实际执行
    for dataset, label, folder in [(test_set, "Test", TEST_DIR), (train_set, "Train", TRAIN_DIR)]:
        print(f"\n📤 正在保存 {label} 集 ({len(dataset)} 组)...")
        ok_count = 0
        for pair in dataset:
            if process_and_save(pair, folder):
                ok_count += 1
        print(f"✅ {label} 集完成: {ok_count}/{len(dataset)}")
    
    print(f"\n🎉 全部完成！")
    print(f"📂 训练数据已准备在: {TRAIN_DIR}")

if __name__ == "__main__":
    main()