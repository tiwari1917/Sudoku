// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const SCORE_KEY = 'sudoku-top-times';
const THEME_KEY = 'sudoku-theme';
let puzzle = [];
let difficulty = 'medium';
let startedAt = 0;
let timerHandle = null;
let solved = false;
let pendingScoreSeconds = 0;

function getBoard() {
  const inputs = [...document.querySelectorAll('.sudoku-cell')];
  return Array.from({length: SIZE}, (_, row) =>
    Array.from({length: SIZE}, (_, col) => {
      const value = inputs[row * SIZE + col].value;
      return value ? Number(value) : 0;
    })
  );
}

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
  const seconds = (totalSeconds % 60).toString().padStart(2, '0');
  return `${minutes}:${seconds}`;
}

function elapsedSeconds() {
  return Math.floor((Date.now() - startedAt) / 1000);
}

function startTimer() {
  clearInterval(timerHandle);
  startedAt = Date.now();
  document.getElementById('timer').innerText = '00:00';
  timerHandle = setInterval(() => {
    document.getElementById('timer').innerText = formatTime(elapsedSeconds());
  }, 1000);
}

function loadScores() {
  try {
    const storedScores = localStorage.getItem(SCORE_KEY);
    if (storedScores === null) return [];
    const scores = JSON.parse(storedScores);
    if (!Array.isArray(scores)) return null;
    return scores.filter(score =>
      score &&
      typeof score.name === 'string' &&
      Number.isFinite(score.seconds) &&
      score.seconds >= 0
    );
  } catch {
    return null;
  }
}

function renderScores() {
  const list = document.getElementById('score-list');
  const emptyMessage = document.getElementById('empty-scores');
  const scores = loadScores();
  list.replaceChildren();
  if (scores === null) {
    emptyMessage.textContent = 'Leaderboard unavailable because browser storage could not be read.';
    emptyMessage.hidden = false;
    return;
  }
  emptyMessage.textContent = 'Solve a puzzle to make the list.';
  scores.sort((a, b) => a.seconds - b.seconds).slice(0, 10).forEach((score, index) => {
    const row = document.createElement('tr');
    [index + 1, score.name, formatTime(score.seconds), score.difficulty, score.hints ?? 0].forEach(value => {
      const cell = document.createElement('td');
      cell.textContent = value;
      row.appendChild(cell);
    });
    list.appendChild(row);
  });
  emptyMessage.hidden = scores.length > 0;
}

function saveScore(event) {
  event.preventDefault();
  const name = document.getElementById('player-name').value.trim().slice(0, 24);
  if (!name) return;
  const scores = loadScores();
  if (scores === null) {
    showMessage('Your browser could not read the leaderboard; this score was not saved.', 'error');
    return;
  }
  scores.push({
    name,
    seconds: pendingScoreSeconds,
    difficulty,
    hints: Number(document.getElementById('hint-count').innerText),
  });
  try {
    localStorage.setItem(SCORE_KEY, JSON.stringify(scores.sort((a, b) => a.seconds - b.seconds).slice(0, 10)));
    document.getElementById('score-entry').hidden = true;
    document.getElementById('player-name').value = '';
    renderScores();
  } catch {
    showMessage('Your browser could not save the leaderboard.', 'error');
  }
}

