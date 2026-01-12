"""
Residue Number System (RNS) encoding for exact numeric values.

Uses different bases for different value ranges:
- HP: mod 3, 5, 7, 11 (can represent 0-1154, but we use 0-31)
- Armor: mod 3, 5, 7 (can represent 0-104, but we use 0-7)
- Damage: mod 3, 5, 7 (can represent 0-104, but we use 0-15)
- Actions: mod 3, 5, 7 (can represent 0-104, but we use 0-7)
"""

from typing import List, Tuple
from functools import reduce


# Base sets for RNS encoding
HP_BASES = [3, 5, 7, 11]  # For HP (0-31 range, but can go higher)
STAT_BASES = [3, 5, 7]    # For armor, damage, actions (smaller ranges)


def encode_rns(value: int, bases: List[int]) -> List[float]:
    """
    Encode an integer value using Residue Number System.
    
    Args:
        value: Integer value to encode (must be >= 0)
        bases: List of coprime bases to use for encoding
    
    Returns:
        List of float values (0.0 or 1.0) representing one-hot encoding
        of residues for each base
    
    Example:
        encode_rns(17, [3, 5, 7])
        Returns: [0,0,1, 0,0,1,0,0, 0,0,0,0,0,1,0]
                 (17 mod 3 = 2, 17 mod 5 = 2, 17 mod 7 = 3)
    """
    encoded = []
    for base in bases:
        residue = value % base
        # One-hot encode the residue
        for i in range(base):
            encoded.append(1.0 if i == residue else 0.0)
    return encoded


def decode_rns(encoded: List[float], bases: List[int]) -> int:
    """
    Decode an RNS-encoded value back to integer.
    
    Uses Chinese Remainder Theorem to recover the original value.
    
    Args:
        encoded: List of float values (0.0 or 1.0) from encode_rns
        bases: List of coprime bases used for encoding
    
    Returns:
        Recovered integer value
    
    Note: This is mainly for testing/debugging. The neural network
    will learn to decode implicitly.
    """
    # Extract residues from one-hot encoding
    residues = []
    idx = 0
    for base in bases:
        # Find which bit is set in this base's encoding
        residue = None
        for i in range(base):
            if encoded[idx + i] > 0.5:  # Threshold for binary
                residue = i
                break
        if residue is None:
            # No bit set - default to 0
            residue = 0
        residues.append(residue)
        idx += base
    
    # Chinese Remainder Theorem to recover value
    # For small bases, we can use brute force
    max_value = reduce(lambda x, y: x * y, bases, 1)
    for value in range(max_value):
        valid = True
        for i, base in enumerate(bases):
            if value % base != residues[i]:
                valid = False
                break
        if valid:
            return value
    
    # Should not reach here
    return 0


def encode_hp(hp: int, max_hp: int = 31) -> List[float]:
    """
    Encode current HP using RNS with bases [3, 5, 7, 11].
    
    Args:
        hp: Current HP value (0 to max_hp)
        max_hp: Maximum HP value (default 31)
    
    Returns:
        List of 26 float values (3+5+7+11 = 26 planes)
    """
    hp_clamped = max(0, min(hp, max_hp))
    return encode_rns(hp_clamped, HP_BASES)


def encode_hp_max(hp_max: int, max_hp_max: int = 31) -> List[float]:
    """
    Encode maximum HP using RNS with bases [3, 5, 7, 11].
    
    Args:
        hp_max: Maximum HP value (0 to max_hp_max)
        max_hp_max: Maximum possible HP value (default 31)
    
    Returns:
        List of 26 float values (3+5+7+11 = 26 planes)
    """
    hp_max_clamped = max(0, min(hp_max, max_hp_max))
    return encode_rns(hp_max_clamped, HP_BASES)


def encode_armor(armor: int, max_armor: int = 7) -> List[float]:
    """
    Encode armor using RNS with bases [3, 5, 7].
    
    Args:
        armor: Armor value (0 to max_armor)
        max_armor: Maximum armor value (default 7)
    
    Returns:
        List of 15 float values (3+5+7 = 15 planes)
    """
    armor_clamped = max(0, min(armor, max_armor))
    return encode_rns(armor_clamped, STAT_BASES)


def encode_damage(damage: int, max_damage: int = 15) -> List[float]:
    """
    Encode damage using RNS with bases [3, 5, 7].
    
    Args:
        damage: Damage value (0 to max_damage)
        max_damage: Maximum damage value (default 15)
    
    Returns:
        List of 15 float values (3+5+7 = 15 planes)
    """
    damage_clamped = max(0, min(damage, max_damage))
    return encode_rns(damage_clamped, STAT_BASES)


