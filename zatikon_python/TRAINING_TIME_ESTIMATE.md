# Training Time Estimate

## Current Setup
- **Games**: 100
- **MCTS simulations**: 50 per move
- **Max turns per game**: 300
- **Device**: CPU (default)

## Time Breakdown Per Game

### Components:
1. **MCTS per turn**: ~50 simulations
   - Each simulation: ~0.1-0.3 seconds (network evaluation + tree traversal)
   - Per turn: ~5-15 seconds
   
2. **Turns per game**: ~20-50 turns (typical)
   - Total MCTS time: ~100-750 seconds per game
   
3. **Turn generation**: ~0.1-0.5 seconds per turn
   - Total: ~2-25 seconds per game
   
4. **Training step**: ~0.1-0.5 seconds per game

### Estimated Time Per Game
- **Best case**: ~2-3 minutes
- **Typical case**: ~5-10 minutes  
- **Worst case**: ~15-20 minutes

### Total Time for 100 Games
- **Best case**: ~3-5 hours
- **Typical case**: ~8-17 hours
- **Worst case**: ~25-33 hours

## Factors Affecting Speed

### Slower:
- CPU-only (vs GPU)
- More MCTS simulations
- Longer games (more turns)
- Larger neural network
- First few games (cold start)

### Faster:
- GPU acceleration (`--device cuda`)
- Fewer MCTS simulations
- Shorter games
- Smaller network
- Later games (warmed up)

## Optimization Tips

1. **Use GPU** (if available):
   ```bash
   python -m zatikon.alphazero --mode train --device cuda
   ```
   - Can be 5-10x faster

2. **Reduce MCTS simulations** for faster iteration:
   ```bash
   python -m zatikon.alphazero --mode train --mcts_sims 25
   ```
   - ~2x faster, slightly lower quality

3. **Start with fewer games**:
   ```bash
   python -m zatikon.alphazero --mode train --train_games 10
   ```
   - Test the setup first

4. **Monitor progress**: The training loop prints progress every 5 games

## Real-Time Monitoring

The training loop prints:
```
[train] game N: loss=X.XXX, v_loss=X.XXX, p_loss=X.XXX, 
       team1_win=X.XXX, team2_win=X.XXX, draw_rate=X.XXX,
       game_time=X.Xs, train_time=X.XXXs, buffer=XXXX, lr=X.XXXXXX
```

Watch `game_time` to see actual per-game time and adjust expectations.

## Expected Timeline

For **100 games with 50 MCTS sims on CPU**:
- **First 10 games**: ~15-20 minutes each (cold start)
- **Games 11-50**: ~8-12 minutes each (warmed up)
- **Games 51-100**: ~5-10 minutes each (optimized)

**Total**: ~10-15 hours (realistic estimate)

## Quick Test

To test timing, run just 1 game:
```bash
python -m zatikon.alphazero --mode train --train_games 1 --mcts_sims 50
```

This will give you a real per-game time estimate for your hardware.

