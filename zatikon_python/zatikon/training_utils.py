"""
Training utilities for AlphaZero Zatikon.
"""
import os
import json
import torch
import numpy as np
from typing import Dict, List, Tuple
from zatikon.alphazero import ZatikonNet, load_latest_model, evaluate_model


def plot_training_curves(metadata: Dict, save_path: str = "training_curves.png"):
    """
    Plot training curves from metadata.
    
    Args:
        metadata: Metadata dictionary with loss lists
        save_path: Path to save plot
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("[warn] matplotlib not available, skipping plot")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    # Loss curves
    if 'train_losses' in metadata:
        losses = metadata['train_losses']
        axes[0, 0].plot(losses)
        axes[0, 0].set_title('Training Loss')
        axes[0, 0].set_xlabel('Update')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].grid(True)
    
    if 'value_losses' in metadata:
        v_losses = metadata['value_losses']
        axes[0, 1].plot(v_losses)
        axes[0, 1].set_title('Value Loss')
        axes[0, 1].set_xlabel('Update')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].grid(True)
    
    if 'policy_losses' in metadata:
        p_losses = metadata['policy_losses']
        axes[1, 0].plot(p_losses)
        axes[1, 0].set_title('Policy Loss')
        axes[1, 0].set_xlabel('Update')
        axes[1, 0].set_ylabel('Loss')
        axes[1, 0].grid(True)
    
    # Win rates
    if 'team1_wins' in metadata and 'team2_wins' in metadata:
        team1_wins = metadata.get('team1_wins', 0)
        team2_wins = metadata.get('team2_wins', 0)
        draws = metadata.get('draws', 0)
        total = team1_wins + team2_wins + draws
        
        if total > 0:
            axes[1, 1].bar(['Team 1', 'Team 2', 'Draws'],
                          [team1_wins/total, team2_wins/total, draws/total])
            axes[1, 1].set_title('Win Rates')
            axes[1, 1].set_ylabel('Rate')
            axes[1, 1].set_ylim([0, 1])
    
    plt.tight_layout()
    plt.savefig(save_path)
    print(f"[plot] Saved training curves to {save_path}")


def compare_models(model_paths: List[str], n_games: int = 20, device: str = "cpu"):
    """
    Compare multiple models by playing them against each other.
    
    Args:
        model_paths: List of paths to model files
        n_games: Number of games per matchup
        device: Device to use
        
    Returns:
        Dictionary of results
    """
    models = []
    for path in model_paths:
        net = ZatikonNet()
        checkpoint = torch.load(path, map_location=device)
        net.load_state_dict(checkpoint['model_state_dict'])
        net.eval()
        models.append((net, path))
    
    results = {}
    
    for i, (net1, path1) in enumerate(models):
        for j, (net2, path2) in enumerate(models):
            if i >= j:
                continue
            
            # Play games
            wins1 = 0
            wins2 = 0
            draws = 0
            
            # TODO: Implement model vs model evaluation
            # For now, just evaluate against RandomAI
            win_rate1 = evaluate_model(net1, n_games=n_games, device=device)
            win_rate2 = evaluate_model(net2, n_games=n_games, device=device)
            
            results[f"{os.path.basename(path1)} vs {os.path.basename(path2)}"] = {
                'model1_win_rate': win_rate1,
                'model2_win_rate': win_rate2,
            }
    
    return results


def export_training_stats(metadata: Dict, output_path: str = "training_stats.json"):
    """
    Export training statistics to JSON.
    
    Args:
        metadata: Metadata dictionary
        output_path: Path to save JSON file
    """
    # Convert numpy arrays to lists for JSON serialization
    export_data = {}
    for key, value in metadata.items():
        if isinstance(value, np.ndarray):
            export_data[key] = value.tolist()
        elif isinstance(value, (np.integer, np.floating)):
            export_data[key] = float(value)
        else:
            export_data[key] = value
    
    with open(output_path, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"[export] Saved training stats to {output_path}")


def analyze_checkpoint(checkpoint_path: str):
    """
    Analyze a checkpoint file and print statistics.
    
    Args:
        checkpoint_path: Path to checkpoint file
    """
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    
    print(f"\n=== Checkpoint Analysis: {checkpoint_path} ===")
    print(f"Total games: {checkpoint.get('total_games', 'Unknown')}")
    
    if 'metadata' in checkpoint:
        metadata = checkpoint['metadata']
        print(f"\nTraining Statistics:")
        if 'train_losses' in metadata:
            losses = metadata['train_losses']
            if len(losses) > 0:
                print(f"  Final training loss: {losses[-1]:.4f}")
                print(f"  Average training loss: {np.mean(losses):.4f}")
        
        if 'team1_wins' in metadata:
            team1_wins = metadata.get('team1_wins', 0)
            team2_wins = metadata.get('team2_wins', 0)
            draws = metadata.get('draws', 0)
            total = team1_wins + team2_wins + draws
            if total > 0:
                print(f"  Team 1 win rate: {team1_wins/total:.3f}")
                print(f"  Team 2 win rate: {team2_wins/total:.3f}")
                print(f"  Draw rate: {draws/total:.3f}")
    
    # Model parameters
    if 'model_state_dict' in checkpoint:
        total_params = sum(p.numel() for p in checkpoint['model_state_dict'].values())
        print(f"\nModel Parameters: {total_params:,}")
    
    print()

