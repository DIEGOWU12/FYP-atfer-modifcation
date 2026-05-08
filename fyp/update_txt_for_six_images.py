import os
import re

# =========================
# 相对路径基准（关键）
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 你的目标数据集路径（相对 BASE_DIR）
target_path = os.path.join(BASE_DIR, "Kohya_new_dataset", "5_BongardStyle")


def modify_bongard_prompts(folder_path):
    if not os.path.exists(folder_path):
        print(f"找不到路径: {folder_path}")
        return

    print(f"📂 scanning: {folder_path}")

    for filename in os.listdir(folder_path):

        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(folder_path, filename)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            # 提取 logic
            match = re.search(r"features a (.*?) logic", content, re.IGNORECASE)

            if match:
                extracted_logic = match.group(1).strip().strip("'").strip('"')
            else:
                extracted_logic = "filled in solid"

            # 新 prompt
            new_prompt = (
                f"Bongard style, one large composite image consisting of six individual images arranged in a 3x2 layout. "
                f"Each of the six images features a '{extracted_logic}' logic."
            )

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_prompt)

            print(f"✅ Updated: {filename}")

        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")


if __name__ == "__main__":
    modify_bongard_prompts(target_path)