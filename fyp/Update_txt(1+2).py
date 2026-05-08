import os
import re

dataset_path = "Kohya_train_data/6_BongardStyle"


def extract_left_logic(text):
    pattern = r"Left Side.*?features a '(.*?)' logic"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else None


def build_full_prompt(left_logic, right_logic):
    return (
        "BongardStyle, a complex black and white geometric 3x4 matrix illustration, "
        "12 distinct panels in two separate 3x2 grids, separated by a distinct central vertical line, white background. "
        f"Left Side (6 panels): each panel features a '{left_logic}' logic, showing geometric shapes with {left_logic} arrangement. "
        f"Right Side (6 panels): each panel features a '{right_logic}' logic, showing geometric shapes with {right_logic} arrangement. "
        "Clear visual logic, stark contrast, minimalist geometric diagram."
    )

def rename_solution_files():
    print("\n📦 Renaming solution.txt files...")

    for root, dirs, files in os.walk(dataset_path):

        folder_name = os.path.basename(root)

        if not folder_name.startswith("BP"):
            continue

        old_path = os.path.join(root, "solution.txt")
        new_path = os.path.join(root, f"{folder_name}.txt")

        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            print(f"✅ {old_path} → {new_path}")
def process_text(content):
    content = content.strip()

    # =========================
    # Case 1: vs format
    # =========================
    if "vs" in content.lower():
        parts = re.split(r'\s+[vV][sS]\.?\s+', content)
        if len(parts) == 2:
            left = parts[0].strip().rstrip(".")
            right = parts[1].strip().rstrip(".")

            return build_full_prompt(left, right)

    # =========================
    # Case 2: not so format
    # =========================
    left_logic = extract_left_logic(content)
    if not left_logic:
        return None

    def repl_logic(m):
        return f"'not so({left_logic})' logic"

    def repl_arr(m):
        return f"not so({left_logic}) arrangement"

    content = re.sub(r"'not so'\s+logic", repl_logic, content)
    content = re.sub(r"not so\s+arrangement", repl_arr, content)

    return content


def process_dataset():
    count = 0

    if not os.path.exists(dataset_path):
        print(f"❌ 路径错误: {dataset_path}")
        return

    print(f"📂 scanning: {dataset_path}")

    # 递归扫描
    for root, dirs, files in os.walk(dataset_path):

        for file in files:

            if not file.lower().endswith(".txt"):
                continue

            file_path = os.path.join(root, file)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                new_content = process_text(content)

                if not new_content:
                    continue

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                print(f"✅ updated: {file_path}")
                count += 1

            except Exception as e:
                print(f"❌ error {file_path}: {e}")

    print(f"\n🚀 done: {count} files updated")


if __name__ == "__main__":
    rename_solution_files()
    process_dataset()