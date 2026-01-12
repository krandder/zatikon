# Zatikon Python Implementation

A terminal-based implementation of Zatikon, a tactical strategy game.

## Status

✅ **Playable!** The game is now fully functional with:
- Complete game engine (turn flow, victory conditions, action handling)
- Terminal client with ASCII board display
- Command-based interface
- Two unit types (Footman, Bear)

## Quick Start

### Human vs Human
```bash
cd zatikon_python
source venv/bin/activate
python -m zatikon.main
```

### AI vs AI (Random)
```bash
cd zatikon_python
source venv/bin/activate
python -m zatikon.ai_client
```

See [PLAY.md](PLAY.md) for detailed gameplay instructions.

## Running Tests

```bash
cd zatikon_python
source venv/bin/activate
python -m pytest tests/ -v
```

All 189 tests passing ✅

## Project Structure

```
zatikon_python/
├── zatikon/              # Core game logic
│   ├── __init__.py
│   ├── constants.py     # Game constants
│   ├── battlefield.py   # Board and coordinate system
│   ├── castle.py        # Castle and command economy
│   ├── unit.py          # Base unit class
│   ├── unit_factory.py  # Unit creation
│   ├── action.py        # Action base class
│   ├── actions/         # Action implementations
│   │   ├── action_move.py
│   │   └── action_attack.py
│   ├── event.py         # Event system
│   ├── game.py          # Game controller
│   ├── terminal_client.py  # Terminal UI
│   └── main.py          # Main game loop
├── tests/               # Test suite
└── requirements.txt     # Dependencies
```

## Features Implemented

- ✅ BattleField coordinate system
- ✅ Unit management and movement
- ✅ Attack system with damage calculation
- ✅ Event system (PREVIEW/WITNESS)
- ✅ Turn flow and command economy
- ✅ Deployment system
- ✅ Victory conditions
- ✅ Terminal client with board display
- ✅ Command parser

## Next Steps

- [ ] ActionRush (move + attack combo for Footman)
- [ ] More unit types
- [ ] Spell actions
- [ ] Unit-specific events
- [ ] Better terminal UI (colors, better formatting)

## Development

This project follows Test-Driven Development (TDD). All features are implemented with tests first.

See [PROGRESS.md](PROGRESS.md) for detailed progress tracking.
