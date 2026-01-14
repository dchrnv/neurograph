#!/usr/bin/env python3
"""
REST API Stress Benchmark - Real Token Creation via HTTP

Tests the NeuroGraph REST API with REAL token creation through HTTP endpoints.
Measures throughput, latency, and overhead compared to direct Python API.

Usage:
    python tests/performance/rest_api_benchmark.py [1k|10k|100k|1m]

Scales:
    1k   - 1,000 tokens (baseline)
    10k  - 10,000 tokens
    100k - 100,000 tokens
    1m   - 1,000,000 tokens
"""

import argparse
import json
import time
import psutil
import requests
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class RestApiBenchmark:
    """REST API stress testing with real token creation."""

    SCALES = {
        '1k': {
            'tokens': 1_000,
            'batch_size': 100,
            'description': '1K tokens',
        },
        '10k': {
            'tokens': 10_000,
            'batch_size': 500,
            'description': '10K tokens',
        },
        '100k': {
            'tokens': 100_000,
            'batch_size': 1_000,
            'description': '100K tokens',
        },
        '1m': {
            'tokens': 1_000_000,
            'batch_size': 5_000,
            'description': '1M tokens',
        },
        '10m': {
            'tokens': 10_000_000,
            'batch_size': 10_000,
            'description': '10M tokens',
        },
        '100m': {
            'tokens': 100_000_000,
            'batch_size': 50_000,
            'description': '100M tokens',
        },
    }

    def __init__(self, scale: str, base_url: str = "http://localhost:8000"):
        if scale not in self.SCALES:
            raise ValueError(f"Invalid scale. Choose from: {list(self.SCALES.keys())}")

        self.scale = scale
        self.config = self.SCALES[scale]
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.results: Dict[str, Any] = {}
        self.process = psutil.Process()

    def check_server(self) -> bool:
        """Check if API server is running."""
        try:
            response = requests.get(f"{self.api_url}/health/live", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def authenticate(self) -> str:
        """Get authentication token (if required)."""
        # For now, assuming no auth required for token creation
        # Add authentication logic here if needed
        return ""

    def create_tokens_batch(self, count: int) -> Dict[str, Any]:
        """Create a batch of tokens via REST API."""
        url = f"{self.api_url}/tokens/batch"
        payload = {"count": count}

        start_time = time.perf_counter()
        response = requests.post(url, json=payload, timeout=30)
        end_time = time.perf_counter()

        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")

        data = response.json()
        duration = end_time - start_time

        return {
            'tokens': data.get('data', {}).get('tokens', []),
            'count': len(data.get('data', {}).get('tokens', [])),
            'duration': duration,
            'status_code': response.status_code,
        }

    def benchmark_batch_creation(self) -> Dict[str, Any]:
        """Benchmark batch token creation via REST API."""
        batch_size = self.config['batch_size']
        total_tokens = self.config['tokens']
        num_batches = total_tokens // batch_size

        print(f"\n{'='*80}")
        print(f"REST API Batch Creation Benchmark")
        print(f"{'='*80}")
        print(f"Scale: {self.config['description']}")
        print(f"Total tokens: {total_tokens:,}")
        print(f"Batch size: {batch_size:,}")
        print(f"Number of batches: {num_batches:,}")
        print(f"API endpoint: {self.api_url}/tokens/batch")
        print(f"{'='*80}\n")

        # Memory before
        mem_before = self.process.memory_info().rss / 1024 / 1024  # MB

        # Benchmarking
        total_created = 0
        total_duration = 0
        batch_durations: List[float] = []

        overall_start = time.perf_counter()

        for batch_num in range(num_batches):
            try:
                result = self.create_tokens_batch(batch_size)
                total_created += result['count']
                batch_durations.append(result['duration'])
                total_duration += result['duration']

                # Progress reporting
                if (batch_num + 1) % max(1, num_batches // 10) == 0:
                    progress = (batch_num + 1) / num_batches * 100
                    avg_throughput = total_created / total_duration if total_duration > 0 else 0
                    print(f"Progress: {progress:5.1f}% | "
                          f"Tokens: {total_created:,} | "
                          f"Avg throughput: {avg_throughput:,.0f} tokens/s")

            except Exception as e:
                print(f"Error in batch {batch_num + 1}: {e}")
                break

        overall_end = time.perf_counter()
        overall_duration = overall_end - overall_start

        # Memory after
        mem_after = self.process.memory_info().rss / 1024 / 1024  # MB
        mem_delta = mem_after - mem_before

        # Calculate metrics
        throughput = total_created / overall_duration if overall_duration > 0 else 0
        latency_per_token = (overall_duration / total_created * 1_000_000) if total_created > 0 else 0  # microseconds
        avg_batch_duration = sum(batch_durations) / len(batch_durations) if batch_durations else 0

        results = {
            'total_tokens': total_created,
            'target_tokens': total_tokens,
            'batch_size': batch_size,
            'num_batches': len(batch_durations),
            'overall_duration_seconds': round(overall_duration, 2),
            'total_api_time_seconds': round(total_duration, 2),
            'throughput_tokens_per_second': int(throughput),
            'latency_per_token_microseconds': round(latency_per_token, 3),
            'avg_batch_duration_seconds': round(avg_batch_duration, 3),
            'memory_before_mb': round(mem_before, 2),
            'memory_after_mb': round(mem_after, 2),
            'memory_delta_mb': round(mem_delta, 2),
            'batches_completed': len(batch_durations),
        }

        return results

    def print_results(self, results: Dict[str, Any]):
        """Print benchmark results."""
        print(f"\n{'='*80}")
        print(f"REST API Benchmark Results - {self.config['description']}")
        print(f"{'='*80}\n")

        print(f"Total tokens created: {results['total_tokens']:,} / {results['target_tokens']:,}")
        print(f"Overall duration: {results['overall_duration_seconds']:.2f}s")
        print(f"Total API time: {results['total_api_time_seconds']:.2f}s")
        print(f"Network/overhead: {results['overall_duration_seconds'] - results['total_api_time_seconds']:.2f}s")
        print(f"\nThroughput: {results['throughput_tokens_per_second']:,} tokens/s")
        print(f"Latency per token: {results['latency_per_token_microseconds']:.3f}µs")
        print(f"Avg batch duration: {results['avg_batch_duration_seconds']:.3f}s")
        print(f"\nMemory before: {results['memory_before_mb']:.2f} MB")
        print(f"Memory after: {results['memory_after_mb']:.2f} MB")
        print(f"Memory delta: {results['memory_delta_mb']:+.2f} MB")
        print(f"\nBatches completed: {results['batches_completed']}/{results['num_batches']}")
        print(f"{'='*80}\n")

    def save_results(self, results: Dict[str, Any]):
        """Save results to JSON file."""
        output_dir = Path("tests/performance")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"rest_api_benchmark_{self.scale}_{timestamp}.json"
        filepath = output_dir / filename

        output = {
            'benchmark_type': 'rest_api',
            'scale': self.scale,
            'description': self.config['description'],
            'timestamp': timestamp,
            'base_url': self.base_url,
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            },
            'results': results,
        }

        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"Results saved to: {filepath}")
        return filepath

    def run(self):
        """Run the complete benchmark."""
        print(f"\n{'#'*80}")
        print(f"# REST API Stress Benchmark - {self.config['description']}")
        print(f"# Real Token Creation via HTTP/REST API")
        print(f"{'#'*80}\n")

        # Check server
        print("Checking API server...")
        if not self.check_server():
            print(f"ERROR: API server not reachable at {self.base_url}")
            print("Please start the API server:")
            print("  python -m src.api.main")
            return None

        print(f"✓ API server is running at {self.base_url}\n")

        # System info
        print(f"System: {psutil.cpu_count()} cores, {psutil.virtual_memory().total / (1024**3):.2f} GB RAM")
        print(f"Process PID: {self.process.pid}\n")

        # Run benchmark
        results = self.benchmark_batch_creation()

        # Print and save results
        self.print_results(results)
        self.save_results(results)

        return results


def main():
    parser = argparse.ArgumentParser(description="REST API Stress Benchmark")
    parser.add_argument(
        'scale',
        choices=['1k', '10k', '100k', '1m', '10m', '100m'],
        help='Benchmark scale (1k, 10k, 100k, 1m, 10m, 100m tokens)'
    )
    parser.add_argument(
        '--url',
        default='http://localhost:8000',
        help='API base URL (default: http://localhost:8000)'
    )

    args = parser.parse_args()

    benchmark = RestApiBenchmark(args.scale, args.url)
    benchmark.run()


if __name__ == '__main__':
    main()
