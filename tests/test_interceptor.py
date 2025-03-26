import os
import unittest
from firebase_grpc_auth.interceptor import FirebaseAuthInterceptor, auth_interceptor_from_env_variables


class TestFirebaseAuthInterceptor(unittest.TestCase):
    def setUp(self):
        os.environ["ENABLE_JWT_AUTH"] = "true"

    def test_auth_disabled(self):
        os.environ["ENABLE_JWT_AUTH"] = "false"
        interceptor = auth_interceptor_from_env_variables()
        self.assertFalse(interceptor.auth_enabled)

    def test_auth_enabled(self):
        os.environ["ENABLE_JWT_AUTH"] = "true"
        interceptor = auth_interceptor_from_env_variables()
        self.assertTrue(interceptor.auth_enabled)


if __name__ == "__main__":
    unittest.main()
