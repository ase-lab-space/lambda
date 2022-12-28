import os
import json
from typing import Any
from urllib import request


def post(url: str, data: dict[str, Any], token: str) -> Any:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    req = request.Request(url, data=json.dumps(data).encode(), headers=headers)
    with request.urlopen(req) as res:
        body = json.load(res)
    return body


def validate_body(event: dict[str, Any]) -> bool:
    for field in ["name", "email", "status", "body"]:
        if not event.get(field):
            return False
    return True


def post_message(msg: str) -> bool:
    data = {
        "channel": "#0_form_notifications",
        "text": msg,
    }
    res = post(
        "https://slack.com/api/chat.postMessage",
        data=data,
        token=os.environ["CONTACT_FORM_NOTIFICATOR_ACCESS_TOKEN"],
    )
    if not res["ok"]:
        return False

    return True


def build_message(name: str, email: str, status: str, body: str) -> str:
    return f"""<!channel>
:raising_hand: ASE-Lab. Contactフォームからご連絡をいただきました :raising_hand:

*お名前*
{name}

*メールアドレス*
{email}

*ご職業*
{status}

*本文*
{body}
"""


def lambda_handler(event: dict[str, Any], _context):
    if event["httpMethod"] not in ["POST"]:
        return {
            "statusCode": 403,
            "body": "",
        }

    if not event["body"]:
        return {
            "statusCode": 400,
            "body": "invalid body",
        }
    body = json.loads(event["body"])
    if not validate_body(body):
        return {
            "statusCode": 400,
            "body": "invalid body",
        }
    msg = build_message(
        name=body["name"],
        email=body["email"],
        status=body["status"],
        body=body["body"],
    )
    if not post_message(msg):
        return {
            "statusCode": 400,
            "body": "post failed",
        }

    return {
        "statusCode": 200,
        "body": "success",
    }
