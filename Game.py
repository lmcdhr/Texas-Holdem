# -*- coding:utf-8 -*-
# AUTHOR：Chen Yifan

import random
from functools import total_ordering

from Constants import *
from Judge import Judge

@total_ordering
class Card:
    def __init__(self, rank, suit):
        """
        初始化
        :param rank: the rank of cards, from 6 to 14, where 'A' is 14
        :param suit: 卡片的花色
        """

        self.rank = rank
        self.suit = suit

        self.symbols = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
        self.ranks = ['6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    def __str__(self):
        return "{:<2}{}".format(self.ranks[self.rank - 6], self.symbols[self.suit])

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __lt__(self, other):
        # We assume that 'A' is the largest rank in our rule
        return self.rank < other.rank


class Deck:
    def __init__(self):
        """
        初始化，生成所需要的扑克牌
        """
        ranks = range(6, 15)
        suits = ['S', 'H', 'D', 'C']

        self.deck = []

        for suit in suits:
            for rank in ranks:
                self.deck.append(Card(rank, suit))

    def shuffle(self):
        """
        洗牌
        :return: None
        """
        random.shuffle(self.deck)

    def deal(self):
        """
        发牌，删除并返回 self.deck 最末尾的牌
        :return:
        """
        return self.deck.pop()

class Player:
    def __init__(self, chips):
        """
        初始化筹码和押注
        :param chips: 筹码
        """
        self.chips = chips
        self.stake = 0
        self.cards = []

    def action(self, available_actions):
        self.show()
        while True:
            act = raw_input("Please enter your action：")
            bet = 0
            if act not in available_actions:
                print("Invalid input, please try again.")
            elif act == 'raise':
                bet = raw_input("Please enter your bet: ")
                try:
                    bet = int(bet)
                    return act, bet
                except ValueError:
                    print("Invalid input, please try again.")
            else:
                return act, bet

    def bet(self, how_much):
        self.stake += how_much
        self.chips -= how_much

    def show(self):
        print("Chips: {:<6} Stake: {:<6} Cards: {card1}, {card2} \n".format(self.chips,
                                                              self.stake,
                                                              card1 = self.cards[0],
                                                              card2 = self.cards[1]))


class GameServer:
    """
    游戏服务器
    """
    def __init__(self):
        """
        By default player1 is the small blind
        """
        self.deck = Deck()
        self.player1 = Player(INITIAL_CHIPS)
        self.player2 = Player(INITIAL_CHIPS)
        self.flop = []
        self.turn = None
        self.river = None

        self.this_player = self.player2
        self.other_player = self.player1 # 一局开始前会对换一次玩家

        self.last_action = None

    def check_winner(self):
        """
        check if the chips of one player is less than the BIG_BLIND_BET. If so, the other
        player is the winner
        :return: 0, 1 or 2. 0 means no winner, 1 means player1 wins, 2 means player2 wins
        """
        if self.player1.chips <= BIG_BLIND_BET:
            return 2
        elif self.player2.chips <= BIG_BLIND_BET:
            return 1
        else:
            return 0

    def start_battle(self):
        # 一直比到一方筹码不足为止

        while True:
            winner = self.check_winner()
            if winner != 0:
                print("winner is player" + str(winner))
                return

            self.start_game()

    def reset_cards(self):
        self.player1.cards = []
        self.player2.cards = []
        self.deck = Deck()
        self.flop = []
        self.turn = None
        self.river = None

    def start_game(self):
        # 一轮游戏而已，问题不大
        if SHOW_MESSAGE:
            print("------ New game round ------\n")

        self.reset_cards()
        self.last_action = None
        # self.next_player()

        # 洗牌
        self.deck.shuffle()

        # 发牌和小盲注，不需要操作
        self.deal()
        self.blind_bet()

        # 发牌前
        if self.preflop_round():
            return

        # 发完 flop 牌
        if self.flop_round():
            return

        # 发完 turn 牌
        if self.turn_round():
            return

        # 发完 river 牌
        if self.river_round():
            return
        else:
            winner = self.showdown()
            self.stake_allocating(winner)
            return

    def deal(self):
        # Deal two cards to each player
        for _ in range(2):
            self.player1.cards.append(self.deck.deal())
            self.player2.cards.append(self.deck.deal())

        for _ in range(3):
            self.flop.append(self.deck.deal())

        self.turn = self.deck.deal()
        self.river = self.deck.deal()

        if SHOW_MESSAGE:
            print("Dealing cards to players.")
            print("Player1:")
            self.player1.show()
            print("Player2:")
            self.player2.show()

    def blind_bet(self):
        """
        Make small and big blind bets automatically
        :return:
        """
        self.this_player.bet(SMALL_BLIND_BET)
        self.other_player.bet(BIG_BLIND_BET)
        if SHOW_MESSAGE:
            print("Making blind bets.")
            print("Player1:")
            self.player1.show()
            print("Player2:")
            self.player2.show()

    def check_available_actions(self):
        available_actions = ['fold']

        if self.this_player.stake == self.other_player.stake:
            available_actions.append("check")

        if (self.this_player.stake < self.other_player.stake
                <= self.this_player.stake + self.this_player.chips):
            available_actions.append("call")

        if (self.this_player.chips + self.this_player.stake
                >= self.other_player.stake + BIG_BLIND_BET):
            available_actions.append("raise")

        if (self.this_player.stake + self.this_player.chips
                < self.other_player.stake):
            available_actions.append("all-in")

        return available_actions

    def showdown(self):
        public = self.flop + [self.turn, self.river]
        list1 = self.player1.cards + public
        list2 = self.player2.cards + public
        judge = Judge(list1, list2)
        judge.show()
        winner = judge.compare()

        return winner

    def next_player(self):
        # 将行动权交给下一个玩家
        self.this_player, self.other_player = self.other_player, self.this_player

    def stake_allocating(self, winner):
        if winner == 0:
            self.player1.chips += self.player1.stake
            self.player2.chips += self.player2.stake
        elif winner == 1:
            if self.player1.stake >= self.player2.stake:
                self.player1.chips += (self.player1.stake + self.player2.stake)
            else:
                self.player1.chips += (self.player1.stake
                                       + int(self.player1.stake / self.player2.stake)
                                       * self.player2.stake)
                self.player2.chips += (self.player2.stake
                                       - int(self.player1.stake / self.player2.stake)
                                       * self.player2.stake)
        else:
            if self.player2.stake >= self.player1.stake:
                self.player2.chips += (self.player2.stake + self.player1.stake)
            else:
                self.player2.chips += (self.player2.stake
                                       + int(self.player2.stake / self.player1.stake)
                                       * self.player1.stake)
                self.player1.chips += (self.player1.stake
                                       - int(self.player2.stake / self.player1.stake)
                                       * self.player1.stake)

    def preflop_round(self):

        self.last_action = None
        if SHOW_MESSAGE:
            print("Current stage is preflop.")

        while True:
            if SHOW_MESSAGE:
                if self.this_player == self.player1:
                    print("\nCurrent player is player1")
                else:
                    print("\nCurrent player is player2")

            act, bet = self.this_player.action(self.check_available_actions())
            if act == 'call':
                how_much = self.other_player.stake - self.this_player.stake
                self.this_player.bet(how_much)

                self.last_action = 'call'
                self.next_player()
            elif act == 'all-in':
                winner = self.showdown()
                self.stake_allocating(winner)
                return True

            elif act == 'fold':
                if self.this_player == self.player1:
                    winner = 2
                else:
                    winner = 1
                self.stake_allocating(winner)
                return True

            elif act == 'check':
                if self.last_action == 'check':
                    return False
                else:
                    self.last_action = 'check'
                    self.next_player()

            elif act == 'raise':
                if bet + self.this_player.stake >= self.other_player.stake:
                    self.this_player.bet(bet)
                    self.last_action = 'raise'
                    self.next_player()
                else:
                    print("Not enough bets. Please try again.")
                    continue

    def flop_round(self):
        self.last_action = None
        if SHOW_MESSAGE:
            print("Current stage is flop.")
            for i in range(len(self.flop)):
                print(self.flop[i])

        while True:
            if SHOW_MESSAGE:
                if self.this_player == self.player1:
                    print("\nCurrent player is player1")
                else:
                    print("\nCurrent player is player2")

            act, bet = self.this_player.action(self.check_available_actions())
            if act == 'call':
                how_much = self.other_player.stake - self.this_player.stake
                self.this_player.bet(how_much)

                self.last_action = 'call'
                self.next_player()
            elif act == 'all-in':
                winner = self.showdown()
                self.stake_allocating(winner)
                return True

            elif act == 'fold':
                if self.this_player == self.player1:
                    winner = 2
                else:
                    winner = 1
                self.stake_allocating(winner)
                return True

            elif act == 'check':
                if self.last_action == 'check':
                    return False
                else:
                    self.last_action = 'check'
                    self.next_player()

            elif act == 'raise':
                if bet + self.this_player.stake >= self.other_player.stake:
                    self.this_player.bet(bet)
                    self.last_action = 'raise'
                    self.next_player()
                else:
                    print("Not enough bets. Please try again.")
                    continue


    def turn_round(self):
        self.last_action = None
        if SHOW_MESSAGE:
            print("Current stage is turn.")
            print(self.turn)

        while True:
            if SHOW_MESSAGE:
                if self.this_player == self.player1:
                    print("\nCurrent player is player1")
                else:
                    print("\nCurrent player is player2")

            act, bet = self.this_player.action(self.check_available_actions())
            if act == 'call':
                how_much = self.other_player.stake - self.this_player.stake
                self.this_player.bet(how_much)

                self.last_action = 'call'
                self.next_player()
            elif act == 'all-in':
                winner = self.showdown()
                self.stake_allocating(winner)
                return True

            elif act == 'fold':
                if self.this_player == self.player1:
                    winner = 2
                else:
                    winner = 1
                self.stake_allocating(winner)
                return True

            elif act == 'check':
                if self.last_action == 'check':
                    return False
                else:
                    self.last_action = 'check'
                    self.next_player()

            elif act == 'raise':
                if bet + self.this_player.stake >= self.other_player.stake:
                    self.this_player.bet(bet)
                    self.last_action = 'raise'
                    self.next_player()
                else:
                    print("Not enough bets. Please try again.")
                    continue

    def river_round(self):
        self.last_action = None
        if SHOW_MESSAGE:
            print("Current stage is river.")
            print(self.river)

        while True:
            if SHOW_MESSAGE:
                if self.this_player == self.player1:
                    print("\nCurrent player is player1")
                else:
                    print("\nCurrent player is player2")

            act, bet = self.this_player.action(self.check_available_actions())
            if act == 'call':
                how_much = self.other_player.stake - self.this_player.stake
                self.this_player.bet(how_much)

                self.last_action = 'call'
                self.next_player()
            elif act == 'all-in':
                winner = self.showdown()
                self.stake_allocating(winner)
                self.next_player()
                return True

            elif act == 'fold':
                if self.this_player == self.player1:
                    winner = 2
                else:
                    winner = 1
                self.stake_allocating(winner)
                self.next_player()
                return True

            elif act == 'check':
                if self.last_action == 'check':
                    return False
                else:
                    self.last_action = 'check'
                    self.next_player()

            elif act == 'raise':
                if bet + self.this_player.stake >= self.other_player.stake:
                    self.this_player.bet(bet)
                    self.last_action = 'raise'
                    self.next_player()
                else:
                    print("Not enough bets. Please try again.")
                    continue


if __name__ == '__main__':
    server = GameServer()

    server.start_battle()
