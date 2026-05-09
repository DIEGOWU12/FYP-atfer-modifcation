import os
import dashscope
from dashscope import MultiModalConversation

# 1. 在这里粘贴你从控制台复制的 Key（保留引号，其他不要动）
RAW_KEY = "sk-7372c21b66f54465b4486781a688b80e"

# 2. 自动清洗：去首尾空格、去换行、剔除所有非ASCII隐藏字符
API_KEY = RAW_KEY.strip().replace('\n', '').replace('\r', '')
API_KEY = ''.join(c for c in API_KEY if ord(c) < 128)  # 彻底过滤零宽空格/乱码

# 3. 基础格式校验
if not API_KEY.startswith('sk-') or len(API_KEY) < 30:
    print("❌ Key 格式异常！请重新复制。")
    print(f"📏 当前长度: {len(API_KEY)} | 🔤 前5位: {API_KEY[:5]}")
    exit()

# 4. 强制覆盖 SDK 配置
os.environ["DASHSCOPE_API_KEY"] = API_KEY
dashscope.api_key = API_KEY

print("✅ Key 格式检查通过，正在发起测试请求...")
resp = MultiModalConversation.call(
    model="qwen-vl-plus",
    messages=[{"role": "user", "content": [{"text": "hi"}]}]
)

if resp.status_code == 200:
    print("🎉 成功！你的 Key 完全正常，可以直接跑批量脚本了。")
else:
    print(f"⚠️ 依然返回: {resp.status_code} | {resp.message}")
    print("👉 请继续执行第二步排查。")
