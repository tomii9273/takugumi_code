import argparse
import time
import numpy as np
from utils import select_file, check_loaded_takugumi_teamsen, takugumi_to_array, array_to_txt, check, TAKUGUMI_DIR

GAME_N = 4  # 4 人麻雀


def make_takugumi(n_player: int) -> bool:
    """
    n_player 人の抜け番あり 4 + 1 戦の卓組の作成を試みる。作成できたら True を返す。
    参考: https://tomii6614.web.fc2.com/nukeari_4and1_sen_method.html
    """
    assert n_player == 15 or n_player >= 19
    n_taku = n_player // GAME_N
    k = n_player % GAME_N
    assert k != 0

    if k in (1, 2):

        takugumi = takugumi_to_array(
            TAKUGUMI_DIR + "/" + select_file(f"{n_taku}taku_{GAME_N*n_taku}nin", "4team.txt"), GAME_N
        )[:4, :]
        check_loaded_takugumi_teamsen(takugumi, GAME_N, taku_check=True)

        n_taisen = takugumi.shape[0]
        n_player_4team = takugumi.shape[1]
        assert n_player_4team == n_player - k

        new_takugumi = np.full((n_taisen + 1, n_player), -1, dtype=int)
        new_takugumi[:n_taisen, :n_player_4team] = takugumi

        new_takugumi[:n_taisen, n_player_4team] = 1
        for s in range(n_taisen):
            for p in range(n_taku):
                if new_takugumi[s, p] == 1:
                    new_takugumi[s, p] = -1
                    new_takugumi[-1, p] = 1

        if k == 2:
            new_takugumi[:n_taisen, n_player_4team + 1] = 2
            for s in range(n_taisen):
                for p in range(n_taku, n_taku * 2):
                    if new_takugumi[s, p] == 2:
                        new_takugumi[s, p] = -1
                        new_takugumi[-1, p] = 2
    else:  # k == 3
        takugumi = takugumi_to_array(
            TAKUGUMI_DIR + "/" + select_file(f"{n_taku+1}taku_{GAME_N*(n_taku+1)}nin", "4team.txt"), GAME_N
        )[:4, :]
        check_loaded_takugumi_teamsen(takugumi, GAME_N, taku_check=False)

        n_taisen = takugumi.shape[0]
        n_player_4team = takugumi.shape[1]
        assert n_player_4team == n_player + 1

        new_takugumi = np.full((n_taisen + 1, n_player), -1, dtype=int)
        new_takugumi[:n_taisen, :n_player] = takugumi[:, :n_player]

        for s in range(n_taisen):
            for p in range(n_player):
                if new_takugumi[s, p] == takugumi[s, -1]:
                    new_takugumi[s, p] = -1
                    new_takugumi[-1, p] = p // (n_taku + 1) + 1

        # 卓番号に抜けがあるので、連続にする
        for s in range(n_taisen + 1):
            taku_num_now = sorted(list(set(new_takugumi[s]) - {-1}))
            taku_num_map = {num: i + 1 for i, num in enumerate(taku_num_now)} | {-1: -1}
            for j in range(n_player):
                new_takugumi[s, j] = taku_num_map[new_takugumi[s, j]]

    assert check(new_takugumi)
    array_to_txt(new_takugumi, f"{n_taku}taku_{n_player}nin_4and1sen.txt")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--n_player", type=int, required=True, help="人数")
    args = parser.parse_args()

    start = time.time()

    print("found" if make_takugumi(n_player=args.n_player) else "notfound")

    elapsed_time = time.time() - start
    print(f"time: {elapsed_time:.2f} sec")
