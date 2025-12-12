import os
import json
from supabase import create_client
from dotenv import load_dotenv

# .env を読み込む
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SECRET_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL または SUPABASE_SECRET_KEY が読み込めませんでした。.env を確認してください。")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def export_json():
    # 必要なカラムだけ選んでもOK（今は全部）
    res = supabase.table("cw_jobs").select("*").execute()
    data = res.data

    print(f"レコード数: {len(data)}")

    # 同じフォルダに JSON を保存
    out_path = "cw_jobs.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ {out_path} に書き出しました")

if __name__ == "__main__":
    export_json()
