#!/usr/bin/env python

import sh
import sys
import glob
import os
import re
import ConfigParser
import subprocess

cfg = {
        'github_user':"alfredperlstein",
        'github_repo':"freebsd",
        'gitdir':"~/git/freebsd.mirror.git",
        'gnats_email':"alfred@freebsd.org",
        'cc_email':"alfred@freebsd.org",
        'pr_category':"misc",
        'db_conn':'sqlite:///github.db',
        }



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


def make_gnats_message(pull_id, cfg, pr_template, repo_obj):
    pull_api_data = get_pull_metadata(cfg["github_user"], cfg["github_repo"], pull_id)
    # go to the dir directory
    pull_diff = repo_obj.get_diff_for_pullrequest(pull_id)
    pull_email = repo_obj.get_email_for_pullrequest(pull_id)
    pull_author = repo_obj.get_author_for_pullrequest(pull_id)

    s = Template(pr_template)
    pr_data = s.substitute(
	    pr_to=cfg["gnats_email"],
	    pr_from="%s <%s>" % (pull_author, pull_email),
	    pr_reply_to="%s <%s>" % (pull_author, pull_email),
	    pr_cc=cfg["cc_email"],
	    originator=pull_author,
	    pull_title=pull_api_data["title"],
	    category=cfg["pr_category"],
	    branch=pull_api_data["base_ref"],
	    pull_id=pull_id,
	    pull_body=pull_api_data["body"],
	    pull_diff=pull_diff)
    return pr_data

def main():
    Config = ConfigParser.SafeConfigParser()

    cfg_file = "make_pr.conf"
    if os.path.isfile(cfg_file):
        Config.readfp(open(cfg_file))
        for section in Config.sections():
            for option in Config.options(section):
                cfg[option] = Config.get(section, option)

    cfg["git_mirror_dir"] = os.path.expandvars(os.path.expanduser(cfg["gitdir"]))

    tracking = Tracking(dbpath=cfg["db_conn"])
    prev_max_pull_id = tracking.get_max_pull_id()

    print "prev_max_pull_id: %d" % prev_max_pull_id

    repo_obj = GitRepo(repo_path=cfg["git_mirror_dir"])
    all_pull_ids = repo_obj.get_all_pull_ids()

    pull_ids_to_work = [elem for elem in all_pull_ids if elem > prev_max_pull_id]

    print "pull_ids_to_work: %s" % pull_ids_to_work

    newcount = 0
    for pull_id in pull_ids_to_work:
        message = make_gnats_message(pull_id=pull_id,
                cfg=cfg,
                pr_template=pr_template,
                repo_obj=repo_obj)
        fname = "pr%d.txt" % pull_id
        pr_file = open(fname, "w")
        pr_file.write(message)
        pr_file.close()
        print "Wrote out: %s" % fname
        # shell command to send-pr:
        #    yes s |send-pr -f x.out
        subprocess.check_call("yes s |send-pr -f %s" % fname, shell=True)
        tracking.record_pr_sent(pull_id)
        newcount += 1

    if newcount > 0:
        print "Finished successfully, made %d new prs!" % newcount
    else:
        print "Finished successfully, no new prs made"

    return 0

if __name__ == "__main__":
    sys.exit(main())
