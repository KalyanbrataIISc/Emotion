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
RESPONSE_WINDOW = 2.0         # Time allowed for participant to respond
FEEDBACK_TIME = 0.5           # Duration of feedback screen

# Break settings
BREAK_INTERVAL = 25           # Number of trials between breaks
BREAK_TEXT = "Take a short break! Press SPACE to continue."

# Trial settings
TOTAL_TRIALS = 200            # Total number of trials in the experiment

# Instructions
INSTRUCTIONS = ("Primary Task: Categorize the shape in the center.\n"
                "Press J for Circle, K for Square, L for Triangle.\n"
                "Ignore the image around the shape.\n"
                "Press SPACE to start.")

# Stimuli paths
SHAPES_PATH = {
    "circle": "shapes/circle.png",
    "square": "shapes/square.png",
    "triangle": "shapes/triangle.png",
}

DISTRACTORS_PATHS = {
    "happy": "distractors/happy",
    "angry": "distractors/angry",
    "neutral": "distractors/neutral"
}

# Key mappings for the primary task
key_mapping = {"circle": pygame.K_j, "square": pygame.K_k, "triangle": pygame.K_l}

# ===============================
# Experiment Code
# ===============================

pygame.init()

# Screen settings
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Emotion Categorization Experiment 2")
font = pygame.font.Font(None, 50)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# Function to display instructions
def display_instructions():
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


# Load distractors
def load_distractors():
    distractors = {"happy": [], "angry": [], "neutral": []}
    for category, folder in DISTRACTORS_PATHS.items():
        for img_file in os.listdir(folder):
            distractors[category].append(os.path.join(folder, img_file))
    return distractors


# Trial generation
def generate_trials():
    trials = []
    shapes = list(SHAPES_PATH.keys())
    distractor_types = list(DISTRACTORS_PATHS.keys())

    for _ in range(TOTAL_TRIALS):
        shape = random.choice(shapes)
        distractor_type = random.choice(distractor_types)
        trials.append({"shape": shape, "distractor_type": distractor_type})
    random.shuffle(trials)
    return trials


# Run experiment
def run_experiment(trials, distractors):
    results = []
    for trial_index, trial in enumerate(trials):
        # Fixation cross
        screen.fill(WHITE)
        fixation = font.render("+", True, BLACK)
        fixation_rect = fixation.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        screen.blit(fixation, fixation_rect)
        pygame.display.flip()
        pygame.time.delay(int(FIXATION_TIME * 1000))

        # Load shape and distractor
        shape_img = pygame.image.load(SHAPES_PATH[trial["shape"]])
        shape_img = pygame.transform.scale(shape_img, (200, 200))
        shape_rect = shape_img.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        distractor_img_path = random.choice(distractors[trial["distractor_type"]])
        distractor_img = pygame.image.load(distractor_img_path)
        distractor_img = pygame.transform.scale(distractor_img, (400, 400))
        distractor_rect = distractor_img.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        # Display stimuli
        screen.fill(WHITE)
        screen.blit(distractor_img, distractor_rect)  # Draw distractor first
        screen.blit(shape_img, shape_rect)           # Overlay shape
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
                    reaction_time = time.time() - start_time
                    correct = key_mapping[trial["shape"]] == response
                    break
            if response:
                break

        # Feedback
        feedback_color = (0, 255, 0) if correct else (255, 0, 0)
        feedback_text = "Correct" if correct else "Incorrect"
        screen.fill(WHITE)
        feedback_surface = font.render(feedback_text, True, feedback_color)
        feedback_rect = feedback_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        screen.blit(feedback_surface, feedback_rect)
        pygame.display.flip()
        pygame.time.delay(int(FEEDBACK_TIME * 1000))

        # Log trial result
        results.append({
            "shape": trial["shape"],
            "distractor_type": trial["distractor_type"],
            "reaction_time": reaction_time,
            "correct": correct
        })

        # Break after specified interval
        if (trial_index + 1) % BREAK_INTERVAL == 0 and trial_index + 1 < TOTAL_TRIALS:
            screen.fill(WHITE)
            break_text = font.render(BREAK_TEXT, True, BLACK)
            break_rect = break_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(break_text, break_rect)
            pygame.display.flip()

            waiting_for_space = True
            while waiting_for_space:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        waiting_for_space = False

    return results


# Main execution
def main():
    display_instructions()
    distractors = load_distractors()
    trials = generate_trials()
    results = run_experiment(trials, distractors)
    print("Experiment Completed! Results:")
    for result in results:
        print(result)


if __name__ == "__main__":
    main()
    pygame.quit()