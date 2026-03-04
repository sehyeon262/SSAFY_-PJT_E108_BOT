import requests
import os

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["DATABASE_ID"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28"
}

TEAM_MEMBERS = [
    "하정호",
    "박서린",
    "임건빈",
    "황인후",
    "심다인",
    "김세현"
]


def get_children(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    res = requests.get(url, headers=headers)
    return res.json()["results"]


# 체크된 회고 조회
query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

query_data = {
    "filter": {
        "property": "Mattermost 알림",
        "checkbox": {
            "equals": True
        }
    }
}

res = requests.post(query_url, headers=headers, json=query_data)
data = res.json()

if not data["results"]:
    print("보낼 회고 없음")
    exit()

page = data["results"][0]
page_id = page["id"]

blocks = get_children(page_id)

message = "## 📋 오늘의 팀 회고\n\n"

written_members = []


for block in blocks:

    if block["type"] == "column_list":

        columns = get_children(block["id"])

        for column in columns:

            column_blocks = get_children(column["id"])

            for item in column_blocks:

                if item["type"] == "callout":

                    callout = item["callout"]["rich_text"]

                    if callout:
                        name = callout[0]["plain_text"]
                        written_members.append(name)
                        message += f"\n### 🙂 {name}\n"

                    children = get_children(item["id"])

                    for child in children:

                        # KEEP / PROBLEM / TRY 제목
                        if child["type"] == "paragraph":

                            text = child["paragraph"]["rich_text"]

                            if not text:
                                continue

                            content = "".join([t["plain_text"] for t in text])

                            if "KEEP" in content.upper():
                                message += "\n##### Keep\n"

                            elif "PROBLEM" in content.upper():
                                message += "\n##### Problem\n"

                            elif "TRY" in content.upper():
                                message += "\n##### Try\n"

                        # 실제 내용
                        elif child["type"] == "bulleted_list_item":

                            text = child["bulleted_list_item"]["rich_text"]

                            if text:
                                content = "".join([t["plain_text"] for t in text])
                                message += f"- {content}\n"

                    message += "\n\n---\n\n"



# 회고 작성 현황
written_count = len(written_members)
total_count = len(TEAM_MEMBERS)

message += f"\n\n### 📊 회고 작성 현황\n"
message += f"- **작성: {written_count}명**\n"
message += f"- **미작성: {total_count - written_count}명**\n"


# 회고 미작성 체크
not_written = [m for m in TEAM_MEMBERS if m not in written_members]

if not_written:
    message += "\n⚠ 미작성자\n"
    for m in not_written:
        message += f"- {m}\n"


# Mattermost 전송
requests.post(WEBHOOK_URL, json={"text": message})


# 알림 체크 해제
update_url = f"https://api.notion.com/v1/pages/{page_id}"

update_data = {
    "properties": {
        "Mattermost 알림": {
            "checkbox": False
        }
    }
}

requests.patch(update_url, headers=headers, json=update_data)

print("전송 완료")