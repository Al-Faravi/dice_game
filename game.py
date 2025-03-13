import sys
import secrets
import hmac
import hashlib
import random
from tabulate import tabulate

class Dice:
    def __init__(self, faces):
        self.faces = faces
    
    def roll(self):
        return random.choice(self.faces)

def parse_dice_args(args):
    dice = []
    for arg in args:
        try:
            faces = list(map(int, arg.split(',')))
            dice.append(Dice(faces))
        except ValueError:
            print(f"Invalid input '{arg}'. Please provide valid comma-separated integers.")
            sys.exit(1)
    return dice

def generate_fair_random_number(user_choice, computer_choice, range_end):
    # Combine both user and computer choices to generate a fair random number
    # This could be a hash of both values for fairness
    key = secrets.token_bytes(32)
    combined_choices = f"{user_choice}{computer_choice}".encode('utf-8')
    hmac_result = hmac.new(key, combined_choices, hashlib.sha3_256).hexdigest()
    x = secrets.randbelow(range_end)
    print(f"HMAC (SHA3-256) for choices {user_choice} and {computer_choice}: {hmac_result}")
    return x, key, hmac_result

class Game:
    def __init__(self, dice):
        self.dice = dice
    
    def start_game(self):
        print("Let's determine who makes the first move.")
        user_choice = self.determine_first_move()
        
        if user_choice is None:  # Check if user didn't input valid guess
            return
        
        user_dice = self.user_select_dice()
        computer_dice = self.computer_select_dice()

        print(f"User selected dice: {user_dice.faces}")
        print(f"Computer selected dice: {computer_dice.faces}")

        user_roll = self.roll_dice(user_dice)
        computer_roll = self.roll_dice(computer_dice)
        
        print(f"User rolled: {user_roll}")
        print(f"Computer rolled: {computer_roll}")
        
        if user_roll > computer_roll:
            print("User wins!")
        elif computer_roll > user_roll:
            print("Computer wins!")
        else:
            print("It's a tie!")

    def determine_first_move(self):
        user_choice = input("Try to guess my selection (0 or 1): ")
        if user_choice not in ['0', '1']:
            print("Invalid input. Please choose 0 or 1.")
            return None
        
        computer_choice = random.choice([0, 1])
        print(f"Computer selected {computer_choice} (Your guess: {user_choice})")

        # Generate fair random number considering both choices
        x, key, hmac_result = generate_fair_random_number(user_choice, computer_choice, 2)
        print(f"Generated random value: {x} (HMAC: {hmac_result})")

        # Determine who goes first based on the fair random number
        if x == 0:
            print("User goes first.")
        else:
            print("Computer goes first.")
        return x

    def user_select_dice(self):
        print("Select your dice:")
        for i, dice in enumerate(self.dice):
            print(f"{i} - {dice.faces}")
        user_choice = int(input())
        return self.dice[user_choice]

    def computer_select_dice(self):
        return random.choice(self.dice)

    def roll_dice(self, dice):
        return dice.roll()

class ProbabilityTable:
    def __init__(self, dice_combinations):
        self.dice_combinations = dice_combinations
    
    def display_table(self):
        # Add some introductory text to explain the table
        print("\nThe table below shows the probabilities of the user winning against each dice combination.")
        print("Each cell represents the probability of the user winning against the respective dice combination.")
        
        headers = ['User Dice v'] + [', '.join(map(str, dice.faces)) for dice in self.dice_combinations]
        rows = []
        
        for dice1 in self.dice_combinations:
            row = [', '.join(map(str, dice1.faces))]
            for dice2 in self.dice_combinations:
                # Skip calculating against self
                if dice1 == dice2:
                    row.append('-')
                else:
                    prob = self.calculate_probability(dice1, dice2)
                    row.append(f"{prob:.4f}")
            rows.append(row)
        
        print(tabulate(rows, headers=headers, tablefmt='grid'))
    
    def calculate_probability(self, dice1, dice2):
        wins = 0
        total = 0
        for face1 in dice1.faces:
            for face2 in dice2.faces:
                total += 1
                if face1 > face2:
                    wins += 1
        return wins / total

def main():
    if len(sys.argv) < 4:
        print("You need to provide at least 3 dice configurations!")
        return
    
    dice = parse_dice_args(sys.argv[1:])
    game = Game(dice)
    game.start_game()

    help_option = input("Do you want to see the help table? (y/n): ")
    if help_option == "y":
        probability_table = ProbabilityTable(dice)
        probability_table.display_table()

if __name__ == "__main__":
    main()
