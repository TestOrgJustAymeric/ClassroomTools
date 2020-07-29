import os

import github


def delete_file(repo, path):
    try:
        contents = repo.get_contents(path=path)
        repo.delete_file(
            path=path,
            message='Deleted file',
            sha=contents.sha,
            branch='master',
        )
        print(f'Deleted: {path}\n from: {repo.full_name}')
    except github.UnknownObjectException:
        print(f'File doesn\'t exist: {path}')


def get_files_from_repo(repo, path):
    contents = repo.get_contents(path=path)
    for content in contents:
        if content.type == 'dir':
            for _content in get_files_from_repo(repo, content.path):
                yield _content
        else:
            yield content


def get_repo(fullname, token=''):
    try:
        g = github.Github(login_or_token=token)
        return g.get_repo(full_name_or_id=fullname)
    except Exception as e:
        print(e)
        raise Exception(f'Couldn\'t get repo: {fullname}')


def get_students_repositories(token, org_name, repo_filter):
    try:
        g = github.Github(login_or_token=token)
        org = g.get_organization(login=org_name)
        student_repos = list(
            filter(
                lambda repo: repo_filter in repo.name,
                org.get_repos()
            )
        )
        return student_repos
    except Exception as e:
        print(e)
        raise Exception(f'Couldn\'t get organization: {org_name}')


def delete_workflow(repo, path):
    print(f'\t\tRemoving: {path}')
    contents = repo.get_contents(path=path)
    repo.delete_file(
        path=path,
        message='Auto deleted workflow',
        sha=contents.sha,
        branch='master',
    )


def delete_all_workflows(repo):
    try:
        contents = repo.get_contents(path='.github/workflows/')
        for content_file in contents:
            delete_workflow(repo, path=content_file.path)
    except github.UnknownObjectException:
        pass


def get_workflow(src_path):
    with open(src_path, 'r') as f:
        content = f.read()
    if '.github/workflows/' not in src_path:
        head, tail = os.path.split(src_path)
        destination_path = '.github/workflows/' + tail
    return destination_path, content


def add_workflow(repo, path, content):
    print(f'\t\tAdding: {path}')
    try:
        old_file = repo.get_contents(path=path)
        repo.update_file(
            path=path,
            message='Auto added workflow',
            content=content,
            sha=old_file.sha,
            branch='master'
        )
    except github.UnknownObjectException:
        repo.create_file(
            path=path,
            message='Auto added workflow',
            content=content,
            branch='master'
        )
