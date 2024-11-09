import datetime
import json
import os
import sys
import time
from itertools import combinations
from random import randint, shuffle

from utils import DualOutput

N_GAME = 4  # ゲーム人数 (4 人麻雀)
t = int(sys.argv[1])  # 卓数
s = int(sys.argv[2])  # 対戦数
p = t * N_GAME  # 人数 (ゲスト含む)
times = 2500  # スワップ試行時に、この回数改善がなければ打ち切る
sets = 200  # 初期値を変えて何セット試行するか

sys.stdout = DualOutput(f"{t}taku_{s}sen_{datetime.datetime.now().isoformat().replace(':','-')}.log")

print("N_GAME", N_GAME)
print("t", t)
print("s", s)
print("p", p)
print("times", times)
print("sets", sets)

# 先頭数戦の卓組を固定する場合、fix_takugumi.txt に指定する
if os.path.exists("fix_takugumi.txt"):
    with open("fix_takugumi.txt", "r") as file:
        value = file.read().replace("\n", "")
    if value != "":
        with open("fix_takugumi.txt", "r") as file:
            FIX_TAKUGUMI = json.load(file)
    else:
        FIX_TAKUGUMI = []
else:
    FIX_TAKUGUMI = []
print("FIX_TAKUGUMI", FIX_TAKUGUMI)

assert 1 <= t
assert 1 <= s
assert all(len(item) == p for item in FIX_TAKUGUMI)

start_time = time.time()

pp = p * p
ppp = p * p * p
pppp = p * p * p * p

combs = [list(combinations(range(1, N_GAME), i)) for i in range(N_GAME)]


def getind2(p0, p1):
    """2 人組を整数に変換 (index 用)"""
    return min(p0, p1) * p + max(p0, p1)


def getind3(p0, p1, p2):
    """3 人組を整数に変換 (index 用)"""
    tmp = [p0, p1, p2]
    tmp.sort()
    return tmp[0] * pp + tmp[1] * p + tmp[2]


def getind4(p0, p1, p2, p3):
    """4 人組を整数に変換 (index 用)"""
    tmp = [p0, p1, p2, p3]
    tmp.sort()
    return tmp[0] * ppp + tmp[1] * pp + tmp[2] * p + tmp[3]


def remove_count(pr, pa, pb, pc):
    """選手 pr の、pa, pb, pc との同卓を削除する (各種同卓回数などを 1 減らす)"""

    for p0 in [pa, pb, pc]:
        tpl = (min(pr, p0), max(pr, p0))
        cnt = count2[getind2(pr, p0)]
        # assert cnt > 0
        chofuku2[cnt].remove(tpl)
        chofuku2_tmps[cnt][pr] -= 1
        chofuku2_tmps[cnt][p0] -= 1
        chofuku2[cnt - 1].append(tpl)
        chofuku2_tmps[cnt - 1][pr] += 1
        chofuku2_tmps[cnt - 1][p0] += 1
        count2[getind2(pr, p0)] -= 1
        count2_counti[cnt] -= 1
        count2_counti[cnt - 1] += 1

    for p0, p1 in [(pa, pb), (pa, pc), (pb, pc)]:
        tpl = tuple(sorted([pr, p0, p1]))
        cnt = count3[getind3(pr, p0, p1)]
        # assert cnt > 0
        chofuku3[cnt].remove(tpl)
        chofuku3_tmps[cnt][pr] -= 1
        chofuku3_tmps[cnt][p0] -= 1
        chofuku3_tmps[cnt][p1] -= 1
        chofuku3[cnt - 1].append(tpl)
        chofuku3_tmps[cnt - 1][pr] += 1
        chofuku3_tmps[cnt - 1][p0] += 1
        chofuku3_tmps[cnt - 1][p1] += 1
        count3[getind3(pr, p0, p1)] -= 1
        count3_counti[cnt] -= 1
        count3_counti[cnt - 1] += 1

    tpl = tuple(sorted([pr, pa, pb, pc]))
    cnt = count4[getind4(pr, pa, pb, pc)]
    # assert cnt > 0
    chofuku4[cnt].remove(tpl)
    chofuku4_tmps[cnt][pr] -= 1
    chofuku4_tmps[cnt][pa] -= 1
    chofuku4_tmps[cnt][pb] -= 1
    chofuku4_tmps[cnt][pc] -= 1
    chofuku4[cnt - 1].append(tpl)
    chofuku4_tmps[cnt - 1][pr] += 1
    chofuku4_tmps[cnt - 1][pa] += 1
    chofuku4_tmps[cnt - 1][pb] += 1
    chofuku4_tmps[cnt - 1][pc] += 1
    count4[getind4(pr, pa, pb, pc)] -= 1
    count4_counti[cnt] -= 1
    count4_counti[cnt - 1] += 1


