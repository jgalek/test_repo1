#coding=utf-8
from flask import Flask, render_template, session, request, redirect, url_for
from collections import OrderedDict
app = Flask(__name__)
app.secret_key = "super secret key"

import random

"""
This program is for the card game Rummy.

Rules:
- Rummy is a card game based on making sets.
- From a stash(or hand) of 13 cards, 4 sets must be created (3 sets of 3, 1 set of 4).
- A valid set can either be a run or a book.
- One set must be a run WITHOUT using a joker.
- A run is a sequence of numbers in a row, all with the same suit.
	For example: 4 of Hearts, 5 of Hearts, and 6 of Hearts
- A book is a set in which the cards all have the same rank but must have different suits.
	For example: 3 of Diamonds, 3 of Spades, 5 of Clubs
- A joker is a card randomly picked from the deck at the start of the game.
- All jokers are considered free cards and can be used to complete sets.
- During each player's turn, the player may take a card from the pile or a card from the deck to help create sets.
  Immediately after, the player must drop a card into the pile so as not go over the 14 card limit.
- When a player has created all the sets, select the close game option and drop the excess card into the pile.
- Card with Rank 10 is represented as Rank T
"""
# constants to be used for the cards used in the game
SYMBOLS = ['S', 'D', 'H', 'C']
SUIT = ['Hearts', 'Clubs', 'Spades', 'Diamonds']
RANK = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
RANK_VALUE = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12,
              'K': 13}
SUIT_SYMBOLS = {'Hearts': 'H', 'Clubs': 'C', 'Spades': 'S', 'Diamonds': 'D'}


class Card:
    """ Card Class - Models a single Playing Card """

    def __init__(self, rank, suit):
        """ Class Constructor
      Args:
          rank: A valid RANK value - a single char
          suit: A valid SUIT value - a string
      Returns:
          No return value
      """
        self.rank = rank
        self.suit = suit
        self.isjoker = False

    def __str__(self):
        """ Helper for builtin __str__ function
      Args:
          no args.
      Returns:
          string representation of the Card.  For Joker a "-J" is added.
          for example for 4 of Hearts, returns 4H
              and if it is a Joker returns 4H-J
      """
        if self.isjoker:
            return (self.rank + SUIT_SYMBOLS[self.suit] + '-J')
        return (self.rank + SUIT_SYMBOLS[self.suit])

    def is_joker(self):
        """Status check to see if this Card is a Joker
      Args:
          no arguments
      Returns:
          True or False
      """
        return self.isjoker


class Deck:
    """ Deck Class - Models the card Deck """

    def __init__(self, packs):
        """ Class Constructor
      Args:
          packs: Number of packs used to create the Deck - int value
      Returns:
          No return value
      """
        self.packs = packs
        self.cards = []
        self.joker = None

        # Create all cards in the Deck
        for i in range(packs):
            for s in SUIT:
                for r in RANK:
                    self.cards.append(Card(r, s))

    def shuffle(self):
        """ Shuffle the Deck, so that cards are ordered in a random order
      Args:
          No args
      Returns:
          No return value
      """
        random.shuffle(self.cards)

    def draw_card(self):
        """ Draw a card from the top of the Deck
      Args:
          No args
      Returns:
          a Card Object
      """
        a = self.cards[0]
        self.cards.pop(0)
        return a

    def set_joker(self):
        """ Set the Joker Cards in the Deck
      A Card is selected at random from the deck as Joker.
      All cards with the same Rank as the Joker are also set to Jokers.
      Args:
          No args
      Returns:
          No returns
      """
        self.joker = random.choice(self.cards)

        # remove the Joker from Deck and display on Table for Players to see
        self.cards.remove(self.joker)

        for card in self.cards:
            if self.joker.rank == card.rank:
                card.isjoker = True


class Table:
    def __init__(self):
        self.stash = []
        self.cards = []


