# Client Implementation Roadmap

This document outlines the steps needed to create a playable terminal-based client for Zatikon using the existing basic units (Footman, Bear).

## Current Status ✅

We have implemented:
- ✅ BattleField with coordinates, unit management, targeting, events
- ✅ Castle with command economy, unit management, modifiers
- ✅ Unit base class with stats, state, actions, damage handling
- ✅ ActionMove and ActionAttack
- ✅ Event system (PREVIEW/WITNESS)
- ✅ UnitFactory with UnitFootman and UnitBear

## What's Needed for a Playable Client

### 1. Game State Management ⚠️

**Priority: HIGH**

- [ ] **Game class** - Main game controller
  - Track current player (TEAM_1 or TEAM_2)
  - Track game phase (DEPLOYMENT, ACTION, END_TURN)
  - Track game over state
  - Initialize two castles with proper locations

- [ ] **Castle locations** - Set castle positions on battlefield
  - Castle 1: Location 0 (top-left corner, 0,0)
  - Castle 2: Location 120 (bottom-right corner, 10,10)
  - Units deploy within range of their castle

### 2. Turn Flow System ⚠️

**Priority: HIGH**

- [ ] **Castle.start_turn()** - Already exists, verify it works correctly
  - Refresh commands (5 commands per turn)
  - Refresh all units (actions, deployed state)
  - Reset temporary modifiers

- [ ] **Castle.refresh()** - Already exists, verify it works correctly
  - Reset commands to MAX_COMMANDS
  - Reset temporary modifiers
  - Refresh all units

- [ ] **Game loop** - Main game loop
  - Player 1 turn → Player 2 turn → repeat
  - Handle END_TURN action
  - Check for victory after each action

### 3. Deployment System ⚠️

**Priority: HIGH**

- [ ] **Castle.deploy()** - Deploy unit from barracks to battlefield
  - Check deploy cost (unit.deploy_cost)
  - Check commands available
  - Validate deployment location (within range of castle)
  - Move unit from barracks to battlefield
  - Set unit location
  - Mark unit as deployed
  - Deduct commands

- [ ] **Castle.get_castle_targets()** - Get valid deployment locations
  - Locations within range 1 of castle
  - Empty locations only (or occupied by powerups)
  - Return list of valid locations

- [ ] **Unit.deploy_cost** - Add deploy_cost property to Unit
  - Footman: 0 (free deployment)
  - Bear: 1 (costs 1 command)

### 4. Victory Conditions ⚠️

**Priority: HIGH**

- [ ] **Check victory** - After each move/attack
  - If unit moves onto enemy castle location → Victory
  - Check unit.can_win flag (some units can't win)
  - Check armistice state (can't win during armistice)

- [ ] **Game.end_game()** - Handle game end
  - Set game over flag
  - Announce winner
  - Clean up

### 5. ActionRush Implementation ⚠️

**Priority: MEDIUM** (Footman uses ActionRush, not ActionAttack)

- [ ] **ActionRush** - Move + Attack combo action
  - If target > 1 range away, move closer first
  - Then attack target
  - Check for victory after move (if moved onto castle)
  - Single action cost (1 action, 1 command)

### 6. Terminal Client Interface ⚠️

**Priority: HIGH**

- [ ] **Board Display** - ASCII art board renderer
  - Display 11x11 grid
  - Show units with symbols (F=Footman, B=Bear)
  - Show castle locations (C1, C2)
  - Show coordinates

- [ ] **Unit Display** - Show unit information
  - Unit name, life, armor, damage
  - Available actions
  - Remaining actions/commands

- [ ] **Input Handler** - Accept player commands
  - Select unit (by location)
  - Select action (move, attack, deploy)
  - Select target location
  - End turn command

- [ ] **Command Parser** - Parse text commands
  - `deploy <unit_index> <location>` - Deploy unit
  - `select <location>` - Select unit
  - `move <location>` - Move selected unit
  - `attack <location>` - Attack with selected unit
  - `end` - End turn
  - `help` - Show help

- [ ] **Game State Display** - Show current state
  - Current player
  - Commands remaining
  - Turn number
  - Game phase

### 7. Missing Unit Properties ⚠️

**Priority: MEDIUM**

- [ ] **Unit.deploy_cost** - Cost to deploy unit
- [ ] **Unit.can_win** - Can this unit capture castle? (default: True)
- [ ] **Unit.castle_cost** - Cost to buy unit (for future use)

### 8. Castle Target Validation ⚠️

**Priority: HIGH**

- [ ] **BattleField.get_castle_targets()** - Get valid deployment locations
  - Locations within range 1 of castle
  - Empty locations (or powerups)
  - Not blocked by other units

### 9. Integration Points ⚠️

**Priority: HIGH**

- [ ] **ActionMove victory check** - Check if move wins game
  - After moving, check if location == enemy castle location
  - If yes, trigger victory

- [ ] **ActionRush victory check** - Check if rush wins game
  - After moving closer, check if on enemy castle
  - If yes, trigger victory

## Implementation Order

### Phase 1: Core Game Flow (Minimum Playable)
1. Game class with turn management
2. Castle locations on battlefield
3. Deployment system
4. Victory condition checking
5. Basic terminal client (display board, accept commands)

### Phase 2: ActionRush (Complete Footman)
6. ActionRush implementation
7. Update UnitFootman to use ActionRush

### Phase 3: Polish
8. Better terminal UI
9. Help system
10. Error messages
11. Game state persistence (optional)

## Example Game Flow

```
1. Initialize Game
   - Create BattleField with two Castles
   - Set Castle 1 at location 0 (0,0)
   - Set Castle 2 at location 120 (10,10)
   - Add units to barracks (Footman, Bear)

2. Player 1 Turn
   - Refresh Castle 1 (5 commands, refresh units)
   - Display board
   - Player deploys units (costs commands)
   - Player moves/attacks with units
   - Player ends turn

3. Player 2 Turn
   - Refresh Castle 2
   - Same as Player 1

4. Repeat until victory
   - Check victory after each move/attack
   - If unit on enemy castle → Victory
```

## Testing Strategy

For each component:
1. Write tests first (TDD)
2. Implement functionality
3. Integration tests with game loop
4. Manual testing with terminal client

## Estimated Complexity

- **Game State Management**: Medium (2-3 hours)
- **Turn Flow**: Low (1 hour, mostly exists)
- **Deployment System**: Medium (2-3 hours)
- **Victory Conditions**: Low (1 hour)
- **ActionRush**: Medium (2 hours)
- **Terminal Client**: High (4-6 hours)
- **Integration**: Medium (2-3 hours)

**Total**: ~15-20 hours of focused development

## Next Steps

1. Start with Game class and turn management
2. Add deployment system
3. Create basic terminal client
4. Test with manual gameplay
5. Add ActionRush
6. Polish UI

