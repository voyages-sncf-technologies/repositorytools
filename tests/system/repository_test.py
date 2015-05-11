from unittest import TestCase
import logging
import time
import os

from repositorytools import *


class RepositoryTest(TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.artifact_local_path = 'test-1.0.txt'

        with open(self.artifact_local_path, 'w') as f:
            f.write('foo')

        self.artifact_for_upload = LocalArtifact(group='com.example.repository-tools',
                                                 local_path=self.artifact_local_path)
        self.repository = repository.Repository()
        self.repo = 'test'

    def tearDown(self):
        os.unlink(self.artifact_local_path)

    def test_upload_artifacts__staging_true(self):
        artifacts = self.repository.upload_artifacts(local_artifacts=[self.artifact_for_upload], repo=self.repo,
                                                     staging=True, upload_filelist=True)
        repo_id = artifacts[0].repo_id
        logging.info('Uploaded to %s', repo_id)

        time.sleep(1)  # without this, it fails on TeamCity, because it is too fast

        # try to download it back
        for cur_artifact in artifacts:
            r = self.repository._session.get(cur_artifact.url)
            r.raise_for_status()

        # drop the repo
        self.repository.drop_staging_repo(repo_id=repo_id)

    def test_set_artifact_metadata(self):
        remote_artifacts = self.repository.upload_artifacts([self.artifact_for_upload], self.repo, False)
        self.assertEqual(len(remote_artifacts), 1)
        remote_artifact = remote_artifacts[0]

        my_metadata = {'foo': 'bar'}
        self.repository.set_artifact_metadata(remote_artifact, metadata=my_metadata)
        metadata_downloaded = self.repository.get_artifact_metadata(remote_artifact)

        self.assertTrue(set(my_metadata.items()).issubset(set(metadata_downloaded.items())))

        # delete the artifact again
        self.repository.delete_artifact(remote_artifact.url)