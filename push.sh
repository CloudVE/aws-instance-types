#!/bin/sh

git config --global user.email "travis@travis-ci.org"p
git config --global user.name "Travis CI"
git pull --no-edit
git checkout master
git add .
git commit -m "Travis update: $(date) (Build $TRAVIS_BUILD_NUMBER)" -m "[skip ci]"
git remote add origin-token https://almahmoud:${GH_TOKEN}@github.com/CloudVE/aws-instance-types.git
git push --quiet origin-token master > /dev/null 2>&1