def add_count(pr, pa, pb, pc):
    """選手 pr の、pa, pb, pc との同卓を追加する (各種同卓回数などを 1 増やす)"""

    for p0 in [pa, pb, pc]:
        tpl = (min(pr, p0), max(pr, p0))
        cnt = count2[getind2(pr, p0)]
        chofuku2[cnt].remove(tpl)
        chofuku2_tmps[cnt][pr] -= 1
        chofuku2_tmps[cnt][p0] -= 1
        chofuku2[cnt + 1].append(tpl)
        chofuku2_tmps[cnt + 1][pr] += 1
        chofuku2_tmps[cnt + 1][p0] += 1
        count2[getind2(pr, p0)] += 1
        count2_counti[cnt] -= 1
        count2_counti[cnt + 1] += 1

    for p0, p1 in [(pa, pb), (pa, pc), (pb, pc)]:
        tpl = tuple(sorted([pr, p0, p1]))
        cnt = count3[getind3(pr, p0, p1)]
        chofuku3[cnt].remove(tpl)
        chofuku3_tmps[cnt][pr] -= 1
        chofuku3_tmps[cnt][p0] -= 1
        chofuku3_tmps[cnt][p1] -= 1
        chofuku3[cnt + 1].append(tpl)
        chofuku3_tmps[cnt + 1][pr] += 1
        chofuku3_tmps[cnt + 1][p0] += 1
        chofuku3_tmps[cnt + 1][p1] += 1
        count3[getind3(pr, p0, p1)] += 1
        count3_counti[cnt] -= 1
        count3_counti[cnt + 1] += 1

    tpl = tuple(sorted([pr, pa, pb, pc]))
    cnt = count4[getind4(pr, pa, pb, pc)]
    chofuku4[cnt].remove(tpl)
    chofuku4_tmps[cnt][pr] -= 1
    chofuku4_tmps[cnt][pa] -= 1
    chofuku4_tmps[cnt][pb] -= 1
    chofuku4_tmps[cnt][pc] -= 1
    chofuku4[cnt + 1].append(tpl)
    chofuku4_tmps[cnt + 1][pr] += 1
    chofuku4_tmps[cnt + 1][pa] += 1
    chofuku4_tmps[cnt + 1][pb] += 1
    chofuku4_tmps[cnt + 1][pc] += 1
    count4[getind4(pr, pa, pb, pc)] += 1
    count4_counti[cnt] -= 1
    count4_counti[cnt + 1] += 1


