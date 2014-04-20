#!/usr/bin/env python

import sh
import glob
import os
import re

github_user="alfredperlstein"
github_repo="freebsd"

gitdir="~/git/freebsd.mirror.git"
git_mirror_dir = os.path.expandvars(os.path.expanduser(gitdir))

gnats_email="alfred@freebsd.org"
cc_email="alfred@freebsd.org"

pr_category="misc"

pr_template = """To: $pr_to
From: $pr_from
Reply-To: $pr_reply_to
Cc: $pr_cc
X-send-pr-version: 3.114
X-GNATS-Notify: 


>Submitter-Id:	current-users
>Originator:	$originator
>Organization:	github
>Confidential:	no
>Synopsis:	[patch] $pull_title
>Severity:	non-critical
>Priority:	medium
>Category:	$category 
>Class:		change-request
>Release:	$branch
>Environment:
System: FreeBSD freefall.freebsd.org 11.0-CURRENT FreeBSD 11.0-CURRENT #0 r264289: Wed Apr 9 02:48:19 UTC 2014 peter@freefall.freebsd.org:/usr/obj/usr/src/sys/FREEFALL amd64

X-pull-request: $pull_id

>Description:

$pull_body
>How-To-Repeat:
>Fix:

$pull_diff

"""

import requests
def get_pull_metadata(github_user, github_repo, pull_id):
    rv = {}
    if True and False:
	rv["title"] = "test title"
	rv["body"] = "test body"
	rv["base_ref"] = "master"
	return rv

    r = requests.get('https://api.github.com/repos/%s/%s/pulls/%d' % (github_user, github_repo, pull_id))
    json = r.json()
    rv["title"] = json["title"]
    rv["body"] = json["body"]
    rv["base_ref"] = json["base"]["ref"]
    return rv

from string import Template

from tracking import Tracking
from gitrepo import GitRepo


def make_gnats_message(pull_id, github_user, github_repo, pr_template, repo_obj):
    pull_api_data = get_pull_metadata(github_user, github_repo, pull_id)
    # go to the dir directory
    pull_diff = repo_obj.get_diff_for_pullrequest(pull_id)
    pull_email = repo_obj.get_email_for_pullrequest(pull_id)
    pull_author = repo_obj.get_author_for_pullrequest(pull_id)

    s = Template(pr_template)
    pr_data = s.substitute(
	    pr_to=gnats_email,
	    pr_from="%s <%s>" % (pull_author, pull_email),
	    pr_reply_to="%s <%s>" % (pull_author, pull_email),
	    pr_cc=cc_email,
	    originator=pull_author,
	    pull_title=pull_api_data["title"],
	    category=pr_category,
	    branch=pull_api_data["base_ref"],
	    pull_id=pull_id,
	    pull_body=pull_api_data["body"],
	    pull_diff=pull_diff)
    return pr_data

def main():
    tracking = Tracking()
    prev_max_pull_id = tracking.get_max_pull_id()

    repo_obj = GitRepo(git_mirror_dir)
    all_pull_ids = repo_obj.get_all_pull_ids()

    pull_ids_to_work = [elem for elem in all_pull_ids if elem > prev_max_pull_id]

    for pull_id in pull_ids_to_work:
        message = make_gnats_message(pull_id=pull_id,
                github_user=github_user,
                github_repo=github_repo,
                pr_template=pr_template,
                repo_obj=repo_obj)
        fname = "pr%d.txt" % pull_id
        pr_file = open(fname, "w")
        pr_file.write(message)
        pr_file.close()
        print "Wrote out: %s" % fname
        tracking.record_pr_sent(pull_id)

if __name__ == "__main__":
    main()
