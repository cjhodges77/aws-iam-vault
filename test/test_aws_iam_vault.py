from unittest import TestCase
from unittest.mock import patch, Mock

import aws_iam_vault


TEST_ACCESS_KEY = 'ASIASGE3ABHLJ4PETTXQ'
TEST_SECRET_KEY = '+Kp++gWlnAIUjOM8nvFbRjtrQdX92gvoJ3r4/M8P'
TEST_TOKEN = 'ZPtnpj+NoTlT2P6syiUCNdinLlxfzoNVn1BlDFrWzRYI93g8Kh+UR+/Enw/lQSu3FlFFCyitx83dBQ=='


class TestCredentials():
    def __init__(self):
        self.access_key = TEST_ACCESS_KEY
        self.secret_key = TEST_SECRET_KEY
        self.token = TEST_TOKEN


class TestMissingValueCredentials():
    def __init__(self):
        self.access_key = ''
        self.secret_key = TEST_SECRET_KEY
        self.token = TEST_TOKEN


class TestMissingKeyCredentials():
    def __init__(self):
        self.secret_key = TEST_SECRET_KEY
        self.token = TEST_TOKEN


class TestGetAWSCreds(TestCase):

    @patch("boto3.Session")
    def test_get_aws_credentials(self, mock_session):
        test_credentials = TestCredentials()
        session = Mock()
        session.get_credentials().get_frozen_credentials.return_value = test_credentials
        mock_session.return_value = session

        result = aws_iam_vault._get_aws_credentials()
        assert test_credentials == result

    @patch("boto3.Session")
    def test_vault_iam_credentials_fail_missing_value(self, mock_session):
        """ When requests to AWS for IAM credentials fail, return 3 """
        session = Mock()
        session.get_credentials().get_frozen_credentials.return_value = TestMissingValueCredentials()
        mock_session.return_value = session

        with self.assertRaises(aws_iam_vault.BadCredentials):
            aws_iam_vault._get_aws_credentials()

    @patch("boto3.Session")
    def test_vault_iam_credentials_fail_missing_key(self, mock_session):
        """ When requests to AWS for IAM credentials fail, return 3 """
        session = Mock()
        session.get_credentials().get_frozen_credentials.return_value = TestMissingKeyCredentials()
        mock_session.return_value = session

        with self.assertRaises(aws_iam_vault.BadCredentials):
            aws_iam_vault._get_aws_credentials()


class TestConnectToVault(TestCase):

    @patch('hvac.Client')
    def test_hvac_client_called_correctly(self, mock_hvac):
        url = 'test_url'
        region = 'test_region'
        result = aws_iam_vault._connect_to_vault(url,
                                                        TEST_ACCESS_KEY,
                                                        TEST_SECRET_KEY,
                                                        TEST_TOKEN,
                                                        region)
        mock_hvac.assert_called_with(url=url)
        mock_hvac().auth_aws_iam.assert_called_with(TEST_ACCESS_KEY,
                                                    TEST_SECRET_KEY,
                                                    TEST_TOKEN,
                                                    region=region)
        self.assertEqual(result, mock_hvac.return_value)


class TestReadVault(TestCase):

    def test_read_vault_returns_object_at_path(self):
        vault_client = Mock()
        path = 'test/path'
        vault_client.read.return_value = {'test_key': 'test_value'}
        result = aws_iam_vault._read_vault(vault_client, path)

        vault_client.read.assert_called_with(path)
        self.assertEqual(result, {'test_key': 'test_value'})


@patch('aws_iam_vault._read_vault', return_value='test_secret')
@patch('aws_iam_vault._get_aws_credentials')
@patch('aws_iam_vault._connect_to_vault')
class TestReadSecret(TestCase):

    def test_read_secret_returns_object_at_path(self, mock_vault, mock_creds, mock_read):
        test_creds = TestCredentials()
        mock_creds.return_value = test_creds
        result = aws_iam_vault.read_secret('test_region', 'test_url', 'test_path')

        mock_creds.assert_called_with()
        mock_vault.assert_called_with('test_url',
                                      test_creds.access_key,
                                      test_creds.secret_key,
                                      test_creds.token,
                                      region='test_region')
        mock_read.assert_called_with(mock_vault.return_value, 'test_path')
        self.assertEqual(result, 'test_secret')
