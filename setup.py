from setuptools import setup, find_packages

setup(
    name="firebase-grpc-auth",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "firebase-admin",
        "grpcio",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A gRPC interceptor for Firebase authentication.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/firebase-grpc-auth",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