class Player:
    """ Player Class - Models Players Hand and play actions """

    def __init__(self, name, deck, game, table):
        """ Class Constructor
      Args:
          name: Name of the Player - string
          deck: Reference to the Deck Object that is part of the Game
          game: Reference to the Game object that is being played now
      Returns:
          No return value
      """

        self.stash = []  # Stash represents the hand of the Player.
        self.name = name
        self.deck = deck
        self.game = game
        self.table = table

    def deal_card(self, card):
        """ Deal a Card to the Player
      Args:
          card:  The Card object provided to Player as part of the deal
      Returns:
          No returns
      """
        try:
            self.stash.append(card)
            if len(self.stash) > 14:
                raise ValueError('ERROR: Player cannot have more than 14 cards during turn')
        except ValueError as err:
            print(err.args)

    def drop_card(self, card):
        """ Drop Card operation by the Player
      Args:
          card: The player input representation of the Card object
              that needs to be dropped.  For example: AC for Ace of Clubs
      Returns:
          No returns
      """
        # Get the actual card object from string representation
        card = get_object(self.stash, card)

        # Cannot drop a card if it is already not in stash
        if card not in self.stash:
            return False

        self.stash.remove(card)

        # Player dropped card goes to Pile
        self.game.add_pile(card)

        return True

    def close_game(self):
        """ Close Game operation by the Player
      Args:
          No args
      Returns:
          Success or Failure as True/False
      """
        # Divide the stash into 4 sets, 3 sets of 3 cards and 1 set of 4 cards
        number = input("How many cards you want to put on the table: ")
        if (int(number) != 3 and int(number) != 4):
            print('Bad number of card')
            return False
        set_array = []
        for i in range(0, int(number)):
            set_array.append(self.stash[i])

        # Need to count the number of sets that are runs without a joker.
        # 	There must be at least one run with out a joker
        # print('Justyna')
        # for s in set_array:
        #	if is_valid_run(s):
        #		count += 1
        # if count == 0:
        #	return False

        # Check if each of the sets is either a run or a book
        print(print_cards(set_array))
        if is_valid_run(set_array) == False and is_valid_book(set_array) == False and is_valid_run_joker(
                set_array) == False:
            return False

        # return True
        new_table_stash = []
        for i in range(0, int(number)):
            new_table_stash.append(set_array[i])
            self.stash.remove(set_array[i])
            if len(self.stash) == 1:
                return True
        self.table.stash.append(new_table_stash)

    def play(self):
        """ Play a single turn by the Player
      Args:
          No args
      Returns:
          Success or Failure as True/False
      """
        global table_stash
        table_stash = self.table.stash
        global name
        name = self.name
        global self_stash
        self_stash = self.stash
        global len_table_stash
        len_table_stash = len(self.table.stash)
        global len_self_stash
        len_self_stash = len(self.stash)
        pile = self_pile[0]


class Game:
    """ Game Class - Models a single Game """

    global self_pile
    self_pile = []

    def __init__(self, hands, deck, table):
        """ Class Constructor
          Args:
              hands:  represents the number of players in the game - an int
              deck: Reference to Deck Object
          Returns:
              No returns
      """
        self.players = []
        self.table = table
        print(hands)
        for i in range(hands):
            name = request.form.get('player-name-'+str(i+1))
            self.players.append(Player(name, deck, self, table))

    def display_pile(self):
        """ Displays the top of the Pile.
          Args:
              No args.
          Returns:
              No returns
      """
        if len(self_pile) == 0:
            print("Empty pile.")
        else:
            print("The card at the top of the pile is: ", self_pile[0])

    def add_pile(self, card):
        """ Adds card to the top of the Pile.
          Args:
              card:  The card that is added to top of the Pile
          Returns:
              No returns
      """
        self_pile.insert(0, card)

    def draw_pile(self):
        """ Draw the top card from the Pile.
          Args:
              No args
          Returns:
              Returns the top Card from the Pile - Card Object
      """
        if len(self_pile) != 0:
            return self_pile.pop(0)
        else:
            return None

    def play(self, i=0):
        """ Play the close_game.
          Args:
              No args
          Returns:
              No returns
      """

        while self.players[i].play() == False:
            print(chr(27) + "[2J")
            i += 1
            if i == len(self.players):
                i = 0
            #print("***", self.players[i].name, "to play now.")
            #input(self.players[i].name + " hit enter to continue...")

        # Game Over
        print("*** GAME OVER ***")
        print("*** ", self.players[i].name, " Won the game ***")


# global nonclass functions
def is_valid_book(sequence):
    """ Check if the sequence is a valid book.
       Args:
           sequence: an array of Card objects.  Array will have either 3 ro 4 cards
       Returns:
           Success or Failure as True/False
   """
    # Move all Jokers to the end of the sequence
    # while(sequence[0].isjoker == True):
    #	sequence.append(sequence.pop(0))

    # Compare Cards in sequnce with 0th Card, except for Jokers.
    # for card in sequence:
    #	if card.is_joker() == True:
    #		continue
    #	if card.rank != sequence[0].rank:
    #		return False

    if (len(sequence)<3):
        return False



    for i in range(1, len(sequence)):
        # print(RANK_VALUE[sequence[i].rank])
        # print( RANK_VALUE[(sequence[i-1].rank)])
        print('spr:')
        print(sequence[i])
        print(RANK_VALUE[sequence[i].rank])

        for x in range(0, len(sequence)):
            if sequence[i].suit == sequence[x].suit and i != x:
                return False

        if RANK_VALUE[sequence[i].rank] != RANK_VALUE[(sequence[i - 1].rank)]:
            # print('not equal')
            return False

    return True


