# More hacking on making nice output for GitHub action runs

import datetime
import itertools
import json
import sys

from rich.console import Console

from .bucketer import DatetimeBucketer
from .utils import nice_time, DictAttr

bucketer = DatetimeBucketer(5)
console = Console(highlight=False)

def run_group_key(run_data):
    return (
        bucketer.defuzz(run_data["startedAt"]),
        run_data["headSha"],
        run_data["event"],
    )

def run_sort_key(run_data):
    return (
        bucketer.defuzz(run_data["startedAt"]),
        run_data["headSha"],
        run_data["event"],
        run_data["workflowName"],
    )

def main():
    runs = json.load(sys.stdin)
    for run in runs:
        run["startedAt"] = datetime.datetime.fromisoformat(run["startedAt"])

    runs.sort(key=run_sort_key, reverse=True)
    for i, (k, g) in enumerate(itertools.groupby(runs, key=run_group_key)):
        if i == 1:
            console.print()
        runs = list(g)
        _ = DictAttr(runs[0])
        console.print(
            f"[white bold]{_.displayTitle}[/] " +
            f"{_.headBranch} " +
            f"\\[{_.event}] " +
            f"  [dim]{_.headSha:.12}  @{nice_time(_.startedAt)}[/]"
        )
        for r in runs:
            _ = DictAttr(r)
            cstyles = {
                "success": "green bold",
                "failure": "red bold",
            }
            console.print(
                f"   " +
                f"{_.status:12} " +
                f"[{cstyles.get(_.conclusion, 'default')}]{_.conclusion:10}[/] " +
                f"{_.workflowName:20} " +
                f"  [blue link={_.url}]view {_.url.split('/')[-1]}[/]"
            )


if __name__ == "__main__":
    main()
