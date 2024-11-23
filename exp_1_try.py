import pygame
import os
import random
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
BREAK_INTERVAL = 10           # Number of trials between breaks
BREAK_TEXT = "Take a short break! Press SPACE to continue."

# Trial settings
TOTAL_TRIALS = 50             # Total number of trials in the practice session

# Instructions
INSTRUCTIONS = ("Practice Session\n"
                "Press J for Happy, K for Neutral, L for Angry.\n"
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
# Practice Program Code
# ===============================

pygame.init()

# Screen settings
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Emotion Categorization Practice")
font = pygame.font.Font(None, 50)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# Function to calculate break statistics
def calculate_stats(session_results):
    total_trials = len(session_results)
    correct_trials = sum(1 for result in session_results if result["correct"])
    avg_reaction_time = (
        sum(result["reaction_time"] for result in session_results if result["reaction_time"] is not None)
        / total_trials
    )
    accuracy = (correct_trials / total_trials) * 100
    return accuracy, avg_reaction_time


# Load stimuli
stimuli = []
for emotion, folder in STIMULI_PATHS.items():
    for img_file in os.listdir(folder):
        stimuli.append({"emotion": emotion, "path": os.path.join(folder, img_file)})

# Randomize stimuli
random.shuffle(stimuli)
stimuli = stimuli[:TOTAL_TRIALS]  # Limit total trials if TOTAL_TRIALS is set

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

# Initialize practice session variables
session_results = []

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

    # Record the trial result
    session_results.append({
        "reaction_time": reaction_time if response else None,
        "correct": correct,
    })

    # Feedback
    feedback_color = (0, 255, 0) if correct else (255, 0, 0)
    feedback_text = "Correct" if correct else "Incorrect"
    screen.fill(WHITE)
    feedback_surface = font.render(feedback_text, True, feedback_color)
    feedback_rect = feedback_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    screen.blit(feedback_surface, feedback_rect)
    pygame.display.flip()
    pygame.time.delay(int(FEEDBACK_TIME * 1000))

    # Break after specified interval
    if (trial_index + 1) % BREAK_INTERVAL == 0 and trial_index + 1 < TOTAL_TRIALS:
        # Calculate stats
        accuracy, avg_reaction_time = calculate_stats(session_results)

        # Display break screen with stats
        screen.fill(WHITE)
        rest_lines = [
            BREAK_TEXT,
            f"Accuracy: {accuracy:.2f}%",
            f"Average Reaction Time: {avg_reaction_time:.2f} seconds",
        ]
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

        # Reset session results
        session_results = []

# End of practice session
screen.fill(WHITE)
text_surface = font.render("Practice Completed! Press ESC to exit.", True, BLACK)
text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
screen.blit(text_surface, text_rect)
pygame.display.flip()

waiting_for_exit = True
while waiting_for_exit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            waiting_for_exit = False

pygame.quit()