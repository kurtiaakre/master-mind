# Master Mind Project Overview

## Project Basics
- Language: Python
- Game: Classic Master Mind (code-breaking game)
- Initial Focus: Presentation layer (screen/GUI) first
- Structure: Divide game components into separate modules (likely separate files for modularity)
- Note: Main module may include ALL output-related code for simplicity

## Game Modes
- Players: Judge (code maker) and Guesser (code breaker)
- Available Modes:
  - Human/Human
  - AI/Human
  - Human/AI
  - AI/AI (pointless for gameplay, but interesting for coding/technological exploration)

## Main Module Responsibilities
This module handles the core flow and user interaction:
- Initialization of the program
- Presentation of the GUI
- Interaction for choosing game mode (e.g., Judge/Guesser combinations as listed above)
- Updating of the GUI
- Initiate interaction:
  - Ask for guess if guesser is human/player
  - Ask for judgement if judge is human/player
- Presentation of results (e.g., judgements or guesses)
- Validation of win/loss conditions:
  - Win: 4 black pegs (exact match)
  - Loss: 12 rows used without achieving 4 black pegs
- Concluding the game
- Exit the game

## Second Module: Player/AI Logic
This module contains procedures for handling guesses and judgements (generally as functions/procedures):
- Player making a judgement: No input supplied; returns a judgement
- AI making a judgement: Supply a guess; returns a judgement
- Player making a guess: No input supplied; returns a guess
- AI making a guess: Supply a list of all previous guesses & judgements; returns a guess

## Project Progress and Plans
- **What We've Done:** (To be updated as we progress)
- **What We Plan to Do:** (To be updated as we work; e.g., implement GUI, add AI logic, etc.)
- Notes: This document will be fed back into sessions for continuity and updated accordingly. No code to be supplied yet—focus on planning and structure.