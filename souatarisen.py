#!/usr/bin/python
# -*- coding: utf-8 -*-

# (3n+1)卓(4(3n+1))人(4n+1)回戦の総当たり戦の卓組のコード、最初の段階から自動でやるプログラム。卓数を入力。時間計測あり。
# 暫定版です。数年前に書いたコードなので、これから解読し、さらに手直しをします。

def sa(a, b):  # リストaの要素からリストbの要素を引いたリストを返す
    set_ab = set(a) - set(b)
    list_ab = list(set_ab)
    return list_ab

def tai(n, tais2):  # 0,1,2,...,2n,2n,...,2,1,0,1,...
    if n >= nn2 + 1:
        if n >= tais2:
            if n >= tais2 + nn2 + 1:
                n = tais2 - (n - tais2)
            else:
                n = n - tais2
        else:
            n = tais2 - n
    return n

def hantei(G2, t2, k2, i2, j2):
    for pp in range(k2):
        if G2[t2][pp][0] == i2:
            return 1
        if G2[t2][pp][1] == j2:
            return 1
    return 0

def ikkaisen(n, n_tables, nn3):
    T = [0 for i in range(n_tables)]

    T[0] = [A[0], B[0], C[0], D[0]]
    for i in range(0, nn3):
        T[i + 1] = [B[N[0][i][0]], B[N[0][i][1]], C[N[0][i][2]],
                    C[N[0][i][3]]]
        T[i + nn3 + 1] = [C[N[1][i][0]], C[N[1][i][1]], D[N[1][i][2]],
                          D[N[1][i][3]]]
        T[i + nn3 * 2 + 1] = [D[N[2][i][0]], D[N[2][i][1]],
                              B[N[2][i][2]], B[N[2][i][3]]]

    return T

def narabekae_issenbun(t):
    V = []
    for p in range(nin):
        V.append(-3)

    for k in range(nin):
        for i in range(n_tables):
            for j in range(4):
                if U[t][i][j] == k:
                    V[k] = i
                    break
            if V[k] != -3:
                break
    return V


if __name__ == '__main__':
    from sys import argv
    n_tables = int(argv[1])  # 卓数
    if n_tables % 3 != 1:
        raise ValueError('number of tables must be equivalent to 1 modulo 3.'
                         )

    nn = int((n_tables - 1) / 3)  # n
    nn2 = 2 * nn
    nin = 4 * n_tables  # 人数
    tais = 4 * nn + 1  # 対戦数

    import time
    start = time.time()




    E = [[[0, 0] for i in range(nn2)] for j in range(nn2)]

    for i in range(nn2):
        for j in range(nn2):
            if i != j:
                a = min(i, j)
                b = max(i, j)
                E[i][j] = [b - a, tai(2 * (a + 1) - 1 + b - a, tais)]

    F = [i + 1 for i in range(nn2)]
    itaisho = [i for i in range(nn2)]
    jtaisho = [i for i in range(nn2)]

    G = [[[-1, -1] for i in range(nn)] for j in range(3)]

    itaishokakunou = [0, 0, 0]
    jtaishokakunou = [0, 0, 0]




    # print(F)

    fl = 0
    yar = 0
    t = 0
    while t <= 2:
        k = 0
        while k <= nn - 1:
            if yar == 0:
                if k == 0:
                    i = 0
                else:
                    i = G[t][k - 1][0]
                    fl = 1
            while i <= nn2 - 1:
                if yar == 0:
                    if fl == 1:
                        if k == 0:
                            j = 0
                        else:
                            j = G[t][k - 1][1] + 1
                            if j == nn2:
                                j = 0
                                i = i + 1
                                if i == nn2:
                                    i = nn2 - 1
                                    j = nn2
                    else:
                        j = 0
                yar = 0
                fl = 0
                while j <= nn2 - 1:

                    # print([t,k,i,j])

                    if E[i][j][0] in F and E[i][j][1] in F and i in itaisho \
                        and j in jtaisho and hantei(G, t, k, i, j) == 0:
                        G[t][k] = [i, j]
                        F = sa(F, E[i][j])
                        i = 1000
                        j = 1000
                    j = j + 1
                i = i + 1
                if i == nn2 and G[t][k] == [-1, -1]:  # 最後まで見つけられなかったとき、kを1つ戻す
                    yar = 1
                    k = k - 1
                    if k == -1:
                        t = t - 1
                        k = nn - 1
                    i = G[t][k][0]
                    j = G[t][k][1] + 1
                    if j == nn2:
                        i = i + 1
                        j = 0
                    if k == nn - 1:  # tが1つ戻ったとき
                        itaisho = itaishokakunou[t]
                        jtaisho = jtaishokakunou[t]
                        F = []
                    F.append(E[G[t][k][0]][G[t][k][1]][0])
                    F.append(E[G[t][k][0]][G[t][k][1]][1])
                    G[t][k] = [-1, -1]
            k = k + 1
        F = []
        dum = []
        for ff in range(nn2):
            F.append(ff + 1)
            dum.append(ff)
        for oo in range(nn):
            dum = sa(dum, [G[t][oo][1]])
        itaisho = dum
        if t == 1:
            dum2 = []
            for uu in range(nn2):
                dum2.append(uu)
            for qq in range(nn):
                dum2 = sa(dum2, [G[0][qq][0]])
            jtaisho = dum2
        itaishokakunou[t] = itaisho
        jtaishokakunou[t] = jtaisho
        t = t + 1

    # print(G)

    N = [[0 for i in range(nn)] for j in range(3)]

    for a in range(0, 3):
        for b in range(0, nn):
            p = G[a][b][0]
            q = G[a][b][1]
            N[a][b] = [nn2 - p, nn2 + 1 + p, nn2 - q, nn2 + 1 + q]

    A = [0]
    B = []
    C = []
    D = []
    for tt in range(tais):
        B.append(tt + 1)
        C.append(tt + tais + 1)
        D.append(tt + tais * 2 + 1)




    U = [0 for i in range(tais)]

    for m in range(tais):
        U[m] = ikkaisen(m, n_tables, nn)

        bb = B[0]
        cc = C[0]
        dd = D[0]

        for i in range(tais - 1):
            B[i] = B[i + 1]
            C[i] = C[i + 1]
            D[i] = D[i + 1]

        B[tais - 1] = bb
        C[tais - 1] = cc
        D[tais - 1] = dd

    # print(U)

    # U=[[[1回戦1卓],...,[1回戦(3n+1)卓]],[2回戦],...,[(4n+1)回戦]]

    W = [0 for i in range(tais)]




    for x in range(tais):
        W[x] = narabekae_issenbun(x)

    # print(W)

    # W=[[1回戦の(4(3n+1))人の卓番号],...,[(4n+1)回戦の(4(3n+1))人の卓番号]]

    for a in range(tais):
        for b in range(nin):
            W[a][b] = W[a][b] + 1

    # print(W)

    # 卓番号を 0~3n → 1~(3n+1) に

    f = open(str(n_tables) + 'sounc3.txt', 'w')
    for b in range(nin):
        sep = ''
        for a in range(tais):
            f.write(sep)
            f.write(str(W[a][b]))
            sep = '\t'
        f.write('\n')

    f.close()

    # (卓数)sounc2.txtは縦軸がプレイヤー、横軸が戦数、成分が卓番号

    elapsed_time = time.time() - start
    print(elapsed_time)
