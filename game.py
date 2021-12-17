"""

Solitaire clone. hopefully not played by me

"""
import arcade
from pyglet.window.key import Q
import const
from card import Card
import random


class MyGame(arcade.Window):
    """Main application class."""

    def __init__(self):
        super().__init__(
            const.SCREEN_WIDTH,
            const.SCREEN_HEIGHT,
            const.SCREEN_TITLE,
            antialiasing=False,
        )

        # Sprite list with all the cards, no matter what pile they are in.
        self.card_list = None

        # list of card we are dragging with the mouse
        self.held_cards = None

        # and the original position of the held cards
        self.held_cards_original_position = None

        # Sprite list with all the mats tha cards lay on.
        self.pile_mat_list = None

        # Create a list of lists, each holds a pile of cards.
        self.piles = None

        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Spritelist with all the cards, not matter what pile they are in
        self.card_list = arcade.SpriteList()

        # list of cards being dragged
        self.held_cards = []

        # position of held cards
        self.held_cards_original_position = []

        # --- Create the mats the cards go on

        # Sprite list with all the mats tha cards lay on.
        self.pile_mat_list: arcade.SpriteList = arcade.SpriteList()

        # Create the mats for the top face down and face up piles
        pile = arcade.SpriteSolidColor(
            const.MAT_WIDTH, const.MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN
        )
        pile.position = const.START_X, const.TOP_Y
        self.pile_mat_list.append(pile)

        pile = arcade.SpriteSolidColor(
            const.MAT_WIDTH, const.MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN
        )
        pile.position = const.START_X + const.X_SPACING, const.TOP_Y
        self.pile_mat_list.append(pile)

        # Create the mats for the top graveyard mats
        for i in range(4):
            pile = arcade.SpriteSolidColor(
                const.MAT_WIDTH,
                const.MAT_HEIGHT,
                arcade.csscolor.DARK_OLIVE_GREEN,
            )
            pile.position = const.START_X + (i + 3) * const.X_SPACING, const.TOP_Y
            self.pile_mat_list.append(pile)

        # Create the seven middle piles
        for i in range(7):
            pile = arcade.SpriteSolidColor(
                const.MAT_WIDTH,
                const.MAT_HEIGHT,
                arcade.csscolor.DARK_OLIVE_GREEN,
            )
            pile.position = (
                const.START_X + i * const.X_SPACING,
                const.MIDDLE_Y,
            )
            self.pile_mat_list.append(pile)

        # create all cards
        for card_suit in const.CARD_SUITS:
            for card_value in const.CARD_VALUES:
                card = Card(card_suit, card_value, const.CARD_SCALE)
                card.position = const.START_X, const.TOP_Y
                self.card_list.append(card)

        # Shuffle the cards
        for pos1 in range(len(self.card_list)):
            pos2 = random.randrange(len(self.card_list))
            self.card_list.swap(pos1, pos2)

        # Create a list of lists, each holds a pile of cards.
        self.piles = [[] for _ in range(const.PILE_COUNT)]

        # Put all the cards in the bottom face-down pile
        for card in self.card_list:
            self.piles[const.TOP_FACE_DOWN_PILE].append(card)

        # - Pull from that pile into the middle piles, all face-down ,list pos 7-13
        # Loop for each pile
        for pile_no in range(const.PLAY_PILE_1, const.PLAY_PILE_7 + 1):
            # Deal proper number of cards for that pile
            for j in range(pile_no - const.PLAY_PILE_1 + 1):
                # Pop the card off the deck we are dealing from
                card = self.piles[const.TOP_FACE_DOWN_PILE].pop()
                # Put in the proper pile
                self.piles[pile_no].append(card)
                # Move card to same position as pile we just put it in
                card.position = self.pile_mat_list[pile_no].position
                # Put on top in draw order
                self.pull_to_top(card)

        # Flip up the top cards
        for i in range(const.PLAY_PILE_1, const.PLAY_PILE_7 + 1):
            self.piles[i][-1].face_up()

    def on_draw(self):
        """Render the screen."""
        # Clear the screen
        arcade.start_render()

        # Draw the mats the cards go on
        self.pile_mat_list.draw()

        # Draw the cards
        self.card_list.draw()

    def pull_to_top(self, card: arcade.Sprite) -> None:
        """Pull card to top of rendering order (last to render, looks on-top)."""

        # Remove and append at the end
        self.card_list.remove(card)
        self.card_list.append(card)

    def remove_card_from_pile(self, card):
        """Remove card from whatever pile it was in."""
        for pile in self.piles:
            if card in pile:
                pile.remove(card)
                break

    def get_pile_for_card(self, card):
        """What pile is this card in?"""
        for index, pile in enumerate(self.piles):
            if card in pile:
                return index

    def move_card_to_new_pile(self, card, pile_index):
        """Move the card to a new pile"""
        self.remove_card_from_pile(card)
        self.piles[pile_index].append(card)

    def on_key_press(self, symbol: int, modifiers: int):
        """User presses key"""
        if symbol == arcade.key.R:
            # Restart
            self.setup()

    def on_mouse_press(self, x: float, y: float, button: int, key_modifiers: int):
        """Called when the user presses a mouse button."""

        # Get list of cards we've clicked on
        cards = arcade.get_sprites_at_point((x, y), self.card_list)

        # Have we clicked on a card?
        if len(cards) > 0:

            # Might be a stack of cards, get the top card
            primary_card = cards[-1]
            assert isinstance(primary_card, Card)

            # Figure out what pile the card is in
            pile_index = self.get_pile_for_card(primary_card)

            # Clicking on source deck? -> flip one
            if pile_index == const.TOP_FACE_DOWN_PILE:
                # Flip one
                # If we run out of cards, stop
                # TODO implement mechanik on flips
                if len(self.piles[const.TOP_FACE_DOWN_PILE]) == 0:
                    return
                # get top card
                card = self.piles[const.TOP_FACE_DOWN_PILE][-1]
                card.face_up()
                # move card position to top left, right pile
                card.position = self.pile_mat_list[const.TOP_FACE_UP_PILE].position
                # remove Card from TOP_FACE_DOWN Stack, move to TOP_FACE_UP
                self.piles[const.TOP_FACE_DOWN_PILE].remove(card)
                self.piles[const.TOP_FACE_UP_PILE].append(card)
                # Put on top draw-order wise
                self.pull_to_top(card)

            elif primary_card.is_face_down:
                # Is the card face down? In one of those middle 7 piles? Then flip up
                primary_card.face_up()

            else:
                # All other cases, grab the face-up card we are clicking on
                self.held_cards = [primary_card]
                # Save the position
                self.held_cards_original_position = [self.held_cards[0].position]
                # Put on top in drawing order
                self.pull_to_top(self.held_cards[0])

                # Is this a stack of cards? If so, grab the other cards too
                card_index = self.piles[pile_index].index(primary_card)
                for i in range(card_index + 1, len(self.piles[pile_index])):
                    card = self.piles[pile_index][i]
                    self.held_cards.append(card)
                    self.held_cards_original_position.append(card.position)
                    self.pull_to_top(card)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """User moves mouse"""

        # if we are holding cards, move them with the mouse
        for card in self.held_cards:
            card.center_x += dx
            card.center_y += dy

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        """Called when the user releases a mouse button."""

        # If we don't have any cards, who cares
        if len(self.held_cards) == 0:
            return

        # Find the closest pile, in case we are in contact with more than one
        pile, distance = arcade.get_closest_sprite(
            self.held_cards[0], self.pile_mat_list
        )
        reset_position = True

        # See if we are in contact with the closest pile
        if arcade.check_for_collision(self.held_cards[0], pile):

            # What pile is it?
            pile_index = self.pile_mat_list.index(pile)

            #  Is it the same pile we came from?
            if pile_index == self.get_pile_for_card(self.held_cards[0]):
                # If so, who cares. We'll just reset our position.
                pass

            # Is it on a middle play pile?
            elif const.PLAY_PILE_1 <= pile_index <= const.PLAY_PILE_7:
                # Are there already cards there?
                if len(self.piles[pile_index]) > 0:
                    # Move cards to proper position
                    top_card = self.piles[pile_index][-1]
                    for i, dropped_card in enumerate(self.held_cards):
                        dropped_card.position = (
                            top_card.center_x,
                            top_card.center_y - const.CARD_VERTICAL_OFFSET * (i + 1),
                        )
                else:
                    # Are there no cards in the middle play pile?
                    for i, dropped_card in enumerate(self.held_cards):
                        # Move cards to proper position
                        dropped_card.position = (
                            pile.center_x,
                            pile.center_y - const.CARD_VERTICAL_OFFSET * i,
                        )

                for card in self.held_cards:
                    # Cards are in the right position, but we need to move them to the right list
                    self.move_card_to_new_pile(card, pile_index)

                # Success, don't reset position of cards
                reset_position = False

            # Release on top play pile? And only one card held?
            elif (
                const.TOP_PILE_1 <= pile_index <= const.TOP_PILE_4
                and len(self.held_cards) == 1
            ):
                # Move position of card to pile
                self.held_cards[0].position = pile.position
                # Move card to card list
                for card in self.held_cards:
                    self.move_card_to_new_pile(card, pile_index)

                reset_position = False

        if reset_position:
            # Where-ever we were dropped, it wasn't valid. Reset the each card's position
            # to its original spot.
            for pile_index, card in enumerate(self.held_cards):
                card.position = self.held_cards_original_position[pile_index]

        # We are no longer holding cards
        self.held_cards = []


def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