def count_first():
    """各種同卓回数などを計算する (初回用であり、更新は add_count, remove_count で行う)"""

    count2 = [0] * pp  # count2[i]: 2 人組 i の同卓回数
    count3 = [0] * ppp  # count3[i]: 3 人組 i の同卓回数
    count4 = [0] * pppp  # count4[i]: 4 人組 i の同卓回数

    for takugumi_one in takugumi:
        for tind in range(t):
            for ind0 in range(N_GAME):
                for ind1 in range(ind0 + 1, N_GAME):
                    p0 = takugumi_one[tind * N_GAME + ind0]
                    p1 = takugumi_one[tind * N_GAME + ind1]
                    count2[getind2(p0, p1)] += 1

            for ind0 in range(N_GAME):
                for ind1 in range(ind0 + 1, N_GAME):
                    for ind2 in range(ind1 + 1, N_GAME):
                        count3[
                            getind3(
                                takugumi_one[tind * N_GAME + ind0],
                                takugumi_one[tind * N_GAME + ind1],
                                takugumi_one[tind * N_GAME + ind2],
                            )
                        ] += 1
            count4[
                getind4(
                    takugumi_one[tind * N_GAME],
                    takugumi_one[tind * N_GAME + 1],
                    takugumi_one[tind * N_GAME + 2],
                    takugumi_one[tind * N_GAME + 3],
                )
            ] += 1

    count2_counti = [0] * (s + 1)  # count2_counti[i]: 同卓回数が i 回の 2 人組の数
    count3_counti = [0] * (s + 1)  # count3_counti[i]: 同卓回数が i 回の 3 人組の数
    count4_counti = [0] * (s + 1)  # count4_counti[i]: 同卓回数が i 回の 4 人組の数

    for c in count2:
        count2_counti[c] += 1
    for c in count3:
        count3_counti[c] += 1
    for c in count4:
        count4_counti[c] += 1

    chofuku2, chofuku3, chofuku4 = get_result_chofuku(count2, count3, count4)

    chofuku2_tmps = [[0] * p for _ in range(s + 1)]
    chofuku3_tmps = [[0] * p for _ in range(s + 1)]
    chofuku4_tmps = [[0] * p for _ in range(s + 1)]

    for s0 in range(s + 1):
        for p0, p1 in chofuku2[s0]:
            chofuku2_tmps[s0][p0] += 1
            chofuku2_tmps[s0][p1] += 1
        for p0, p1, p2 in chofuku3[s0]:
            chofuku3_tmps[s0][p0] += 1
            chofuku3_tmps[s0][p1] += 1
            chofuku3_tmps[s0][p2] += 1
        for p0, p1, p2, p3 in chofuku4[s0]:
            chofuku4_tmps[s0][p0] += 1
            chofuku4_tmps[s0][p1] += 1
            chofuku4_tmps[s0][p2] += 1
            chofuku4_tmps[s0][p3] += 1

    return (
        count2,
        count3,
        count4,
        count2_counti,
        count3_counti,
        count4_counti,
        chofuku2,
        chofuku3,
        chofuku4,
        chofuku2_tmps,
        chofuku3_tmps,
        chofuku4_tmps,
    )


def calc_cost():
    """
    卓組のコスト値を計算する。
    詳細: https://tomii6614.web.fc2.com/guest_method.html#cost_value
    """
    cost = []
    # コストには以下の優先順位を定める
    # 3. s回同卓する4人組数、s回同卓する3人組数、s回同卓する2人組数、...、2回同卓する4人組数、2回同卓する3人組数、2回同卓する2人組数
    for i in range(s, 1, -1):
        cost.append(count4_counti[i])
        cost.append(count3_counti[i])
        cost.append(count2_counti[i])
        # cost += [count4_counti[i], count3_counti[i], count2_counti[i]] より少し速い

    # 4.
    # 「s回同卓する4人組リスト」に最も多く登場する選手の登場回数、「s回同卓する3人組リスト」に最も多く登場する選手の登場回数、「s回同卓する2人組リスト」に最も多く登場する選手の登場回数、
    # ...、
    # 「2回同卓する4人組リスト」に最も多く登場する選手の登場回数、「2回同卓する3人組リスト」に最も多く登場する選手の登場回数、「2回同卓する2人組リスト」に最も多く登場する選手の登場回数
    for s0 in range(s, 1, -1):
        cost.append(max(chofuku4_tmps[s0]))
        cost.append(max(chofuku3_tmps[s0]))
        cost.append(max(chofuku2_tmps[s0]))

    return cost


