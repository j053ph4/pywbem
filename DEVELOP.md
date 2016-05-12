Development of PyWBEM Client
============================

Git workflow
------------

* Long-lived branches:
  - `master` - for next functional release
  - `stable_M.N` - for next fix release on fix stream `M.N`.
* We use topic branches for everything!
  - Based upon the intended long-lived branch, if no dependencies
  - Based upon an earlier topic branch, in case of dependencies
  - It is valid to rebase topic branches and force-push them.
* We use pull requests to review the branches.
  - Use the correct long-lived branch (e.g. `master` or `stable_0.8`) as a
    merge target!
  - Review happens as comments on the pull requests.
  - At least two +1 are required for merging.

Releasing to PyPI
-----------------

Currently, there is quite a bit of manual work to be done for a release to
PyPI. This is all done by one person, and it assumes that the `pywbem/pywbem`
repo and the `pywbem/pywbem.github.io` repo are both cloned locally in
adjacent directories named `pywbem` and `pywbem.github.io`.
The upstream repos are assumed to have the remote name `origin`.

The following description applies to v0.8.x only!

A shell variable `$MNU` is used in the description to refer to the `M.N.U`
version (e.g. `0.8.4`) that is to be released.

1.  Switch to the directory of the `pywbem` repo, and perform the following
    steps in that directory.

    - `cd pywbem` - this is where the `makefile` is.

2.  Set a shell variable for the version to be released:

    - `MNU='0.8.x'`

3.  Verify that your working directory is in a git-wise clean state:

    - `git status`

4.  Check out the `stable_0.8` branch, because that will be the basis for the
    topic branch (this description applies to 0.8.x only), and update from
    upstream:

    - `git checkout stable_0.8`
    - `git pull`

5.  Create a topic branch for the changes:

    - `git checkout -b release_$MNU`

6.  Edit the change log to reflect all changes in the release:

    - `vi pywbem/NEWS`

7.  Finalize the package versions in the following files by changing the
    development version `M.N.U.dev0` to the final version `M.N.U`:

    - `vi setup.py`
    - `vi pywbem/__init__.py`
    - `vi pywbem/NEWS`

    Note: The `makefile` determines the package version at run time from
    `pywbem/__init__.py`, so it does not need to be updated.

8.  Perform a complete build (in your favorite Python virtual environment):

    - `make clobber all`

    If this fails, fix and iterate over this step until it succeeds.

    Note: This is for a quick turnaround when fixing issues. In Step 11, Tox is
    used to run `make test` in multiple Python environments, for a complete
    Python environment coverage. 

9.  Commit the changes and push to upstream:

    - `git commit -a -m "Release v$MNU"`
    - Push the commit upstream, using one of:

      - `git push --set-upstream origin release_$MNU` - if branch is pushed for the first time
      - `git push` - after first time, for normal additional commit
      - `git push -f` - after first time, if a rebase was used

10. On Github, create a Pull Request for the target branch. This will trigger
    the Travis CI run.

    **Important:** Regardless of which branch the commit was based upon, GitHub
    will by default target the `master` branch for the merge. Because our branch
    is `stable_0.8`, the target branch for the PR needs to be changed to
    `stable_0.8`.

11. Perform a complete test using Tox:

    - `tox`

    This single command will run `make test` in all supported Python
    environments.

12. Perform an install test:

    - `cd testsuite; ./test_install.sh`

    Note: The changed directory is necessary so that the locally available
    package directory is not used.

13. Perform a test in a CI environment (Andy):

    - Post the results to the release PR.

14. Perform a test against a real WBEM server (Karl):

    - Post the results to the release PR.

15. If any of the tests (including the Travis CI run of the Pull Request) fails,
    fix the problem and iterate back to step 8. until they all succeed.

16. Once all tests succeed:

    - Merge the PR (no review is needed)
    - Delete the PR (which also deletes the branch in the GitHub repo)

    Note: Dont do this before the Travis run succeeds, because the Travis run
    needs to still have the branch for checking out the code under test.

17. Clean up local branches:

    - `git-prune origin` (From `andy-maier/gitsurvival`)

    Or, alternatively:

    - `git remote prune origin`
    - For each remote branch listed by this command, remove the corresponding
      local branch:

      - `git branch -d <branch>`

      Note: If this delete fails, reporting unmerged changes, the reason could
      be that you worked on another system and force-pushed changes there. If
      you are sure that that is the case, you can force-delete the branch with:

      - `git branch -D <branch>`

18. Tag the release:

    - Delete any preliminary M.N* tags, if any:

      - `git tag | grep "0\.8\."`
      - `git tag -d <tags ...>`

    - If a tag for the release already exists for some reason, delete it:

      - `git tag -d v$MNU`

    - Push these tag deletions upstream:

      - `git push --tags`
      
    - Create the final tag for the release:

      - `git tag v$MNU`

    - Push the final tag upstream:

      - `git push --tags`

19. On GitHub, edit the new tag, and create a release description on it. This
    will cause it to appear in the Release tab.

