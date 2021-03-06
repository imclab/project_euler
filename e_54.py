#!/usr/bin/env python
'''
Created on 11 sept. 2013

@author: Julien Lengrand-Lambert

DESCRIPTION: Solves problem 54 of Project Euler

Ranking Description
High Card: Highest value card.
One Pair: Two cards of the same value.
Two Pairs: Two different pairs.
Three of a Kind: Three cards of the same value.
Straight: All cards are consecutive values.
Flush: All cards of the same suit.
Full House: Three of a kind and a pair.
Four of a Kind: Four cards of the same value.
Straight Flush: All cards are consecutive values of same suit.
Royal Flush: Ten, Jack, Queen, King, Ace, in same suit.

The file, poker.txt, contains one-thousand random hands dealt to two players.
Each line of the file contains ten cards (separated by a single space):
the first five are Player 1's cards and the last five are Player 2's cards.
You can assume that all hands are valid (no invalid characters or repeated
    cards), each player's hand is in no specific order, and in each hand there
is a clear winner.

How many hands does Player 1 win?
'''
import collections

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

class PokerRanking:

    _ranks=enum("High_Card",
                "One_Pair",
                "Two_Pairs",
                "Three_of_a_Kind",
                "Straight",
                "Flush",
                "Full_House",
                "Four_of_a_Kind",
                "Straight_Flush",
                "Royal_Flush")

    def calculate_hand_rank(self, hand):
        """
        Given a PokerHand, calculate its value
        The Poker hand is assumed to be sorted by value
        """
        rank = None
        if(self.is_straight(hand)):
            straight = True
            rank = self._ranks.Straight
        else:
            straight = False

        if(self.is_flush(hand)):
            flush = True
            rank = self._ranks.Flush  # this is better!
        else:
            flush = False

        if straight or flush:  # We gonna finish early
            if straight and flush:  # even better news
                if self.is_royal_flush(hand):
                    rank = self._ranks.Royal_Flush  # Jackpot!
                else:
                    rank = self._ranks.Straight_Flush  # Not bad :)


        else:  # We have something less funny
            rank = self.same_cards(hand)  # All combinaisons that involve having several times the same cards

        return rank

    def same_cards(self, hand):
        """
        The hand s rank is based on pairs, or other card combination.
        We gonna search which
        """
        vals = [card.value for card in hand.cards]

        combs = collections.Counter(vals).items()
        # sorting by card count
        combs = sorted(combs, key = lambda x: x[1], reverse=True)

        if len(combs) == 5:
            rank = self._ranks.High_Card  # crappy hand
        elif len(combs) == 4:
            rank = self._ranks.One_Pair
        elif len(combs) == 3:
            # Two pairs, or Three of a Kind
            if combs[0][1] == 3:
                rank = self._ranks.Three_of_a_Kind
            else:
                rank = self._ranks.Two_Pairs
        elif len(combs) == 2:
            # Full House or Four of a Kind
            if combs[0][1] == 4:
                rank = self._ranks.Four_of_a_Kind
            else:
                rank = self._ranks.Full_House
        else:
            raise Exception("Unable to find player's rank!")

        return rank

    def is_flush(self, hand):
        """
        Define whether all cards in the given hand have the same suit.
        Returns a boolean
        """
        first_color = hand.cards[0].color
        bools = [card.color == first_color for card in hand.cards]
        return (len([x for x in bools if x is True]) == len(bools))

    def is_royal_flush(self, hand, check=False):
        """
        Testing if we have a royal flush
        We may check whether we have a flush and a straight first.
        But in our current context, we already know this, so this is easier
        """
        if check:
            straight = self.is_straight(hand)
            flush = self.is_flush(hand)
            res = (straight is True and flush is True)
        else:
            res = True

        if res:
            if hand.cards[0].value == Card._values[-1]:  # Highest value
                return True

        return False  # Not Royal Flush

    def is_straight(self, hand):
        """
        Detect whether the user has a straight hand or not
        """
        list_values = [Card._values.index(card.value) for card in hand.cards]

        for idx in range(len(list_values) - 1):

            diff = list_values[idx] - list_values[idx + 1]

            if diff != 1:
                return False
        return True


