#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from github_webhook import Webhook
from flask import Flask
import json
import github
import os
import re


MAX_WORKING = 3
TOKEN = os.environ["GITHUB_TOKEN"]
CMD_LIST = ["/accept", "/pushed", "/merged"]

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


app = Flask(__name__)
webhook = Webhook(app)


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
    #检查命令
    cmd = get_cmd(data["comment"]["body"])
    if not cmd:
        print("Not my style.")
        return
    client = github.Github(TOKEN)
    owner_login = data["repository"]["owner"]["login"]
    repo_obj = client.get_repo(data["repository"]["id"])
    creater_obj = client.get_user(data["sender"]["login"])
    issue_obj = repo_obj.get_issue(data["issue"]["number"])
    if not repo_obj.has_in_assignees(creater_obj):
        print("Not in member list")
        return
    label_name_list = get_labels(issue_obj)
    assignee_login_list = get_assignees(issue_obj)
    assigned = len(issue_obj.assignees) > 0
    if (cmd == "accept"):
        if (assigned) or (not ("pending" in label_name_list)):
            print("The issue had been assigned.")
            return
        if not get_issue_by_assignee(repo_obj, data["sender"]["login"], "translating"):
            print("You have accept too many issues.")
            return            
        issue_obj.add_to_assignees(creater_obj)
        issue_obj.remove_from_labels("pending")
        issue_obj.add_to_labels("translating")
        return

    if (cmd == "pushed"):
        if (not ("translating") in label_name_list) or not assigned:
            print("Can't be pushed.")
            return
        if (not data["sender"]["login"] in assignee_login_list):
            print("You are not member of the assignees")
            return
        issue_obj.remove_from_labels("translating")
        issue_obj.add_to_labels("pushed")

    if (cmd == "merged"):
        if (not ("pushed") in label_name_list) or not assigned:
            print("Can't be merged.")
            return
        if (not data["sender"]["login"] in assignee_login_list):
            print("You are not member of the assignees")
            return
        issue_obj.remove_from_labels("pushed")
        issue_obj.add_to_labels("finished")
        issue_obj.edit(state="closed")        


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
