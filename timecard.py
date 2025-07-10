import streamlit as st
import gspread
from datetime import datetime
import pandas as pd
from google.oauth2.service_account import Credentials
import json

#環境変数取得
SHEET_KEY = st.secrets["sheet_key"]

#認証
SCOPE = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
service_account_info = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(service_account_info)
gc = gspread.authorize(creds)

#スプレッドシート設定
sh = gc.open_by_key(SHEET_KEY)

#名前一覧取得
names_sheet = sh.worksheet("names")
names = names_sheet.col_values(1) # A列の名前

#名前選択
selected_name = st.selectbox("🌟スタッフ名を選択", names)

#出勤ボタン
if st.button("出勤"):
  target_sheet = sh.worksheet(selected_name)
  now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  target_sheet.append_row([selected_name, now, "", ""])
  st.success(f"{selected_name}さんの出勤を記録しました！")

#退勤ボタン
if st.button("退勤"):
  target_sheet = sh.worksheet(selected_name)
  records = target_sheet.get_all_values()
  df = pd.DataFrame(records[1:],columns=records[0])

  #最後の未退勤レコードを探す
  target = df[(df['名前'] == selected_name) & (df['退勤時刻'] == "")]
  if not target.empty:
    idx = target.index[-1] + 2 #スプシは1始まり＋ヘッダー
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_time = datetime.strptime(df.loc[idx - 2, '出勤時刻'], "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
    work_duration = round((end_time - start_time).total_seconds() / 3600, 2)

    target_sheet.update(f'B{idx}', now)
    target_sheet.update(f'D{idx}', str(work_duration))
    st.success(f"{selected_name}さんの退勤を記録しました！\n勤務時間:{work_duration}時間")
  else:
    st.warning(f"{selected_name}さんの出勤記録が見つかりません。")