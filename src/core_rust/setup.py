
    # NeuroGraph - Высокопроизводительная система пространственных вычислений на основе токенов.
    # Copyright (C) 2024-2025 Chernov Denys

    # This program is free software: you can redistribute it and/or modify
    # it under the terms of the GNU Affero General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.

    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    # GNU Affero General Public License for more details.

    # You should have received a copy of the GNU Affero General Public License
    # along with this program. If not, see <https://www.gnu.org/licenses/>.
    

"""
Setup script for NeuroGraph Core Python bindings

This uses maturin (or setuptools-rust) to build the Rust extension.

Installation:
    pip install maturin
    maturin develop --release --features python

Or for production:
    maturin build --release --features python
    pip install target/wheels/*.whl
"""

from setuptools import setup

setup(
    name="ngcore",
    version="1.0.0",
    author="Chernov Denys",
    author_email="noreply@neurograph.dev",
    description="High-performance cognitive computing platform with Rust Core (304K events/sec, 0.39μs latency)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dchrnv/neurograph",
    project_urls={
        "Bug Tracker": "https://github.com/dchrnv/neurograph/issues",
        "Documentation": "https://github.com/dchrnv/neurograph/tree/main/docs",
        "Source Code": "https://github.com/dchrnv/neurograph",
        "Changelog": "https://github.com/dchrnv/neurograph/blob/main/CHANGELOG.md",
    },
    packages=["neurograph"],
    package_dir={"neurograph": "python"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Rust",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Framework :: AsyncIO",
        "Typing :: Typed",
    ],
    keywords="cognitive-architecture neuroscience ai rust websocket real-time event-processing pytorch machine-learning",
    python_requires=">=3.10",
    install_requires=[],
    zip_safe=False,
    license="AGPL-3.0",
)
