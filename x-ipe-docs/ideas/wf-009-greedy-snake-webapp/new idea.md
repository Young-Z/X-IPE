# Greedy Snake Web App

## Problem
Build a classic greedy snake (Snake Game) as a standalone web application. The game should be fun, responsive, and playable in any modern browser without requiring any server-side logic.

## What to Build
A single-page web application implementing the classic Snake game where:
- The snake moves on a grid-based canvas
- - Player controls the snake using arrow keys (or WASD)
- - Snake grows longer when eating food
- - Game ends when the snake hits the wall or itself
- - Score tracking with high score persistence (localStorage)

## Key Features
1. **Game Canvas** — Responsive HTML5 Canvas with grid-based rendering
2. 2. **Snake Movement** — Smooth directional movement with keyboard controls (Arrow keys + WASD)
3. 3. **Food System** — Random food placement on the grid, snake grows on consumption
4. 4. **Collision Detection** — Wall collision and self-collision detection for game over
5. 5. **Score System** — Current score display, high score saved to localStorage
6. 6. **Game States** — Start screen, playing, paused (Space key), game over screen with restart
7. 7. **Speed Progression** — Snake speed increases as score grows for difficulty scaling
8. 8. **Mobile Support** — Touch/swipe controls for mobile devices
9. 9. **Visual Polish** — Clean modern UI with gradient snake body, grid lines, and animations

## Tech Stack
- Pure HTML5 + CSS3 + Vanilla JavaScript (no frameworks)
- - HTML5 Canvas for game rendering
- - Single HTML file deployment (self-contained)