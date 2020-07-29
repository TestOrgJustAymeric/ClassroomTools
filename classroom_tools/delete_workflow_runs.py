import argparse

import github
import requests

parser = argparse.ArgumentParser()
parser.add_argument(
    '--token',
    required=True,
    help='GitHub personal access token with repo permissions'
)
parser.add_argument(
    '--repo_fullname',
    required=True,
    help='Repository fullname'
)
parser.add_argument(
    '--workflow_name_filter',
    help='Delete workflow runs with names that contain this filter'
)
parser.add_argument(
    '--delete_only_failed_runs',
    default=False,
    action='store_true',
    help='Delete only workflow runs that failed'
)


def delete_workflow_run(workflow_run_url, token):
    print(f'Deleting: {workflow_run_url}')
    res = requests.delete(url=workflow_run_url,
                          headers={'Authorization': f'token {token}'})
    print('Success' if res.ok else 'Failed')


if __name__ == '__main__':
    args = parser.parse_args()
    g = github.Github(login_or_token=args.token)
    repo = g.get_repo(full_name_or_id=args.repo_fullname)
    if args.delete_only_failed_runs:
        workflow_runs = list(
            filter(
                lambda run: run.conclusion == 'failure' and run.status == 'completed',
                repo.get_workflow_runs()
            ),
        )
    else:
        workflow_runs = list(repo.get_workflow_runs())

    workflow_dict = {}
    for run in workflow_runs:
        workflow_name = repo.get_workflow(id_or_name=str(run.raw_data['workflow_id'])).name
        workflow_dict.setdefault(workflow_name, [])
        workflow_dict[workflow_name].append(run)
    for workflow_name, runs in workflow_dict.items():
        if len(runs) > 1:
            runs.sort(key=lambda run: run.created_at, reverse=True)
            for run in runs[1:]:
                if args.workflow_name_filter is not None:
                    if args.workflow_name_filter in workflow_name:
                        delete_workflow_run(run.url, args.token)
                else:
                    delete_workflow_run(run.url, args.token)