def get_rand_takugumi():
    """
    初期値の卓組 (卓番号がランダム) を生成する。
    詳細: https://tomii6614.web.fc2.com/guest_method.html の「方法」の 1
    """
    # 5卓6戦重複なし用
    # takugumi = [[-1] * p for _ in range(5)]
    # for s0 in range(5):
    #     takugumi_pre = [-1] * p
    #     for t0 in range(5):
    #         for g0 in range(4):
    #             takugumi_pre[t0 + g0 * t] = (t0 + g0 * s0) % t
    #     ind = 0
    #     for tt in range(5):
    #         for ii in range(p):
    #             if takugumi_pre[ii] == tt:
    #                 takugumi[s0][ind] = ii
    #                 ind += 1
    # print(takugumi)
    # takugumi_one = list(range(p))
    # shuffle(takugumi_one)
    # takugumi.append(takugumi_one)

    # 7卓18戦重複なし用
    # takugumi_pre = [
    #     [1, 1, 3, 6, 7, 2, 2, 7, 6, 3, 1, 5, 4, 2, 3, 3, 2, 4, 5, 1, 4, 7, 5, 6, 6, 5, 7, 4],
    #     [1, 3, 1, 3, 6, 7, 2, 2, 7, 6, 5, 1, 5, 4, 2, 3, 3, 2, 4, 4, 1, 4, 7, 5, 6, 6, 5, 7],
    #     [1, 6, 3, 1, 3, 6, 7, 2, 2, 7, 4, 5, 1, 5, 4, 2, 3, 3, 2, 7, 4, 1, 4, 7, 5, 6, 6, 5],
    #     [1, 7, 6, 3, 1, 3, 6, 7, 2, 2, 2, 4, 5, 1, 5, 4, 2, 3, 3, 5, 7, 4, 1, 4, 7, 5, 6, 6],
    #     [1, 2, 7, 6, 3, 1, 3, 6, 7, 2, 3, 2, 4, 5, 1, 5, 4, 2, 3, 6, 5, 7, 4, 1, 4, 7, 5, 6],
    #     [1, 2, 2, 7, 6, 3, 1, 3, 6, 7, 3, 3, 2, 4, 5, 1, 5, 4, 2, 6, 6, 5, 7, 4, 1, 4, 7, 5],
    #     [1, 7, 2, 2, 7, 6, 3, 1, 3, 6, 2, 3, 3, 2, 4, 5, 1, 5, 4, 5, 6, 6, 5, 7, 4, 1, 4, 7],
    #     [1, 6, 7, 2, 2, 7, 6, 3, 1, 3, 4, 2, 3, 3, 2, 4, 5, 1, 5, 7, 5, 6, 6, 5, 7, 4, 1, 4],
    #     [1, 3, 6, 7, 2, 2, 7, 6, 3, 1, 5, 4, 2, 3, 3, 2, 4, 5, 1, 4, 7, 5, 6, 6, 5, 7, 4, 1],
    #     [1, 1, 3, 6, 7, 2, 2, 7, 6, 3, 4, 2, 3, 5, 1, 4, 7, 4, 6, 7, 5, 3, 5, 4, 5, 1, 6, 2],
    #     [1, 3, 1, 3, 6, 7, 2, 2, 7, 6, 5, 3, 2, 1, 5, 2, 4, 7, 6, 5, 4, 3, 6, 1, 7, 4, 5, 4],
    #     [1, 6, 3, 1, 3, 6, 7, 2, 2, 7, 1, 3, 4, 5, 4, 3, 1, 5, 5, 6, 2, 2, 6, 4, 4, 7, 7, 5],
    #     [1, 7, 6, 3, 1, 3, 6, 7, 2, 2, 5, 2, 5, 4, 2, 3, 4, 6, 7, 6, 3, 4, 5, 7, 1, 5, 4, 1],
    #     [1, 2, 7, 6, 3, 1, 3, 6, 7, 2, 4, 4, 1, 2, 3, 2, 7, 6, 4, 5, 3, 5, 7, 5, 4, 6, 1, 5],
    #     [1, 2, 2, 7, 6, 3, 1, 3, 6, 7, 2, 5, 5, 3, 3, 4, 5, 5, 1, 7, 2, 1, 4, 6, 7, 6, 4, 4],
    #     [1, 7, 2, 2, 7, 6, 3, 1, 3, 6, 3, 1, 4, 3, 2, 5, 6, 7, 4, 4, 4, 5, 1, 6, 5, 5, 7, 2],
    #     [1, 6, 7, 2, 2, 7, 6, 3, 1, 3, 3, 5, 2, 2, 4, 1, 6, 4, 7, 1, 5, 4, 4, 5, 6, 7, 5, 3],
    #     [1, 3, 6, 7, 2, 2, 7, 6, 3, 1, 2, 4, 3, 4, 5, 5, 5, 1, 5, 4, 1, 2, 7, 7, 6, 4, 6, 3],
    # ]
    # takugumi = [[-1] * p for _ in range(s)]
    # for s0 in range(s):
    #     ind = 0
    #     for tt in range(t):
    #         for ii in range(p):
    #             if takugumi_pre[s0][ii] == tt + 1:
    #                 takugumi[s0][ind] = ii
    #                 ind += 1

    # 通常
    takugumi = []
    for i in range(s):
        if i < len(FIX_TAKUGUMI):
            takugumi.append(FIX_TAKUGUMI[i][:])
        else:
            takugumi_one = list(range(p))
            shuffle(takugumi_one)
            takugumi.append(takugumi_one)

    return takugumi


