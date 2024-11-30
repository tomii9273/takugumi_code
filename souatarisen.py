#!/usr/bin/python
# -*- coding: utf-8 -*-

# (3n+1)卓(4(3n+1))人(4n+1)回戦の総当たり戦の卓組のコード、最初の段階から自動でやるプログラム。卓数を入力。時間計測あり。
# 暫定版です。数年前に書いたコードなので、これから解読し、さらに手直しをします。

from logging import getLogger
logger = getLogger(__name__)

def sa(a, b):  # リストaの要素からリストbの要素を引いたリストを返す
    set_ab = set(a) - set(b)
    list_ab = list(set_ab)
    return list_ab

def tai(n, n_games, nn2):  # 0,1,2,...,2n,2n,...,2,1,0,1,...
    if n >= nn2 + 1:
        if n >= n_games:
            if n >= n_games + nn2 + 1:
                n = n_games - (n - n_games)
            else:
                n = n - n_games
        else:
            n = n_games - n
    return n

def hantei(G2, t2, k2, i2, j2):
    for pair in G2[t2][:k2]:
        if pair[0] == i2 or pair[1]== j2:
            return 1
    return 0

def ikkaisen(n_tables, nn, A, B, C, D, N):
    T = [0 for i in range(n_tables)]

    T[0] = [A[0], B[0], C[0], D[0]]
    for i in range(0, nn):
        T[i          + 1] = [
                B[N[0][i][0]], B[N[0][i][1]], C[N[0][i][2]], C[N[0][i][3]]]
        T[i + nn     + 1] = [
                C[N[1][i][0]], C[N[1][i][1]], D[N[1][i][2]], D[N[1][i][3]]]
        T[i + nn * 2 + 1] = [
                D[N[2][i][0]], D[N[2][i][1]], B[N[2][i][2]], B[N[2][i][3]]]

    return T

def narabekae_issenbun(t, n_players, n_tables, U):
    V = [-3 for p in range(n_players)]

    for k in range(n_players):
        for i in range(n_tables):
            for j in range(4):
                if U[t][i][j] == k:
                    V[k] = i
                    break
            if V[k] != -3:
                break
    return V

