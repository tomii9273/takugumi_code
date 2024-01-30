import time
import itertools
import argparse


def chofuku_check(n: int) -> bool:
    """n 戦目について、過去 n-1 戦と重複対戦がなければ True を返す。"""
    for i in range(n):
        if ((top_B[i] - top_C[i]) - (top_B[n] - top_C[n])) % n_taku == 0:
            return False
    return True


def dfs_top_C(now_taisen: int, taku_no_list: list[int]) -> bool:
    """
    チーム C (3 チーム目) の先頭の選手の卓番号を深さ優先探索で探索する。
    最終戦まで求められたら True を返す。
    now_taisen: 現在の深さ (now_taisen 戦目 (0-indexed) を探索する)
    taku_no_list: now_taisen 戦目以降で使うことのできる卓番号のリスト
    """
    if now_taisen == n_taisen:
        maketxt()
        return True
    else:
        for taku_no in taku_no_list:
            top_C[now_taisen] = taku_no
            if chofuku_check(now_taisen):
                taku_no_list_new = taku_no_list[:]
                taku_no_list_new.pop(taku_no_list.index(taku_no))
                if dfs_top_C(now_taisen + 1, taku_no_list_new):
                    return True
        top_C[now_taisen] = -1
    return False


def maketxt() -> None:
    """2, 3 チーム目の先頭の選手の卓番号の配列 top_B, top_C をもとに、卓組 txt ファイルを作成"""
    takugumi = [[0] * (3 * n_taku) for _ in range(n_taisen)]
    for s in range(n_taisen):
        for p in range(n_taku):
            takugumi[s][p] = p % n_taku
            takugumi[s][p + n_taku] = (p + top_B[s]) % n_taku
            takugumi[s][p + 2 * n_taku] = (p + top_C[s]) % n_taku

    # 卓番号を 1-indexed に変更
    for s in range(n_taisen):
        for p in range(3 * n_taku):
            takugumi[s][p] = takugumi[s][p] + 1

    # txt として保存
    with open(f"{n_taku}taku_{3*n_taku}nin_{n_taisen}sen_3team.txt", "w") as f:
        for p in range(3 * n_taku):
            for s in range(n_taisen):
                f.write(str(takugumi[s][p]))
                f.write("\t")
            f.write("\n")


def make_takugumi() -> bool:
    """
    3 人麻雀 3 チーム戦を、n_taku 卓で n_taisen 戦分作成する。
    見つかったら True を返す。
    参考: https://tomii6614.web.fc2.com/3g_3team_sen_method.html の ②
    """
    assert 3 <= n_taku  # 2 卓以下では 1 戦分しか作成できない
    assert 1 <= n_taisen <= n_taku

    result = False
    for comb_from_1 in list(itertools.combinations(range(1, n_taku), n_taisen - 1)):
        global top_B, top_C
        # チーム B (2 チーム目) の先頭の選手の卓番号は「0, 1, 2, ..., n_taku-1 から必ず 0 を含めて n_taisen 個選んだもの」を全て調べる
        top_B = [0] + list(comb_from_1)
        # チーム C (3 チーム目) の先頭の選手の卓番号は関数 dfs_top_C で探索する
        top_C = [-1] * n_taisen
        top_C[0] = 0
        result |= dfs_top_C(1, list(range(1, n_taku)))
        if result:
            return result
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--n_taku", type=int, required=True, help="卓数")
    parser.add_argument("-s", "--n_taisen", type=int, required=True, help="対戦数")
    args = parser.parse_args()

    start = time.time()

    n_taku = args.n_taku
    n_taisen = args.n_taisen

    # チーム A (1 チーム目) の先頭の選手の卓番号はすべて 0 に固定
    top_B = []  # チーム B (2 チーム目) の先頭の選手の卓番号
    top_C = []  # チーム C (3 チーム目) の先頭の選手の卓番号

    print("found" if make_takugumi() else "notfound")

    elapsed_time = time.time() - start
    print(f"time: {elapsed_time:.2f} sec")
