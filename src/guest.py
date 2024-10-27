import sys
import time
from itertools import combinations
from random import randint, shuffle

N_GAME = 4  # ゲーム人数 (4 人麻雀)
g = int(sys.argv[1])  # ゲスト人数
t = int(sys.argv[2])  # 卓数
s = int(sys.argv[3])  # 対戦数
p = t * N_GAME  # 人数 (ゲスト含む)
times = 50000  # スワップ試行時に、この回数改善がなければ打ち切る (本実行では 50000)
sets = 10  # 初期値を変えて何セット試行するか (本実行では 10)

assert 1 <= g
assert 1 <= t
assert 1 <= s
assert 3 * g * s >= p - g  # (ゲストの対戦可能総人数) >= (一般選手数)

if g > t:
    g_fix = 1  # 卓を固定するゲストの人数
else:
    g_fix = g


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

    if pr < g:
        for p0 in [pa, pb, pc]:
            if p0 >= g:
                cnt = guest_count[pr][p0]
                guest_count_counti[pr][cnt] -= 1
                guest_count_counti[pr][cnt - 1] += 1
                guest_count[pr][p0] -= 1
                cnt = guest_count_sum[p0]
                guest_count_sum_counti[cnt] -= 1
                guest_count_sum_counti[cnt - 1] += 1
                guest_count_sum[p0] -= 1
    if pa < g:
        for p0 in [pr, pb, pc]:
            if p0 >= g:
                cnt = guest_count[pa][p0]
                guest_count_counti[pa][cnt] -= 1
                guest_count_counti[pa][cnt - 1] += 1
                guest_count[pa][p0] -= 1
                cnt = guest_count_sum[p0]
                guest_count_sum_counti[cnt] -= 1
                guest_count_sum_counti[cnt - 1] += 1
                guest_count_sum[p0] -= 1
    if pb < g:
        for p0 in [pr, pa, pc]:
            if p0 >= g:
                cnt = guest_count[pb][p0]
                guest_count_counti[pb][cnt] -= 1
                guest_count_counti[pb][cnt - 1] += 1
                guest_count[pb][p0] -= 1
                cnt = guest_count_sum[p0]
                guest_count_sum_counti[cnt] -= 1
                guest_count_sum_counti[cnt - 1] += 1
                guest_count_sum[p0] -= 1
    if pc < g:
        for p0 in [pr, pa, pb]:
            if p0 >= g:
                cnt = guest_count[pc][p0]
                guest_count_counti[pc][cnt] -= 1
                guest_count_counti[pc][cnt - 1] += 1
                guest_count[pc][p0] -= 1
                cnt = guest_count_sum[p0]
                guest_count_sum_counti[cnt] -= 1
                guest_count_sum_counti[cnt - 1] += 1
                guest_count_sum[p0] -= 1


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

    if pr < g:
        for p0 in [pa, pb, pc]:
            if p0 >= g:
                cnt = guest_count[pr][p0]
                guest_count_counti[pr][cnt] -= 1
                guest_count_counti[pr][cnt + 1] += 1
                guest_count[pr][p0] += 1
                cnt = guest_count_sum[p0]
                guest_count_sum_counti[cnt] -= 1
                guest_count_sum_counti[cnt + 1] += 1
                guest_count_sum[p0] += 1
    if pa < g:
        for p0 in [pr, pb, pc]:
            if p0 >= g:
                cnt = guest_count[pa][p0]
                guest_count_counti[pa][cnt] -= 1
                guest_count_counti[pa][cnt + 1] += 1
                guest_count[pa][p0] += 1
                cnt = guest_count_sum[p0]
                guest_count_sum_counti[cnt] -= 1
                guest_count_sum_counti[cnt + 1] += 1
                guest_count_sum[p0] += 1
    if pb < g:
        for p0 in [pr, pa, pc]:
            if p0 >= g:
                cnt = guest_count[pb][p0]
                guest_count_counti[pb][cnt] -= 1
                guest_count_counti[pb][cnt + 1] += 1
                guest_count[pb][p0] += 1
                cnt = guest_count_sum[p0]
                guest_count_sum_counti[cnt] -= 1
                guest_count_sum_counti[cnt + 1] += 1
                guest_count_sum[p0] += 1
    if pc < g:
        for p0 in [pr, pa, pb]:
            if p0 >= g:
                cnt = guest_count[pc][p0]
                guest_count_counti[pc][cnt] -= 1
                guest_count_counti[pc][cnt + 1] += 1
                guest_count[pc][p0] += 1
                cnt = guest_count_sum[p0]
                guest_count_sum_counti[cnt] -= 1
                guest_count_sum_counti[cnt + 1] += 1
                guest_count_sum[p0] += 1


