import os
import shutil

src1 = "bongard_augmented_dataset_v3"
src2 = "Bongard_Dataset_v3_new_struct"

target = "Kohya_train_data/6_BongardStyle"
#4
def merge_folder(src):

    if not os.path.exists(src):
        print(f"❌ not found: {src}")
        return

    for bp_folder in os.listdir(src):

        src_bp_path = os.path.join(src, bp_folder)

        if not os.path.isdir(src_bp_path):
            continue

        dst_bp_path = os.path.join(target, bp_folder)

        os.makedirs(dst_bp_path, exist_ok=True)

        for file in os.listdir(src_bp_path):

            src_file = os.path.join(src_bp_path, file)
            dst_file = os.path.join(dst_bp_path, file)

            # 如果文件已存在 → 跳过（防止覆盖）
            if os.path.exists(dst_file):
                print(f"⚠ skip existing: {dst_file}")
                continue

            shutil.copy2(src_file, dst_file)

        print(f"✅ merged: {bp_folder}")


if __name__ == "__main__":

    os.makedirs(target, exist_ok=True)

    print("🚀 merging dataset...")

    merge_folder(src1)
    merge_folder(src2)

    print("\n🎉 DONE! merged dataset saved in:", target)