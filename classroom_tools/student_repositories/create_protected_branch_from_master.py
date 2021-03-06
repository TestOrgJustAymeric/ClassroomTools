import argparse
import pprint

from colorama import Fore

from classroom_tools import github_utils

parser = argparse.ArgumentParser(
    'Create a protected branch to freeze assignment submissions using the latest commit on master')
parser.add_argument(
    '--token',
    required=True,
    help='GitHub personal access token with repo permissions'
)
parser.add_argument(
    '--org_name',
    required=True,
    help='GitHub organization name'
)
parser.add_argument(
    '--repo_filter',
    required=True,
    help='Prefix to filter repositories for a given assignment or exercise'
)
parser.add_argument(
    '--branch',
    required=True,
    help='Name of protected branch'
)


def create_or_update_ref(repo, branch_name):
    master_branch = repo.get_branch('master')
    try:
        branch = repo.get_branch(branch_name)
        if branch.protected:
            branch.remove_protection()
        ref = repo.get_git_ref(f'heads/{branch_name}')
        ref.edit(sha=master_branch.commit.sha, force=True)
    except:
        repo.create_git_ref(f'refs/heads/{branch_name}', sha=master_branch.commit.sha)


def add_push_restrictions(repo, branch_name):
    branch = repo.get_branch(branch_name)
    branch.edit_protection(
        user_push_restrictions=['']
    )


def main(args):
    print('\n\n' + 'Creating protected branches'.center(80, '='))
    args = parser.parse_args(args)
    print('Args:\n' + ''.join(f'\t{k}: {v}\n' for k, v in vars(args).items()))
    github_utils.verify_token(args.token)
    repositories = github_utils.get_students_repositories(
        token=args.token,
        org_name=args.org_name,
        repo_filter=args.repo_filter
    )
    num_fail = 0
    for repo in repositories:
        try:
            create_or_update_ref(repo=repo, branch_name=args.branch)
            add_push_restrictions(repo=repo, branch_name=args.branch)
            print(f'{Fore.GREEN}Repo: {repo.full_name}')
        except Exception as e:
            print(f'{Fore.RED}Repo: {repo.full_name}')
            pprint.pprint(vars(repo))
            print(f'{Fore.RED}{e}')
            num_fail += 1
    print('\nSummary:')
    print(f'\tTotal number of repositories: {len(repositories)}')
    print(f'\tTotal number failed: {num_fail}')
    if num_fail > 0:
        raise Exception(f'{Fore.RED}Couldn\'t create protected branches')


if __name__ == '__main__':
    import sys

    main(sys.argv[1:])
