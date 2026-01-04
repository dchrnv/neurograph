# NeuroGraph OS

> High-performance cognitive platform with Rust Core, WebSocket API, and Jupyter integration

[![Version](https://img.shields.io/badge/version-0.63.1-blue.svg)](https://github.com/chrnv/neurograph-os-mvp)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![Rust](https://img.shields.io/badge/rust-2021-orange.svg)](https://www.rust-lang.org/)
[![License](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](LICENSE)

## What is NeuroGraph?

NeuroGraph OS is a cognitive computing platform that combines:
- **Rust Core** - High-performance event processing (304K events/sec, 0.39μs latency)
- **WebSocket API** - Real-time bidirectional communication (~5ms latency)
- **Jupyter Integration** - Interactive notebooks with magic commands
- **Web Dashboard** - React SPA with real-time monitoring

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/chrnv/neurograph-os-mvp.git
cd neurograph-os-mvp

# Install dependencies
pip install -e ".[all]"  # Full installation
# or
pip install -e ".[jupyter]"  # Jupyter only
pip install -e ".[api]"  # API server only
```

### Usage

**Jupyter Notebook:**
```python
%load_ext neurograph_jupyter
%neurograph init --path ./my_graph.db
%neurograph query "find all nodes"
```

**Python API:**
```python
from neurograph import NeuroGraph

# Your code here
```

**WebSocket Client:**
```python
from neurograph_client import WebSocketClient

client = WebSocketClient("ws://localhost:8000/ws")
await client.subscribe("metrics")
```

## Features

- ✅ **Rust Core** - 304K events/sec processing
- ✅ **WebSocket API** - Real-time events with ~5ms latency
- ✅ **Jupyter Integration** - Magic commands and widgets
- ✅ **Web Dashboard** - React SPA with monitoring
- ✅ **Module Registry** - Dynamic module management
- ✅ **RBAC** - Role-based access control
- ✅ **CI/CD** - GitHub Actions with pytest and cargo test

## Documentation

- **Docs:** [docs/](docs/)
- **Guides:** [docs/guides/](docs/guides/)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run Rust tests
cd src/core_rust && cargo test

# Build package
maturin build --release
```

## Project Status

**Current:** v0.63.1 - ~80% complete, ready for PyPI publication

**Completed:**
- ✅ Rust Core (v0.57.0)
- ✅ WebSocket API (v0.60.0)
- ✅ Jupyter Integration (v0.61.1)
- ✅ Web Dashboard (v0.62.0)
- ✅ Module Registry (v0.63.0)

**Next Steps:**
- PyPI publication (v0.64.0)
- Production deployment (v0.65.0)

See [CHANGELOG.md](CHANGELOG.md) for detailed history.

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## License

AGPL-3.0 - See [LICENSE](LICENSE) file for details.

## Links

- **Repository:** https://github.com/chrnv/neurograph-os-mvp
- **Documentation:** [docs/](docs/)
- **Issues:** https://github.com/chrnv/neurograph-os-mvp/issues
