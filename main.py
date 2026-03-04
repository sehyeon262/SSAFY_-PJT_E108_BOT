import requests
import os

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["DATABASE_ID"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28"
}

# Database 조회
query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
res = requests.post(query_url, headers=headers)
data = res.json()

page_id = data["results"][0]["id"]

# 페이지 블록 가져오기
block_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
res = requests.get(block_url, headers=headers)
blocks = res.json()["results"]

message = "📋 오늘의 팀 회고\n\n"

current_person = None

for block in blocks:

    # 이름 (heading)
    if block["type"].startswith("heading"):

        text = block[block["type"]]["rich_text"]
        if text:
            current_person = text[0]["plain_text"]
            message += f"\n🙂 {current_person}\n"

    # 문단
    if block["type"] == "paragraph":

        text = block["paragraph"]["rich_text"]

        if text:
            content = text[0]["plain_text"]

            if "Keep" in content:
                message += "K\n"

            elif "Problem" in content:
                message += "P\n"

            elif "Try" in content:
                message += "T\n"

            else:
                message += f"- {content}\n"

# Mattermost 전송
requests.post(WEBHOOK_URL, json={"text": message})