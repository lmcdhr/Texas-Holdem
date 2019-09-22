#!/usr/bin/env python
# coding: utf-8
# AUTHOR: Luo Mucheng

"""
lmcNB! lmcdhr!
"""


class Judge:
    def __init__(self, list1, list2):
        """
        每个玩家的可支配牌（5+2）list
        """
        self.list_player1 = list1
        self.list_player2 = list2

    def show(self):
        """
        test
        """
        print("player1:")
        for i in range(7):
            print(self.list_player1[i])
        print("player2:")
        for i in range(7):
            print(self.list_player2[i])

    def compare(self):
        """
        比较大小：-1（玩家1赢），0（平），1（玩家2赢）
        """
        result_1 = self.get_score(sorted(self.list_player1))
        result_2 = self.get_score(sorted(self.list_player2))
        print("score of player 1: " + str(result_1[0]))
        print("score of player 2: " + str(result_2[0]))
        return self.get_biggest(result_1, result_2)

    def get_biggest(self, result_1, result_2):
        if result_1[0] < result_2[0]:
            print("player 2 wins!")
            return 2
        elif result_1[0] == result_2[0]:
            print("tie!")
            return 0
        else:
            print("player 1 wins!")
            return 1

    def get_score(self, list):
        suit_list = []
        rank_list = []
        for c in list:
            suit_list.append(c.suit)
            rank_list.append(c.rank)
        """
        顺序：先找顺子
        """
        start_shunzi = self.find_shunzi(rank_list)
        temp = []
        """
        temp用来记临时分数，因为是否是顺子会先判断，但是如果他还是普通同花牌，分数会更高
        """
        if start_shunzi != -1:
            """
            是否是顺子，再根据是否同花分为同花顺和一般顺子
            """
            if self.if_tonghuashun(suit_list, start_shunzi):
                """
                 是否是同花顺，如果是，进一步判断是否是皇家同花顺
                 皇家同花顺直接return10分，同花顺返回9分和顶牌
                """
                if rank_list[start_shunzi] == 10:
                    return [10]
                else:
                    return [9, rank_list[start_shunzi + 4]]
            else:
                """
                一般顺子,将temp记为5分和顶牌，待下一步判断
                """
                temp = [5, rank_list[start_shunzi + 4]]
        tonghua_index = self.find_tonghua(suit_list)
        if tonghua_index != []:
            """
            是否是同花，如果可以是同花，返回6和5张牌值，因为这种牌型既不可能是葫芦也不可能是四条
            
            """
            tonghua_score = [6]
            for i in tonghua_index:
                tonghua_score.append(rank_list[i])
            return tonghua_score
        """
        不是同花，但是可以是顺子，则不可能是分数更高的四条和葫芦，则返回顺子的分数和顶牌
        """
        if temp != [] and temp[0] == 5:
            return temp
        """
        顺子同花判断完毕，接下来顺序是4条-》葫芦-》三条
        如果是四条，返回8分和第五张牌
        """
        sitiao_result = self.if_sitiao(rank_list)
        if sitiao_result != False:
            return [8, sitiao_result]
        """
        判断葫芦和三条，先找三条后判断是否满足葫芦
        """
        san_index = self.if_yousan(rank_list)
        if san_index != -1:
            temp = rank_list[0:san_index] + rank_list[san_index + 3:]
            for i in rank_list:
                if temp.count(i) == 2:
                    return [7, rank_list[san_index]]
            return [4, rank_list[san_index]]
        """
        判断对，先找一对，再找两对
        """
        er_pai = self.if_er(rank_list)
        if er_pai != -1:
            k = rank_list.index(er_pai)
            temp = rank_list[0:k] + rank_list[k + 2:]
            dierdui_pai = self.if_er(temp)
            if dierdui_pai != -1:
                return [3, er_pai, dierdui_pai]
            else:
                return [2, er_pai]
        """
        啥也不是，返回高牌一分和最大的五张牌
        """
        return [1, rank_list[2:7]]

    def find_shunzi(self, rank_list):
        start = -1
        quchong = sorted(set(rank_list), key=rank_list.index)
        if len(quchong) < 5:
            return -1
        for i in range(0, 3):
            if i + 4 < len(quchong) and quchong[i + 4] == rank_list[i] + 4:
                start = rank_list.index(quchong[i])
        return start

    def find_tonghua(self, suit_list):
        tonghua_suit_index = []
        count = 0
        """
        count是为了提取最大值最大的那一组同花牌
        """
        for i in ['S', 'H', 'D', 'C']:
            if suit_list.count(i) >= 5:
                for j in range(6, -1, -1):
                    if suit_list[j] == i and count < 5:
                        tonghua_suit_index.append(j)
                        count += 1
        return tonghua_suit_index

    def if_tonghuashun(self, suit_list, start):
        if suit_list[start] == suit_list[start + 1] == suit_list[start + 2] == suit_list[start + 3] == suit_list[
            start + 4]:
            return True
        else:
            return False

    def if_sitiao(self, rank_list):
        sitiao_pai = 0
        for i in range(6, 15):
            if rank_list.count(i) == 4:
                sitiao_pai = i
                index = rank_list.index(i)
                if index == 3:
                    return rank_list[2]
                else:
                    return rank_list[6]
        return False

    def if_yousan(self, rank_list):
        for i in range(6, 15):
            if rank_list.count(i) == 3:
                san_pai = i
                san_index = rank_list.index(i)
                return san_index
        return -1

    def if_er(self, rank_list):
        for i in range(len(rank_list) - 1, -1, -1):
            if rank_list.count(rank_list[i]) == 2:
                er_pai = rank_list[i]
                return er_pai
        return -1