def encode_actions(actions: int, max_actions: int = 7) -> List[float]:
    """
    Encode current actions left using RNS with bases [3, 5, 7].
    
    Args:
        actions: Current actions left (0 to max_actions)
        max_actions: Maximum actions value (default 7)
    
    Returns:
        List of 15 float values (3+5+7 = 15 planes)
    """
    actions_clamped = max(0, min(actions, max_actions))
    return encode_rns(actions_clamped, STAT_BASES)


def encode_actions_max(actions_max: int, max_actions_max: int = 7) -> List[float]:
    """
    Encode maximum actions using RNS with bases [3, 5, 7].
    
    Args:
        actions_max: Maximum actions value (0 to max_actions_max)
        max_actions_max: Maximum possible actions value (default 7)
    
    Returns:
        List of 15 float values (3+5+7 = 15 planes)
    """
    actions_max_clamped = max(0, min(actions_max, max_actions_max))
    return encode_rns(actions_max_clamped, STAT_BASES)


def encode_deploy_cost(cost: int, max_cost: int = 5) -> List[float]:
    """
    Encode deploy cost using RNS with bases [3, 5, 7].
    
    Args:
        cost: Deploy cost value (0 to max_cost)
        max_cost: Maximum deploy cost (default 5)
    
    Returns:
        List of 15 float values (3+5+7 = 15 planes)
    """
    cost_clamped = max(0, min(cost, max_cost))
    return encode_rns(cost_clamped, STAT_BASES)


def encode_commands(commands: int, max_commands: int = 5) -> List[float]:
    """
    Encode commands left using RNS with bases [3, 5, 7].
    
    Args:
        commands: Commands left (0 to max_commands)
        max_commands: Maximum commands (default 5)
    
    Returns:
        List of 15 float values (3+5+7 = 15 planes)
    """
    commands_clamped = max(0, min(commands, max_commands))
    return encode_rns(commands_clamped, STAT_BASES)


def encode_commands_max(commands_max: int, max_commands_max: int = 5) -> List[float]:
    """
    Encode maximum commands using RNS with bases [3, 5, 7].
    
    Args:
        commands_max: Maximum commands value (0 to max_commands_max)
        max_commands_max: Maximum possible commands (default 5)
    
    Returns:
        List of 15 float values (3+5+7 = 15 planes)
    """
    commands_max_clamped = max(0, min(commands_max, max_commands_max))
    return encode_rns(commands_max_clamped, STAT_BASES)


def encode_effective_armor(effective_armor: int, max_armor: int = 7) -> List[float]:
    """
    Encode effective armor (base + modifiers) using RNS with bases [3, 5, 7].
    
    Args:
        effective_armor: Effective armor value (0 to max_armor)
        max_armor: Maximum armor value (default 7)
    
    Returns:
        List of 15 float values (3+5+7 = 15 planes)
    """
    armor_clamped = max(0, min(effective_armor, max_armor))
    return encode_rns(armor_clamped, STAT_BASES)


def encode_effective_damage(effective_damage: int, max_damage: int = 15) -> List[float]:
    """
    Encode effective damage (base + modifiers) using RNS with bases [3, 5, 7].
    
    Args:
        effective_damage: Effective damage value (0 to max_damage)
        max_damage: Maximum damage value (default 15)
    
    Returns:
        List of 15 float values (3+5+7 = 15 planes)
    """
    damage_clamped = max(0, min(effective_damage, max_damage))
    return encode_rns(damage_clamped, STAT_BASES)


def encode_reserved_unit_value(value: int, max_value: int = 31) -> List[float]:
    """
    Encode a reserved numeric value for future unit properties.
    Uses HP bases [3, 5, 7, 11] for consistency with HP encoding.
    
    Args:
        value: Value to encode (0 to max_value)
        max_value: Maximum value (default 31)
    
    Returns:
        List of 26 float values (3+5+7+11 = 26 planes)
    """
    value_clamped = max(0, min(value, max_value))
    return encode_rns(value_clamped, HP_BASES)


def encode_thresholds(value: int, thresholds: List[int] = [3, 5, 7, 11]) -> List[float]:
    """
    Encode value using threshold planes (>= threshold).
    Provides additional redundancy for the RNS encoding.
    
    Args:
        value: Value to encode
        thresholds: List of threshold values
    
    Returns:
        List of float values (one per threshold)
    
    Example:
        encode_thresholds(6, [3, 5, 7, 11])
        Returns: [1.0, 1.0, 0.0, 0.0]  # >=3 ✓, >=5 ✓, >=7 ✗, >=11 ✗
    """
    return [1.0 if value >= threshold else 0.0 for threshold in thresholds]