20. Close milestone `M.N.U` on GitHub.

21. Upload the package to PyPI:

    **Attention!!** This only works once. You cannot re-release the same
    version to PyPI.

    - `make upload`

    Verify that it arrived on PyPI: https://pypi.python.org/pypi/pywbem/

22. Publish the API docs (that were generated in step 8) to the adjacent
    `pywbem.github.io` repo directory:

    - `make publish`

    Note: For this to work, the work directory for the `pywbem.github.io` repo
    needs to be a sibling to the work directory of the `pywbem`repo.

23. Switch to the directory of the `pywbem.github.io` repo and perform the
    following steps from that directory:

    - `cd ../pywbem.github.io`
 
24. Verify that your working directory is in a git-wise clean state:

    - `git status`

25. Check out the `master` branch (on `pywbem.github.io`, we only have that one
    long-lived branch), and update it from upstream:

    - `git checkout master`
    - `git pull`

26. Copy the manually maintained HTML files for the API docs of the new release
    from an earlier release, e.g. the last stable release:

    - `cp pywbem/doc/stable/*.html pywbem/doc/$MNU/`

27. Adjust the manually maintained HTML files for the API docs of the new
    release by editing them and changing the old version to the new version
    `M.N.U`:

    - `vi pywbem/doc/$MNU/index.html`
    - `vi pywbem/doc/$MNU/changelog.html`

28. Update the download table in `pywbem/installation.html` for the new release,
    by updating the row for the M.N.U-1 release:

    - `vi pywbem/installation.html`

29. Adjust the *stable release* link:

    - `rm pywbem/doc/stable`
    - `ln -s $MNU pywbem/doc/stable`

30. Verify that the installation page (`pywbem/installation.html` in your web
    browser) shows the new release correctly, and that all of its links work.

31. Commit the changes and push to the upstream repo (we dont use a topic branch
    for this):

    - `git add --all`
    - `git commit -m "Release v$MNU"`
    - `git push`

32. Verify that the
    [PyWBEM installation page](http://pywbem.github.io/pywbem/installation.html)
    has been updated, and that all the links work and show the intended version.

33. Announce the new release on the
    [pywbem-devel mailing list](http://sourceforge.net/p/pywbem/mailman/pywbem-devel/).

Starting development of a new v0.8.x release
--------------------------------------------

This description applies to a new release, and not to a new topic branch
within a release. It applies to v0.8.x only!

A shell variable `$MNU` is used in the description to refer to the `M.N.U`
version (e.g. `0.8.4`) whose development is started.

1.  Switch to the directory of the `pywbem` repo, and perform the following
    steps in that directory.

2.  Set a shell variable for the new version to be developed:

    - `MNU='0.8.x'`

3.  Verify that your working directory is in a git-wise clean state:

    - `git status`

4.  Check out the `stable_0.8` branch, because that will be the basis for the
    new 0.8.x release (this description applies to 0.8.x only), and upddate
    it from upstream:

    - `git checkout stable_0.8`
    - `git pull`

5.  Create a topic branch for the new release:

    - `git checkout -b start_$MNU`

6.  Increase the package versions in the following files by changing the
    old final version `M.N.U-1` to the new development version `M.N.U.dev0`:

    - `vi setup.py`
    - `vi pywbem/__init__.py`
    - `vi pywbem/NEWS`

7. Commit the changes and push to upstream:

    - `git commit -a -m "Start development of v$MNU"`
    - Push the commit upstream, using one of:

      - `git push --set-upstream origin start_$MNU` - if branch is pushed for the first time
      - `git push` - after first time, for normal additional commit
      - `git push -f` - after first time, if a rebase was used

8.  On Github, create a Pull Request for the target branch. This will trigger
    the Travis CI run.

    **Important:** Regardless of which branch the commit was based upon, GitHub
    will by default target the `master` branch for the merge. Because our branch
    is `stable_0.8`, the target branch for the PR needs to be changed to
    `stable_0.8`.

9.  If the Travis CI run fails (should not happen) fix it and go back to step 7, until
    it succeeds.

10. Once the Travis CI run for this PR succeeds:

    - Merge the PR (no review is needed)
    - Delete the PR (which also deletes the branch in the GitHub repo)

    Note: Dont do this before the Travis run succeeds, because the Travis run
    needs to still have the branch for checking out the code under test.

11. Clean up local branches:

    - `git-prune origin` (From `andy-maier/gitsurvival`)

    Or, alternatively:

    - `git remote prune origin`
    - For each remote branch listed by this command, remove the corresponding
      local branch:

      - `git branch -d <branch>`

      Note: If this delete fails, reporting unmerged changes, the reason could
      be that you worked on another system and force-pushed changes there. If
      you are sure that that is the case, you can force-delete the branch with:

      - `git branch -D <branch>`

12. On GitHub, create a new milestone `M.N.U`.

13. On GitHub, list all open issues that still have a milestone of less thani
    `M.N.U` set, and update them to target milestone `M.N.U`.
    