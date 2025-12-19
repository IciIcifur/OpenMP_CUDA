import csv
import statistics
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict

ROOT_DIR = Path(__file__).resolve().parents[1]

BUILD_DIR = ROOT_DIR / "cmake-build-debug"

MANDEL_EXE = BUILD_DIR / "mandelbrot.exe"

RESULTS_DIR = ROOT_DIR / "results" / "mandelbrot"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

TIMINGS_CSV = RESULTS_DIR / "timings_task1.csv"
METRICS_CSV = RESULTS_DIR / "metrics_task1.csv"


def run_mandelbrot(nthreads: int, npoints: int) -> float:
    if not MANDEL_EXE.exists():
        raise FileNotFoundError(f"mandelbrot executable not found: {MANDEL_EXE}")

    cmd = [str(MANDEL_EXE), str(nthreads), str(npoints)]

    proc = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(ROOT_DIR),
    )

    if proc.returncode != 0:
        raise RuntimeError(
            f"mandelbrot failed for nthreads={nthreads}, npoints={npoints}, "
            f"returncode={proc.returncode}, stderr:\n{proc.stderr}"
        )

    time_sec = None
    for line in proc.stderr.splitlines():
        line = line.strip()
        if line.startswith("TIME_SECONDS="):
            value_str = line.split("=", 1)[1].strip()
            value_str = value_str.replace(",", ".")
            time_sec = float(value_str)
            break

    if time_sec is None:
        raise ValueError(
            f"Could not parse TIME_SECONDS from stderr for nthreads={nthreads}, "
            f"npoints={npoints}. Stderr was:\n{proc.stderr}"
        )

    return time_sec


def collect_timings(
        nthreads_list: List[int],
        npoints: int,
        runs_per_config: int,
) -> List[Tuple[int, int, int, float]]:
    results: List[Tuple[int, int, int, float]] = []

    for nt in nthreads_list:
        for r in range(1, runs_per_config + 1):
            print(f"[INFO] Running mandelbrot: nthreads={nt}, npoints={npoints}, run={r}/{runs_per_config} ...")
            t = run_mandelbrot(nt, npoints)
            print(f"[INFO]   -> time = {t:.6f} s")
            results.append((nt, npoints, r, t))

    return results


def save_timings_csv(rows: List[Tuple[int, int, int, float]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["nthreads", "npoints", "run_index", "time"])
        for nt, np, r, t in rows:
            writer.writerow([nt, np, r, f"{t:.6f}"])


def aggregate_by_nthreads(
        timings: List[Tuple[int, int, int, float]]
) -> List[Tuple[int, int, float]]:
    times_by_nt: Dict[int, List[float]] = {}
    npoints_by_nt: Dict[int, int] = {}

    for nt, np, _, t in timings:
        times_by_nt.setdefault(nt, []).append(t)
        npoints_by_nt[nt] = np

    aggregated: List[Tuple[int, int, float]] = []
    for nt in sorted(times_by_nt.keys()):
        t_list = times_by_nt[nt]
        mean_t = statistics.mean(t_list)
        aggregated.append((nt, npoints_by_nt[nt], mean_t))

    return aggregated


def compute_metrics(
        aggregated_timings: List[Tuple[int, int, float]]
) -> List[Tuple[int, int, float, float, float]]:
    if not aggregated_timings:
        raise ValueError("No aggregated timings provided")

    t_base = None
    base_nthreads = None

    for nt, np, t in aggregated_timings:
        if nt == 1:
            t_base = t
            base_nthreads = 1
            break

    if t_base is None:
        base_entry = min(aggregated_timings, key=lambda row: row[0])  # по nthreads
        base_nthreads = base_entry[0]
        t_base = base_entry[2]
        print(f"[INFO] No nthreads=1 in timings, using nthreads={base_nthreads} as base")

    metrics = []
    for nt, np, t in aggregated_timings:
        sp = t_base / t
        ep = sp / nt
        metrics.append((nt, np, t, sp, ep))

    return metrics


def save_metrics_csv(
        rows: List[Tuple[int, int, float, float, float]],
        path: Path,
) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["nthreads", "npoints", "mean_time", "acceleration", "efficiency"])
        for nt, np, t, sp, ep in rows:
            writer.writerow(
                [
                    nt,
                    np,
                    f"{t:.6f}",
                    f"{sp:.6f}",
                    f"{ep:.6f}",
                ]
            )


def main():
    nthreads_list = [1, 2, 4, 8, 16]
    npoints = 5000
    runs_per_config = 10

    print(f"[INFO] Mandelbrot executable: {MANDEL_EXE}")
    print(f"[INFO] Results directory:     {RESULTS_DIR}")
    print(f"[INFO] nthreads list:         {nthreads_list}")
    print(f"[INFO] npoints:               {npoints}")
    print(f"[INFO] runs_per_config:       {runs_per_config}")

    timings = collect_timings(nthreads_list, npoints, runs_per_config)

    print(f"[INFO] Saving raw timings to {TIMINGS_CSV}")
    save_timings_csv(timings, TIMINGS_CSV)

    aggregated = aggregate_by_nthreads(timings)

    metrics = compute_metrics(aggregated)

    print(f"[INFO] Saving metrics to {METRICS_CSV}")
    save_metrics_csv(metrics, METRICS_CSV)

    print("[INFO] Done.")


if __name__ == "__main__":
    main()