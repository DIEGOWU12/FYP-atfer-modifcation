from pytorch_fid import fid_score

def calculate_my_fid():
    real_path = "data/real"
    fake_path = "generated_results" # 你之前生图代码保存的文件夹
    
    print("正在计算 FID 分数，请稍候...")
    
    # dims=2048 是 InceptionV3 的标准特征维度
    score = fid_score.calculate_fid_given_paths(
        [real_path, fake_path],
        batch_size=50,
        device='cuda', # 如果没显卡改成 'cpu'
        dims=2048
    )
    
    print(f"==============================")
    print(f"最终 FID 得分: {score}")
    print(f"==============================")
    return score

if __name__ == "__main__":
    # 在你跑完批量生图逻辑后调用
    calculate_my_fid()