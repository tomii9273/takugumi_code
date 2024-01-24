import argparse
import time


def make_takugumi(n_taku, n_game):
    """
    n_game 人麻雀 n_game チーム戦を、n_taku 卓で n_taku 戦分作成する。
    以下の条件を必要とし、また以下の条件を満たせば必ず作成できる (必要十分条件)。
    「2 以上 n_game 未満の任意の整数 m について、n_taku を m で割った余りが 0 にならない。」
    参考: https://tomii6614.web.fc2.com/4team_sen_method.html の ① (n_game = 4 の場合)
    """
    assert n_game <= n_taku
    for m in range(2, n_game):
        assert n_taku % m != 0

    n_taisen = n_taku

    E = [[0] * (n_game * n_taku) for _ in range(n_taisen)]
    for s in range(n_taisen):
        for t in range(n_taku):
            for g in range(n_game):
                E[s][t + g * n_taku] = (t + g * s) % n_taku

    # 卓番号を 1-indexed に変更
    for s in range(n_taisen):
        for p in range(n_game * n_taku):
            E[s][p] = E[s][p] + 1

    # txt として保存
    with open(
        f"{n_taku}taku_{n_game*n_taku}nin_{n_taisen}sen_{n_game}team.txt", "w"
    ) as f:
        for p in range(n_game * n_taku):
            for s in range(n_taisen):
                f.write(str(E[s][p]))
                f.write("\t")
            f.write("\n")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-g", "--n_game", type=int, default=4, help="同卓する人数 (例: 4 人麻雀なら 4) かつチーム数"
    )
    parser.add_argument("-t", "--n_taku", type=int, required=True, help="卓数")
    args = parser.parse_args()

    start = time.time()

    print(
        "found" if make_takugumi(n_taku=args.n_taku, n_game=args.n_game) else "notfound"
    )

    elapsed_time = time.time() - start
    print(f"time: {elapsed_time:.2} sec")
