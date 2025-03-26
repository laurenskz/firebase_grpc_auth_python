# Firebase gRPC Authentication Interceptor

[![PyPI version](https://badge.fury.io/py/firebase-grpc-auth.svg)](https://pypi.org/project/firebase-grpc-auth/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Versions](https://img.shields.io/pypi/pyversions/firebase-grpc-auth.svg)](https://pypi.org/project/firebase-grpc-auth/)

## Overview

`firebase-grpc-auth` is a gRPC server interceptor that enforces Firebase authentication by verifying JWT (JSON Web Token) ID tokens sent by Firebase clients. This allows secure authentication for microservices and backends using Firebase.

## Why Use This?

- **Secures gRPC services** using Firebase authentication.
- **Automatically verifies JWT tokens** sent via `Authorization` headers.
- **Supports Firebase Service Account or Google Application Default Credentials**.
- **Configurable via environment variables** for easy integration.

## Installation

Install via PyPI:

```sh
pip install firebase-grpc-auth
```

## Basic example
```python
import grpc
from concurrent import futures
from firebase_grpc_auth.interceptor import FirebaseAuthInterceptor

# Initialize the Firebase Auth Interceptor
interceptor = FirebaseAuthInterceptor()

# Create a gRPC server with the interceptor
server = grpc.server(
    futures.ThreadPoolExecutor(max_workers=10),
    interceptors=(interceptor,)
)

# Add your gRPC services to the server
# server.add_insecure_port("[::]:50051")
# server.start()

```

## Environment Variables

| Variable                        | Description                                         | Required | Default  |
|----------------------------------|-----------------------------------------------------|----------|----------|
| `ENABLE_JWT_AUTH`               | Enables authentication (`true` or `false`)         | No       | `false`  |
| `FIREBASE_SERVICE_ACCOUNT_PATH`  | Path to Firebase Service Account JSON file         | No       | Uses Google Application Default Credentials |

## Token Verification Flow

1. The client authenticates using Firebase Authentication (e.g., Google Sign-In, Email/Password, etc.).
2. Firebase issues an **ID token** (`JWT`).
3. The client sends this token in the `Authorization` header.
4. The interceptor extracts, decodes, and verifies the token.
5. If valid, it **appends the Firebase `uid` to the gRPC metadata**.
6. If invalid, the request is rejected with `grpc.StatusCode.UNAUTHENTICATED`.

## Example: gRPC Client Sending Token

Here’s an example of a gRPC client that authenticates using Firebase:

```python
import grpc

# Firebase ID Token retrieved from client-side Firebase authentication
firebase_token = "your_firebase_id_token_here"

# Create metadata with Authorization header
metadata = [("authorization", f"Bearer {firebase_token}")]

# Create gRPC channel and stub
channel = grpc.insecure_channel("localhost:50051")
stub = YourGrpcServiceStub(channel)

# Make a request with authentication
response = stub.YourRpcMethod(YourRequestMessage(), metadata=metadata)
print(response)
```

