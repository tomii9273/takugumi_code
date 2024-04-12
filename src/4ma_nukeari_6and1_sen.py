import argparse
import time
import numpy as np
from utils import select_file, check_loaded_takugumi_teamsen, takugumi_to_array, array_to_txt, check, TAKUGUMI_DIR

GAME_N = 4  # 4 人麻雀


def make_takugumi(n_taku: int) -> bool:
    """
    n_taku 卓の抜け番あり 6 + 1 戦の卓組の作成を試みる。作成できたら True を返す。
    参考: https://tomii6614.web.fc2.com/nukeari_6and1_sen_method.html
    """
    assert n_taku >= 7

    takugumi = takugumi_to_array(
        TAKUGUMI_DIR + "/" + select_file(f"{n_taku}taku_{GAME_N*n_taku}nin", "4team.txt"), GAME_N
    )[:6, :]
    check_loaded_takugumi_teamsen(takugumi, GAME_N, taku_check=True)

    n_taisen = takugumi.shape[0]
    n_player = takugumi.shape[1]
    assert n_taku == n_player // GAME_N

    p_cands = []  # 2 選手 (A, B) の候補

    for p0 in range(n_player):
        for p1 in range(p0 + 1, n_player):
            if p0 // n_taku == p1 // n_taku:
                continue
            cnt = 0
            for s in range(n_taisen):
                if takugumi[s][p0] == takugumi[s][p1]:
                    cnt += 1
            if cnt == 0:
                p_cands.append((p0, p1))

    for p0, p1 in p_cands:
        print(f"p0 = {p0}, p1 = {p1} start")

        for s0 in range(1, 6):
            del_taku_0 = takugumi[s0, p0]
            del_taku_1 = takugumi[s0, p1]
            if del_taku_0 in takugumi[1:, p1].flatten() or del_taku_1 in takugumi[1:, p0].flatten():  # 操作 4 の条件
                continue

            new_takugumi = np.full((n_taisen + 1, n_player + 2), -1, dtype=int)
            new_takugumi[:n_taisen, :n_player] = takugumi

            for s in range(1, 6):
                for p in range((p0 // n_taku) * n_taku, (p0 // n_taku + 1) * n_taku):
                    if new_takugumi[s][p] == del_taku_0:
                        new_takugumi[s][p] = -1
                        new_takugumi[6][p] = 1 if s != s0 else 3
                for p in range((p1 // n_taku) * n_taku, (p1 // n_taku + 1) * n_taku):
                    if new_takugumi[s][p] == del_taku_1:
                        new_takugumi[s][p] = -1
                        new_takugumi[6][p] = 2 if s != s0 else 3
                new_takugumi[s, -2] = del_taku_0
                new_takugumi[s, -1] = del_taku_1

            new_takugumi[6, -2] = 3
            new_takugumi[6, -1] = 3

            assert check(new_takugumi)
            array_to_txt(new_takugumi, f"{n_taku}taku_{n_player}nin_4and1sen.txt")
            return True

    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--n_taku", type=int, required=True, help="卓数")
    args = parser.parse_args()

    start = time.time()

    print("found" if make_takugumi(n_taku=args.n_taku) else "notfound")

    elapsed_time = time.time() - start
    print(f"time: {elapsed_time:.2f} sec")
