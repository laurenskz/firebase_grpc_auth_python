import os
import firebase_admin
import grpc
from firebase_admin import credentials, auth
from grpc import ServerInterceptor


class FirebaseAuthInterceptor(ServerInterceptor):
    def __init__(self):
        """
        gRPC Interceptor that enforces Firebase Authentication if ENABLE_JWT_AUTH is set.
        It uses FIREBASE_SERVICE_ACCOUNT_PATH if available, otherwise falls back to
        Google Application Default Credentials.
        """
        self.auth_enabled = os.getenv("ENABLE_JWT_AUTH", "false").lower() == "true"
        self.cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")

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
            handler_call_details.invocation_metadata.append(("uid", decoded_token.get("uid")))
        except Exception:
            return self._invalid_token

        return continuation(handler_call_details)