def is_valid_run(sequence):
    """ Check if the sequence is a valid run.
       Args:
           sequence: an array of Card objects.  Array will have either 3 ro 4 cards
       Returns:
           Success or Failure as True/False
   """
    if (len(sequence)<3):
        return False

    RANK_VALUE["A"] = 1  # resetting value of A (may have been set to 14 in previous run)

    # Order the Cards in the sequence
    sort_sequence(sequence)

    # Check to see if all Cards in the sequence have the same SUIT
    # for card in sequence:
    #	if card.suit != sequence[0].suit:
    #		return False

    # this is to sort a sequence that has K, Q and A
    if sequence[0].rank == "A":
        if sequence[1].rank == "Q" or sequence[1].rank == "J" or sequence[1].rank == "K":
            RANK_VALUE[sequence[0].rank] = 14
            sort_sequence(sequence)

    # Rank Comparison
    for i in range(1, len(sequence)):
        for x in range(0, len(sequence)):
            if sequence[i].suit != sequence[x].suit and i != x:
                return False
        if RANK_VALUE[sequence[i].rank] != RANK_VALUE[(sequence[i - 1].rank)] + 1:
            # print('są nie pokolei')
            return False

    return True


def is_valid_run_joker(sequence):
    """ Check if the sequence with Jokers is a valid run.
       Args:
           sequence: an array of Card objects.  Array will have either 3 ro 4 cards
       Returns:
           Success or Failure as True/False
   """

    RANK_VALUE["A"] = 1  # resetting value of A (may have been set to 14 in previous run)

    # Order the Cards in the sequence
    sort_sequence(sequence)

    # Push all Jokers to the end and count the number of Jokers
    push_joker_toend(sequence)
    joker_count = 0
    for card in sequence:
        if card.is_joker() == True:
            joker_count += 1

    # Make sure the Suit Match except for Jokers.
    for card in sequence:
        if card.is_joker() == True:
            continue
        if card.suit != sequence[0].suit:
            return False

    # This is to cover for K, Q and A run with Jokers
    if sequence[0].rank == "A":
        if sequence[1].rank == "Q" or sequence[1].rank == "J" or sequence[1].rank == "K":
            RANK_VALUE[sequence[0].rank] = 14
            sort_sequence(sequence)
            push_joker_toend(sequence)

    rank_inc = 1
    for i in range(1, len(sequence)):
        if sequence[i].is_joker() == True:
            continue
        # Compare RANK values with accomodating for Jokers.
        while (RANK_VALUE[sequence[i].rank] != RANK_VALUE[(sequence[i - 1].rank)] + rank_inc):
            # Use Joker Count for missing Cards in the run
            if joker_count > 0:
                rank_inc += 1
                joker_count -= 1
                continue
            else:
                # if No more Jokers left, then revert to regular comparison
                if RANK_VALUE[sequence[i].rank] != RANK_VALUE[(sequence[i - 1].rank)] + 1:
                    return False
                else:
                    break
    return True


def push_joker_toend(sequence):
    """ Push the Joker to the end of the sequence.
       Args:
           sequence: sequence of Card Objects.
       Returns:
           no return
   """
    sort_sequence(sequence)
    joker_list = []
    for card in sequence:
        if card.is_joker() == True:
            sequence.remove(card)
            joker_list.append(card)
    sequence += joker_list
    return sequence


def get_object(arr, str_card):
    """ Get Card Object using its User Input string representation
   Args:
       arr: array of Card objects
       str_card: Card descriptor as described by user input, that is a 2 character
           string of Rank and Suit of the Card.  For example, KH for King of Hearts.
   Returns:
       object pointer corresponding to string, from the arr
   """
    # Make sure the str_card has only a RANK letter and SUIT letter
    #		for example KH for King of Hearts.
    if len(str_card) != 2:
        return None

    for item in arr:
        if item.rank == str_card[0] and item.suit[0] == str_card[1]:
            return item

    return None


def print_cards(arr):
    """ Print Cards in a single line
       Args:
           arr: array of Card Objects
       Returns:
           a displayable string representation of the Cards in the arr
   """
    s = ""
    for card in arr:
        s = s + " " + str(card)
    return s


