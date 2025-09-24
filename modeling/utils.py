import os

import numpy as np
from matplotlib import pyplot as plt


def plot_novel_trajectory(sample, c, dir, filename):
    # Extract trajectories
    x_new, y_new = sample[0, :, 0].cpu().numpy(), sample[0, :, 1].cpu().numpy()
    x_human, y_human = c[0, :, 0].cpu().numpy(), c[0, :, 1].cpu().numpy()

    plt.figure(figsize=(8, 6))

    # Plot novel animation with a colormap (progression in time)
    points = np.array([x_new, y_new]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    from matplotlib.collections import LineCollection
    lc = LineCollection(segments, cmap="Blues", linewidth=2)
    lc.set_array(np.arange(len(x_new)))  # color by step index
    plt.gca().add_collection(lc)

    # Plot human input as dashed line with markers
    plt.plot(x_human, y_human, color="orange", label="Human input", alpha=0.7)

    # Mark start and end of novel animation
    plt.scatter(x_new[0], y_new[0], color="green", s=80, marker="o", label="Start (novel)")
    plt.scatter(x_new[-1], y_new[-1], color="red", s=80, marker="X", label="End (novel)")

    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Animation Trajectory with Motion Path")
    plt.legend()
    plt.grid(True)
    plt.colorbar(lc, label="Time step")  # shows progression
    plt.tight_layout()
    plt.savefig(
        os.path.join(dir, filename),
        bbox_inches="tight"
    )