#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from github_webhook import Webhook
from flask import Flask
import json
import github
import os
import re

import logging
import logging.handlers

LOG_FILE = 'webhook.log'
MAX_LOG_BYTES = 1024 * 1024
MAX_WORKING = 3
LOG_LEVEL = os.getenv('LOG_LEVEL',  str(logging.INFO))
TOKEN = os.getenv('GITHUB_TOKEN', "")
CMD_LIST = ["/accept", "/pushed", "/merged"]
ADMIN_LIST = "@fleeto, @rootsongjc"

handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=MAX_LOG_BYTES, backupCount=50)
fmt = '%(asctime)s - [%(levelname)s] - %(filename)s:%(lineno)s - %(message)s'

formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(int(LOG_LEVEL))

app = Flask(__name__)
webhook = Webhook(app)


def get_cmd(body):
    cmd = body.strip().lower()
    if cmd in CMD_LIST:
        return cmd[1:]
    else:
        return False


def get_labels(issue):
    label_list = issue.get_labels()
    name_list = []
    for label_obj in label_list:
        name_list.append(label_obj.name)
    return name_list


def get_assignees(issue):
    assignees = issue.assignees
    name_list = []
    for assignee in assignees:
        name_list.append(assignee.login)
    return name_list


def get_issue_by_assignee(repo, login, flag):
    issue_list = repo.get_issues(assignee=login, labels=[repo.get_label(flag)])
    count = 0
    for issue in issue_list:
        count += 1
        if count >= MAX_WORKING:
            break
    return count < MAX_WORKING


def log_incoming_comment(data):
    line = "User: {} Issue: {} Comment: {}"
    content = line.format(
        data["repository"]["owner"]["login"],
        data["issue"]["number"],
        data["comment"]["body"]
    )
    logger.info(line)


@app.route("/")
def hello_world():
    return "Hello, World!"


@webhook.hook("issues")
def on_issues(data):
    action = data["action"]
    if action != "opened":
        return
    client = github.Github(TOKEN)
    repo_obj = client.get_repo(data["repository"]["id"])
    issue_obj = repo_obj.get_issue(data["issue"]["number"])
    issue_obj.add_to_labels("welcome")


@webhook.hook("issue_comment")
def on_issue_comment(data):
    log_incoming_comment(data)
    # 检查命令
    cmd = get_cmd(data["comment"]["body"])
    if not cmd:
        logging.info("No availible command found in the issue")
        return
    client = github.Github(TOKEN)
    owner_login = data["repository"]["owner"]["login"]
    repo_obj = client.get_repo(data["repository"]["id"])
    creater_obj = client.get_user(data["sender"]["login"])
    issue_obj = repo_obj.get_issue(data["issue"]["number"])
    if not repo_obj.has_in_assignees(creater_obj):
        logging.info("The author isn't in the list of assignees")
        return
    label_name_list = get_labels(issue_obj)
    assignee_login_list = get_assignees(issue_obj)
    logging.info(
        "Current assignees: {}".format(",".join(assignee_login_list))
    )
    logging.info(
        "Current Labels: {}".format(",".join(label_name_list))
    )
    assigned = len(issue_obj.assignees) > 0
    if (cmd == "accept"):
        if (assigned) or (not ("pending" in label_name_list)):
            logging.info("The issue had been assigned.")
            return
        if not get_issue_by_assignee(repo_obj, data["sender"]["login"], "translating"):
            body = "@{}: There are too many issues in your queue. {}".format(
                data["sender"]["login"], ADMIN_LIST)
            issue_obj.create_comment(body)
            return
        issue_obj.add_to_assignees(creater_obj)
        issue_obj.remove_from_labels("pending")
        issue_obj.add_to_labels("translating")
        return

    if (cmd == "pushed"):
        if (not ("translating") in label_name_list) or not assigned:
            logging.info("Can't be pushed.")
            return
        if (not data["sender"]["login"] in assignee_login_list):
            logging.info("You are not member of the assignees")
            return
        issue_obj.remove_from_labels("translating")
        issue_obj.add_to_labels("pushed")

    if (cmd == "merged"):
        if (not ("pushed" in label_name_list)) or not assigned:
            logging.info("Can't be merged.")
            return
        if (not data["sender"]["login"] in assignee_login_list):
            logging.info("You are not member of the assignees")
            return
        issue_obj.remove_from_labels("pushed")
        issue_obj.add_to_labels("finished")
        issue_obj.edit(state="closed")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
