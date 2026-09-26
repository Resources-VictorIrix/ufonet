#!/usr/bin/env python3
"""update.Updater stashes local changes before pulling and restores them (no data loss). Runs in an isolated throwaway repo, never the real one."""
import sys, os, tempfile, shutil, subprocess

def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

err = []
sandbox = tempfile.mkdtemp(prefix="ufonet_update_test_")
origin = os.path.join(sandbox, "origin.git")
work = os.path.join(sandbox, "work")
ID = "-c user.email=t@t.t -c user.name=tester"
cwd0 = os.getcwd()
try:
    run(f"git init --bare -b master {origin}", sandbox)
    run(f"git {ID} clone {origin} {work}", sandbox)
    with open(os.path.join(work, "file.txt"), "w") as f:
        f.write("base\n")
    run(f"git {ID} add .", work)
    run(f"git {ID} commit -m base", work)
    run(f"git {ID} branch -M master", work)
    run(f"git {ID} push -u origin master", work)

    # local uncommitted modification that must survive the update
    with open(os.path.join(work, "file.txt"), "w") as f:
        f.write("LOCAL EDIT\n")

    os.chdir(work)
    try:
        from core.update import Updater
        Updater()  # git stash push -> git pull -> git stash pop
    finally:
        os.chdir(cwd0)

    with open(os.path.join(work, "file.txt")) as f:
        content = f.read()
    if "LOCAL EDIT" not in content:
        err.append(f"local modification lost after update: {content!r}")
except Exception as e:
    os.chdir(cwd0)
    err.append(f"exception: {type(e).__name__}: {e}")
finally:
    shutil.rmtree(sandbox, ignore_errors=True)

print(f"update preserves local changes: {'OK' if not err else 'FAILED'}")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
