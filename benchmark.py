import csv
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from statistics import mean, median

from app import App


def percentile(values, percentile_rank):
	index = (len(values) - 1) * percentile_rank / 100
	lower = int(index)
	upper = min(lower + 1, len(values) - 1)
	fraction = index - lower
	return values[lower] + (values[upper] - values[lower]) * fraction


def git_version():
	try:
		version = subprocess.run(
			["git", "rev-parse", "--short", "HEAD"],
			cwd=Path(__file__).resolve().parent,
			capture_output=True,
			text=True,
			check=True,
		).stdout.strip()
		dirty = subprocess.run(
			["git", "diff", "--quiet"],
			cwd=Path(__file__).resolve().parent,
		).returncode != 0
		return f"{version}-dirty" if dirty else version
	except (OSError, subprocess.CalledProcessError):
		return "unknown"


def save_csv(result, summary, output_path):
	fieldnames = [
		"scenario", "record_type", "frame", "frame_time_ms", "world_time_ms",
		"world_generation_time_ms", "chunk_generation_time_ms",
		"chunk_baking_time_ms", "world_render_time_ms", "value",
	]
	with output_path.open("w", newline="", encoding="utf-8") as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
		writer.writeheader()
		for record_type, records in (("warmup", result["warmup"]), ("frame", result["frames"])):
			for frame in records:
				writer.writerow({
					"scenario": result["scenario"],
					"record_type": record_type,
					"frame": frame["frame"],
					"frame_time_ms": frame["frame_time"] * 1000,
					"world_time_ms": frame["world_time"] * 1000,
					"world_generation_time_ms": frame["world_generation_time"] * 1000,
					"chunk_generation_time_ms": frame["chunk_generation_time"] * 1000,
					"chunk_baking_time_ms": frame["chunk_baking_time"] * 1000,
					"world_render_time_ms": frame["world_render_time"] * 1000,
				})
		for name, value in summary.items():
			writer.writerow({
				"scenario": result["scenario"],
				"record_type": "summary",
				"frame": name,
				"value": value,
			})


def main():
	parser = argparse.ArgumentParser(description="Run the Tiny Horizons benchmark")
	parser.add_argument(
		"scenario",
		nargs="?",
		choices=("static", "traversal"),
		default="static",
		help="benchmark workload (default: static)",
	)
	args = parser.parse_args()
	result = App(benchmark=True, benchmark_scenario=args.scenario).run()
	frame_times = sorted(frame["frame_time"] for frame in result["frames"])
	mean_frame = mean(frame_times)
	summary = {
		"warmup_frames": result["warmup_frames"],
		"measured_frames": result["measured_frames"],
		"resolution": f"{result['width']}x{result['height']}",
		"simulation_dt_ms": result["simulation_dt"] * 1000,
		"world_seed": result["world_seed"],
		"start_x": result["start_position"][0],
		"start_y": result["start_position"][1],
		"end_x": result["end_position"][0],
		"end_y": result["end_position"][1],
		"mean_frame_ms": mean_frame * 1000,
		"median_frame_ms": median(frame_times) * 1000,
		"p95_frame_ms": percentile(frame_times, 95) * 1000,
		"p99_frame_ms": percentile(frame_times, 99) * 1000,
		"min_frame_ms": min(frame_times) * 1000,
		"max_frame_ms": max(frame_times) * 1000,
		"mean_fps": 1 / mean_frame if mean_frame else 0,
	}
	run_id = f"{result['scenario']}_{git_version()}_{datetime.now():%Y%m%d_%H%M%S}"
	output_path = Path(__file__).resolve().parent / "benchmarks" / f"benchmark_results_{run_id}.csv"
	save_csv(result, summary, output_path)

	print("=== Tiny Horizons Benchmark ===\n")
	print(f"Scenario:         {result['scenario']}")
	print(f"Warmup frames:    {summary['warmup_frames']}")
	print(f"Measured frames:  {summary['measured_frames']}")
	print(f"Resolution:       {summary['resolution']}")
	print(f"Simulation dt:    {summary['simulation_dt_ms']:.3f} ms")
	print(f"World seed:       {summary['world_seed']}\n")
	print(f"Mean frame:       {summary['mean_frame_ms']:.3f} ms")
	print(f"Median frame:     {summary['median_frame_ms']:.3f} ms")
	print(f"P95 frame:        {summary['p95_frame_ms']:.3f} ms")
	print(f"P99 frame:        {summary['p99_frame_ms']:.3f} ms")
	print(f"Min frame:        {summary['min_frame_ms']:.3f} ms")
	print(f"Max frame:        {summary['max_frame_ms']:.3f} ms")
	print(f"Mean FPS:         {summary['mean_fps']:.1f}")
	print(f"Player position:  {result['start_position']} -> {result['end_position']}")
	print(f"Raw results:      {output_path.name}")


if __name__ == "__main__":
	main()