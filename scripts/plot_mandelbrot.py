import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]

METRICS_CSV = ROOT_DIR / "results" / "mandelbrot" / "metrics_task1.csv"
POINTS_CSV = ROOT_DIR / "results" / "mandelbrot" / "points_task1.csv"

OUT_DIR = ROOT_DIR / "results" / "mandelbrot"
SPEEDUP_PNG = OUT_DIR / "mandelbrot_speedup.png"
EFFICIENCY_PNG = OUT_DIR / "mandelbrot_efficiency.png"
FRACTAL_PNG = OUT_DIR / "mandelbrot_fractal.png"


def load_metrics():
    if not METRICS_CSV.exists():
        raise FileNotFoundError(
            f"Metrics file not found: {METRICS_CSV}\n"
        )

    df = pd.read_csv(METRICS_CSV)

    required_cols = {"nthreads", "mean_time", "acceleration", "efficiency"}
    if not required_cols.issubset(df.columns):
        raise ValueError(
            f"CSV {METRICS_CSV} must contain columns: {required_cols}, "
            f"but has: {set(df.columns)}"
        )

    df = df.sort_values("nthreads").reset_index(drop=True)
    return df


def plot_speedup(df):
    plt.figure(figsize=(6, 4), dpi=120)

    x = df["nthreads"]
    y = df["acceleration"]

    plt.plot(x, x, "--", color="gray", label="Ideal speedup = p")

    plt.plot(x, y, "o-", color="tab:blue", label="Measured speedup")

    plt.xlabel("Number of threads p")
    plt.ylabel("Speedup")
    plt.title("Mandelbrot: Speedup vs. number of threads")
    plt.grid(True, which="both", linestyle="--", alpha=0.5)
    plt.xticks(x)
    plt.legend()

    plt.tight_layout()
    plt.savefig(SPEEDUP_PNG)
    plt.close()


def plot_efficiency(df):
    plt.figure(figsize=(6, 4), dpi=120)

    x = df["nthreads"]
    y = df["efficiency"]

    plt.plot(x, y, "o-", color="tab:green", label="Measured efficiency")

    plt.xlabel("Number of threads p")
    plt.ylabel("Efficiency")
    plt.title("Mandelbrot: Efficiency vs. number of threads")
    plt.grid(True, which="both", linestyle="--", alpha=0.5)
    plt.xticks(x)
    plt.ylim(0, 1.05)

    plt.tight_layout()
    plt.savefig(EFFICIENCY_PNG)
    plt.close()

def plot_fractal():
    if not POINTS_CSV.exists():
        raise FileNotFoundError(
            f"Points file not found: {POINTS_CSV}\n"
        )

    df = pd.read_csv(POINTS_CSV)

    required_cols = {"x", "y"}
    if not required_cols.issubset(df.columns):
        raise ValueError(
            f"CSV {POINTS_CSV} must contain columns: {required_cols}, "
            f"but has: {set(df.columns)}"
        )

    bins = 512

    H, xedges, yedges = np.histogram2d(df['x'], df['y'], bins=bins)

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

    plt.figure(figsize=(8, 8), dpi=150)
    plt.imshow(np.log10(H.T + 1), extent=extent, origin='lower', cmap='turbo', aspect='auto')
    plt.imshow(H.T, extent=extent, origin='lower', cmap='turbo', aspect='auto')
    plt.colorbar(label="Density")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title(f"Mandelbrot: Fractal Plot (density: {bins}x{bins} bins)")
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig(FRACTAL_PNG)
    plt.close()

    return 0


def main():
    print(f"[INFO] Reading metrics from {METRICS_CSV}")
    df = load_metrics()

    print(f"[INFO] Plotting speedup -> {SPEEDUP_PNG}")
    plot_speedup(df)

    print(f"[INFO] Plotting efficiency -> {EFFICIENCY_PNG}")
    plot_efficiency(df)

    print(f"[INFO] Plotting fractal -> {FRACTAL_PNG}")
    plot_fractal()

    print("[INFO] Done.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)