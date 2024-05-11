import re
import pandas as pd
# Function to parse the relevant game data from each line
def parse_game_data(lines):
    data = []
    for line in lines:
        if 'Level' in line and 'episode' in line:
            # Extracting details from each relevant line
            level_match = re.search(r'Level (\d+),', line)
            rounds_match = re.search(r'rounds (\d+),', line)
            steps_match = re.search(r'use (\d+) step', line)
            reward_match = re.search(r'earn (\d+) rewards', line)
            time_match = re.search(r'in (\d+\.\d+) seconds', line)

            if level_match and rounds_match and steps_match and reward_match and time_match:
                level = int(level_match.group(1))
                rounds = int(rounds_match.group(1))
                steps = int(steps_match.group(1))
                reward = int(reward_match.group(1))
                time_use = float(time_match.group(1))

                # Determine if the line is a 'win' based on the presence of 'win' keyword in the next line
                win = 0  # Default to 0 (loss)
                data.append([level, rounds, steps, reward, win, time_use])
        elif 'Next Level!' in line:
            # The line before 'Next Level!' is a win, so set the last entry's win status to 1
            if data:
                data[-1][4] = 1  # Set 'win' to 1 for the last game round before level up

    return data

# Read the contents of the file
with open('output/output_trail3.txt', 'r') as file:
    lines = file.readlines()

# Parse the game data
game_data = parse_game_data(lines)

# Create a DataFrame
columns = ['Level', 'Rounds', 'Steps', 'Reward', 'Win', 'Time Use']
game_df = pd.DataFrame(game_data, columns=columns)

# Save the DataFrame to an Excel file
excel_path = 'output/result_trail3.xlsx'
game_df.to_excel(excel_path, index=False)

excel_path  # Return the path to the created Excel file for download