def sort_sequence(sequence):
    """ Sort the Cards in the sequence in the incresing order of RANK values
       Args:
           sequence: array of Card objects
       Returns:
           sorted sequence.
   """
    is_sort_complete = False

    while is_sort_complete == False:
        is_sort_complete = True
        for i in range(0, len(sequence) - 1):
            if RANK_VALUE[sequence[i].rank] > RANK_VALUE[sequence[i + 1].rank]:
                a = sequence[i + 1]
                sequence[i + 1] = sequence[i]
                sequence[i] = a
                is_sort_complete = False
    return sequence



@app.route("/")
def index():
    return render_template('index.htm')


@app.route("/start")
def start():
    session.clear()
    return render_template('players.htm')

@app.route("/settings", methods=['GET', 'POST'])
def settings():
    global number_of_people
    number_of_people = request.form.get('number_of_people')
    global who_is_playing
    who_is_playing = request.form.get('number_of_people')
    return render_template('settings.htm', number_of_people=number_of_people)

@app.route("/take_card", methods=['GET','POST'])
def main():
    """ Main Program """
    #return render_template('play_game.htm')

    # Create Deck with 2 Packs
    global deck
    deck = Deck(int(number_of_people))
    deck.shuffle()

    # Joker Logic is disabled currently.
    # deck.set_joker()

    # New game with 2 players
    global table
    table = Table()
    global g
    g = Game(int(number_of_people), deck, table)
    global len_run
    len_run = []

    # Deal Cards
    for i in range(13):
        for hand in g.players:
            card = deck.draw_card()
            hand.deal_card(card)

    # Create Pile
    first_card = deck.draw_card()
    g.add_pile(first_card)

    # Now let the Players begin
    g.play()

    return render_template('take_a_card.htm', table_stash=table_stash, name=name, self_stash=self_stash,
                           len_table_stash=len_table_stash, len_self_stash=len_self_stash, pile=self_pile[0])

    # return render_template('play_game.htm')
    #return render_template('play_game.htm', Player.name)

@app.route("/play_game", methods=['GET', 'POST'])
def take_card():
    take = request.form.get('take_a_card')
    print(take)
    global pile
    pile = []

    # Pick card from Pile
    if take == 'P' or take == 'p':
        if len(self_stash) < 14:
            c = g.draw_pile()
            self_stash.insert(len(self_stash),c)

        else:
            input("ERROR: You have " + str(len(self_stash)) + " cards. Cannot pick anymore. Enter to continue")

    # Take Card from Deck
    if take == 'T' or take == 't':
        if len(self_stash) < 14:
            c = deck.draw_card()
            self_stash.insert(len(self_stash), c)
        else:
            input("ERROR: You have " + str(len(self.stash)) + " cards. Cannot take anymore. Enter to continue")

    hand = self_stash
    len_hand = len(hand)
    new_table_stash = table_stash
    len_new_table_stash = len(new_table_stash)
    if len(self_pile)!= 0:
        pile = self_pile[0]


    return render_template('play_game.htm', self_stash=self_stash, name=name, hand=hand, new_table_stash = new_table_stash,
                           len_new_table_stash=len_new_table_stash, len_hand=len_hand, pile=pile, len_run=len_run)


