#!/usr/bin/env python3
"""
NeuroGraph - Comprehensive Stress Benchmark
Version: v0.67.4
Date: 2026-01-10

Safe stress testing on multiple scales: 1M, 10M, 100M tokens
Tests Token operations with real Rust Core module.

Usage:
    python tests/performance/stress_benchmark.py 1m      # 1 million tokens
    python tests/performance/stress_benchmark.py 10m     # 10 million tokens
    python tests/performance/stress_benchmark.py 100m    # 100 million tokens
    python tests/performance/stress_benchmark.py all     # All scales
"""

import sys
import time
import psutil
import json
from datetime import datetime
from pathlib import Path

# Add python path
sys.path.insert(0, 'python')

try:
    import neurograph
    print(f"✅ neurograph v{neurograph.__version__} loaded")
except Exception as e:
    print(f"❌ Failed to import neurograph: {e}")
    sys.exit(1)


# Benchmark configurations
SCALES = {
    "1m": {
        "name": "1M Tokens",
        "tokens": 1_000_000,
        "batch_size": 100_000,
        "access_sample": 10_000,
        "expected_time": "~1 minute",
        "emoji": "🔥"
    },
    "10m": {
        "name": "10M Tokens",
        "tokens": 10_000_000,
        "batch_size": 500_000,
        "access_sample": 100_000,
        "expected_time": "~10 minutes",
        "emoji": "💥"
    },
    "100m": {
        "name": "100M Tokens",
        "tokens": 100_000_000,
        "batch_size": 1_000_000,
        "access_sample": 1_000_000,
        "expected_time": "~2 hours",
        "emoji": "🚀"
    }
}