def get_rns_plane_counts() -> dict:
    """
    Get the number of planes needed for each RNS encoding.
    
    Returns:
        Dictionary with plane counts for each stat type
    """
    hp_planes = sum(HP_BASES)  # 26 planes
    stat_planes = sum(STAT_BASES)  # 15 planes
    threshold_planes = 4  # [3, 5, 7, 11] thresholds
    
    return {
        # Unit stats
        'hp': hp_planes,                          # Current HP: 26 planes
        'hp_max': hp_planes,                      # Max HP: 26 planes
        'armor_base': stat_planes,                # Base armor: 15 planes
        'armor_effective': stat_planes,           # Effective armor: 15 planes
        'damage_base': stat_planes,               # Base damage: 15 planes
        'damage_effective': stat_planes,          # Effective damage: 15 planes
        'actions': stat_planes,                   # Current actions: 15 planes
        'actions_max': stat_planes,                # Max actions: 15 planes
        'reserved_unit': hp_planes,               # Reserved slot: 26 planes
        
        # Unit thresholds (redundancy)
        'hp_thresholds': threshold_planes,        # HP thresholds: 4 planes
        'hp_max_thresholds': threshold_planes,    # Max HP thresholds: 4 planes
        
        # Game stats
        'commands': stat_planes,                  # Commands left: 15 planes
        'commands_max': stat_planes,              # Max commands: 15 planes
        'deploy_cost': stat_planes,               # Deploy cost: 15 planes
        
        # Totals
        'total_unit_stats': (
            2 * hp_planes +           # HP, HP_max
            4 * stat_planes +         # armor_base, armor_effective, damage_base, damage_effective
            2 * stat_planes +         # actions, actions_max
            hp_planes +               # reserved_unit
            2 * threshold_planes     # hp_thresholds, hp_max_thresholds
        ),  # = 2*26 + 4*15 + 2*15 + 26 + 2*4 = 52 + 60 + 30 + 26 + 8 = 176 planes per unit
        
        'total_game_stats': (
            2 * stat_planes +         # commands, commands_max
            stat_planes               # deploy_cost
        ),  # = 3*15 = 45 planes
        
        'total_all_stats': (
            2 * hp_planes +           # HP, HP_max
            4 * stat_planes +         # armor_base, armor_effective, damage_base, damage_effective
            2 * stat_planes +         # actions, actions_max
            hp_planes +               # reserved_unit
            2 * threshold_planes +   # hp_thresholds, hp_max_thresholds
            3 * stat_planes          # commands, commands_max, deploy_cost
        ),  # = 176 + 45 = 221 planes total
    }


