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

def generate_fair_random_number():
    # Step 1: Computer generates a random number x from range (0 to 5 inclusive)
    x = random.randint(0, 5)
    
    # Step 2: Computer generates a secret key
    key = secrets.token_bytes(32)

    # Step 3: Calculate and display HMAC(key, x)
    hmac_result = hmac.new(key, str(x).encode('utf-8'), hashlib.sha3_256).hexdigest()
    print(f"Computer generated random number: {x}")
    print(f"Computer generated secret key: {key.hex()}")
    print(f"HMAC (SHA3-256) for random number {x}: {hmac_result}")
    
    return x, key, hmac_result

def collaborative_random_number_generation(x, y):
    # Step 5: Calculate the final result (x + y) % 6
    result = (x + y) % 6
    print(f"User selected: {y}")
    print(f"Collaborative result (x + y) % 6: {result}")
    return result

class Game:
    def __init__(self, dice):
        self.dice = dice
    
    def start_game(self):
        print("Let's determine who makes the first move.")
        x, key, hmac_result = generate_fair_random_number()
        
        # Step 4: User selects a number (y ∈ {0,1,2,3,4,5})
        user_choice = input("Select a number (0 to 5): ")
        try:
            user_choice = int(user_choice)
            if user_choice not in range(6):
                print("Invalid choice. Please choose a number between 0 and 5.")
                return
        except ValueError:
            print("Invalid input. Please choose a valid integer between 0 and 5.")
            return

        # Step 6: Compute the final result and display it
        result = collaborative_random_number_generation(x, user_choice)

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
