from __future__ import absolute_import, division, unicode_literals

import os
import unittest

from cola import gitcmds
from cola import gitcfg

from test import helper


class GitCmdsTestCase(helper.GitRepositoryTestCase):
    """Tests the cola.gitcmds module."""
    def setUp(self):
        helper.GitRepositoryTestCase.setUp(self)
        self.config = self.context.cfg

    def test_currentbranch(self):
        """Test current_branch()."""
        self.assertEqual(gitcmds.current_branch(self.context), 'master')

    def test_branch_list_local(self):
        """Test branch_list(remote=False)."""
        context = self.context
        expect = ['master']
        actual = gitcmds.branch_list(context, remote=False)
        self.assertEqual(expect, actual)

    def test_branch_list_remote(self):
        """Test branch_list(remote=False)."""
        context = self.context
        expect = []
        actual = gitcmds.branch_list(context, remote=True)
        self.assertEqual(expect, actual)

        self.git('remote', 'add', 'origin', '.')
        self.git('fetch', 'origin')
        expect = ['origin/master']
        actual = gitcmds.branch_list(context, remote=True)
        self.assertEqual(expect, actual)

        self.git('remote', 'rm', 'origin')
        expect = []
        actual = gitcmds.branch_list(context, remote=True)
        self.assertEqual(expect, actual)

    def test_upstream_remote(self):
        """Test getting the configured upstream remote"""
        context = self.context
        self.assertEqual(gitcmds.upstream_remote(context), None)
        self.git('config', 'branch.master.remote', 'test')
        self.config.reset()
        self.assertEqual(gitcmds.upstream_remote(context), 'test')

    def test_tracked_branch(self):
        """Test tracked_branch()."""
        context = self.context
        self.assertEqual(gitcmds.tracked_branch(context), None)
        self.git('config', 'branch.master.remote', 'test')
        self.git('config', 'branch.master.merge', 'refs/heads/master')
        self.config.reset()
        self.assertEqual(gitcmds.tracked_branch(context), 'test/master')

    def test_tracked_branch_other(self):
        """Test tracked_branch('other')."""
        context = self.context
        self.assertEqual(gitcmds.tracked_branch(context, 'other'), None)
        self.git('config', 'branch.other.remote', 'test')
        self.git('config', 'branch.other.merge', 'refs/heads/other/branch')
        self.config.reset()
        self.assertEqual(gitcmds.tracked_branch(context, 'other'),
                         'test/other/branch')

    def test_untracked_files(self):
        """Test untracked_files()."""
        context = self.context
        self.touch('C', 'D', 'E')
        self.assertEqual(gitcmds.untracked_files(context), ['C', 'D', 'E'])

    def test_all_files(self):
        context = self.context
        self.touch('other-file')
        all_files = gitcmds.all_files(context)

        self.assertTrue('A' in all_files)
        self.assertTrue('B' in all_files)
        self.assertTrue('other-file' in all_files)

    def test_tag_list(self):
        """Test tag_list()."""
        context = self.context
        self.git('tag', 'a')
        self.git('tag', 'b')
        self.git('tag', 'c')
        self.assertEqual(gitcmds.tag_list(context), ['c', 'b', 'a'])

    def test_merge_message_path(self):
        """Test merge_message_path()."""
        context = self.context
        self.touch('.git/SQUASH_MSG')
        self.assertEqual(gitcmds.merge_message_path(context),
                         os.path.abspath('.git/SQUASH_MSG'))
        self.touch('.git/MERGE_MSG')
        self.assertEqual(gitcmds.merge_message_path(context),
                         os.path.abspath('.git/MERGE_MSG'))
        os.unlink(gitcmds.merge_message_path(context))
        self.assertEqual(gitcmds.merge_message_path(context),
                         os.path.abspath('.git/SQUASH_MSG'))
        os.unlink(gitcmds.merge_message_path(context))
        self.assertEqual(gitcmds.merge_message_path(context), None)

    def test_all_refs(self):
        self.git('branch', 'a')
        self.git('branch', 'b')
        self.git('branch', 'c')
        self.git('tag', 'd')
        self.git('tag', 'e')
        self.git('tag', 'f')
        self.git('remote', 'add', 'origin', '.')
        self.git('fetch', 'origin')
        refs = gitcmds.all_refs(self.context)
        self.assertEqual(refs,
                         ['a', 'b', 'c', 'master',
                          'origin/a', 'origin/b', 'origin/c', 'origin/master',
                          'f', 'e', 'd'])

    def test_all_refs_split(self):
        self.git('branch', 'a')
        self.git('branch', 'b')
        self.git('branch', 'c')
        self.git('tag', 'd')
        self.git('tag', 'e')
        self.git('tag', 'f')
        self.git('remote', 'add', 'origin', '.')
        self.git('fetch', 'origin')
        local, remote, tags = gitcmds.all_refs(self.context, split=True)
        self.assertEqual(local, ['a', 'b', 'c', 'master'])
        self.assertEqual(remote,
                         ['origin/a', 'origin/b', 'origin/c', 'origin/master'])
        self.assertEqual(tags, ['f', 'e', 'd'])


if __name__ == '__main__':
    unittest.main()
