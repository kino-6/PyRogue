# PyRogue Refactored

This is a refactored version of the PyRogue game, focusing on:
- Clean architecture
- Better separation of concerns
- Improved maintainability
- Enhanced testability

## Project Structure

```
src2/
├── core/           # Core systems
│   ├── entity.py   # Entity base class
│   ├── map.py      # Map system
│   └── state.py    # State management
├── game/           # Game logic
│   ├── character.py
│   ├── item.py
│   └── effect.py
├── ui/             # UI system
│   ├── display.py
│   └── input.py
├── utils/          # Utilities
│   └── logger.py
└── main.py         # Entry point
```

## Development Plan

1. Core Systems
   - Entity system
   - Map system
   - State management

2. Game Logic
   - Character system
   - Item system
   - Effect system

3. UI System
   - Display system
   - Input handling

4. Integration and Testing
   - System integration
   - Test cases 