def count_first():
    """各種同卓回数などを計算する (初回用であり、更新は add_count, remove_count で行う)"""

    count2 = [0] * pp  # count2[i]: 2 人組 i の同卓回数
    count3 = [0] * ppp  # count3[i]: 3 人組 i の同卓回数
    count4 = [0] * pppp  # count4[i]: 4 人組 i の同卓回数

    # guest_count[i][j]: ゲスト i と一般選手 j の同卓回数 (ゲスト同士の同卓はカウントしない)
    guest_count = [[0] * p for _ in range(g)]
    # guest_count_counti[i][j]: ゲスト i との同卓回数が j 回の一般選手数
    guest_count_counti = [[0] * (s + 1) for _ in range(g)]
    # guest_count_sum[i]: 一般選手 i の、ゲストとの (延べ) 総同卓回数
    guest_count_sum = [0] * p
    # guest_count_sum_counti[i]: ゲストとの (延べ) 総同卓回数が i 回の一般選手数
    guest_count_sum_counti = [0] * (s * g + 1)

    for takugumi_one in takugumi:
        for tind in range(t):
            for ind0 in range(N_GAME):
                for ind1 in range(ind0 + 1, N_GAME):
                    p0 = takugumi_one[tind * N_GAME + ind0]
                    p1 = takugumi_one[tind * N_GAME + ind1]
                    count2[getind2(p0, p1)] += 1
                    if p0 < g and p1 >= g:
                        guest_count[p0][p1] += 1
                        guest_count_sum[p1] += 1
                    if p1 < g and p0 >= g:
                        guest_count[p1][p0] += 1
                        guest_count_sum[p0] += 1

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

    for g0 in range(g):
        for p0 in range(g, p):
            guest_count_counti[g0][guest_count[g0][p0]] += 1
    for p0 in range(g, p):
        guest_count_sum_counti[guest_count_sum[p0]] += 1

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
        guest_count,
        guest_count_counti,
        guest_count_sum,
        guest_count_sum_counti,
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
    # コストには以下の優先順位を定める
    # 0.
    # ゲストとの総同卓回数が 0 回 である一般選手 (=ゲスト以外の選手) の数、
    # ゲスト1と同卓しない一般選手数、...、ゲストgと同卓しない一般選手数
    cost = [guest_count_sum_counti[0]]
    for g0 in range(g):
        cost.append(guest_count_counti[g0][0])

    if g > t:
        # 1. [ゲスト同士の同卓がある場合のみ]
        # ゲスト同士の同卓回数の総和、他ゲストとの同卓回数が最も多いゲストと最も少ないゲストの回数差
        g_sum_all = 0
        g_sums = [0] * g
        for g0 in range(g):
            for g1 in range(g0 + 1, g):
                # guest_count はゲスト同士の同卓をカウントしていないので、count2 から計算
                cnt = count2[getind2(g0, g1)]
                g_sum_all += cnt
                g_sums[g0] += cnt
                g_sums[g1] += cnt
        cost.append(g_sum_all)
        cost.append(max(g_sums) - min(g_sums))

    # 2.
    # ゲストとの (延べ) 総同卓回数が s*g 回である一般選手数、...、ゲストとの (延べ) 総同卓回数が 2 回である一般選手数、
    # ゲスト1とs回同卓する一般選手数、...、ゲストgとs回同卓する一般選手数、
    # ...
    # ゲスト1と2回同卓する一般選手数、...、ゲストgと2回同卓する一般選手数
    for i in range(s * g, 1, -1):
        cost.append(guest_count_sum_counti[i])
    for i in range(s, 1, -1):
        for g0 in range(g):
            cost.append(guest_count_counti[g0][i])

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
    初期値の卓組 (一部ゲスト以外は卓番号がランダム) を生成する。
    詳細: https://tomii6614.web.fc2.com/guest_method.html の「方法」の 1
    """
    takugumi = []
    for _ in range(s):
        takugumi_one = [-1] * p
        gind = 0
        for i in range(g_fix):
            takugumi_one[gind] = i
            gind += N_GAME
        ind = 0
        tmp = list(range(g_fix, p))
        shuffle(tmp)
        for i in range(len(tmp)):
            while takugumi_one[ind] != -1:
                ind += 1
            takugumi_one[ind] = tmp[i]

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
        guest_count,
        guest_count_counti,
        guest_count_sum,
        guest_count_sum_counti,
        chofuku2,
        chofuku3,
        chofuku4,
        chofuku2_tmps,
        chofuku3_tmps,
        chofuku4_tmps,
    ) = count_first()
    cost = calc_cost()

    print("first_cost", cost)
    print("first_guest_count", guest_count)

    time_count = 0
    time_count_all = 0
    break_flag = False
    while True:
        # print(cost, guest_count)
        target0_ind = -1
        target1_ind = -1
        while True:
            sind = randint(0, s - 1)
            target0_ind = randint(1, p - 1)  # 0 番目は必ずゲストのため 1 から
            target1_ind = randint(1, p - 1)  # 0 番目は必ずゲストのため 1 から
            target0 = takugumi[sind][target0_ind]
            target1 = takugumi[sind][target1_ind]
            if target0_ind // N_GAME != target1_ind // N_GAME and target0 >= g_fix and target1 >= g_fix:
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
        guest_count_,
        guest_count_counti_,
        guest_count_sum_,
        guest_count_sum_counti_,
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
    assert guest_count == guest_count_
    assert guest_count_counti == guest_count_counti_
    assert guest_count_sum == guest_count_sum_
    assert guest_count_sum_counti == guest_count_sum_counti_
    assert chofuku2 == chofuku2_
    assert chofuku3 == chofuku3_
    assert chofuku4 == chofuku4_
    assert chofuku2_tmps == chofuku2_tmps_
    assert chofuku3_tmps == chofuku3_tmps_
    assert chofuku4_tmps == chofuku4_tmps_

    # guest_count ではゲスト同士の同卓をカウントしないはず
    for g0 in range(g):
        assert guest_count_sum[g0] == 0
        for g1 in range(g):
            assert guest_count[g0][g1] == 0

    cost_ = calc_cost()
    assert cost == cost_

    print("time_count_all", time_count_all)
    print("final_cost", cost)
    print("final_takugumi", takugumi)
    print("final_chofuku2(2-)", chofuku2[2:])
    print("final_chofuku3(2-)", chofuku3[2:])
    print("final_chofuku4(2-)", chofuku4[2:])
    print("final_guest_count", guest_count)

    if best_cost == [] or cost < best_cost:
        best_cost = cost
        best_takugumi = takugumi
        if sum(best_cost) == 0:
            break


print("best_takugumi", best_takugumi)
takugumi = best_takugumi
(
    count2,
    count3,
    count4,
    count2_counti,
    count3_counti,
    count4_counti,
    guest_count,
    guest_count_counti,
    guest_count_sum,
    guest_count_sum_counti,
    chofuku2,
    chofuku3,
    chofuku4,
    chofuku2_tmps,
    chofuku3_tmps,
    chofuku4_tmps,
) = count_first()
cost = calc_cost()

assert cost == best_cost

print("best_cost", best_cost)

if best_cost[0] == 0:
    print("found")
else:
    print("notfound")
    sys.exit()


# ----------------- 卓組ページ html の作成 -----------------


n_col = s
if g == 1:
    n_col += 1  # ゲストとの同卓回数
else:
    n_col += g + 1  # ゲストxとの同卓回数、いずれかのゲストとの同卓回数

takugumi_new = [[0] * n_col for _ in range(p)]

for sind in range(s):
    for pind in range(p):
        p0 = takugumi[sind][pind]
        takugumi_new[p0][sind] = pind // N_GAME + 1

for p0 in range(p):
    for g0 in range(g):
        takugumi_new[p0][s + g0] = guest_count[g0][p0]
for g0 in range(g):
    for g1 in range(g):
        takugumi_new[g0][s + g1] += count2[getind2(g0, g1)]

if g > 1:
    for p0 in range(p):
        takugumi_new[p0][-1] = sum(takugumi_new[p0][-1 - g : -1])

if g == 1:
    takugumi_new[g:] = sorted(takugumi_new[g:], key=lambda x: x[s], reverse=True)
else:
    for g0 in range(g - 1, -1, -1):
        takugumi_new[g:] = sorted(takugumi_new[g:], key=lambda x: x[s + g0], reverse=True)
    takugumi_new[g:] = sorted(takugumi_new[g:], key=lambda x: x[s + g], reverse=True)

print("takugumi_new", takugumi_new)  # ゲストとの同卓回数の列を追加した卓組表


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
    if g == 1:
        table_str += "        <td>ゲストとの同卓回数</td>\n"
    else:
        for g_ind in range(g):
            table_str += f"        <td>ゲスト{g_ind + 1}との同卓回数</td>\n"
        table_str += "        <td>ゲストとの総同卓回数</td>\n"
    table_str += "      </tr>\n"

    for player_ind, row in enumerate(takugumi):
        table_str += '      <tr align="right">\n'
        player_type = "ゲスト" if player_ind < g else "選手"
        table_str += f"        <td>{player_type}{player_ind + 1}</td>\n"
        for col in row:
            table_str += "        <td>" + str(col) + "</td>\n"
        table_str += "      </tr>\n"
    table_str += "    </table>\n"
    return table_str


def make_cost():
    """卓組表の下の「コスト値の詳細」「重複同卓者の詳細」項目の作成"""

    cost_name = ["どのゲストとも同卓しない選手 (ゲスト以外) の数"]

    for g0 in range(g):
        cost_name.append(f"ゲスト {g0+1} と同卓しない選手 (ゲスト以外) の数")

    if g > t:
        cost_name.append("ゲスト同士の同卓回数の総和")
        cost_name.append("他ゲストとの同卓回数が最も多いゲストと最も少ないゲストの回数差")

    for sg0 in range(s * g, 1, -1):
        cost_name.append(f"ゲストとの総同卓回数が {sg0} 回である選手 (ゲスト以外) の数")
    for s0 in range(s, 1, -1):
        for g0 in range(g):
            cost_name.append(f"ゲスト {g0+1} と {s0} 回同卓する選手 (ゲスト以外) の数")

    cost_assert_ind = len(cost_name)

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
    assert cost[0] == 0

    ans = ""
    ans += '    <h3><a href="../guest_method.html#cost_value">コスト値</a>の詳細</h3>\n'
    if all(c == 0 for c in cost):
        ans += "    <p>コスト値はすべて 0。</p>\n"
    else:
        ans += "    <p>(値が 0 のものは省略)</p>\n"
        ans += "    <ul>\n"
        for name, c in zip(cost_name, cost):
            if c > 0:
                ans += f"      <li>{name}: {c}</li>\n"
        ans += "    </ul>\n"

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
    return ans


def takugumi_to_html(takugumi: list, title: str) -> str:
    print("start", title)
    return make_header(title) + list_to_table(takugumi) + make_cost() + make_footer()


with open(f"{t}taku_{p}nin_{s}sen_{g}guest.html", "w", encoding="utf-8") as f:
    f.write(takugumi_to_html(takugumi_new, f"{t} 卓 {p} 人 {s} 戦 {g} ゲスト"))

end_time = time.time()
print("time[s]:", end_time - start_time)