class PokerRank:
    """
    Defines a set of cards rank, with all info needed to
    precisely compare two ranks
    """
    def __init__(self, rank_val, cards):
        self.cards = cards
        self.rank_val = rank_val # Should be one of the rank enums

        #FIXME: This is a copy paste, and should probably be removed
        vals = [card.value for card in self.cards]
        combs = collections.Counter(vals).items()
        # sorting by card count
        combs = sorted(combs, key = lambda x: x[1], reverse=True)
        self.combs = [comb[0] for comb in combs]

        # ugly hack here
        self.more = [comb[0] for comb in combs if comb[1] > 1] # here we sort by card count
        self.single = [comb[0] for comb in combs if comb[1] == 1] # but for single cards, we have to sort by value
        self.single = sorted(self.single, key = lambda x: Card._values.index(x), reverse=True)
        self.combs = self.more + self.single

    def __eq__(self, other_rank):
        """
        Defines whether two ranks are equal
        """
        if self.rank_val != other_rank.rank_val:
            return False
        else:
            # we also have to check each card
            if len(self.combs) != len(other_rank.combs):
                raise AttributeError("both ranks are supposed to have the same \
                    number of cards!")

            for idx in range(len(self.combs)):
                if self.combs[idx] != other_rank.combs[idx]:
                    return False

        return True  # True if we go till there.

    def __gt__(self, other_rank):
        "Define whether our rank if better than the other"
        if self.rank_val > other_rank.rank_val:
            return True

        # We have to check the card values in care we have the same combination
        if self.rank_val == other_rank.rank_val:
            # let the fun begin!
            ctr = 0
            while(ctr < range(len(self.combs))):
                idx_1 = Card._values.index(self.combs[ctr])
                idx_2 = Card._values.index(other_rank.combs[ctr])
                if idx_2 > idx_1:
                    return False
                elif idx_1 > idx_2:
                    return True

                ctr += 1;

        return False

    def __ge__(self, other_rank):
        return (self.__gt__(other_rank) or self.__eq__(other_rank))

    def __st__(self, other_rank):
        return not(self.__ge__(other_rank))

    def __se__(self, other_rank):
        return not(self.__gt__(other_rank))

class PokerGame:
    """
    A game is defined as two players having a hand of 5 cards each.
    """
    def __init__(self, hand_1, hand_2):  # Could be more. Use lists instead
        # Should be PokerHands
        self.hand_1 = hand_1
        self.hand_1_rank = 0
        self.hand_2 = hand_2
        self.hand_2_rank = 0

class PokerHand:
    def __init__(self, cards):
        # should be 5 cards in a poker hand.
        if len(cards) !=5 :
            raise AttributeError("A Poker hand should be 5 cards")
        # cards sorted on creation
        self.cards = cards
        self.sort_hand()

    def __str__(self):
        "How to print a full poker hand"
        hand = ""
        for card in self.cards:
            hand += card.__str__() + " "
        return hand

    def sort_hand(self):
        """
        Sorts a hand of cards in descending order.
        """
        sorted_hand = list(self.cards)
        sorted_hand.sort(key=lambda x: Card._values.index(x.value), reverse=True)
        self.cards = sorted_hand

class Card:
    _values = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    _colors = ["H", "C", "S", "D"]
    def __init__(self, value, color):
        self.value = value
        self.color = color

    def __str__(self):
        """
        How to print a card
        """
        return self.value + self.color

##

def load_data(line):
    """
    Processes the input line according to the Description
    Returns a list of two hands of poker players.
    """
    cards_in_poker = 5

    res = line.rstrip() # also removes eol
    res_spl = res.split(" ")

    # creating left and right player's hands
    left = res_spl[:cards_in_poker]
    right = res_spl[cards_in_poker:]

    return [left, right]

def create_game(data):
    """
    Transforms a list of poker cards into a proper Poker game
    """
    def create_hand(cards):
        """
        Create a poker hand out of a list of cards
        """
        if len(cards) != 5:
            raise AttributeError("Expecting 5 cards!")

        poker_cards = [Card(card[0], card[1]) for card in cards]
        return PokerHand(poker_cards)

    game = PokerGame(create_hand(data[0]), create_hand(data[1]))
    return game

def who_wins(game):
    """
    Returns the index of the player who won the game in a game with several
    hands.
    Currently works with only 2 hands. We could generalize that easily.
    """
    pok = PokerRanking()
    rank_1 = PokerRank(pok.calculate_hand_rank(game.hand_1), game.hand_1.cards)
    rank_2 = PokerRank(pok.calculate_hand_rank(game.hand_2), game.hand_2.cards)


    if rank_1 > rank_2:
        return 1, [rank_1, rank_2]
    elif rank_1 < rank_2:
        return 2, [rank_1, rank_2]
    else:
        return 0, [rank_1, rank_2]

def winning_hands(filename, player=1):
    """
    Returns the number of winning hands for player 1 or 2
    """
    file = open(filename, "r")

    wins_1 = 0
    wins_2 = 0
    draws = 0
    played = 0

    for line in file :
        # loads and prepares data
        data = load_data(line)
        game = create_game(data)

        # finds winner
        ret, ranks = who_wins(game)
        if ret == 1:
            wins_1 += 1
        elif ret == 2:
            wins_2 += 1
        elif ret == 0:
            draws += 1
        else:
            raise Exception("Value not expected!")

        played += 1

    print "1 : " + str(wins_1) + ", 2 : " + str(wins_2) + ", draw : " + str(draws) + ", tot: " + str(played)

    file.close()

if __name__ == '__main__':
    winning_hands("./e_54_poker.txt")