
import sh
import glob
import os

github_user="alfredperlstein"
github_repo="freebsd"

gitdir="~/git/freebsd.mirror.git"

gnats_email="alfred@freebsd.org"
cc_email="alfred@freebsd.org"

pr_template = """
To: $to
From: $from
Reply-To: $reply_to
Cc: $cc
X-send-pr-version: 3.114
X-GNATS-Notify: 


>Submitter-Id:	current-users
>Originator:	$originator
>Organization:	github
>Confidential:	no
>Synopsis:	$pull_title
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

def git(*args):
    print "git ",
    for a in args:
	print a,
    print ""

    rv = sh.git("--no-pager", *args)

    print "rv.stdout: %s\n===END===" % rv.stdout

    return rv.stdout

def get_diff_for_pullrequest(pullid):
    #merge_shas = sh.cat(sh.git("-c", "color.status=false", "log", "--format=%p", "-1",
    branch_sha = git("rev-parse", "refs/pull/%d/merge^" % pullid).rstrip()
    pull_sha =  git("rev-parse", "refs/pull/%d/head" % pullid).rstrip()
    #merge_shas = git("log", "--format=%p", "-1", "refs/pull/%d/merge" % pullid).rstrip()
    #branch_sha, pull_sha = str(merge_shas).split(" ")
    base_sha = git("merge-base", branch_sha, pull_sha).rstrip()
    diff = git("diff", "%s..%s" % (base_sha, pull_sha))
    return diff

def main():
    # go to the dir directory
    os.chdir(os.path.expandvars(os.path.expanduser(gitdir)))
    diff = get_diff_for_pullrequest(1)
    print "diff: %s" % diff
    return
    print "test"
    x = sh.ls()
    print x
    y = sh.false()

    




if __name__ == "__main__":
    main()