class StressBenchmark:
    """Safe stress benchmark runner."""

    def __init__(self, scale: str):
        self.scale_name = scale
        self.config = SCALES[scale]
        self.process = psutil.Process()
        self.results = {
            "scale": scale,
            "config": self.config,
            "timestamp": datetime.now().isoformat(),
            "system": self._get_system_info(),
            "benchmarks": {}
        }

    def _get_system_info(self):
        """Collect system info."""
        return {
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_threads": psutil.cpu_count(logical=True),
            "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "python_version": sys.version.split()[0],
            "neurograph_version": neurograph.__version__
        }

    def log(self, msg: str, emoji: str = "ℹ️"):
        """Log with timestamp."""
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] {emoji} {msg}")

    def get_memory_mb(self):
        """Current memory in MB."""
        return self.process.memory_info().rss / (1024**2)

    def benchmark_single_creation(self):
        """Benchmark single token creation."""
        self.log(f"Testing single token creation ({self.config['tokens']:,} tokens)...")

        # Use smaller sample for very large scales
        test_count = min(100_000, self.config['tokens'])

        start_mem = self.get_memory_mb()
        start_time = time.perf_counter()

        tokens = []
        for i in range(test_count):
            token = neurograph.Token(i)
            tokens.append(token)

            if (i + 1) % 10_000 == 0:
                elapsed = time.perf_counter() - start_time
                rate = (i + 1) / elapsed
                self.log(f"  Progress: {i+1:,}/{test_count:,} ({rate:,.0f} tokens/s)", "📊")

        elapsed = time.perf_counter() - start_time
        end_mem = self.get_memory_mb()

        result = {
            "test_count": test_count,
            "time_sec": round(elapsed, 3),
            "rate_per_sec": round(test_count / elapsed, 2),
            "latency_us": round((elapsed / test_count) * 1_000_000, 3),
            "memory_start_mb": round(start_mem, 2),
            "memory_end_mb": round(end_mem, 2),
            "memory_delta_mb": round(end_mem - start_mem, 2)
        }

        self.log(f"✅ Single creation: {result['rate_per_sec']:,.0f} tokens/s, "
                f"{result['latency_us']:.3f}µs/token", "✅")

        return result

    def benchmark_batch_creation(self):
        """Benchmark batch token creation in chunks."""
        self.log(f"Testing batch creation ({self.config['tokens']:,} tokens in batches)...")

        batch_size = self.config['batch_size']
        total_tokens = self.config['tokens']
        num_batches = total_tokens // batch_size

        start_mem = self.get_memory_mb()
        start_time = time.perf_counter()

        total_created = 0
        batch_times = []

        for batch_num in range(num_batches):
            batch_start = time.perf_counter()

            # Create batch
            batch = neurograph.Token.create_batch(batch_size)
            total_created += batch_size

            batch_elapsed = time.perf_counter() - batch_start
            batch_times.append(batch_elapsed)

            # Clear batch to free memory
            del batch

            # Progress
            elapsed = time.perf_counter() - start_time
            rate = total_created / elapsed
            mem = self.get_memory_mb()
            progress = (batch_num + 1) / num_batches * 100

            self.log(f"  Batch {batch_num+1}/{num_batches} ({progress:.1f}%): "
                    f"{total_created:,} tokens, {rate:,.0f} tokens/s, {mem:.1f}MB", "📊")

        total_elapsed = time.perf_counter() - start_time
        end_mem = self.get_memory_mb()

        result = {
            "total_tokens": total_created,
            "num_batches": num_batches,
            "batch_size": batch_size,
            "time_sec": round(total_elapsed, 2),
            "rate_per_sec": round(total_created / total_elapsed, 2),
            "latency_us": round((total_elapsed / total_created) * 1_000_000, 3),
            "avg_batch_time_sec": round(sum(batch_times) / len(batch_times), 3),
            "memory_start_mb": round(start_mem, 2),
            "memory_end_mb": round(end_mem, 2),
            "memory_delta_mb": round(end_mem - start_mem, 2)
        }

        self.log(f"✅ Batch creation: {result['rate_per_sec']:,.0f} tokens/s, "
                f"{result['latency_us']:.3f}µs/token, {num_batches} batches", "✅")

        return result

    def benchmark_token_access(self):
        """Benchmark token attribute access."""
        self.log(f"Testing token access ({self.config['access_sample']:,} accesses)...")

        # Create tokens for access test
        sample_size = min(10_000, self.config['access_sample'])
        tokens = [neurograph.Token(i) for i in range(sample_size)]

        access_count = self.config['access_sample']
        start_time = time.perf_counter()

        for i in range(access_count):
            token = tokens[i % sample_size]
            _ = token.id
            _ = token.coordinates

            if (i + 1) % 100_000 == 0:
                elapsed = time.perf_counter() - start_time
                rate = (i + 1) / elapsed
                self.log(f"  Progress: {i+1:,}/{access_count:,} ({rate:,.0f} accesses/s)", "📊")

        elapsed = time.perf_counter() - start_time

        result = {
            "access_count": access_count,
            "sample_size": sample_size,
            "time_sec": round(elapsed, 3),
            "rate_per_sec": round(access_count / elapsed, 2),
            "latency_ns": round((elapsed / access_count) * 1_000_000_000, 1)
        }

        self.log(f"✅ Token access: {result['rate_per_sec']:,.0f} accesses/s, "
                f"{result['latency_ns']:.1f}ns/access", "✅")

        return result

    def run(self):
        """Execute all benchmarks."""
        self.log("=" * 80)
        self.log(f"{self.config['emoji']} {self.config['name']} STRESS BENCHMARK", "🚀")
        self.log("=" * 80)
        self.log(f"Total tokens: {self.config['tokens']:,}")
        self.log(f"Batch size: {self.config['batch_size']:,}")
        self.log(f"Expected time: {self.config['expected_time']}")
        self.log(f"System: {self.results['system']['cpu_cores']} cores, "
                f"{self.results['system']['memory_gb']} GB RAM")
        self.log("=" * 80)

        overall_start = time.time()

        try:
            # 1. Single token creation (sample)
            self.results['benchmarks']['single_creation'] = self.benchmark_single_creation()

            # 2. Batch creation (full scale)
            self.results['benchmarks']['batch_creation'] = self.benchmark_batch_creation()

            # 3. Token access
            self.results['benchmarks']['token_access'] = self.benchmark_token_access()

            overall_elapsed = time.time() - overall_start
            self.results['total_time_sec'] = round(overall_elapsed, 2)
            self.results['status'] = 'SUCCESS'

            self.log("=" * 80)
            self.log(f"✅ BENCHMARK COMPLETE in {overall_elapsed:.1f}s", "✅")
            self.log("=" * 80)

        except Exception as e:
            self.log(f"❌ BENCHMARK FAILED: {e}", "❌")
            import traceback
            traceback.print_exc()
            self.results['status'] = 'FAILED'
            self.results['error'] = str(e)

        return self.results

    def print_summary(self):
        """Print benchmark summary."""
        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)

        print(f"\nScale: {self.config['name']} ({self.config['tokens']:,} tokens)")
        print(f"Status: {'✅ SUCCESS' if self.results['status'] == 'SUCCESS' else '❌ FAILED'}")
        print(f"Total Time: {self.results.get('total_time_sec', 0):.1f}s")

        if 'benchmarks' in self.results:
            benchmarks = self.results['benchmarks']

            if 'batch_creation' in benchmarks:
                bc = benchmarks['batch_creation']
                print(f"\n🔥 Batch Creation ({bc['total_tokens']:,} tokens):")
                print(f"  • Throughput: {bc['rate_per_sec']:,.0f} tokens/s")
                print(f"  • Latency: {bc['latency_us']:.3f}µs/token")
                print(f"  • Batches: {bc['num_batches']} x {bc['batch_size']:,}")
                print(f"  • Memory: {bc['memory_delta_mb']:.1f}MB delta")

            if 'single_creation' in benchmarks:
                sc = benchmarks['single_creation']
                print(f"\n📌 Single Creation (sample {sc['test_count']:,}):")
                print(f"  • Throughput: {sc['rate_per_sec']:,.0f} tokens/s")
                print(f"  • Latency: {sc['latency_us']:.3f}µs/token")

            if 'token_access' in benchmarks:
                ta = benchmarks['token_access']
                print(f"\n⚡ Token Access ({ta['access_count']:,} accesses):")
                print(f"  • Throughput: {ta['rate_per_sec']:,.0f} accesses/s")
                print(f"  • Latency: {ta['latency_ns']:.1f}ns/access")

        print("\n" + "=" * 80)

    def save_results(self):
        """Save results to JSON."""
        filename = f"stress_benchmark_{self.scale_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = Path("tests/performance") / filename

        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)

        self.log(f"💾 Results saved: {filepath}", "💾")
        return filepath


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nAvailable scales:")
        for scale, config in SCALES.items():
            print(f"  {config['emoji']} {scale:5} - {config['name']} ({config['expected_time']})")
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "all":
        # Run all scales
        all_results = []
        for scale in ["1m", "10m", "100m"]:
            print(f"\n{'='*80}")
            print(f"Starting {SCALES[scale]['name']} benchmark...")
            print(f"{'='*80}\n")

            benchmark = StressBenchmark(scale)
            results = benchmark.run()
            benchmark.print_summary()
            filepath = benchmark.save_results()

            all_results.append({
                "scale": scale,
                "filepath": str(filepath),
                "status": results['status']
            })

        # Final summary
        print("\n" + "="*80)
        print("📊 ALL BENCHMARKS SUMMARY")
        print("="*80)
        for r in all_results:
            status = "✅" if r['status'] == 'SUCCESS' else "❌"
            print(f"{status} {r['scale']:5} - {r['filepath']}")
        print("="*80)

    elif mode in SCALES:
        # Run single scale
        benchmark = StressBenchmark(mode)
        results = benchmark.run()
        benchmark.print_summary()
        benchmark.save_results()
    else:
        print(f"❌ Unknown scale: {mode}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