@app.route("/action", methods=['GET','POST'])
def action():

        # Get Player Action
        action = request.form.get('action')
        # print(action)
        # input(
        # "*** " + self.name + ", What would you like to do? ***, \n(M)ove Cards, (P)ick from pile, (T)ake from deck, (D)rop, (S)ort, (C)lose Game, (A)dd to the table, (R)ules: ")

        # Move or Rearrange Cards in the stash
        if action == 'M' or action == 'm':
            # Get the Card that needs to moved.
            cards = []
            if len(self_stash) <= 14:
                for i in range(0, len(table_stash)):
                    for x in range(0, len(table_stash[i])):
                        table = 'table-card-' + str(i)+'-'+str(x)
                        #print(request.form.get(table))
                        if request.form.get(table):
                            what = request.form.get(table)
                            what = what.strip()
                            what = get_object(table_stash[i], what.upper())
                            if what:
                                number = i
                                cards.append(what)
                for i in range(0, 14):
                    card = 'card-' + str(i)
                    if request.form.get(card):
                        what = request.form.get(card)
                        what = what.strip()
                        what = get_object(self_stash, what.upper())
                        if what:
                            cards.append(what)



                if (is_valid_run(cards) or is_valid_book(cards)):
                    counter = len(cards)
                    check = list(table_stash[number])

                    for i in range(0, counter):
                        if cards[i] in check:
                            check.remove(cards[i])


                    if (is_valid_run(check) or is_valid_book(check) or len(check)==0):
                        len_run.append(len(cards))
                        table_stash.append(cards)
                        for i in range(0, counter):
                            if cards[i] in table_stash[number]:
                                print ('ole')
                                table_stash[number].remove(cards[i])
                            if cards[i] in self_stash:
                                self_stash.remove(cards[i])
                                counter -= 1


        # Sort cards in the stash
        if action == 'S' or action == 's':
            sort_sequence(self_stash)

        #Drop card to Pile
        if action == 'D' or action == 'd':
            if len(self_stash)==1:
                return render_template('winner.htm', name=name)


            # Get the Card that needs to removed.
            for i in range(0, 14):
                card = 'card-' + str(i)
                if request.form.get(card):
                    drop = request.form.get(card)
                    drop.strip()
                    if get_object(self_stash, drop.upper()) not in self_stash:
                        input("ERROR: That card is not in your stash.  Enter to continue")

            # Perform the Drop Operation
            drop = get_object(self_stash, drop.upper())
            if drop != "":
                self_stash.remove(drop)
                g.add_pile(drop)

                for i in range(0, int(number_of_people)):
                    if g.players[i].name == name:
                        if i+1==int(number_of_people):
                            g.play(0)
                            break
                        else:
                            g.play(i+1)
                            break
                        break


                hand = self_stash
                len_hand = len(hand)

                new_table_stash = table_stash
                len_new_table_stash = len(new_table_stash)

            return render_template('take_a_card2.htm', new_table_stash=new_table_stash, name=name, hand=hand,
                               len_new_table_stash=len_new_table_stash, len_hand=len_hand, pile=self_pile[0], len_run=len_run)



        if action == 'C' or action == 'c':

            cards = []
            if len(self_stash) <= 14:
                for i in range(0, 14):
                    card = 'card-' + str(i)
                    if request.form.get(card):
                        what = request.form.get(card)
                        what = what.strip()
                        what = get_object(self_stash, what.upper())
                        cards.append(what)

                if (is_valid_run(cards) or is_valid_book(cards)):
                    # print("valid")
                    # print run
                    len_run.append(len(cards))
                    table_stash.append(cards)
                    counter = len(cards)
                    for i in range(0, counter):
                        if cards[i] in self_stash:
                            self_stash.remove(cards[i])
                            counter -= 1



                #if Player.drop_card(drop):
                #    pass
                #if Player.close_game():
                #    print(print_cards(self_stash))
                #    # Return True because Close ends the Game.
                #    return True
                #else:
                #    input("Yeah!!! You did it!!! Enter to Continue playing.")
                # if this Close was false alarm then discarded Card will
                #		have to be put back into the stash for the Player to continue.
                # self.stash.append(self.game.draw_pile())
            # else:
            #	input("ERROR: Not a valid card, Enter to continue")
            else:
                input("ERROR: You do not have enough cards to close the game. Enter to Continue playing.")
                
        if action == 'A' or action == 'a':
            if self.add():
                pass

        # Show Rules of the game
        if action == 'R' or action == 'r':
            print("------------------ Rules --------------------",
                          "\n- Rummy is a card game based on making sets.",
                          "\n- From a stash of 13 cards, 4 sets must be created (3 sets of 3, 1 set of 4).",
                          "\n- The set of 4 must always be at the end"
                          "\n- A valid set can either be a run or a book.",
                          "\n- One set must be a run WITHOUT using a joker."
                          "\n- A run is a sequence of numbers in a row, all with the same suit. ",
                          "\n \tFor example: 4 of Hearts, 5 of Hearts, and 6 of Hearts",
                          "\n- A book of cards must have the same rank but may have different suits.",
                          "\n \tFor example: 3 of Diamonds, 3 of Spades, 3 of Clubs",
                          "\n- Jokers are randomly picked from the deck at the start of the game.",
                          "\n- Joker is denoted by '-J' and can be used to complete sets.",
                          "\n- During each turn, the player may take a card from the pile or from the deck.",
                          "Immediately after, the player must drop any one card into the pile so as not go over the 13 card limit.",
                          "\n- When a player has created all the sets, select Close Game option and drop the excess card into the pile.",
                          "\n- Card with Rank 10 is represented as Rank T"
                          "\n--------------------------------------------")

        hand = self_stash
        len_hand = len(hand)

        new_table_stash = table_stash
        len_new_table_stash = len(new_table_stash)


        return render_template('play_game.htm', new_table_stash=new_table_stash, name=name, hand=hand,
                               len_new_table_stash=len_new_table_stash, len_hand=len_hand, pile=pile, len_run=len_run)

#@app.route("/game", methods=['GET','POST'])
#def start_the_game():
#    main()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011, debug=True)
