# AlphaZero Training Guide

## Overview

This guide explains how to train the AlphaZero-style Zatikon agent.

## Quick Start

### Basic Training

```bash
# Train for 100 games with default settings
python -m zatikon.alphazero --mode train --train_games 100

# Train with more MCTS simulations (better but slower)
python -m zatikon.alphazero --mode train --train_games 100 --mcts_sims 100

# Train with GPU (if available)
python -m zatikon.alphazero --mode train --train_games 100 --device cuda
```

### Evaluation

```bash
# Evaluate latest model against RandomAI
python -m zatikon.alphazero --mode eval --eval_games 20

# Evaluate specific model
python -m zatikon.alphazero --mode eval --model_path zatikon_net_g500.pt --eval_games 20
```

## Training Parameters

### Core Parameters

- `--train_games`: Number of self-play games to generate (default: 100)
- `--mcts_sims`: MCTS simulations per move (default: 50)
  - More simulations = better moves but slower training
  - Recommended: 50-200 for training, 400+ for evaluation
- `--batch_size`: Batch size for training (default: 64)
- `--lr`: Learning rate (default: 1e-3)
- `--lr_decay`: Learning rate decay factor (default: 0.99)
  - Applied every `save_every` games
  - 1.0 = no decay, <1.0 = decay

### Checkpointing

- `--save_every`: Save checkpoint every N games (default: 200)
- Checkpoints are saved as `zatikon_net_g{N}.pt`
- Latest checkpoint is always saved as `zatikon_net_latest.pt`

### Evaluation

- `--eval_every`: Evaluate model every N games (default: 50)
- `--eval_games`: Number of games for evaluation (default: 10)
- Evaluation plays model against RandomAI

## Training Process

### Self-Play

1. **Game Generation**: MCTS generates self-play games
2. **Data Collection**: Action-level training data is collected
3. **Training**: Network is trained on collected data
4. **Evaluation**: Model is periodically evaluated against RandomAI

### Training Data

Each training example contains:
- **State**: Encoded game state (327 planes, 11x11 board)
- **Policy**: MCTS action-level policy (31703 actions)
- **Value**: Turn value or game outcome (-1 to +1)

### Loss Function

- **Value Loss**: MSE between predicted and actual value
- **Policy Loss**: Cross-entropy between predicted and MCTS policy
- **Total Loss**: Value Loss + Policy Loss

## Checkpoint Management

### Loading Checkpoints

Training automatically resumes from the latest checkpoint:
- Searches for `zatikon_net_g*.pt` files
- Loads the one with highest game count
- Falls back to `zatikon_net_latest.pt` if no numbered checkpoints

### Checkpoint Contents

Each checkpoint contains:
- `model_state_dict`: Neural network weights
- `optimizer_state_dict`: Optimizer state (for resuming)
- `total_games`: Number of games played
- `metadata`: Training statistics (losses, win rates, etc.)

### Analyzing Checkpoints

```python
from zatikon.training_utils import analyze_checkpoint

analyze_checkpoint("zatikon_net_g500.pt")
```

## Training Tips

### Early Training

- Start with fewer MCTS simulations (25-50) for faster iteration
- Use higher learning rate (1e-3 to 5e-3)
- Focus on getting the training loop working

### Mid Training

- Increase MCTS simulations (50-100)
- Reduce learning rate (5e-4 to 1e-3)
- Monitor evaluation win rate

### Advanced Training

- Use many MCTS simulations (100-200+)
- Lower learning rate (1e-4 to 5e-4)
- Train for many games (1000+)

### Monitoring Training

Watch for:
- **Loss decreasing**: Good sign
- **Win rate increasing**: Model improving
- **Loss plateauing**: May need learning rate adjustment
- **Win rate ~0.5**: Model learning balanced play

## Troubleshooting

### Out of Memory

- Reduce `batch_size`
- Reduce `mcts_sims`
- Use CPU instead of GPU

### Training Too Slow

- Reduce `mcts_sims`
- Reduce `eval_every` or set to 0
- Use GPU if available

### Model Not Improving

- Check if losses are decreasing
- Try different learning rate
- Increase MCTS simulations
- Train for more games

### Checkpoint Issues

- Ensure sufficient disk space
- Check file permissions
- Verify checkpoint format with `analyze_checkpoint`

## Example Training Scripts

### Short Training Run

```bash
python -m zatikon.alphazero \
    --mode train \
    --train_games 50 \
    --mcts_sims 25 \
    --batch_size 32 \
    --save_every 50
```

### Long Training Run

```bash
python -m zatikon.alphazero \
    --mode train \
    --train_games 1000 \
    --mcts_sims 100 \
    --batch_size 64 \
    --lr 5e-4 \
    --lr_decay 0.995 \
    --save_every 200 \
    --eval_every 100 \
    --eval_games 20 \
    --device cuda
```

### Evaluation Only

```bash
python -m zatikon.alphazero \
    --mode eval \
    --model_path zatikon_net_g1000.pt \
    --eval_games 50
```

## Advanced Usage

### Custom Training Loop

```python
from zatikon.alphazero import ZatikonNet, train, load_latest_model

net = ZatikonNet()
start_games, metadata = load_latest_model(net)

train(net,
      n_games=100,
      mcts_sims=50,
      start_games=start_games,
      device="cuda")
```

### Plotting Training Curves

```python
from zatikon.training_utils import plot_training_curves, load_latest_model
from zatikon.alphazero import ZatikonNet

net = ZatikonNet()
_, metadata = load_latest_model(net)
plot_training_curves(metadata, "training_curves.png")
```

## Performance Expectations

### Training Speed

- **CPU**: ~1-5 games/minute (depending on MCTS sims)
- **GPU**: ~5-20 games/minute (depending on hardware)

### Model Quality

- **RandomAI baseline**: ~50% win rate
- **After 100 games**: ~60-70% win rate
- **After 500 games**: ~70-80% win rate
- **After 1000+ games**: ~80-90% win rate

*Note: Actual performance depends on hyperparameters and training setup.*

