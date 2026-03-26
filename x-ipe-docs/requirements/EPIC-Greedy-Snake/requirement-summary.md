# Greedy Snake — Requirement Summary

## Project Overview
A browser-based Greedy Snake game delivered as a single HTML file with embedded JavaScript and CSS.

## Functional Requirements

### FR-1: Game Board
- Canvas-based grid (20x20 default)
- Configurable grid size
- Clear visual grid boundaries

### FR-2: Snake Control
- Arrow keys and WASD for direction
- Snake cannot reverse direction (e.g., moving right cannot go left)
- Smooth continuous movement on a timer

### FR-3: Food System
- Food spawns at random unoccupied grid cells
- Food is visually distinct from the snake
- Eating food grows the snake by 1 segment

### FR-4: Collision Detection
- Wall collision → game over
- Self collision → game over
- Food collision → eat and grow

### FR-5: Scoring & High Score
- +10 points per food eaten
- High score persisted in localStorage
- Score displayed during gameplay

### FR-6: Game States
- **Start Screen**: Title + "Press Enter to Start"
- **Playing**: Active game loop
- **Paused**: Space key toggle
- **Game Over**: Final score + "Press Enter to Restart"

### FR-7: Difficulty Progression
- Base speed: 150ms per tick
- Speed increases by 5ms every 50 points (min 50ms)

### FR-8: Visual Polish
- Gradient-colored snake body
- Rounded food items
- Score display overlay
- Clean dark/light theme

## Non-Functional Requirements
- Single HTML file, zero dependencies
- Works in Chrome, Firefox, Safari, Edge
- Responsive canvas sizing
- 60fps rendering target
