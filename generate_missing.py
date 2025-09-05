"""
Generate charts for the 8 excluded Pokémon using their manually downloaded artwork.

This script processes the Pokémon that were skipped in the main generate.py script
due to missing data in the Pokédex JSON file. These Pokémon are:
- 221: Piloswine (ice, ground)
- 824: Blipbug (bug)
- 916: Oinkologne (normal)
- 925: Maushold (normal)
- 931: Squawkabilly (normal, flying)
- 964: Palafin (water)
- 978: Tatsugiri (dragon, water)
- 982: Dudunsparce (normal)

The script:
1. Uses manually downloaded art files from the art/ folder
2. Creates basic Pokédex data for these missing Pokémon
3. Generates color charts using the same algorithm as generate.py
4. Outputs the chart images to art/art_XXX_image.png

Usage: python generate_missing.py
"""

import json
import os
import time
import math
from PIL import Image, ImageEnhance, ImageFilter
from chart import *

# Import constants from generate.py
SAVE_POKES = True
SAVE_POKES_FORCED = False
INDIVIDUAL_KS = (1, 3, 5, 7)
INDIVIDUAL_CHART_SIZE = CHART_SIZE
INDIVIDUAL_PREFIX = 'art/art_'
INDIVIDUAL_FILENAME = f'_image.png'

# The 8 excluded Pokémon IDs
EXCLUDED_POKEMON_IDS = [221, 824, 916, 925, 931, 964, 978, 982]

# Constants from pokemon.py
IMAGE_PREFIXES = [('art', 1, 32), ('game', 1, 0)]
POKE_TYPES = ['grass', 'poison', 'fire', 'flying', 'water', 'bug', 'normal', 'electric', 'ground', 'fairy', 'fighting', 'psychic', 'rock', 'steel', 'ice', 'ghost', 'dragon', 'dark']

def time_print(func, string, *args, **kwargs):
    """Time a function and print the elapsed time."""
    print(string, end='', flush=True)
    t0 = time.time()
    result = func(*args, **kwargs)
    elapsed = time.time() - t0
    print(f'done. ({elapsed:.3f}s)')
    return result