def get_result_chofuku(count2, count3, count4):
    """同卓回数ごとの選手リストを作成する"""

    chofuku2 = [[] for _ in range(s + 1)]  # 同卓回数ごとの 2 人組リスト
    chofuku3 = [[] for _ in range(s + 1)]  # 同卓回数ごとの 3 人組リスト
    chofuku4 = [[] for _ in range(s + 1)]  # 同卓回数ごとの 4 人組リスト

    for p0 in range(p):
        for p1 in range(p0 + 1, p):
            chofuku2[count2[getind2(p0, p1)]].append((p0, p1))

    for p0 in range(p):
        for p1 in range(p0 + 1, p):
            for p2 in range(p1 + 1, p):
                chofuku3[count3[getind3(p0, p1, p2)]].append((p0, p1, p2))

    for p0 in range(p):
        for p1 in range(p0 + 1, p):
            for p2 in range(p1 + 1, p):
                for p3 in range(p2 + 1, p):
                    chofuku4[count4[getind4(p0, p1, p2, p3)]].append((p0, p1, p2, p3))
    return chofuku2, chofuku3, chofuku4


best_cost = []
best_takugumi = []

for i_set in range(sets):
    print("set start", i_set)

    takugumi = get_rand_takugumi()

    print("first_takugumi", takugumi)

    (
        count2,
        count3,
        count4,
        count2_counti,
        count3_counti,
        count4_counti,
        chofuku2,
        chofuku3,
        chofuku4,
        chofuku2_tmps,
        chofuku3_tmps,
        chofuku4_tmps,
    ) = count_first()

    cost = calc_cost()
    print("first_cost", cost)

    if len(FIX_TAKUGUMI) >= s:
        print("FIX_TAKUGUMI 全体またはその先頭部分をそのまま使用します")
        best_cost = cost
        best_takugumi = takugumi
        break

    time_count = 0
    time_count_all = 0
    break_flag = False
    while True:
        # print(cost, guest_count)
        target0_ind = -1
        target1_ind = -1

        target_yuusen = []
        for s0 in range(s, 1, -1):
            if len(chofuku4[s0]) > 0:
                for p0, p1, p2, p3 in chofuku4[s0]:
                    target_yuusen += [p0, p1, p2, p3]
                break
            if len(chofuku3[s0]) > 0:
                for p0, p1, p2 in chofuku3[s0]:
                    target_yuusen += [p0, p1, p2]
                break
            if len(chofuku2[s0]) > 0:
                for p0, p1 in chofuku2[s0]:
                    target_yuusen += [p0, p1]
                break

        choice_type = randint(0, 1)
        if choice_type == 0:
            while True:
                sind = randint(len(FIX_TAKUGUMI), s - 1)
                target0_ind = randint(0, p - 1)
                target1_ind = randint(0, p - 1)
                target0 = takugumi[sind][target0_ind]
                target1 = takugumi[sind][target1_ind]
                if target0_ind // N_GAME != target1_ind // N_GAME:
                    break
        else:
            while True:
                sind = randint(len(FIX_TAKUGUMI), s - 1)
                target0 = target_yuusen[randint(0, len(target_yuusen) - 1)]
                target0_ind = takugumi[sind].index(target0)
                target1_ind = randint(0, p - 1)
                target1 = takugumi[sind][target1_ind]
                if target0_ind // N_GAME != target1_ind // N_GAME:
                    break

        taku_0 = target0_ind // N_GAME
        taku_1 = target1_ind // N_GAME
        taku_0_p0 = takugumi[sind][taku_0 * N_GAME + (target0_ind % 4 + 1) % 4]
        taku_0_p1 = takugumi[sind][taku_0 * N_GAME + (target0_ind % 4 + 2) % 4]
        taku_0_p2 = takugumi[sind][taku_0 * N_GAME + (target0_ind % 4 + 3) % 4]
        taku_1_p0 = takugumi[sind][taku_1 * N_GAME + (target1_ind % 4 + 1) % 4]
        taku_1_p1 = takugumi[sind][taku_1 * N_GAME + (target1_ind % 4 + 2) % 4]
        taku_1_p2 = takugumi[sind][taku_1 * N_GAME + (target1_ind % 4 + 3) % 4]

        takugumi[sind][target0_ind], takugumi[sind][target1_ind] = (
            takugumi[sind][target1_ind],
            takugumi[sind][target0_ind],
        )
        remove_count(target0, taku_0_p0, taku_0_p1, taku_0_p2)
        remove_count(target1, taku_1_p0, taku_1_p1, taku_1_p2)
        add_count(target0, taku_1_p0, taku_1_p1, taku_1_p2)
        add_count(target1, taku_0_p0, taku_0_p1, taku_0_p2)

        cost_new = calc_cost()

        time_count_all += 1
        if cost_new >= cost:
            time_count += 1
            if time_count >= times:
                break_flag = True
            if time_count % (times // 10) == 0:
                print("time_count", time_count)
        else:
            print("new_cost", cost_new, time_count, time_count_all)
            time_count = 0

        if cost_new > cost:
            takugumi[sind][target0_ind], takugumi[sind][target1_ind] = (
                takugumi[sind][target1_ind],
                takugumi[sind][target0_ind],
            )
            remove_count(target0, taku_1_p0, taku_1_p1, taku_1_p2)
            remove_count(target1, taku_0_p0, taku_0_p1, taku_0_p2)
            add_count(target0, taku_0_p0, taku_0_p1, taku_0_p2)
            add_count(target1, taku_1_p0, taku_1_p1, taku_1_p2)
        else:
            cost = cost_new

            if sum(cost) == 0:
                break_flag = True

        if break_flag:
            break

    for item in chofuku2:
        item.sort()
    for item in chofuku3:
        item.sort()
    for item in chofuku4:
        item.sort()

    (
        count2_,
        count3_,
        count4_,
        count2_counti_,
        count3_counti_,
        count4_counti_,
        chofuku2_,
        chofuku3_,
        chofuku4_,
        chofuku2_tmps_,
        chofuku3_tmps_,
        chofuku4_tmps_,
    ) = count_first()

    assert count2 == count2_
    assert count3 == count3_
    assert count4 == count4_
    assert count2_counti == count2_counti_
    assert count3_counti == count3_counti_
    assert count4_counti == count4_counti_
    assert chofuku2 == chofuku2_
    assert chofuku3 == chofuku3_
    assert chofuku4 == chofuku4_
    assert chofuku2_tmps == chofuku2_tmps_
    assert chofuku3_tmps == chofuku3_tmps_
    assert chofuku4_tmps == chofuku4_tmps_

    cost_ = calc_cost()
    assert cost == cost_

    print("time_count_all", time_count_all)
    print("final_cost", cost)
    print("final_takugumi", takugumi)
    print("final_chofuku2(2-)", chofuku2[2:])
    print("final_chofuku3(2-)", chofuku3[2:])
    print("final_chofuku4(2-)", chofuku4[2:])

    if best_cost == [] or cost < best_cost:
        best_cost = cost
        best_takugumi = takugumi
        print("best_cost_new", best_cost)
        print("best_takugumi_new", best_takugumi)
        if sum(best_cost) == 0:
            break

    if i_set % 1000 == 0:
        print("i_set", i_set)
        print("best_cost_now", best_cost)
        print("best_takugumi_now", best_takugumi)


print("best_takugumi", best_takugumi)
takugumi = best_takugumi
(
    count2,
    count3,
    count4,
    count2_counti,
    count3_counti,
    count4_counti,
    chofuku2,
    chofuku3,
    chofuku4,
    chofuku2_tmps,
    chofuku3_tmps,
    chofuku4_tmps,
) = count_first()
cost = calc_cost()

assert cost == best_cost

assert best_takugumi[: min(s, len(FIX_TAKUGUMI))] == FIX_TAKUGUMI[: min(s, len(FIX_TAKUGUMI))]

print("best_cost", best_cost)
print("found")

# ----------------- 卓組ページ html の作成 -----------------

# takugumi_new[i][j]: 選手 i の j 戦目の卓番号 (1-indexed)
takugumi_new = [[0] * s for _ in range(p)]

for sind in range(s):
    for pind in range(p):
        p0 = takugumi[sind][pind]
        takugumi_new[p0][sind] = pind // N_GAME + 1

takugumi_new.sort()  # 選手を、卓番号配列の辞書順に並び替える

# fix_takugumi 用に、best_takugumi と同じ形式でも出力する
best_takugumi_sorted = [[] for _ in range(s)]
for s0 in range(s):
    for t0 in range(t):
        for p0 in range(p):
            if takugumi_new[p0][s0] == t0 + 1:
                best_takugumi_sorted[s0].append(p0)

print("takugumi_new", takugumi_new)
print("best_takugumi_sorted", best_takugumi_sorted)
print("FIX_TAKUGUMI", FIX_TAKUGUMI)


def make_header(title: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ja">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="keyword" content="麻雀, 卓組" />
    <title>{title} - 麻雀大会用卓組表</title>
    <link rel="stylesheet" href="../takugumi.css" type="text/css" />
  </head>
  <body bgcolor="#e0ffe0">
"""


def make_footer() -> str:
    return """  </body>
</html>
"""


def txt_to_list(path: str) -> list:
    with open(path, "r") as f:
        takugumi = []
        for item in f.readlines():
            takugumi.append(list(item.split()))
    return takugumi


def list_to_table(takugumi: list) -> str:
    """卓組表 takugumi_new を html の table 形式に変換する"""

    table_str = '    <table border="1" style="border-collapse: collapse">\n'

    table_str += '      <tr align="right">\n'
    table_str += "        <td></td>\n"
    for taisen_ind in range(s):
        table_str += f"        <td>{taisen_ind + 1}戦目</td>\n"
    table_str += "      </tr>\n"

    for player_ind, row in enumerate(takugumi):
        table_str += '      <tr align="right">\n'
        player_type = "選手"
        table_str += f"        <td>{player_type}{player_ind + 1}</td>\n"
        for col in row:
            table_str += "        <td>" + str(col) + "</td>\n"
        table_str += "      </tr>\n"
    table_str += "    </table>\n"
    return table_str


def make_cost():
    """卓組表の下の「コスト値の詳細」「重複同卓者の詳細」「2 人組の同卓回数」項目の作成"""
    # 「コスト値の詳細」

    cost_name = []

    cost_assert_ind = 0

    for s0 in range(s, 1, -1):
        cost_name += [
            f"{s0} 回同卓する 4 人組数",
            f"{s0} 回同卓する 3 人組数",
            f"{s0} 回同卓する 2 人組数",
        ]

    for s0 in range(s, 1, -1):
        cost_name += [
            f"「{s0} 回同卓する 4 人組リスト」に最も多く登場する選手の登場回数",
            f"「{s0} 回同卓する 3 人組リスト」に最も多く登場する選手の登場回数",
            f"「{s0} 回同卓する 2 人組リスト」に最も多く登場する選手の登場回数",
        ]

    assert len(cost_name) == len(cost)
    # assert cost[0] == 0

    ans = ""
    ans += '    <h3><a href="../kojin_duplicate_method.html#cost_value">コスト値</a>の詳細</h3>\n'
    if all(c == 0 for c in cost):
        ans += "    <p>コスト値はすべて 0。</p>\n"
    else:
        ans += "    <p>(値が 0 のものは省略)</p>\n"
        ans += "    <ul>\n"
        for name, c in zip(cost_name, cost):
            if c > 0:
                ans += f"      <li>{name}: {c}</li>\n"
        ans += "    </ul>\n"

    # 「重複同卓者の詳細」「2 人組の同卓回数」のための集計
    chofuku4 = [[] for _ in range(s + 1)]
    chofuku3 = [[] for _ in range(s + 1)]
    chofuku2 = [[] for _ in range(s + 1)]
    doutaku2 = [[0] * p for _ in range(p)]

    for p0, p1, p2, p3 in combinations(range(p), 4):
        cnt = 0
        for s0 in range(s):
            if takugumi_new[p0][s0] == takugumi_new[p1][s0] == takugumi_new[p2][s0] == takugumi_new[p3][s0]:
                cnt += 1
        chofuku4[cnt].append((p0, p1, p2, p3))

    for p0, p1, p2 in combinations(range(p), 3):
        cnt = 0
        for s0 in range(s):
            if takugumi_new[p0][s0] == takugumi_new[p1][s0] == takugumi_new[p2][s0]:
                cnt += 1
        chofuku3[cnt].append((p0, p1, p2))

    for p0, p1 in combinations(range(p), 2):
        cnt = 0
        for s0 in range(s):
            if takugumi_new[p0][s0] == takugumi_new[p1][s0]:
                cnt += 1
        chofuku2[cnt].append((p0, p1))
        doutaku2[p0][p1] = cnt
        doutaku2[p1][p0] = cnt

    # 「重複同卓者の詳細」
    ans += "    <h3>重複同卓者の詳細</h3>\n"
    chofuku2, chofuku3, chofuku4 = get_result_chofuku(count2, count3, count4)
    if (
        all(len(chofuku2[s0]) == 0 for s0 in range(s, 1, -1))
        and all(len(chofuku3[s0]) == 0 for s0 in range(s, 1, -1))
        and all(len(chofuku4[s0]) == 0 for s0 in range(s, 1, -1))
    ):
        assert cost[cost_assert_ind:] == [0] * (len(cost) - cost_assert_ind)
        ans += "    <p>重複同卓者なし。どの 2 人も互いに 0 ～ 1 回同卓。</p>\n"
    else:
        ans += "    <ul>\n"
        for s0 in range(s, 1, -1):
            assert cost[cost_assert_ind] == len(chofuku4[s0])
            cost_assert_ind += 1
            if len(chofuku4[s0]) > 0:
                ans += f"      <li>{s0} 回同卓する 4 人組 ({len(chofuku4[s0])} 組): "
                for ind, (p0, p1, p2, p3) in enumerate(chofuku4[s0]):
                    ans += f"({p0 + 1}, {p1 + 1}, {p2 + 1}, {p3 + 1})"
                    if ind < len(chofuku4[s0]) - 1:
                        ans += ", "
                ans += "</li>\n"

            assert cost[cost_assert_ind] == len(chofuku3[s0])
            cost_assert_ind += 1
            if len(chofuku3[s0]) > 0:
                ans += f"      <li>{s0} 回同卓する 3 人組 ({len(chofuku3[s0])} 組): "
                for ind, (p0, p1, p2) in enumerate(chofuku3[s0]):
                    ans += f"({p0 + 1}, {p1 + 1}, {p2 + 1})"
                    if ind < len(chofuku3[s0]) - 1:
                        ans += ", "
                ans += "</li>\n"

            assert cost[cost_assert_ind] == len(chofuku2[s0])
            cost_assert_ind += 1
            if len(chofuku2[s0]) > 0:
                ans += f"      <li>{s0} 回同卓する 2 人組 ({len(chofuku2[s0])} 組): "
                for ind, (p0, p1) in enumerate(chofuku2[s0]):
                    ans += f"({p0 + 1}, {p1 + 1})"
                    if ind < len(chofuku2[s0]) - 1:
                        ans += ", "
                ans += "</li>\n"
        ans += "    </ul>\n"

    # 「2 人組の同卓回数」
    ans += "    <h3>2 人組の同卓回数</h3>\n"
    ans += '    <table border="1" style="border-collapse: collapse">\n'

    ans += '      <tr align="right">\n'
    ans += "        <td></td>\n"
    for p0 in range(p):
        ans += f"        <td>選手{p0 + 1}</td>\n"
    ans += "      </tr>\n"

    for p0 in range(p):
        ans += '      <tr align="right">\n'
        ans += f"        <td>選手{p0 + 1}</td>\n"
        for p1 in range(p):
            val = str(doutaku2[p0][p1]) if p0 != p1 else "-"
            ans += "        <td>" + val + "</td>\n"
        ans += "      </tr>\n"
    ans += "    </table>\n"
    return ans


def takugumi_to_html(takugumi: list, title: str) -> str:
    print("start", title)
    return make_header(title) + list_to_table(takugumi) + make_cost() + make_footer()


with open(f"{t}taku_{p}nin_{s}sen_kojin.html", "w", encoding="utf-8") as f:
    f.write(takugumi_to_html(takugumi_new, f"{t} 卓 {p} 人 {s} 戦"))

end_time = time.time()
print("time [sec]:", end_time - start_time)
print("time [min]:", (end_time - start_time) / 60)

sys.stdout.close()
sys.stdout = sys.__stdout__
