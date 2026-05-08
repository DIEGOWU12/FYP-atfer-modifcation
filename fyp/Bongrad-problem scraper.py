import requests
from bs4 import BeautifulSoup
import os
import csv
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from threading import Lock

# ==========================================================
# 1. 参数设置
# ==========================================================
BASE_URL = "https://oebp.org/BP"

START_ID = 1
END_ID = 5000
TARGET_COUNT = 1000

OUTPUT_DIR = "Bongard_Dataset_v3"

SOLUTION_FILE = os.path.join(OUTPUT_DIR, "solutions_and_images.csv")
REPORT_FILE = os.path.join(OUTPUT_DIR, "patterns_report.txt")

MAX_WORKERS = 7

success_count = 0
count_lock = Lock()
report_lock = Lock()

# ==========================================================
# 2. Session 设置
# ==========================================================
session = requests.Session()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

retry = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)

adapter = HTTPAdapter(max_retries=retry)

session.mount("https://", adapter)
session.mount("http://", adapter)

session.headers.update(HEADERS)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================================
# 3. 下载图片
# ==========================================================
def download_image(img_url, filename, bp_id):

    bp_dir = os.path.join(OUTPUT_DIR, f"BP{bp_id}")
    os.makedirs(bp_dir, exist_ok=True)

    image_path = os.path.join(bp_dir, filename)

    if os.path.exists(image_path):
        return os.path.join(f"BP{bp_id}", filename)

    try:
        r = session.get(img_url, timeout=10)

        if r.status_code == 200:
            with open(image_path, "wb") as f:
                f.write(r.content)

            return os.path.join(f"BP{bp_id}", filename)

    except Exception:
        pass

    return "download_failed"

# ==========================================================
# 4. 抓取函数
# ==========================================================
def fetch_problem(bp_id):

    url = f"{BASE_URL}{bp_id}"

    try:
        r = session.get(url, timeout=10)

        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")

        # ==================================================
        # images
        # ==================================================
        img_tags = soup.find_all(
            "img",
            src=lambda src: src and "/examples/" in src
        )

        img_count = len(img_tags)

        if img_count < 12:
            return None

        # ==================================================
        # report
        # ==================================================
        if img_count > 12:
            with report_lock:
                with open(REPORT_FILE, "a", encoding="utf-8") as rf:
                    rf.write(f"ID: BP{bp_id} | Total Images: {img_count}\n")

        # ==================================================
        # solution extraction
        # ==================================================
        solution_text = "No solution found"

        solution_tds = soup.find_all("td")

        for td in solution_tds:

            text = td.get_text(" ", strip=True)

            # 核心规则：必须包含 vs
            if "vs" not in text.lower():
                continue

            # 防止 BP 编号误命中
            if text.startswith("BP"):
                continue

            # 太长的排除（避免误抓说明段）
            if len(text) > 200:
                continue

            # 必须像一句 pattern（可选增强）
            if "." not in text:
                continue

            solution_text = text
            break
        print(f"🧠 BP{bp_id} solution: {solution_text}")
        # ==================================================
        # save solution.txt  ⭐⭐⭐
        # ==================================================
        bp_dir = os.path.join(OUTPUT_DIR, f"BP{bp_id}")
        os.makedirs(bp_dir, exist_ok=True)

        with open(os.path.join(bp_dir, "solution.txt"), "w", encoding="utf-8") as f:
            f.write(solution_text)

        # ==================================================
        # download images
        # ==================================================
        image_paths = []

        for img in img_tags:
            src = img["src"]
            img_url = urljoin("https://oebp.org", src)
            filename = os.path.basename(src)

            path = download_image(img_url, filename, bp_id)
            image_paths.append(path)

        print(f"✅ BP{bp_id} success ({img_count} images)")

        return {
            "BP_ID": f"BP{bp_id}",
            "solution": solution_text,
            "image_paths": image_paths
        }

    except Exception as e:
        print(f"❌ BP{bp_id} error: {e}")
        return None

# ==========================================================
# 5. 主程序
# ==========================================================
if __name__ == "__main__":

    with open(REPORT_FILE, "w", encoding="utf-8") as rf:
        rf.write("--- Bongard Problems with > 12 Images ---\n")

    print("🚀 Start crawling...")

    with open(SOLUTION_FILE, "w", newline="", encoding="utf-8") as f:

        fieldnames = ["BP_ID", "solution"] + [f"Image_{i+1}_path" for i in range(12)]

        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

            futures = {
                executor.submit(fetch_problem, i): i
                for i in range(START_ID, END_ID + 1)
            }

            for future in as_completed(futures):

                result = future.result()

                if result:

                    with count_lock:
                        if success_count >= TARGET_COUNT:
                            break
                        success_count += 1
                        current = success_count

                    row = {
                        "BP_ID": result["BP_ID"],
                        "solution": result["solution"]
                    }

                    for j in range(min(12, len(result["image_paths"]))):
                        row[f"Image_{j+1}_path"] = result["image_paths"][j]

                    writer.writerow(row)
                    f.flush()

                    print(f"📊 Collected {current}/{TARGET_COUNT}")

    print(f"\n🎉 Finished! Report saved in {REPORT_FILE}")