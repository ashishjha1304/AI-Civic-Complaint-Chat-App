#!/usr/bin/env python3

import subprocess
import os

# Run git filter-branch to rewrite author information
cmd = [
    'git', 'filter-branch', '--env-filter',
    '''
if [ "$GIT_AUTHOR_NAME" = "Ashish Jha" ]; then
    export GIT_AUTHOR_NAME="ashishjha1304"
    export GIT_AUTHOR_EMAIL="ashishjha1304@outlook.com"
fi
if [ "$GIT_COMMITTER_NAME" = "Ashish Jha" ]; then
    export GIT_COMMITTER_NAME="ashishjha1304"
    export GIT_COMMITTER_EMAIL="ashishjha1304@outlook.com"
fi
''',
    '--tag-name-filter', 'cat',
    '--', '--all'
]

# Set environment variable to suppress warning
env = os.environ.copy()
env['FILTER_BRANCH_SQUELCH_WARNING'] = '1'

result = subprocess.run(cmd, env=env, capture_output=True, text=True)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
