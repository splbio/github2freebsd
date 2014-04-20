import sh
import os
import re

class GitRepo:
    def __init__(self, repo_path):
	self.repo_path = repo_path

    def git(self, *args):
	if True:
	    print "git ",
	    for a in args:
		print a,
	    print ""

	rv = self.gitCmd(*args)

	#print "rv.stdout: %s\n===END===" % rv.stdout

	return rv.stdout

    def gitCmd(self, *args):
	return sh.git("--no-pager", "-C", self.repo_path, *args)

    def get_diff_for_pullrequest(self, pullid):
	#merge_shas = sh.cat(sh.git("-c", "color.status=false", "log", "--format=%p", "-1",
	branch_sha = self.git("rev-parse", "refs/pull/%d/merge^" % pullid).rstrip()
	pull_sha =  self.git("rev-parse", "refs/pull/%d/head" % pullid).rstrip()
	base_sha = self.git("merge-base", branch_sha, pull_sha).rstrip()
	diff = self.git("diff", "%s..%s" % (base_sha, pull_sha))
	return diff

    def get_email_for_pullrequest(self, pull_id):
	return self.git("log", "--format=%ae", "-1", "refs/pull/%d/merge" % pull_id).rstrip()

    def get_author_for_pullrequest(self, pull_id):
	return self.git("log", "--format=%an", "-1", "refs/pull/%d/merge" % pull_id).rstrip()

    def update_mirror(self):
	self.git("fetch")

    # return an array of integer ids for all pull reqs in the repo.
    def get_all_pull_ids(self):
	rv = []
	p = re.compile('refs/pull/(\d+)/head')
	for line in self.gitCmd("show-ref"):
	    #print "> ", line, " <"
	    sha, ref = line.rstrip().split()
	    res = p.match(ref)
	    if res is not None:
		rv.append(int(res.group(1)))
	return rv
