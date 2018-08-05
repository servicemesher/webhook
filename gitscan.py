#!/usr/bin/env python3

import glob
import os
import subprocess

REPO = os.getenv("GITREPO")
LOG_CMD = ["git", "log", "-1", "--pretty=format:'%ad'", "--date=iso8601"]
HASH_CMD = ["git", "log", "-1", "--pretty=format:'%H'"]
DIFF_CMD = ["git", "diff", "HEAD"]

os.chdir(REPO)
en_list = glob.glob(os.path.join(
    "content/**", "*.md"), recursive=True)
en_list = [filename.replace("content/", "") for filename in en_list]
zh_list = glob.glob(os.path.join(
    "content_zh/**", "*.md"), recursive=True)
zh_list = [filename.replace("content_zh/", "") for filename in zh_list]
added = list(set(en_list) - set(zh_list))
tobe_del = list(set(zh_list) - set(en_list))
added.sort()
tobe_del.sort()

print("\n## New File\n")
for filename in added:
    print("- " + filename)

print("\n## Orphan File\n")
for filename in tobe_del:
    print("- " + filename)
#
# 

subprocess.check_call(["git", "pull"])

print("\n## Changed File\n\n|File|Changed Lines|\n|---|---|")

# check each file in 'content_zh'
zh_list = list(zh_list)
zh_list.sort()
for filename in zh_list:
    # filename = filename.replace(os.path.join(REPO, "content_zh/"), "")
    zh_filename = os.path.join("content_zh", filename)
    en_filename = os.path.join("content", filename)
    if not os.path.exists(en_filename):
        continue
    zh_last_commit_time = subprocess.check_output(LOG_CMD + [zh_filename]).decode("UTF-8")
    en_last_hash = subprocess.check_output(HASH_CMD + ["--before", zh_last_commit_time, en_filename]).decode("UTF-8").strip("'")
    diff_content = subprocess.check_output(DIFF_CMD + [en_last_hash, en_filename]).decode("UTF-8")

    if (len(diff_content) > 0):
        print("|{}|{}|".format(en_filename, len(diff_content.split("\n"))))
        
