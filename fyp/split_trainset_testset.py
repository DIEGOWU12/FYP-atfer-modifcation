import os
import random
import shutil

# =========================================================
# BASE DIR（跨电脑）
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SOURCE_DIR = os.path.join(BASE_DIR, "Kohya_new_dataset", "5_BongardStyle")

TRAIN_DIR = os.path.join(BASE_DIR, "Kohya_new_dataset", "train", "5_BongardStyle")
TEST_DIR  = os.path.join(BASE_DIR, "Kohya_new_dataset", "test", "5_BongardStyle")

os.makedirs(TRAIN_DIR, exist_ok=True)
os.makedirs(TEST_DIR, exist_ok=True)

# =========================================================
# 参数
# =========================================================
TEST_NUM = 300
SEED = 42

random.seed(SEED)


# =========================================================
# 1. 获取所有 BP id（以 _left.png 为 anchor）
# =========================================================
def get_bp_list():
    bp_set = set()

    for f in os.listdir(SOURCE_DIR):
        if f.endswith("_left.png"):
            bp_id = f.replace("_left.png", "")
            bp_set.add(bp_id)

    return list(bp_set)


# =========================================================
# 2. split dataset
# =========================================================
def split_dataset():

    if not os.path.exists(SOURCE_DIR):
        print(f"❌ 找不到数据集: {SOURCE_DIR}")
        return

    bp_list = get_bp_list()

    print(f"📦 total BP samples: {len(bp_list)}")

    random.shuffle(bp_list)

    split_idx = min(TEST_NUM, len(bp_list))

    test_bp = set(bp_list[:split_idx])
    train_bp = set(bp_list[split_idx:])

    print(f"🧪 test BP: {len(test_bp)}")
    print(f"🚂 train BP: {len(train_bp)}")

    # =====================================================
    # copy function
    # =====================================================
    def copy_bp(bp_set, dst_folder):

        for bp in bp_set:

            for suffix in ["_left.png", "_right.png", "_left.txt", "_right.txt"]:

                src = os.path.join(SOURCE_DIR, bp + suffix)
                dst = os.path.join(dst_folder, bp + suffix)

                if os.path.exists(src):
                    shutil.copy2(src, dst)

    # =====================================================
    # copy test
    # =====================================================
    print("\n📤 copying test set...")
    copy_bp(test_bp, TEST_DIR)

    # =====================================================
    # copy train
    # =====================================================
    print("\n📤 copying train set...")
    copy_bp(train_bp, TRAIN_DIR)

    # =====================================================
    # done
    # =====================================================
    print("\n✅ Done!")
    print(f"📁 train -> {TRAIN_DIR}")
    print(f"📁 test  -> {TEST_DIR}")


# =========================================================
# main
# =========================================================
if __name__ == "__main__":
    split_dataset()