import pygame
import os
import random
import csv
import time

# ===============================
# Customizable Variables
# ===============================

# Time settings (in seconds)
FIXATION_TIME = 0.5           # Duration of fixation cross
STIMULUS_TIME = 0.2           # Duration of stimulus presentation
RESPONSE_WINDOW = 2.5         # Time allowed for participant to respond
FEEDBACK_TIME = 0.5           # Duration of feedback screen

# Break settings
BREAK_INTERVAL = 20           # Number of trials between breaks
BREAK_TEXT = "Take a short break! Press SPACE to continue."

# Trial settings
TOTAL_TRIALS = 60             # Total number of trials in the experiment
TRIALS_PER_SET = 10           # Number of trials in each set (if sets are used)

# Participant info defaults (useful for testing)
DEFAULT_PARTICIPANT_NAME = "Test"
DEFAULT_PARTICIPANT_NUMBER = "01"

# Instructions
INSTRUCTIONS = ("Press Z for Happy, X for Angry, C for Neutral.\n"
                "Press SPACE to start.")

# Paths to stimuli
STIMULI_PATHS = {
    "happy": "happy",
    "angry": "angry",
    "neutral": "neutral"
}

# ===============================
# Experiment Code
# ===============================

pygame.init()

# Screen settings
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Emotion Categorization Experiment")
font = pygame.font.Font(None, 50)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# Function to display participant info input form
def get_participant_info():
    participant_name = ""
    participant_number = ""
    active_field = "name"

    instructions = [
        "Enter Participant Name:",
        "Enter Participant Number:",
        "Press ENTER to start the experiment."
    ]

    while True:
        screen.fill(WHITE)

        for i, text in enumerate(instructions):
            text_surface = font.render(text, True, BLACK)
            screen.blit(text_surface, (50, 100 + i * 100))

        name_field = font.render(f"Name: {participant_name}", True, BLACK)
        number_field = font.render(f"Number: {participant_number}", True, BLACK)
        screen.blit(name_field, (50, 400))
        screen.blit(number_field, (50, 500))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None, None

            if event.type == pygame.KEYDOWN:
                if active_field == "name":
                    if event.key == pygame.K_RETURN:
                        active_field = "number"
                    elif event.key == pygame.K_BACKSPACE:
                        participant_name = participant_name[:-1]
                    else:
                        participant_name += event.unicode
                elif active_field == "number":
                    if event.key == pygame.K_RETURN:
                        return participant_name.strip(), participant_number.strip()
                    elif event.key == pygame.K_BACKSPACE:
                        participant_number = participant_number[:-1]
                    else:
                        participant_number += event.unicode


# Load stimuli
stimuli = []
for emotion, folder in STIMULI_PATHS.items():
    for img_file in os.listdir(folder):
        stimuli.append({"emotion": emotion, "path": os.path.join(folder, img_file)})

# Randomize stimuli
random.shuffle(stimuli)
stimuli = stimuli[:TOTAL_TRIALS]  # Limit total trials if TOTAL_TRIALS is set

# Key mappings
key_mapping = {"happy": pygame.K_z, "angry": pygame.K_x, "neutral": pygame.K_c}

# Get participant info
participant_name, participant_number = get_participant_info()
if not participant_name or not participant_number:
    pygame.quit()
    quit()

# Instructions
screen.fill(WHITE)
lines = INSTRUCTIONS.split("\n")
for i, line in enumerate(lines):
    text_surface = font.render(line, True, BLACK)
    screen.blit(text_surface, (50, 250 + i * 50))
pygame.display.flip()

waiting_for_space = True
while waiting_for_space:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            waiting_for_space = False

# Run trials
results = []
for trial_index, trial in enumerate(stimuli):
    # Show trials left
    screen.fill(WHITE)
    trials_left_text = font.render(f"Trials Left: {TOTAL_TRIALS - trial_index}", True, BLACK)
    screen.blit(trials_left_text, (50, 50))

    # Fixation cross
    text_surface = font.render("+", True, BLACK)
    screen.blit(text_surface, (400, 300))
    pygame.display.flip()
    pygame.time.delay(int(FIXATION_TIME * 1000))

    # Show stimulus
    img = pygame.image.load(trial["path"])
    img = pygame.transform.scale(img, (400, 400))
    screen.fill(WHITE)
    screen.blit(img, (200, 100))
    pygame.display.flip()

    # Collect response
    start_time = time.time()
    response = None
    reaction_time = None
    correct = False
    while time.time() - start_time < RESPONSE_WINDOW:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                response = event.key
                end_time = time.time()
                reaction_time = end_time - start_time
                correct = key_mapping[trial["emotion"]] == response
                break
        if response:
            break

    # Determine response type
    if not response:
        response_type = "No Response"
    else:
        response_type = "Correct" if correct else "Incorrect"

    # Feedback
    screen.fill(WHITE)
    feedback_color = (0, 255, 0) if response_type == "Correct" else (255, 0, 0)
    text_surface = font.render(response_type, True, feedback_color)
    screen.blit(text_surface, (350, 300))
    pygame.display.flip()
    pygame.time.delay(int(FEEDBACK_TIME * 1000))

    # Log trial results
    results.append({
        "emotion": trial["emotion"],
        "reaction_time": reaction_time,
        "response_type": response_type
    })

    # Break after specified interval
    if (trial_index + 1) % BREAK_INTERVAL == 0 and trial_index + 1 < TOTAL_TRIALS:
        screen.fill(WHITE)
        rest_text = font.render(BREAK_TEXT, True, BLACK)
        screen.blit(rest_text, (50, 300))
        pygame.display.flip()

        waiting_for_space = True
        while waiting_for_space:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting_for_space = False

# Save results to a CSV file named after the participant
output_file = f"{participant_name}_{participant_number}_results.csv"
with open(output_file, mode="w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["emotion", "reaction_time", "response_type"])
    writer.writeheader()
    writer.writerows(results)

# End of experiment
screen.fill(WHITE)
text_surface = font.render("Experiment Completed! Results saved.", True, BLACK)
screen.blit(text_surface, (150, 300))
pygame.display.flip()
pygame.time.delay(3000)

pygame.quit()