import os

def prepend_trigger_word(folder_path, trigger_word="BongardStyle"):
    """
    遍历文件夹内的所有 txt 文件，在内容最前面添加触发词
    """
    if not os.path.exists(folder_path):
        print(f"错误: 找不到路径 {folder_path}")
        return

    count = 0
    # 确保触发词后面跟着逗号和空格
    prefix = f"{trigger_word}, "

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            
            try:
                # 1. 读取原始内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()

                # 2. 检查是否已经加过了，避免重复运行脚本导致叠加
                if content.startswith(trigger_word):
                    print(f"跳过: {filename} (已包含触发词)")
                    continue

                # 3. 写入新内容 (触发词 + 原内容)
                new_content = prefix + content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                count += 1
                print(f"成功更新: {filename}")
            
            except Exception as e:
                print(f"处理 {filename} 时出错: {e}")

    print(f"\n任务完成！共更新了 {count} 个标签文件。")

# --- 你的文件夹路径 ---
path = r'C:\Users\Lenovo\OneDrive\文档\GitHub\FYP-atfer-modifcation\fyp\Kohya_new_dataset\5_BongardStyle'

# 执行操作
prepend_trigger_word(path)