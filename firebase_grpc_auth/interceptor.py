import os
import firebase_admin
import grpc
from firebase_admin import credentials, auth
from grpc import ServerInterceptor


def auth_interceptor_from_env_variables():
    return FirebaseAuthInterceptor(
        auth_enabled=os.getenv("ENABLE_JWT_AUTH", "false").lower() == "true",
        cred_path=os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
    )


class FirebaseAuthInterceptor(ServerInterceptor):
    def __init__(self, cred_path: str, auth_enabled: bool):
        """
        gRPC Interceptor that enforces Firebase Authentication if ENABLE_JWT_AUTH is set.
        It uses FIREBASE_SERVICE_ACCOUNT_PATH if available, otherwise falls back to
        Google Application Default Credentials.
        """
        self.auth_enabled = auth_enabled
        self.cred_path = cred_path

        if self.auth_enabled:
            if not firebase_admin._apps:
                cred = credentials.Certificate(self.cred_path) if self.cred_path else credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred)

            self._no_token = grpc.unary_unary_rpc_method_handler(self._create_abort("No token supplied"))
            self._invalid_token = grpc.unary_unary_rpc_method_handler(self._create_abort("Invalid token"))

    def _create_abort(self, reason: str):
        def abort(ignored_request, context):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, reason)

        return abort

    def intercept_service(self, continuation, handler_call_details):
        if not self.auth_enabled:
            return continuation(handler_call_details)

        metadata = dict(handler_call_details.invocation_metadata)
        token = metadata.get("authorization")

        if not token or not token.startswith("Bearer "):
            return self._no_token

        try:
            decoded_token = auth.verify_id_token(token.split(" ")[1].strip())
        except Exception:
            return self._invalid_token

        return continuation(handler_call_details)
