#!/usr/bin/env python

"""
Query GitHub API for the status of the GitHub actions runs associated
with a commit.

Requirements: `pygithub`, the rest is standard lib.
"""

from github import Github
import sched
import time
import sys
from collections import Counter
import logging
import argparse

FAILED_CONCLUSIONS = ["failure", "cancelled", "timed_out", "action_required"]
SUCCESSFUL_CONCLUSIONS = ["success", "neutral", "skipped"]


def print_summary(gh_check_runs):
    """Print table of all checks and their status"""
    for run in gh_check_runs:
        print(
            run.name
            + ": "
            + run.status
            + (" with '" + run.conclusion + "'" if run.status == "completed" else "")
        )


def on_timeout(timeout):
    print(
        f"Reached timeout of {timeout}s without conclusion of the status checks. Aborting."
    )
    sys.exit(1)


def query_status(s, g, repo, commit, interval):
    """query the status of github runs associated with the commit. `s` is the scheduler
    to schedule the next query"""
    gh_commit = g.get_repo(repo).get_commit(commit)
    gh_check_runs = list(gh_commit.get_check_runs())

    # one of: queued, in_progress, completed
    statuses = [run.status for run in gh_check_runs]

    # one of: success, failure, neutral, cancelled, skipped, timed_out, action_required, null
    conclusions = [run.conclusion for run in gh_check_runs]

    status_count = Counter(statuses)

    logging.info(
        f"Current status: {status_count['queued']} queued, {status_count['in_progress']} in progress and {status_count['completed']} completed checks."
    )

    if any(x in FAILED_CONCLUSIONS for x in conclusions):
        print("At least one check has failed. Aborting. Check summary below: ")
        print()
        print_summary(gh_check_runs)
        sys.exit(1)

    if all(x in SUCCESSFUL_CONCLUSIONS for x in conclusions):
        print("All checks successful!")
        print()
        print_summary(gh_check_runs)
        sys.exit(0)

    # schedule next query
    s.enter(interval, 1, query_status, (s, g, repo, commit, interval))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query GitHub status checks")
    parser.add_argument(
        "--commit",
        type=str,
        help="Commit identifier for which to query the status checks",
        required=True,
    )
    parser.add_argument(
        "--repo",
        type=str,
        help="Github repo identifier, e.g. scverse/scanpy",
        required=True,
    )
    parser.add_argument(
        "--gh_token", type=str, help="Github PAT (scope `repo`)", required=True
    )
    parser.add_argument(
        "--timeout", type=int, default=60 * 30, help="Timeout in seconds"
    )
    parser.add_argument(
        "--interval", type=int, default=10, help="Query interval in seconds"
    )

    args = parser.parse_args()

    logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)
    g = Github(args.gh_token)
    s = sched.scheduler(time.time, time.sleep)

    s.enter(args.timeout, 1, on_timeout, (args.timeout,))
    s.enter(0, 1, query_status, (s, g, args.repo, args.commit, args.interval))
    s.run()
