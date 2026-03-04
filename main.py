import requests
import os

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["DATABASE_ID"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28"
}

query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

res = requests.post(query_url, headers=headers)
data = res.json()

page_id = data["results"][0]["id"]

block_url = f"https://api.notion.com/v1/blocks/{page_id}/children"

res = requests.get(block_url, headers=headers)
blocks = res.json()["results"]

message = "📌 오늘의 팀 회고\n\n"

for block in blocks:

    if block["type"] == "paragraph":

        text = block["paragraph"]["rich_text"]

        if text:
            message += text[0]["plain_text"] + "\n"

requests.post(WEBHOOK_URL, json={"text": message})