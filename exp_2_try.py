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
DISTRACTOR_ONLY_TIME = 1.0    # Duration to display the distractor alone
RESPONSE_WINDOW = 2.0         # Time allowed for participant to respond
FEEDBACK_TIME = 0.5           # Duration of feedback screen

# Break settings
BREAK_INTERVAL = 10           # Number of trials between breaks
BREAK_TEXT = "Take a short break!"

# Trial settings
TOTAL_TRIALS = 30             # Total number of trials in the experiment

# Instructions
INSTRUCTIONS = ("Primary Task: Categorize the shape in the center.\n"
                "Press J for Circle, K for Square, L for Triangle.\n"
                "Ignore the image around the shape.\n"
                "Press SPACE to start.")

# Paths to stimuli
SHAPES_PATH = {
    "circle": "shapes/circle",
    "square": "shapes/square",
    "triangle": "shapes/triangle"
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
pygame.display.set_caption("Emotion Categorization Experiment (Trial Version)")
font = pygame.font.Font(None, 50)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# Function to display experiment instructions
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


# Load all images from subfolders
def load_images(folder):
    if not os.path.exists(folder):
        raise FileNotFoundError(f"Folder not found: {folder}")
    images = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    print(f"Debug: Found {len(images)} images in {folder}")  # Debugging line
    if not images:
        raise ValueError(f"No valid images found in folder: {folder}")
    return images


# Load distractors
def load_distractors():
    distractors = {"happy": [], "angry": [], "neutral": []}
    for category, folder in DISTRACTORS_PATHS.items():
        distractors[category].extend(load_images(folder))
    return distractors


# Load shapes
def load_shapes():
    shapes = {"circle": [], "square": [], "triangle": []}
    for shape, folder in SHAPES_PATH.items():
        shapes[shape].extend(load_images(folder))
    return shapes


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


# Function to calculate break statistics
def calculate_statistics(results):
    total_trials = len(results)
    correct_trials = sum(1 for r in results if r["correctness"] == "Correct")
    total_reaction_time = sum(r["reaction_time"] for r in results if r["correctness"] == "Correct")
    
    percentage_correct = (correct_trials / total_trials) * 100 if total_trials > 0 else 0
    avg_reaction_time = (total_reaction_time / correct_trials) if correct_trials > 0 else 0

    return percentage_correct, avg_reaction_time


# Run experiment
def run_experiment(trials, shapes, distractors):
    session_results = []
    session_number = 1

    for trial_index, trial in enumerate(trials):
        # Fixation cross
        screen.fill(WHITE)
        fixation = font.render("+", True, BLACK)
        fixation_rect = fixation.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        screen.blit(fixation, fixation_rect)
        pygame.display.flip()
        pygame.time.delay(int(FIXATION_TIME * 1000))

        # Load distractor and shape
        distractor_img_path = random.choice(distractors[trial["distractor_type"]])
        distractor_img = pygame.image.load(distractor_img_path)
        distractor_img = pygame.transform.scale(distractor_img, (400, 400))
        distractor_rect = distractor_img.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        shape_img_path = random.choice(shapes[trial["shape"]])
        shape_img = pygame.image.load(shape_img_path)
        shape_img = pygame.transform.scale(shape_img, (200, 200))
        shape_rect = shape_img.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        # Display distractor only (for 1 second)
        screen.fill(WHITE)
        screen.blit(distractor_img, distractor_rect)
        pygame.display.flip()
        pygame.time.delay(int(DISTRACTOR_ONLY_TIME * 1000))  # Display distractor for 1 second

        # Display distractor + shape
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

        # Log trial result
        response_str = next((key for key, value in key_mapping.items() if value == response), "No Response")
        session_results.append({
            "distractor_type": trial["distractor_type"],
            "shape": trial["shape"],
            "response": response_str,
            "reaction_time": reaction_time if response else 0,
            "correctness": "Correct" if correct else "Incorrect"
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
        if (trial_index + 1) % BREAK_INTERVAL == 0 or trial_index + 1 == len(trials):
            percentage_correct, avg_reaction_time = calculate_statistics(session_results)

            # Display break statistics
            screen.fill(WHITE)
            stats_lines = [
                BREAK_TEXT,
                f"Percentage Correct: {percentage_correct:.2f}%",
                f"Average Reaction Time: {avg_reaction_time:.2f} seconds",
                "Press SPACE to continue."
            ]
            for i, line in enumerate(stats_lines):
                text_surface = font.render(line, True, BLACK)
                text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, 200 + i * 50))
                screen.blit(text_surface, text_rect)
            pygame.display.flip()

            # Wait for SPACE to continue
            waiting_for_space = True
            while waiting_for_space:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        waiting_for_space = False

            # Clear session results for the next session
            session_results = []
            session_number += 1


# Main execution
def main():
    display_instructions()
    distractors = load_distractors()
    shapes = load_shapes()
    trials = generate_trials()
    run_experiment(trials, shapes, distractors)
    print("Trial completed. No data saved.")


if __name__ == "__main__":
    main()
    pygame.quit()