class Searcher():
    def __init__(self, n_tables):
        if n_tables % 3 != 1:
            raise ValueError(
                    'number of tables must be equivalent to 1 modulo 3.')
        self.n_tables = n_tables
        self.nn = int((n_tables - 1) / 3)  # n
        self.nn2 = 2 * self.nn
        self.n_players = 4 * n_tables  # 人数
        self.n_games = 4 * self.nn + 1  # 対戦数

    def prepare(self):
        E = [[[0, 0] for i in range(self.nn2)] for j in range(self.nn2)]

        for i in range(self.nn2):
            for j in range(i):
                # here j < i holds.
                E[i][j] = [i - j, tai(i + j + 1, self.n_games, self.nn2)]
                E[j][i] = [i - j, tai(i + j + 1, self.n_games, self.nn2)]

        return E

    def search(self, E):
        F = list(range(1, self.nn2 + 1))
        itaisho = list(range(self.nn2))
        jtaisho = list(range(self.nn2))

        G = [[[-1, -1] for i in range(self.nn)] for j in range(3)]

        itaishokakunou = [0, 0, 0]
        jtaishokakunou = [0, 0, 0]

        fl = 0
        yar = 0
        t = 0
        while t <= 2:
            k = 0
            while k <= self.nn - 1:
                if yar == 0:
                    if k == 0:
                        i = 0
                    else:
                        i = G[t][k - 1][0]
                        fl = 1
                while i <= self.nn2 - 1:
                    if yar == 0:
                        if fl == 1:
                            if k == 0:
                                j = 0
                            else:
                                j = G[t][k - 1][1] + 1
                                if j == self.nn2:
                                    j = 0
                                    i = i + 1
                                    if i == self.nn2:
                                        i = self.nn2 - 1
                                        j = self.nn2
                        else:
                            j = 0
                    yar = 0
                    fl = 0
                    while j <= self.nn2 - 1:

                        # print([t,k,i,j])

                        if E[i][j][0] in F and E[i][j][1] in F and i in itaisho \
                            and j in jtaisho and hantei(G, t, k, i, j) == 0:
                            G[t][k] = [i, j]
                            F = sa(F, E[i][j])
                            i = 1000
                            j = 1000
                        j = j + 1
                    i = i + 1
                    if i == self.nn2 and G[t][k] == [-1, -1]:  # 最後まで見つけられなかったとき、kを1つ戻す
                        yar = 1
                        k = k - 1
                        if k == -1:
                            t = t - 1
                            k = self.nn - 1
                        i = G[t][k][0]
                        j = G[t][k][1] + 1
                        if j == self.nn2:
                            i = i + 1
                            j = 0
                        if k == self.nn - 1:  # tが1つ戻ったとき
                            itaisho = itaishokakunou[t]
                            jtaisho = jtaishokakunou[t]
                            F = []
                        F.append(E[G[t][k][0]][G[t][k][1]][0])
                        F.append(E[G[t][k][0]][G[t][k][1]][1])
                        G[t][k] = [-1, -1]
                k = k + 1
            F = []
            dum = []
            for ff in range(self.nn2):
                F.append(ff + 1)
                dum.append(ff)
            for oo in range(self.nn):
                dum = sa(dum, [G[t][oo][1]])
            itaisho = dum
            if t == 1:
                dum2 = []
                for uu in range(self.nn2):
                    dum2.append(uu)
                for qq in range(self.nn):
                    dum2 = sa(dum2, [G[0][qq][0]])
                jtaisho = dum2
            itaishokakunou[t] = itaisho
            jtaishokakunou[t] = jtaisho
            t = t + 1

        return G

    def generate_output(self, G):

        N = [[0 for i in range(self.nn)] for j in range(3)]

        for a in range(0, 3):
            for b in range(0, self.nn):
                p = G[a][b][0]
                q = G[a][b][1]
                N[a][b] = [self.nn2 - p, self.nn2 + 1 + p, self.nn2 - q, self.nn2 + 1 + q]

        A = [0]
        B = list(range(                   1,     self.n_games + 1))
        C = list(range(    self.n_games + 1, 2 * self.n_games + 1))
        D = list(range(2 * self.n_games + 1, 3 * self.n_games + 1))

        U = [0 for i in range(self.n_games)]

        for m in range(self.n_games):
            U[m] = ikkaisen(self.n_tables, self.nn, A, B, C, D, N)

            B = B[1:] + B[:1]
            C = C[1:] + C[:1]
            D = D[1:] + D[:1]

        # print(U)

        # U=[[[1回戦1卓],...,[1回戦(3n+1)卓]],[2回戦],...,[(4n+1)回戦]]

        W = [0 for i in range(self.n_games)]

        for x in range(self.n_games):
            W[x] = narabekae_issenbun(x, self.n_players, self.n_tables, U)

        # print(W)

        # W=[[1回戦の(4(3n+1))人の卓番号],...,[(4n+1)回戦の(4(3n+1))人の卓番号]]

        # print(W)

        # 卓番号を 0~3n → 1~(3n+1) に

        with open(str(self.n_tables) + 'sounc3.txt', 'w') as f:
            for b in range(self.n_players):
                f.write('\t'.join(str(W[a][b]+1) for a in range(self.n_games)))
                f.write('\n')

        # (卓数)sounc2.txtは縦軸がプレイヤー、横軸が戦数、成分が卓番号

def main(n_tables):
    searcher = Searcher(n_tables)
    searcher.generate_output(
            searcher.search(
                    searcher.prepare()))

if __name__ == '__main__':
    from sys import argv
    from datetime import datetime
    import logging
    logging.basicConfig(level=logging.INFO)
    start = datetime.now()
    main(int(argv[1]))
    logger.info('{}'.format(datetime.now() - start))
