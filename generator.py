import random
from collections import Counter

class Box:
    def __init__(self, x, y, z, w, h, d):
        self.x = x  # origin (왼쪽-앞-아래 코너)
        self.y = y
        self.z = z
        self.w = w  # width  (x 방향 길이)
        self.h = h  # height (y 방향 길이)
        self.d = d  # depth  (z 방향 길이)

    def size_key(self):
        """합동 판정용 키 (정렬된 변 길이 3개)"""
        return tuple(sorted((self.w, self.h, self.d)))

    def longest_axis(self):
        """가장 긴 변이 어느 축인지 리턴: 'x' / 'y' / 'z' / 'tie'"""
        lengths = {'x': self.w, 'y': self.h, 'z': self.d}
        max_len = max(lengths.values())
        axes = [ax for ax, v in lengths.items() if v == max_len]
        if len(axes) == 1:
            return axes[0]
        return 'tie'  # 정사각기둥처럼 가장 긴 변이 여러 축에서 동일

    def __repr__(self):
        return f"Box(pos=({self.x},{self.y},{self.z}), size=({self.w},{self.h},{self.d}))"


def random_cut(box, min_size, shape_keys, max_retry=20):
    """
    box 하나를 x/y/z 중 한 축으로 자르되,
    잘린 두 조각이 기존과 합동이 되면 그 시도는 버림.
    """
    for _ in range(max_retry):
        axis = random.choice(['x', 'y', 'z'])

        # 축별로 자를 수 있는지 체크 + 실제 컷 수행
        if axis == 'x' and box.w > 2 * min_size:
            cut = random.randint(min_size, box.w - min_size)
            b1 = Box(box.x,          box.y, box.z, cut,           box.h, box.d)
            b2 = Box(box.x + cut,    box.y, box.z, box.w - cut,   box.h, box.d)
        elif axis == 'y' and box.h > 2 * min_size:
            cut = random.randint(min_size, box.h - min_size)
            b1 = Box(box.x, box.y,          box.z, box.w, cut,           box.d)
            b2 = Box(box.x, box.y + cut,    box.z, box.w, box.h - cut,   box.d)
        elif axis == 'z' and box.d > 2 * min_size:
            cut = random.randint(min_size, box.d - min_size)
            b1 = Box(box.x, box.y, box.z,          box.w, box.h, cut)
            b2 = Box(box.x, box.y, box.z + cut,    box.w, box.h, box.d - cut)
        else:
            # 이 축으로는 자를 수 없음 → 다른 축으로 재시도
            continue

        k1 = b1.size_key()
        k2 = b2.size_key()

        # 합동 조각 중복 체크
        if k1 in shape_keys or k2 in shape_keys:
            # 이 컷은 버린다
            continue

        # 유효하면 shape_keys에 추가하고 반환
        shape_keys.add(k1)
        shape_keys.add(k2)
        return b1, b2

    # max_retry 동안 유효한 컷을 못 만들면 실패
    return None, None


def generate_pieces(W, H, D, target_count, min_size=1, max_global_retry=5000):
    """
    W×H×D 박스를 합동 없는 직육면체들로 랜덤 분할.
    - target_count: 만들고 싶은 조각 개수(정확히 보장되진 않을 수 있음)
    - min_size: 각 축 최소 길이
    """
    pieces = [Box(0, 0, 0, W, H, D)]
    shape_keys = {pieces[0].size_key()}

    attempts = 0
    while len(pieces) < target_count and attempts < max_global_retry:
        attempts += 1

        base_idx = random.randrange(len(pieces))
        base = pieces[base_idx]

        b1, b2 = random_cut(base, min_size, shape_keys)
        if b1 is None:
            # 이 조각은 더 쪼개기 힘든 상태 → 다른 조각 대상으로 시도
            continue

        # 기존 조각을 두 개로 교체
        pieces[base_idx] = b1
        pieces.append(b2)

    return pieces


def check_volume(pieces, W, H, D):
    total = sum(b.w * b.h * b.d for b in pieces)
    return total == W * H * D, total


if __name__ == "__main__":
    # 실험용 파라미터
    W, H, D = 10, 8, 6
    target_count = 12
    min_size = 1

    pieces = generate_pieces(W, H, D, target_count, min_size)

    # 부피 체크
    ok, total_vol = check_volume(pieces, W, H, D)
    print(f"volume_ok={ok}, total_vol={total_vol}, box_vol={W*H*D}")
    print(f"piece_count={len(pieces)}\n")

    # 각 조각 정보 출력
    for i, b in enumerate(pieces, start=1):
        print(f"[{i}] {b}  longest_axis={b.longest_axis()}")

    # 가장 긴 축 통계
    axis_stats = Counter(b.longest_axis() for b in pieces)
    print("\nlongest_axis stats:", axis_stats)
