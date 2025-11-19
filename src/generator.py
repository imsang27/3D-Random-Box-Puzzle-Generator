import random
from dataclasses import dataclass
from typing import List, Tuple, Set

@dataclass
class Box:
    """
    축 정렬 직육면체 조각 하나를 표현하는 데이터 구조.
    (x, y, z)는 박스의 최소 코너(왼쪽-앞-아래)를 기준으로 한다.
    """
    x: int
    y: int
    z: int
    w: int
    h: int
    d: int

    def size_key(self) -> Tuple[int, int, int]:
        """
        합동 판정용 키.
        변 길이를 정렬해서 튜플로 만든다.
        예) 2x3x5, 3x2x5, 5x3x2 → (2,3,5) 로 동일.
        """
        return tuple(sorted((self.w, self.h, self.d)))

    def volume(self) -> int:
        return self.w * self.h * self.d

    def longest_axis(self) -> str:
        """
        가장 긴 변이 어느 축인지 리턴: 'x' / 'y' / 'z' / 'tie'
        (tie는 정사각기둥처럼 최대 길이가 여러 축에서 같은 경우)
        """
        lengths = {'x': self.w, 'y': self.h, 'z': self.d}
        max_len = max(lengths.values())
        axes = [ax for ax, v in lengths.items() if v == max_len]
        if len(axes) == 1:
            return axes[0]
        return 'tie'

def _choose_axis(axis_weights: Tuple[float, float, float]) -> str:
    """
    axis_weights: (wx, wy, wz)
    가중치에 따라 x / y / z 중 하나를 선택.
    """
    wx, wy, wz = axis_weights
    axes = ["x", "y", "z"]
    weights = [max(wx, 0.0), max(wy, 0.0), max(wz, 0.0)]

    # 모든 가중치가 0이면 기본값으로 균등 분포
    if weights[0] == 0 and weights[1] == 0 and weights[2] == 0:
        weights = [1.0, 1.0, 1.0]

    return random.choices(axes, weights=weights, k=1)[0]

def _random_cut(
    box: Box,
    min_size: int,
    shape_keys: Set[Tuple[int, int, int]],
    axis_weights: Tuple[float, float, float],
    max_retry: int = 20,
) -> Tuple[Box, Box] | Tuple[None, None]:
    """
    box 하나를 x/y/z 중 한 축 기준으로 잘라서 두 조각을 만든다.
    - 어떤 축을 고를지는 axis_weights (wx, wy, wz)를 따른다.
    - 각 조각의 size_key가 기존 shape_keys에 있으면 그 시도는 버린다.
    - max_retry 동안 유효한 컷을 못 만들면 (None, None)을 반환.
    """
    for _ in range(max_retry):
        axis = _choose_axis(axis_weights)

        if axis == "x" and box.w > 2 * min_size:
            cut = random.randint(min_size, box.w - min_size)
            b1 = Box(box.x,          box.y, box.z, cut,           box.h, box.d)
            b2 = Box(box.x + cut,    box.y, box.z, box.w - cut,   box.h, box.d)

        elif axis == "y" and box.h > 2 * min_size:
            cut = random.randint(min_size, box.h - min_size)
            b1 = Box(box.x, box.y,          box.z, box.w, cut,           box.d)
            b2 = Box(box.x, box.y + cut,    box.z, box.w, box.h - cut,   box.d)

        elif axis == "z" and box.d > 2 * min_size:
            cut = random.randint(min_size, box.d - min_size)
            b1 = Box(box.x, box.y, box.z,          box.w, box.h, cut)
            b2 = Box(box.x, box.y, box.z + cut,    box.w, box.h, box.d - cut)

        else:
            # 이 축으로는 유효하게 자를 수 없음 → 다른 축으로 재시도
            continue

        k1 = b1.size_key()
        k2 = b2.size_key()

        # 합동 조각 중복 금지
        if k1 in shape_keys or k2 in shape_keys:
            continue

        shape_keys.add(k1)
        shape_keys.add(k2)
        return b1, b2

    return None, None

def generate_pieces(
    W: int,
    H: int,
    D: int,
    target_count: int,
    min_size: int = 1,
    max_global_retry: int = 5000,
    axis_weights: Tuple[float, float, float] = (1.0, 1.0, 0.3),
) -> List[Box]:
    """
    W×H×D 박스를 합동 없는 직육면체 조각들로 랜덤 분할한다.

    - target_count: 만들고 싶은 조각 개수 (정확히 도달 못할 수도 있음)
    - min_size: 각 축의 최소 길이
    - max_global_retry: 전체 시도 제한 (무한루프 방지용)
    - axis_weights: (wx, wy, wz)
        * 기본값 (1.0, 1.0, 0.3) : z축으로 자르는 비중을 줄여서
          위/아래로 층층이 쌓인 기둥 느낌을 약하게 만든다.
        * 예) z축 컷을 완전히 막고 싶으면 (1.0, 1.0, 0.0)
    """
    pieces: List[Box] = [Box(0, 0, 0, W, H, D)]
    shape_keys: Set[Tuple[int, int, int]] = {pieces[0].size_key()}

    attempts = 0
    while len(pieces) < target_count and attempts < max_global_retry:
        attempts += 1

        base_idx = random.randrange(len(pieces))
        base = pieces[base_idx]

        b1, b2 = _random_cut(base, min_size, shape_keys, axis_weights)
        if b1 is None:
            # 이 조각은 더 이상 의미 있게 자르기 힘든 상태
            continue

        pieces[base_idx] = b1
        pieces.append(b2)

    return pieces

def check_volume(pieces: List[Box], W: int, H: int, D: int) -> tuple[bool, int, int]:
    """
    전체 조각의 부피 합이 원래 박스 부피와 같은지 확인.
    returns: (ok, total_volume, box_volume)
    """
    total = sum(b.volume() for b in pieces)
    box_vol = W * H * D
    return total == box_vol, total, box_vol

if __name__ == "__main__":
    # 간단한 테스트 실행용
    from config import W, H, D, target_count, min_size, axis_weights

    pieces = generate_pieces(W, H, D, target_count, min_size, axis_weights=axis_weights)

    ok, total, box_vol = check_volume(pieces, W, H, D)
    print(f"volume_ok={ok}, total_vol={total}, box_vol={box_vol}")
    print(f"piece_count={len(pieces)}\n")

    for i, b in enumerate(pieces, start=1):
        print(f"[{i}] pos=({b.x},{b.y},{b.z}) size=({b.w},{b.h},{b.d}) longest_axis={b.longest_axis()}")
