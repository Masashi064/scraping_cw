CrowdWorks Jobs Scraper → Supabase Saver

CrowdWorks（クラウドワークス）の案件一覧ページを取得し、各案件の詳細ページから本文・依頼者名・予算・日付などを抽出して Supabase（cw_jobs テーブル）へ upsert 保存するスクリプトです。

main

できること

Selenium（Headless Chrome）で CrowdWorks の案件一覧ページを開き、JS描画後のHTMLを取得

main

一覧から以下を抽出

タイトル / URL / カテゴリ / 金額（固定報酬・時給など）

main

各案件の詳細ページを requests + BeautifulSoup で取得し、以下を抽出

main

仕事内容本文（td.confirm_outside_link）

依頼者（a.display_link_none）

予算詳細（div.fixed_price_budget）

掲載日 / 開始日 / 終了日（詳細情報テーブルの想定行から）

main

job_id（URL末尾）をキーに cw_jobs へ upsert（重複防止） 保存

main

注意（必ず読んでください）

本スクリプトはWebスクレイピングを行います。対象サイトの利用規約・robots.txt・法令に従い、過度なアクセスにならないよう注意してください。

コード内では負荷低減のために time.sleep(1.5) を入れていますが、運用時はさらに緩める・実行頻度を下げるなど配慮推奨です。

main

動作要件

Python 3.10+ 推奨

Google Chrome（または Chromium）

必要ライブラリ

requests

beautifulsoup4

python-dotenv

supabase（Python client）

selenium

webdriver-manager

セットアップ
1) 依存関係インストール
pip install requests beautifulsoup4 python-dotenv supabase selenium webdriver-manager

2) .env を作成

プロジェクト直下に .env を作り、以下を設定してください。

main

例（.env.example として保存推奨）：

SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SECRET_KEY=your_service_role_or_secret_key


SUPABASE_SECRET_KEY は強い権限を持つ場合があるので、GitHubへ絶対にコミットしないでください。

3) Supabase テーブルを用意

スクリプトは cw_jobs テーブルへ次のカラムを保存します。

main

job_id（URL末尾のID、on_conflict対象）

title

url

category

price

employer

budget_detail

posted_date

start_date

end_date

description

最低限、job_id をユニーク（またはPK）にしてください。

実行方法
python main.py


実行すると、一覧ページを開いて案件数を表示し、各案件を順に処理してSupabaseへ保存します。

main

仕組み（ざっくり）

Seleniumで https://crowdworks.jp/public/jobs を開く

4秒待機してHTML解析

案件カード（div._root_b2jur_2）をループ

詳細ページは requests.get() で取得して必要項目を抽出

job_id をキーに cw_jobs に upsert 保存

main

よくある問題 / 対処

案件数が0件になる

CrowdWorks側のDOM構造（class名）が変わった可能性があります。セレクタを見直してください。

Chrome/Driver関連エラー

Chromeがインストールされているか確認

企業端末などでDriverダウンロードがブロックされる場合があります（ネットワーク制限）

詳細ページの取得が失敗する

429（レート制限）や一時的なブロックの可能性 → 待ち時間を長くする／頻度を下げる

セキュリティ

.env（Supabaseキー等）はコミットしない

必要なら .env.example を置き、環境変数名だけ共有する

ライセンス

（任意）あなたの方針に合わせて追記してください（例：個人利用のみ、社内利用のみ、MITなど）