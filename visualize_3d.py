import random
from typing import List
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (필요한 임포트)
from src.generator import Box, generate_pieces

def set_axes_equal(ax):
    """
    x, y, z 스케일을 동일하게 맞춰서 비틀려 보이지 않게 하는 함수.
    """
    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = x_limits[1] - x_limits[0]
    y_range = y_limits[1] - y_limits[0]
    z_range = z_limits[1] - z_limits[0]

    max_range = max(x_range, y_range, z_range)

    x_middle = (x_limits[0] + x_limits[1]) / 2
    y_middle = (y_limits[0] + y_limits[1]) / 2
    z_middle = (z_limits[0] + z_limits[1]) / 2

    ax.set_xlim3d([x_middle - max_range / 2, x_middle + max_range / 2])
    ax.set_ylim3d([y_middle - max_range / 2, y_middle + max_range / 2])
    ax.set_zlim3d([z_middle - max_range / 2, z_middle + max_range / 2])

def plot_pieces_3d(pieces: List[Box], W: int, H: int, D: int):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    # 각 조각을 3D bar 형태로 그리기
    for box in pieces:
        x = box.x
        y = box.y
        z = box.z
        dx = box.w
        dy = box.h
        dz = box.d

        color = (random.random(), random.random(), random.random())

        ax.bar3d(
            x, y, z,
            dx, dy, dz,
            color=color,
            edgecolor="k",
            shade=True,
            alpha=0.8,
        )

    # 박스 전체 범위 맞추기
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_zlim(0, D)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    set_axes_equal(ax)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # 공통 설정값 가져오기
    from config import W, H, D, target_count, min_size, axis_weights

    pieces = generate_pieces(W, H, D, target_count, min_size, axis_weights=axis_weights)
    plot_pieces_3d(pieces, W, H, D)