function showMessage(text, kind = '') {
  const message = document.getElementById('message');
  message.textContent = text;
  message.dataset.kind = kind;
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.inputMode = 'numeric';
      input.setAttribute('aria-label', `Row ${i + 1}, column ${j + 1}`);
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function handleBoardInput(event) {
  const input = event.target;
  if (!(input instanceof HTMLInputElement) || !input.matches('.sudoku-cell') || input.disabled) return;
  input.value = input.value.replace(/[^1-9]/g, '').slice(0, 1);
  updateMoveFeedback();
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.classList.add('prefilled');
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

async function newGame() {
  const newGameButton = document.getElementById('new-game');
  const requestedDifficulty = document.getElementById('difficulty').value;
  newGameButton.disabled = true;
  try {
    const res = await fetch(`/new?difficulty=${requestedDifficulty}`);
    const data = await res.json();
    if (!res.ok) {
      showMessage(data.error || 'Unable to start a game.', 'error');
      return;
    }
    renderPuzzle(data.puzzle);
    difficulty = data.difficulty;
    solved = false;
    document.getElementById('hint-count').textContent = '0';
    document.getElementById('hint-button').disabled = false;
    document.getElementById('check-solution').disabled = false;
    document.getElementById('score-entry').hidden = true;
    showMessage('');
    startTimer();
  } catch {
    showMessage('Could not connect to the game server.', 'error');
  } finally {
    newGameButton.disabled = false;
  }
}

function updateMoveFeedback() {
  const inputs = [...document.querySelectorAll('.sudoku-cell')];
  const invalid = new Set();
  const markDuplicates = (indexes) => {
    const seen = new Map();
    for (const idx of indexes) {
      const value = inputs[idx].value;
      if (!value) continue;
      if (seen.has(value)) {
        invalid.add(idx);
        invalid.add(seen.get(value));
      } else {
        seen.set(value, idx);
      }
    }
  };

  for (let i = 0; i < SIZE; i++) {
    markDuplicates(Array.from({length: SIZE}, (_, j) => i * SIZE + j));
    markDuplicates(Array.from({length: SIZE}, (_, j) => j * SIZE + i));
  }
  for (let boxRow = 0; boxRow < 3; boxRow++) {
    for (let boxCol = 0; boxCol < 3; boxCol++) {
      const indexes = [];
      for (let row = 0; row < 3; row++) {
        for (let col = 0; col < 3; col++) {
          indexes.push((boxRow * 3 + row) * SIZE + boxCol * 3 + col);
        }
      }
      markDuplicates(indexes);
    }
  }

  inputs.forEach((input, idx) => {
    if (!input.disabled) input.classList.toggle('conflict', invalid.has(idx));
  });
  const message = document.getElementById('message');
  if (invalid.size) {
    showMessage('That entry conflicts with its row, column, or box.', 'error');
  } else if (message.dataset.kind === 'error') {
    showMessage('');
  }
}

async function checkSolution() {
  if (solved) return;
  const inputs = [...document.querySelectorAll('.sudoku-cell')];
  try {
    const res = await fetch('/check', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board: getBoard()}),
    });
    const data = await res.json();
    if (!res.ok || data.error) {
      showMessage(data.error || 'Could not check this puzzle.', 'error');
      return;
    }
    const incorrect = new Set(data.incorrect.map(([row, col]) => row * SIZE + col));
    inputs.forEach((input, index) => {
      if (!input.disabled) input.classList.toggle('incorrect', incorrect.has(index));
    });
    if (data.solved) {
      solved = true;
      clearInterval(timerHandle);
      pendingScoreSeconds = elapsedSeconds();
      document.getElementById('timer').textContent = formatTime(pendingScoreSeconds);
      document.getElementById('hint-button').disabled = true;
      document.getElementById('check-solution').disabled = true;
      showMessage(`Congratulations! You solved it in ${formatTime(pendingScoreSeconds)} with ${document.getElementById('hint-count').textContent} hints.`, 'success');
      document.getElementById('score-entry').hidden = false;
      document.getElementById('player-name').focus();
    } else if (incorrect.size) {
      showMessage('Some entries are incorrect.', 'error');
    } else {
      showMessage('Keep going; the puzzle is not complete yet.');
    }
  } catch {
    showMessage('Could not connect to the game server.', 'error');
  }
}

async function requestHint() {
  if (solved) return;
  try {
    const response = await fetch('/hint', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board: getBoard()}),
    });
    const data = await response.json();
    if (!response.ok) {
      showMessage(data.error || 'Unable to get a hint.', 'error');
      return;
    }
    const input = document.querySelector(`.sudoku-cell[data-row="${data.row}"][data-col="${data.col}"]`);
    input.value = data.value;
    input.disabled = true;
    input.classList.remove('incorrect');
    input.classList.add('hinted');
    document.getElementById('hint-count').textContent = data.hints;
    showMessage('A correct cell was revealed and locked.', 'success');
    updateMoveFeedback();
  } catch {
    showMessage('Could not connect to the game server.', 'error');
  }
}

function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  const button = document.getElementById('theme-toggle');
  const next = theme === 'dark' ? 'light' : 'dark';
  button.textContent = `${next === 'dark' ? '☾' : '☼'} ${next} mode`;
  button.setAttribute('aria-label', `Switch to ${next} mode`);
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch {
    showMessage('Theme preference cannot be saved in this browser.');
  }
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('sudoku-board').addEventListener('input', handleBoardInput);
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint-button').addEventListener('click', requestHint);
  document.getElementById('score-entry').addEventListener('submit', saveScore);
  document.getElementById('theme-toggle').addEventListener('click', () => {
    setTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');
  });
  let savedTheme = 'light';
  try {
    savedTheme = localStorage.getItem(THEME_KEY) || savedTheme;
  } catch {
    savedTheme = 'light';
  }
  if (savedTheme !== 'dark') savedTheme = 'light';
  setTheme(savedTheme);
  renderScores();
  newGame();
});