class MissingPokemon:
    """Modified Pokemon class for processing excluded Pokémon with existing art files."""
    
    # Class variables for aggregating data
    dex = {}
    all_colors = Chart()
    type_charts = {}
    type_groups = {}
    
    @classmethod
    def load_dex_data(cls):
        """Load Pokédex data from JSON file and missing Pokémon data."""
        # Load main Pokédex data
        with open('pokedex.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # The JSON structure is {string_id: {pokemon_data}}
            for string_id, pokemon_data in data.items():
                pokemon_id = int(string_id)
                cls.dex[pokemon_id] = pokemon_data
        
        # Load missing Pokémon data
        try:
            with open('missing_pokemon_data.json', 'r', encoding='utf-8') as f:
                missing_data = json.load(f)
                for pokemon_id, pokemon_data in missing_data.items():
                    cls.dex[int(pokemon_id)] = pokemon_data
        except FileNotFoundError:
            print("Warning: missing_pokemon_data.json not found. Creating basic data...")
            # Create basic data for missing Pokémon
            missing_pokemon_basic = {
                221: {"id": 221, "name": "Piloswine", "types": ["ice", "ground"], "stats": {"hp": 100, "attack": 100, "defense": 80, "special-attack": 60, "special-defense": 60, "speed": 50}},
                824: {"id": 824, "name": "Blipbug", "types": ["bug"], "stats": {"hp": 25, "attack": 20, "defense": 20, "special-attack": 25, "special-defense": 45, "speed": 45}},
                916: {"id": 916, "name": "Oinkologne", "types": ["normal"], "stats": {"hp": 110, "attack": 100, "defense": 75, "special-attack": 59, "special-defense": 80, "speed": 65}},
                925: {"id": 925, "name": "Maushold", "types": ["normal"], "stats": {"hp": 74, "attack": 75, "defense": 70, "special-attack": 65, "special-defense": 75, "speed": 111}},
                931: {"id": 931, "name": "Squawkabilly", "types": ["normal", "flying"], "stats": {"hp": 82, "attack": 96, "defense": 51, "special-attack": 45, "special-defense": 51, "speed": 92}},
                964: {"id": 964, "name": "Palafin", "types": ["water"], "stats": {"hp": 100, "attack": 70, "defense": 72, "special-attack": 53, "special-defense": 62, "speed": 100}},
                978: {"id": 978, "name": "Tatsugiri", "types": ["dragon", "water"], "stats": {"hp": 68, "attack": 50, "defense": 60, "special-attack": 120, "special-defense": 95, "speed": 82}},
                982: {"id": 982, "name": "Dudunsparce", "types": ["normal"], "stats": {"hp": 125, "attack": 100, "defense": 80, "special-attack": 85, "special-defense": 75, "speed": 55}}
            }
            for pokemon_id, pokemon_data in missing_pokemon_basic.items():
                cls.dex[pokemon_id] = pokemon_data
        
        # Initialize type charts and groups
        for t in POKE_TYPES:
            cls.type_charts[t] = Chart()
            cls.type_groups[t] = []
    
    def __init__(self, number: int, prefix: str='art/art_', suffix: str='.png'):
        """Create Pokemon from Pokédex number, specifically for excluded Pokémon.
        
        Args:
            number: The Pokédex number to generate the Pokemon from.
            prefix: Output filename prefix.
            suffix: Output filename suffix.
        """
        if number not in EXCLUDED_POKEMON_IDS:
            raise ValueError(f"This script is only for excluded Pokémon IDs: {EXCLUDED_POKEMON_IDS}")
        
        # Get stats and data from json file
        self.number = number
        self.string = format(number, "03d")
        self.dex = MissingPokemon.dex[number]
        self.name = self.dex['name']
        self.types = self.dex['types']
        
        if 'description' in self.dex:
            self.description = self.dex['description']
        
        if len(self.types) == 2:
            self.type1 = self.types[0]
            self.type2 = self.types[1]
        else:
            self.type1 = self.types[0]
            self.type2 = ''
        
        self.stats = self.dex['stats']
        
        self.filename = prefix + self.string + suffix
        self.chartname = prefix + self.string + '_image' + suffix
        
        self._printline = f'#{self.string} {self.name}:'.ljust(17)
        
        # Get color data for pokemon using only existing art files
        self.chart = Chart()
        
        # Only process art files (skip game files as they may not exist)
        art_file = f'art/art_{self.string}.png'
        if os.path.exists(art_file):
            print(f"  Processing {art_file}")
            self.chart.addImage(art_file, 1)  # weight=1
            self.chart.removeBlack(32)  # threshold=32
        else:
            raise FileNotFoundError(f"Art file not found: {art_file}")
        
        self.chart.removeFraction(float(COLOR_REMOVE)/100.0)
        
        # Add to aggregated color data
        MissingPokemon.all_colors.addDict(self.chart)
        
        # Add to type color dictionaries
        frac = 1.0
        if self.type2 != '':
            frac = 0.5
            MissingPokemon.type_groups[self.type2].append(self)
            MissingPokemon.type_charts[self.type2].addDict(self.chart, frac)
        
        MissingPokemon.type_groups[self.type1].append(self)
        MissingPokemon.type_charts[self.type1].addDict(self.chart, frac)
    
    def __str__(self):
        return self._printline


def main():
    """Main function to process the excluded Pokémon."""
    print("=== Processing Excluded Pokémon ===")
    print(f"Processing Pokémon IDs: {EXCLUDED_POKEMON_IDS}")
    
    # Load Pokédex data
    print("Loading Pokédex data...")
    MissingPokemon.load_dex_data()
    
    print('\n- Input -')
    
    # Process each excluded Pokémon
    pokes = []
    for pokemon_id in EXCLUDED_POKEMON_IDS:
        try:
            p = time_print(MissingPokemon, f'Loading Pokemon #{pokemon_id}... ', pokemon_id)
            pokes.append(p)
        except Exception as e:
            print(f"Error processing Pokémon #{pokemon_id}: {e}")
            continue
    
    if not pokes:
        print("No Pokémon were successfully processed!")
        return
    
    print('\n- Output -')
    
    # Generate individual pokemon charts
    if SAVE_POKES:
        num = len(pokes)
        t0 = time.time()
        for p in pokes:
            try:
                print(f"Generating chart for {p.name} (#{p.string})...")
                p.chart.save(
                    INDIVIDUAL_PREFIX + p.string + INDIVIDUAL_FILENAME,
                    size=INDIVIDUAL_CHART_SIZE,
                    ks=INDIVIDUAL_KS,
                    forced=SAVE_POKES_FORCED
                )
                print(f"  Saved: {INDIVIDUAL_PREFIX + p.string + INDIVIDUAL_FILENAME}")
            except Exception as e:
                print(f"  Error saving chart for {p.name}: {e}")
        
        total_time = time.time() - t0
        print(f'\nSaved {num} charts in {total_time:.3f}s ({total_time/num:.3f}s each)')
    
    # Clean up
    for p in pokes:
        del p
    
    print("\n=== Processing Complete ===")
    print("The excluded Pokémon charts have been generated using their existing art files.")


if __name__ == '__main__':
    main()
