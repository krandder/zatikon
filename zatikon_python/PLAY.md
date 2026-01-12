# How to Play Zatikon

## Running the Game

### Human vs Human Mode
```bash
cd zatikon_python
source venv/bin/activate
python -m zatikon.main
```

### AI vs AI Mode (Random)
Watch two random AIs play against each other:
```bash
cd zatikon_python
source venv/bin/activate
python -m zatikon.ai_client
```

## Game Rules

### Objective
Move a unit onto your opponent's castle to win!

### Setup
- Each player starts with units in their barracks
- Castle 1 (Player 1) is at location 0 (top-left, 0,0)
- Castle 2 (Player 2) is at location 120 (bottom-right, 10,10)

### Turn Flow
1. **Deploy Phase**: Deploy units from barracks to the battlefield
   - Units can deploy adjacent to your castle (within range 1)
   - Each unit has a deploy cost (Footman: 0, Bear: 1)
   - You have 5 commands per turn

2. **Action Phase**: Move and attack with deployed units
   - Select a unit, then move or attack
   - Units have limited actions per turn
   - Commands are consumed for actions

3. **End Turn**: Type `end` to end your turn

### Commands

- `deploy <index> <location>` - Deploy unit from barracks
  - Example: `deploy 0 1` (deploy unit at index 0 to location 1)
  
- `select <location>` - Select a unit
  - Example: `select 1` (select unit at location 1)
  
- `move <location>` - Move selected unit
  - Example: `move 2` (move to location 2)
  
- `attack <location>` - Attack with selected unit
  - Example: `attack 11` (attack unit at location 11)
  
- `end` - End your turn
  
- `help` - Show help

### Location Format
- Coordinates: `5,5` (x=5, y=5)
- Location number: `60` (direct location number)

### Example Gameplay

```
> deploy 0 1
Deployed Footman to location 1

> select 1
Selected Footman at location 1

> move 2
OK

> attack 11
Footman attacked EnemyFootman for 2 damage

> end
Turn ended
```

## Current Units

- **Footman**: Basic melee unit (4 life, 2 armor, 3 damage, 2 actions)
- **Bear**: Strong melee unit (6 life, 1 armor, 4 damage, 2 actions)

## Tips

- Deploy units near your castle first
- Use commands wisely - you only get 5 per turn
- Move units toward the enemy castle to win
- Attack enemy units to clear the path
- Watch your unit's life - dead units are removed from the board

