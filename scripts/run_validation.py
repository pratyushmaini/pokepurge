#!/usr/bin/env python3
import subprocess
import itertools
from typing import List, Dict
import json
import os
from concurrent.futures import ThreadPoolExecutor
import time
from tqdm import tqdm

# Load held out prompts
import sys
sys.path.append('data')
from heldout_prompts import heldout_prompts

# Blue teams to test
BLUE_TEAMS = [
    'NoDefenseTeam',  # This will be our baseline
    'BaseDefenseTeam',
    'EmeraldDefenseTeam',
    'TeamPikaDefense'
    'PichuPixelPatrolBlue',
]

def get_output_path(team: str, prompt_type: str, prompt_index: int) -> str:
    """Generate organized output path for validation results"""
    # Structure: validation_outputs/team/prompt_type/prompt_index/
    path = os.path.join(
        'validation_outputs',
        team,
        prompt_type,
        f'prompt_{prompt_index}'
    )
    return path

def run_validation(task: tuple) -> tuple:
    """Run a single validation test"""
    (team, prompt_type, prompt, prompt_idx), gpu_id = task
    output_dir = get_output_path(team, prompt_type, prompt_idx)
    
    # Skip if already completed
    if os.path.exists(os.path.join(output_dir, "completed.txt")):
        return (True, team, prompt_type, prompt, "Already completed")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Construct command
    cmd = [
        "python", "main.py",
        "--blue", team,
        "--red", "NoAttackTeam",  # Use neutral red team
        "--prompt", prompt,
        "--output_dir", output_dir
    ]
    
    # Set environment variables
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    
    # Log file
    log_file = os.path.join(output_dir, "validation.log")
    
    try:
        with open(log_file, 'w') as f:
            process = subprocess.Popen(
                cmd,
                stdout=f,
                stderr=subprocess.STDOUT,
                env=env,
                text=True
            )
            
            try:
                process.wait(timeout=300)  # 5 minute timeout
                if process.returncode == 0:
                    with open(os.path.join(output_dir, "completed.txt"), 'w') as cf:
                        cf.write(f"Completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    return (True, team, prompt_type, prompt, "Success")
                else:
                    return (False, team, prompt_type, prompt, f"Process failed with code {process.returncode}")
            except subprocess.TimeoutExpired:
                process.kill()
                return (False, team, prompt_type, prompt, "Timeout after 5 minutes")
                
    except Exception as e:
        return (False, team, prompt_type, prompt, str(e))

def distribute_validation_tasks(gpu_count: int = 8):
    """Distribute validation tasks across GPUs"""
    tasks = []
    
    # Generate tasks for each team and prompt type
    for team in BLUE_TEAMS:
        for prompt_type, prompts in heldout_prompts.items():
            for i, prompt in enumerate(prompts):
                tasks.append(((team, prompt_type, prompt, i), len(tasks) % gpu_count))
    
    print(f"Total validation tasks: {len(tasks)}")
    print(f"Tasks per GPU: ~{len(tasks) // gpu_count}")
    
    results = []
    with ThreadPoolExecutor(max_workers=gpu_count) as executor:
        for result in tqdm(
            executor.map(lambda x: run_validation(x), tasks),
            total=len(tasks),
            desc="Running validation"
        ):
            results.append(result)
    
    return results

def main():
    print(f"Starting validation runs across 8 GPUs at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
    start_time = time.time()
    
    try:
        results = distribute_validation_tasks(gpu_count=8)
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Saving partial results...")
        results = []
        
    # Create summary
    summary = {
        "total_tasks": len(results),
        "successful": len([r for r in results if r[0]]),
        "failed": len([r for r in results if not r[0]]),
        "by_team": {},
        "by_prompt_type": {},
        "failures": []
    }
    
    # Collect statistics
    for success, team, prompt_type, prompt, status in results:
        # Team stats
        if team not in summary["by_team"]:
            summary["by_team"][team] = {"total": 0, "successful": 0, "failed": 0}
        summary["by_team"][team]["total"] += 1
        if success:
            summary["by_team"][team]["successful"] += 1
        else:
            summary["by_team"][team]["failed"] += 1
            summary["failures"].append({
                "team": team,
                "prompt_type": prompt_type,
                "prompt": prompt,
                "error": status
            })
            
        # Prompt type stats
        if prompt_type not in summary["by_prompt_type"]:
            summary["by_prompt_type"][prompt_type] = {"total": 0, "successful": 0, "failed": 0}
        summary["by_prompt_type"][prompt_type]["total"] += 1
        if success:
            summary["by_prompt_type"][prompt_type]["successful"] += 1
        else:
            summary["by_prompt_type"][prompt_type]["failed"] += 1
    
    # Save summary
    os.makedirs("validation_outputs", exist_ok=True)
    with open("validation_outputs/summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print("\nValidation Summary:")
    print(f"Total tasks: {summary['total_tasks']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"Duration: {time.time() - start_time:.1f} seconds")
    
    print("\nResults by team:")
    for team, stats in summary["by_team"].items():
        if stats['total'] > 0:
            print(f"{team}:")
            print(f"  Total: {stats['total']}")
            print(f"  Success rate: {(stats['successful']/stats['total'])*100:.1f}%")
    
    print("\nResults by prompt type:")
    for ptype, stats in summary["by_prompt_type"].items():
        if stats['total'] > 0:
            print(f"{ptype}:")
            print(f"  Total: {stats['total']}")
            print(f"  Success rate: {(stats['successful']/stats['total'])*100:.1f}%")

if __name__ == "__main__":
    main()

'''
chmod +x scripts/run_validation.py
./scripts/run_validation.py 
'''