# Test the encoding
if __name__ == "__main__":
    print("Testing RNS Encoding")
    print("=" * 60)
    
    # Test HP encoding
    print("\nHP Encoding (bases: [3, 5, 7, 11]):")
    for hp in [0, 1, 6, 17, 31]:
        encoded = encode_hp(hp)
        decoded = decode_rns(encoded, HP_BASES)
        print(f"  HP={hp:2d} → Encoded ({len(encoded)} planes) → Decoded={decoded}")
        # Show residues
        residues = []
        idx = 0
        for base in HP_BASES:
            residue = None
            for i in range(base):
                if encoded[idx + i] > 0.5:
                    residue = i
                    break
            residues.append(f"{hp} mod {base} = {residue}")
            idx += base
        print(f"    Residues: {', '.join(residues)}")
    
    # Test Armor encoding
    print("\nArmor Encoding (bases: [3, 5, 7]):")
    for armor in [0, 1, 2, 3, 7]:
        encoded = encode_armor(armor)
        decoded = decode_rns(encoded, STAT_BASES)
        print(f"  Armor={armor} → Encoded ({len(encoded)} planes) → Decoded={decoded}")
    
    # Test Damage encoding
    print("\nDamage Encoding (bases: [3, 5, 7]):")
    for damage in [0, 3, 6, 15]:
        encoded = encode_damage(damage)
        decoded = decode_rns(encoded, STAT_BASES)
        print(f"  Damage={damage} → Encoded ({len(encoded)} planes) → Decoded={decoded}")
    
    # Test Actions encoding
    print("\nActions Encoding (bases: [3, 5, 7]):")
    for actions in [0, 1, 2, 3, 7]:
        encoded = encode_actions(actions)
        decoded = decode_rns(encoded, STAT_BASES)
        print(f"  Actions={actions} → Encoded ({len(encoded)} planes) → Decoded={decoded}")
    
    # Test Max HP encoding
    print("\nMax HP Encoding (bases: [3, 5, 7, 11]):")
    for hp_max in [4, 6, 10, 20, 31]:
        encoded = encode_hp_max(hp_max)
        decoded = decode_rns(encoded, HP_BASES)
        print(f"  Max HP={hp_max} → Encoded ({len(encoded)} planes) → Decoded={decoded}")
    
    # Test Max Actions encoding
    print("\nMax Actions Encoding (bases: [3, 5, 7]):")
    for actions_max in [1, 2, 3, 7]:
        encoded = encode_actions_max(actions_max)
        decoded = decode_rns(encoded, STAT_BASES)
        print(f"  Max Actions={actions_max} → Encoded ({len(encoded)} planes) → Decoded={decoded}")
    
    # Test Deploy Cost encoding
    print("\nDeploy Cost Encoding (bases: [3, 5, 7]):")
    for cost in [0, 1, 2, 3, 5]:
        encoded = encode_deploy_cost(cost)
        decoded = decode_rns(encoded, STAT_BASES)
        print(f"  Deploy Cost={cost} → Encoded ({len(encoded)} planes) → Decoded={decoded}")
    
    # Test Commands encoding
    print("\nCommands Encoding (bases: [3, 5, 7]):")
    for commands in [0, 1, 3, 5]:
        encoded = encode_commands(commands)
        decoded = decode_rns(encoded, STAT_BASES)
        print(f"  Commands={commands} → Encoded ({len(encoded)} planes) → Decoded={decoded}")
    
    # Test Max Commands encoding
    print("\nMax Commands Encoding (bases: [3, 5, 7]):")
    for commands_max in [3, 5]:
        encoded = encode_commands_max(commands_max)
        decoded = decode_rns(encoded, STAT_BASES)
        print(f"  Max Commands={commands_max} → Encoded ({len(encoded)} planes) → Decoded={decoded}")
    
    # Test Effective Armor encoding
    print("\nEffective Armor Encoding (bases: [3, 5, 7]):")
    for eff_armor in [0, 1, 2, 3]:
        encoded = encode_effective_armor(eff_armor)
        decoded = decode_rns(encoded, STAT_BASES)
        print(f"  Effective Armor={eff_armor} → Encoded ({len(encoded)} planes) → Decoded={decoded}")
    
    # Test Effective Damage encoding
    print("\nEffective Damage Encoding (bases: [3, 5, 7]):")
    for eff_damage in [3, 5, 7, 10]:
        encoded = encode_effective_damage(eff_damage)
        decoded = decode_rns(encoded, STAT_BASES)
        print(f"  Effective Damage={eff_damage} → Encoded ({len(encoded)} planes) → Decoded={decoded}")
    
    # Test Reserved Unit Value encoding
    print("\nReserved Unit Value Encoding (bases: [3, 5, 7, 11]):")
    for value in [0, 5, 10, 20]:
        encoded = encode_reserved_unit_value(value)
        decoded = decode_rns(encoded, HP_BASES)
        print(f"  Reserved Value={value} → Encoded ({len(encoded)} planes) → Decoded={decoded}")
    
    # Test Threshold encoding
    print("\nThreshold Encoding (>= 3, 5, 7, 11):")
    for value in [0, 3, 5, 7, 11, 17]:
        encoded = encode_thresholds(value)
        print(f"  Value={value:2d} → Thresholds: >=3={encoded[0]:.0f}, >=5={encoded[1]:.0f}, >=7={encoded[2]:.0f}, >=11={encoded[3]:.0f}")
    
    # Summary
    print("\n" + "=" * 60)
    counts = get_rns_plane_counts()
    print("Plane Counts:")
    print("\nUnit Stats:")
    unit_stats = ['hp', 'hp_max', 'armor_base', 'armor_effective', 'damage_base', 
                   'damage_effective', 'actions', 'actions_max', 'reserved_unit',
                   'hp_thresholds', 'hp_max_thresholds']
    for key in unit_stats:
        if key in counts:
            print(f"  {key}: {counts[key]} planes")
    
    print("\nGame Stats:")
    game_stats = ['commands', 'commands_max', 'deploy_cost']
    for key in game_stats:
        if key in counts:
            print(f"  {key}: {counts[key]} planes")
    
    print("\nTotals:")
    print(f"  Unit stats per unit: {counts['total_unit_stats']} planes")
    print(f"  Game stats: {counts['total_game_stats']} planes")
    print(f"  All numeric stats: {counts['total_all_stats']} planes")
    print(f"\nNote: Unit stats are encoded per unit on the board.")
    print(f"      Game stats are encoded once per game state.")

