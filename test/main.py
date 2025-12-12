from bs4 import BeautifulSoup
import requests
import time
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SECRET_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 一覧ページ（ローカル保存したHTML）
file_path = r"C:\Users\mkawa\myproject\scraping_cw\jobs.html"

with open(file_path, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

jobs = soup.select("div._root_b2jur_2")
print("案件数:", len(jobs))

def extract_price(job):
    # 金額ボックスの div を探す（class 名の一部一致で検索）
    price_div = job.find("div", class_=lambda x: x and "_paymentBox" in x)
    if not price_div:
        return ""

    # 固定報酬・時給などのラベル
    label_tag = price_div.find("span", class_=lambda x: x and "paymentLabelPc" in x)
    label = label_tag.get_text(strip=True) if label_tag else ""

    # 金額
    prices = price_div.find_all("span", class_=lambda x: x and "amountValuePc" in x)

    if len(prices) == 2:
        p1 = prices[0].get_text(strip=True)
        p2 = prices[1].get_text(strip=True)
        return f"{label}: {p1}〜{p2}円"

    if len(prices) == 1:
        p1 = prices[0].get_text(strip=True)
        return f"{label}: {p1}円"

    return ""

# 🔹 詳細ページから「仕事内容本文」をスクレイピングする関数
def scrape_detail_page(url: str) -> dict:
    """案件の詳細ページから本文・企業名・予算・日付をまとめて取得する"""

    if not url:
        # URL が空なら空データを返す
        return {
            "description": "",
            "employer": "",
            "budget": "",
            "posted_date": "",
            "start_date": "",
            "end_date": "",
        }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[WARN] 詳細ページ取得失敗: {url} ({e})")
        return {
            "description": "",
            "employer": "",
            "budget": "",
            "posted_date": "",
            "start_date": "",
            "end_date": "",
        }

    detail_soup = BeautifulSoup(resp.text, "html.parser")

    # ① 本文（td.confirm_outside_link 内のテキスト）
    desc_td = detail_soup.select_one("td.confirm_outside_link")
    if desc_td:
        description = desc_td.get_text(strip=True, separator="\n")
    else:
        description = ""

    # ② 企業名（依頼者名）
    employer_tag = detail_soup.select_one("a.display_link_none")
    employer = employer_tag.get_text(strip=True) if employer_tag else ""

    # ③ 予算（固定報酬制の金額レンジ）
    budget_tag = detail_soup.select_one("div.fixed_price_budget")
    budget = budget_tag.get_text(strip=True) if budget_tag else ""

    # ④ 掲載日・開始日・終了日
    posted_date = ""
    start_date = ""
    end_date = ""

    # 「詳細情報」のテーブルから日付の行を取る想定
    detail_table = detail_soup.select_one("section.cw-section.detail_information table.job_offer_detail_table")
    if detail_table:
        # 2行目（インデックス1）の <td> を想定
        date_tds = detail_table.select("tbody tr:nth-of-type(2) td")
        if len(date_tds) >= 3:
            posted_date = date_tds[0].get_text(strip=True)
            start_date = date_tds[1].get_text(strip=True)
            end_date = date_tds[2].get_text(strip=True)

    return {
        "description": description,
        "employer": employer,
        "budget": budget,
        "posted_date": posted_date,
        "start_date": start_date,
        "end_date": end_date,
    }

def save_to_supabase(data: dict):
    """辞書データを Supabase cw_jobs テーブルに保存する"""

    # job_id は URL の末尾の数字を取得
    job_id = data["url"].rstrip("/").split("/")[-1]

    row = {
        "job_id": job_id,
        "title": data["title"],
        "url": data["url"],
        "category": data["category"],
        "price": data["price"],
        "employer": data["employer"],
        "budget_detail": data["budget_detail"],
        "posted_date": data["posted_date"],
        "start_date": data["start_date"],
        "end_date": data["end_date"],
        "description": data["description"],
    }

    # ★ 既存チェックをして upsert する（重複防止）
    supabase.table("cw_jobs").upsert(row).execute()

# 🔄 一覧の各案件をループ
for idx, job in enumerate(jobs, start=1):

    # タイトル
    title_a = job.select_one("h3 a")
    title = title_a.get_text(strip=True) if title_a else ""
    url = title_a["href"] if title_a else ""

    # カテゴリ（aタグ）
    category_div = job.select_one("div._jobCategoryVue_b2jur_52")
    if category_div:
        category_a = category_div.find("a")
        category = category_a.get_text(strip=True) if category_a else ""
    else:
        category = ""

    # 金額
    price = extract_price(job)

    # ★ 詳細ページから本文取得
    detail = scrape_detail_page(url)
    description = detail["description"]
    employer = detail["employer"]
    budget_detail = detail["budget"]
    posted_date = detail["posted_date"]
    start_date = detail["start_date"]
    end_date = detail["end_date"]

    print(f"\n=== {idx} 件目 ===")
    print("タイトル:", title)
    print("URL:", url)
    print("カテゴリ:", category)
    print("金額:", price)
    print("依頼者:", employer)
    print("詳細予算:", budget_detail)
    print("掲載日:", posted_date)
    print("開始日:", start_date)
    print("終了日:", end_date)

    # 本文は長いので先頭だけプレビュー
    if description:
        preview = description.replace("\n", " ")
        if len(preview) > 120:
            preview = preview[:120] + "..."
        print("本文抜粋:", preview)
    else:
        print("本文抜粋: 取得できませんでした")

    # 相手サイトへの負荷を下げるため、少し待つ（1秒）
    time.sleep(1)

    # ★ DB に保存
    save_to_supabase({
    "title": title,
    "url": url,
    "category": category,
    "price": price,
    "employer": employer,
    "budget_detail": budget_detail,
    "posted_date": posted_date,
    "start_date": start_date,
    "end_date": end_date,
    "description": description,  # ⭐全文
})


