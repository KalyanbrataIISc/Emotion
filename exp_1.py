import pygame
import os
import random
import csv
import time

# ===============================
# Customizable Variables
# ===============================

# Window settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Time settings (in seconds)
FIXATION_TIME = 0.5           # Duration of fixation cross
RESPONSE_WINDOW = 1.5         # Time allowed for participant to respond
FEEDBACK_TIME = 0.5           # Duration of feedback screen

# Break settings
BREAK_INTERVAL = 25           # Number of trials between breaks
BREAK_TEXT = "Take a short break! Press SPACE to continue."

# Trial settings
TOTAL_TRIALS = 200            # Total number of trials in the experiment

# Instructions
INSTRUCTIONS = ("Press J for Happy, K for Neutral, L for Angry.\n"
                "Press SPACE to start.")

# Paths to stimuli
STIMULI_PATHS = {
    "happy": "distractors/happy",
    "neutral": "distractors/neutral",
    "angry": "distractors/angry"
}

# Key mappings
key_mapping = {"happy": pygame.K_j, "neutral": pygame.K_k, "angry": pygame.K_l}

# ===============================
# Experiment Code
# ===============================

pygame.init()

# Screen settings
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
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
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, 100 + i * 100))
            screen.blit(text_surface, text_rect)

        name_surface = font.render(f"Name: {participant_name}", True, BLACK)
        name_rect = name_surface.get_rect(center=(WINDOW_WIDTH // 2, 400))
        screen.blit(name_surface, name_rect)

        number_surface = font.render(f"Number: {participant_number}", True, BLACK)
        number_rect = number_surface.get_rect(center=(WINDOW_WIDTH // 2, 500))
        screen.blit(number_surface, number_rect)

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


# Create or append results to a CSV file
def save_results(participant_name, participant_number, results, is_first_write=False):
    output_file = f"{participant_name}_{participant_number}_results.csv"
    with open(output_file, mode="a", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=["session_number", "emotion", "user_emotion", "reaction_time", "response_type"]
        )
        if is_first_write:
            writer.writeheader()  # Write header only once
        writer.writerows(results)


# Load stimuli
stimuli = []
for emotion, folder in STIMULI_PATHS.items():
    for img_file in os.listdir(folder):
        stimuli.append({"emotion": emotion, "path": os.path.join(folder, img_file)})

# Randomize stimuli
random.shuffle(stimuli)
stimuli = stimuli[:TOTAL_TRIALS]  # Limit total trials if TOTAL_TRIALS is set

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
    text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, 200 + i * 50))
    screen.blit(text_surface, text_rect)
pygame.display.flip()

waiting_for_space = True
while waiting_for_space:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            waiting_for_space = False

# Initialize experiment variables
results = []
session_number = 1
first_write = True

# Run trials
for trial_index, trial in enumerate(stimuli):
    # Fixation cross
    screen.fill(WHITE)
    text_surface = font.render("+", True, BLACK)
    text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()
    pygame.time.delay(int(FIXATION_TIME * 1000))

    # Show stimulus
    img = pygame.image.load(trial["path"])
    img = pygame.transform.scale(img, (400, 400))  # Resize the image
    img_rect = img.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    screen.fill(WHITE)
    screen.blit(img, img_rect)  # Center the image
    pygame.display.flip()  # Render the image on the screen

    # Start response window only after image is displayed
    start_time = time.time()
    response = None
    reaction_time = None
    correct = False
    user_emotion = None
    while time.time() - start_time < RESPONSE_WINDOW:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                response = event.key
                end_time = time.time()
                reaction_time = end_time - start_time

                # Determine user input emotion
                for emotion, key in key_mapping.items():
                    if response == key:
                        user_emotion = emotion
                        break

                # Check correctness
                correct = trial["emotion"] == user_emotion
                break
        if response:
            break

    # Only log valid responses
    if response:
        response_type = "Correct" if correct else "Incorrect"
        results.append({
            "session_number": session_number,
            "emotion": trial["emotion"],
            "user_emotion": user_emotion,
            "reaction_time": reaction_time,
            "response_type": response_type,
        })

        # Feedback
        screen.fill(WHITE)
        feedback_color = (0, 255, 0) if response_type == "Correct" else (255, 0, 0)
        text_surface = font.render(response_type, True, feedback_color)
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        pygame.time.delay(int(FEEDBACK_TIME * 1000))

    # Break after specified interval
    if (trial_index + 1) % BREAK_INTERVAL == 0 and trial_index + 1 < TOTAL_TRIALS:
        # Save results so far
        save_results(participant_name, participant_number, results, is_first_write=first_write)
        first_write = False  # Header already written
        results = []  # Clear results for the next session

        # Increment session number
        session_number += 1

        # Display break screen
        remaining_trials = TOTAL_TRIALS - (trial_index + 1)
        screen.fill(WHITE)
        rest_lines = [BREAK_TEXT, f"Trials Remaining: {remaining_trials}"]
        for i, line in enumerate(rest_lines):
            text_surface = font.render(line, True, BLACK)
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, 200 + i * 50))
            screen.blit(text_surface, text_rect)
        pygame.display.flip()

        waiting_for_space = True
        while waiting_for_space:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting_for_space = False

# Save final session results
if results:
    save_results(participant_name, participant_number, results, is_first_write=first_write)

# End of experiment
screen.fill(WHITE)
text_surface = font.render("Experiment Completed! Results saved.", True, BLACK)
text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
screen.blit(text_surface, text_rect)
pygame.display.flip()
pygame.time.delay(3000)

pygame.quit()