from typing import List
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from src.generator import Box, generate_pieces

def box_vertices(box: Box):
    """
    Box의 8개 꼭짓점 좌표를 리턴.
    (x, y, z)는 박스의 최소 코너(왼쪽-앞-아래).
    """
    x, y, z = box.x, box.y, box.z
    w, h, d = box.w, box.h, box.d

    # 8 vertices
    return [
        (x,     y,     z),
        (x+w,   y,     z),
        (x+w,   y+h,   z),
        (x,     y+h,   z),
        (x,     y,     z+d),
        (x+w,   y,     z+d),
        (x+w,   y+h,   z+d),
        (x,     y+h,   z+d),
    ]

def box_faces(verts):
    """
    8개 꼭짓점에서 6개 면의 정점 리스트를 구성.
    verts 인덱스:
      0:(x,y,z)      1:(x+w,y,z)      2:(x+w,y+h,z)      3:(x,y+h,z)
      4:(x,y,z+d)    5:(x+w,y,z+d)    6:(x+w,y+h,z+d)    7:(x,y+h,z+d)
    """
    return [
        # 바닥(z 고정)
        [verts[0], verts[1], verts[2], verts[3]],
        # 천장(z+d)
        [verts[4], verts[5], verts[6], verts[7]],
        # 앞면(y 고정)
        [verts[0], verts[1], verts[5], verts[4]],
        # 뒷면(y+h)
        [verts[3], verts[2], verts[6], verts[7]],
        # 왼쪽(x 고정)
        [verts[0], verts[3], verts[7], verts[4]],
        # 오른쪽(x+w)
        [verts[1], verts[2], verts[6], verts[5]],
    ]

def set_axes_equal(ax):
    """
    3D에서 x, y, z 비율을 동일하게 맞춰주는 헬퍼.
    """
    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = x_limits[1] - x_limits[0]
    y_range = y_limits[1] - y_limits[0]
    z_range = z_limits[1] - z_limits[0]

    max_range = max(x_range, y_range, z_range)

    x_middle = sum(x_limits) / 2
    y_middle = sum(y_limits) / 2
    z_middle = sum(z_limits) / 2

    ax.set_xlim3d([x_middle - max_range / 2, x_middle + max_range / 2])
    ax.set_ylim3d([y_middle - max_range / 2, y_middle + max_range / 2])
    ax.set_zlim3d([z_middle - max_range / 2, z_middle + max_range / 2])

def plot_pieces_3d(pieces: List[Box], W: int, H: int, D: int):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    # 큰 박스 외곽선(와이어프레임) 그리기
    outer = Box(0, 0, 0, W, H, D)
    verts = box_vertices(outer)
    faces = box_faces(verts)
    outer_collection = Poly3DCollection(
        faces,
        facecolors="none",
        edgecolors="black",
        linewidths=1.0,
    )
    ax.add_collection3d(outer_collection)

    # 각 조각을 색을 달리해서 채워서 그리기
    for box in pieces:
        verts = box_vertices(box)
        faces = box_faces(verts)

        # 랜덤 색 (투명도 약간)
        color = (random.random(), random.random(), random.random(), 0.6)

        collection = Poly3DCollection(
            faces,
            facecolors=color,
            edgecolors="k",
            linewidths=0.5,
        )
        ax.add_collection3d(collection)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_zlim(0, D)
    set_axes_equal(ax)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # 박스 크기와 조각 개수는 여기서 실험하면서 바꾸면 됨
    W, H, D = 10, 8, 6
    target_count = 12
    min_size = 1

    pieces = generate_pieces(W, H, D, target_count, min_size)
    plot_pieces_3d(pieces, W, H, D)
