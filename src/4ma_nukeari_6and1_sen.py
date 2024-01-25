import argparse
import os
import time

import numpy as np

GAME_N = 4  # 4 人麻雀
TAKUGUMI_DIR = "../takugumi_txt"  # 元にする卓組ファイルがあるディレクトリ


def select_file(prefix: str, suffix: str) -> str:
    """prefix で始まり suffix で終わる卓組ファイル名を TAKUGUMI_DIR から探し、一意に定まる場合は返す。"""
    files = os.listdir(TAKUGUMI_DIR)
    ans = []
    for file in files:
        if file.startswith(prefix) and file.endswith(suffix):
            ans.append(file)
    assert len(ans) == 1, (prefix, suffix)
    return ans[0]


def check_loaded_takugumi(takugumi: np.ndarray) -> None:
    """
    既存の卓組が正しいかどうかを確認する。
    takugumi[対戦番号, 選手番号] = 卓番号 の形式であり、卓番号は 1-indexed である
    (ただし抜け番には -1 が入っている) ことを求める。
    """
    n_taisen = takugumi.shape[0]
    n_player = takugumi.shape[1]

    assert n_player % GAME_N == 0 or takugumi.min() == -1

    for s in range(n_taisen):
        taku_cnt = [0] * (takugumi[s].max() + 1)
        for p in range(n_player):
            assert takugumi[s][p] == -1 or 1 <= takugumi[s][p] <= n_player // GAME_N
            if takugumi[s][p] != -1:
                taku_cnt[takugumi[s][p]] += 1
        assert taku_cnt == [0] + [GAME_N] * takugumi[s].max()

    assert -1 <= takugumi.min() and takugumi.max() <= n_player // GAME_N
    assert 0 not in takugumi


def takugumi_to_array(path: str) -> np.ndarray:
    """既存の卓組を読み込み ndarray に変換。軸は (対戦, 選手) にする。"""
    with open(path, "r") as f:
        ar = []
        for item in f.readlines():
            ar.append(list(map(int, item.split())))
    ar = np.array(ar).T
    check_loaded_takugumi(ar)
    return ar


def check_loaded_takugumi_teamsen(
    takugumi: np.ndarray, taku_check: bool = False
) -> None:
    """
    既存の卓組が GAME_N チーム戦として正しいかどうかを確認する。
    takugumi[対戦番号, 選手番号] = 卓番号 の形式であり、
    第 1 チームの選手 → 第 2 チームの選手 → ... 第 GAME_N チームの選手の順に選手番号が振られており、
    同チームの選手との同卓はなく、他チームの選手との同卓は最大 1 回であることを求める。
    taku_check ならば、同じ卓に同じ選手が複数回つかないことも求める。
    """
    n_taisen = takugumi.shape[0]
    n_player = takugumi.shape[1]
    assert n_player % GAME_N == 0
    n_taku = n_player // GAME_N

    vs_cnt = np.zeros((n_player, n_player), dtype=int)
    for s in range(n_taisen):
        for p in range(n_player):
            for q in range(p + 1, n_player):
                if takugumi[s][p] == takugumi[s][q]:
                    vs_cnt[p][q] += 1
                    vs_cnt[q][p] += 1

    for p in range(n_player):
        for q in range(n_player):
            if p // n_taku == q // n_taku:
                assert vs_cnt[p][q] == 0
            else:
                assert vs_cnt[p][q] in (0, 1)

    if taku_check:
        for p in range(n_player):
            assert len(set(takugumi[:, p])) == n_taisen, (p, takugumi[:, p])


def check(takugumi: np.ndarray) -> bool:
    """(作成した) 卓組が抜け番ありの個人戦として問題ないかを確認する。"""
    n_taisen = takugumi.shape[0]
    n_player = takugumi.shape[1]

    # 卓番号とその個数が正常であることを確認
    for i in range(n_taisen):
        taku_cnt = [0] * (takugumi[i].max() + 1)
        for p in range(n_player):
            assert takugumi[i][p] > 0 or takugumi[i][p] == -1
            if takugumi[i][p] != -1:
                taku_cnt[takugumi[i][p]] += 1
        assert taku_cnt == [0] + [4] * takugumi[i].max(), taku_cnt

    # 重複対戦がなく、各選手の抜け番が 1 回であることを確認
    vs_cnt = np.zeros((n_player, n_player), dtype=int)
    nuke_cnt = np.zeros(n_player, dtype=int)
    for s in range(n_taisen):
        for p in range(n_player):
            for q in range(p + 1, n_player):
                if takugumi[s][p] == takugumi[s][q] and takugumi[s][p] != -1:
                    vs_cnt[p][q] += 1
                    vs_cnt[q][p] += 1
            if takugumi[s][p] == -1:
                nuke_cnt[p] += 1

    for p in range(n_player):
        for q in range(n_player):
            if vs_cnt[p][q] not in (0, 1):
                print("vs_count ng")
                return False

    if nuke_cnt.min() == nuke_cnt.max() == 1:
        return True
    print("nuke_cnt ng")
    return False


def array_to_txt(takugumi: np.ndarray) -> None:
    """卓組の配列を txt ファイルに変換"""
    n_taisen = takugumi.shape[0]
    n_player = takugumi.shape[1]
    n_taku = n_player // GAME_N
    with open(f"{n_taku}taku_{n_player}nin_6and1sen.txt", "w") as f:
        for i in range(n_player):
            for j in range(n_taisen):
                w = str(takugumi[j][i]) if takugumi[j][i] != -1 else "--"
                f.write(w)  # ここで転置する
                f.write("\t")
            f.write("\n")


def make_takugumi(n_taku: int) -> bool:
    """
    n_taku 卓の抜け番あり 6 + 1 戦の卓組の作成を試みる。作成できたら True を返す。
    参考: https://tomii6614.web.fc2.com/nukeari_6and1_sen_method.html
    """
    assert n_taku >= 7

    takugumi = takugumi_to_array(
        TAKUGUMI_DIR
        + "/"
        + select_file(f"{n_taku}taku_{GAME_N*n_taku}nin", "4team.txt")
    )[:6, :]
    check_loaded_takugumi_teamsen(takugumi, taku_check=True)

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
            if (
                del_taku_0 in takugumi[1:, p1].flatten()
                or del_taku_1 in takugumi[1:, p0].flatten()
            ):  # 操作 4 の条件
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
            array_to_txt(new_takugumi)
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
