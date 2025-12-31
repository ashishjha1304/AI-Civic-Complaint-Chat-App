#!/bin/bash

# Script to rewrite Git author information
git filter-branch --env-filter '
if [ "$GIT_AUTHOR_NAME" = "Ashish Jha" ]; then
    export GIT_AUTHOR_NAME="ashishjha1304"
    export GIT_AUTHOR_EMAIL="ashishjha1304@outlook.com"
fi
if [ "$GIT_COMMITTER_NAME" = "Ashish Jha" ]; then
    export GIT_COMMITTER_NAME="ashishjha1304"
    export GIT_COMMITTER_EMAIL="ashishjha1304@outlook.com"
fi
' --tag-name-filter cat -- --branches --tags

