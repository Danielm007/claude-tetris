# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Idioma

Responde siempre en español en este proyecto: explicaciones, resúmenes, preguntas y mensajes de commit/PR.

## Running

Vanilla HTML/CSS/JS Tetris with no dependencies: no package.json, build step, linter, or test suite. Open `index.html` directly, or serve the folder with a static server:

    python3 -m http.server 8000   # then open http://localhost:8000

You can only verify a change by loading the page in a browser and playing.

## Architecture

All game logic lives in `game.js`, a single classic (non-module) script in `'use strict'` mode that `index.html` loads at the end of `<body>`. It uses module-level mutable globals (`board`, `current`, `next`, `score`, `lines`, `level`, `paused`, `gameOver`, `dropInterval`, `dropAccum`, `lastTime`, `animId`). `init()` resets all of them and also runs as the restart handler.

Key conventions that span several functions:

- **Piece type = color index = board cell value.** `PIECES[t]` matrices are filled with the value `t` (1–7), and `COLORS[t]` is its color. `merge()` copies those values straight into `board`, so a cell's value is also its color. Index 0 / `null` means empty. If you add or reorder pieces, keep `PIECES`, `COLORS`, and `randomPiece()` (hardcoded `* 7`) in sync.
- **Collision is the single gate for movement.** Every move, rotation, drop, the ghost projection (`ghostY`), and spawn-time game-over detection go through `collide(shape, x, y)`. Cells above the board (`y < 0`) count as free.
- **Rotation** is clockwise only (`rotateCW`, a transpose-and-reverse on the square matrix). `tryRotate` applies a simple horizontal kick list `[0, -1, 1, -2, 2]`. This is not SRS.
- **Piece lifecycle:** gravity in `loop` / `softDrop` / `hardDrop` → `lockPiece()` → `merge()` → `clearLines()` (updates score, lines, level, and `dropInterval`) → `spawn()` (promotes `next`, and calls `endGame()` if the new piece collides immediately).
- **Game loop** uses `requestAnimationFrame` with a time accumulator (`dropAccum` vs. `dropInterval`). Pause and game over call `cancelAnimationFrame(animId)`; resuming resets `lastTime` and calls `loop` again.
- **Rendering** redraws the whole board every frame in `draw()` (grid → locked cells → ghost at alpha 0.2 → current piece). The next-piece preview (`drawNext`) redraws only on spawn, on its own 120×120 canvas that fits a 4×4 grid.
- **DOM coupling:** `game.js` looks up elements by id (`board`, `next-canvas`, `score`, `lines`, `level`, `overlay`, `overlay-title`, `overlay-score`, `restart-btn`). One overlay serves both pause and game over, and the code sets its text.

## Gotchas

- The board canvas size in `index.html` (`300×600`) must equal `COLS*BLOCK × ROWS*BLOCK`. Changing `COLS`, `ROWS`, or `BLOCK` in `game.js` means updating the `<canvas id="board">` attributes too.
- User-facing text (overlay messages, controls list, README) is in Spanish. Keep new UI strings consistent.
