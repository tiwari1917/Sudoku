# Refactor a Sudoku Game written in Python Flask

Use this simple Sudoku game as a starting point to practice your skills with GitHub Copilot. The goal is to refactor the code to use modern technologies, while also adding new features and improving the overall user experience.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Dependencies

```
- Modern web browser (Chrome, Firefox, Edge, etc.)
- Python 3
```

### Installation

1. Fork this repository to your GitHub account. (You can use the "Fork" button on the top right corner of the repository page.)

2. Clone your forked repository to your local machine.

3. Open a terminal window and navigate to the "github-copilot-python/starter" directory.

4. Create a Python virtual environment and activate it (optional but highly recommended).

```bash
python3 -m venv .venv
source .venv/bin/activate
```

5. Install required Python packages.

```bash
pip install -r requirements.txt
```

6. Run the Flask app.

```bash
python app.py
```

7. Open http://127.0.0.1:5000 in your browser.

## Tests

From the repository root, install the development dependencies and run the test suite:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest starter/tests -q
```

## Project Instructions

Use GitHub Copilot to refactor the code for this game to add more advanced features. The goal is to create a more modern and maintainable codebase and add additional functionality to the final product. You can use any combination of code completion and chat features, like Ask, Edit, or Agent modes.

- Errors should be handled gracefully with appropriate messages to the user.
- Implement a Sudoku board generator that creates a valid Sudoku puzzle with a unique solution.
- Add a timer to track how long it takes to solve the puzzle.
- Implement a solution checker that verifies if the user's solution is correct using event delegation.
- Add a difficulty selector to allow users to choose between easy, medium, and hard puzzles.
- Add a hint feature that provides clues for the user that are noted with unique colors.
- Add a check puzzle button that checks the current state of the board against the solution.
- User should get immediate feedback on their input, such as highlighting invalid entries.
- Top 10 scores should be saved in local storage and displayed on the page with the user's name, time taken, hints used, and difficulty level.
- The game should be responsive and work well on both desktop and mobile devices.
- UI colors should be visually appealing and accessible.
- Completed and correct puzzles should display a congratulatory message with the time taken and hints used and ask for the user's name for Top 10 times.

## Copilot Setup and Use

Document how GitHub Copilot helped with the work. Use screenshots that show the relevant prompt or suggestion, your review of it, and the resulting change or verification. Treat Copilot as an assistant: check suggestions against the project requirements, edit or reject incorrect or inefficient output, and run the relevant tests rather than accepting generated code without review.

Include evidence for these milestones:

- Testing framework: show how the test framework was installed or configured, and how the tests were run.
- Unique puzzle solutions: show the prompt and the implementation or test that verifies a generated puzzle has exactly one solution.
- Top 10 scores: show the implementation of score recording and retrieval with local storage, including the displayed player name, time, hints, and difficulty.
- 3×3 grid styling: show the CSS or UI change that distinguishes the 3×3 Sudoku boxes, and check that the colors remain readable and accessible.

Give screenshots descriptive filenames that identify their evidence, for example `copilot_testing_framework.png`, `copilot_unique_solution_prompt.png`, `copilot_top10_scores.png`, and `copilot_grid_styling.png`. Keep them in `Screenshots/`; make sure each filename matches the actual screenshot content.

### References

- [GitHub Copilot configuration](https://docs.github.com/en/copilot/configuring-copilot)
- [GitHub Copilot prompt and instruction best practices](https://docs.github.com/en/copilot/using-github-copilot/best-practices-for-writing-prompts)
- [GitHub Blog: Copilot instructions](https://github.blog/changelog/2024-03-27-github-copilot-workflows-and-instructions/)
- [GitHub Copilot responsible use guidelines](https://docs.github.com/en/copilot/responsible-use-of-github-copilot)
- [W3C WCAG 2.1 contrast guidance](https://www.w3.org/WAI/WCAG21/quickref/#contrast-minimum)
- [Sudoku hint logic example](https://medium.com/@vishalg94/sudoku-game-using-javascript-4f048a042b8e)
- [Input validation and mistake highlighting](https://www.geeksforgeeks.org/sudoku-solver-in-javascript/)
- [How unique Sudoku puzzles are generated](https://www.sudokuwiki.org/Sudoku_Creation_and_Grading)
