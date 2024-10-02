# main.py

import torch
from diffusers import FluxPipeline
import methods.input_filters as input_filters_module
import methods.output_filters as output_filters_module
import methods.model_modifications as model_modifications_module
import attacks.black_box_attack as black_box_attack_module
import attacks.white_box_attack as white_box_attack_module
import metrics.performance_metrics as performance_metrics_module
import metrics.content_detection_metrics as content_detection_metrics_module
import argparse
import os
import logging
import numpy as np

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Pokémon Purge Challenge")
    parser.add_argument('--team', type=str, required=True, choices=['blue', 'red'], help='Team color')
    parser.add_argument('--input_filter', type=str, default='SimpleWordFilter', help='Input filter method')
    parser.add_argument('--output_filter', type=str, default='SimpleImageFilter', help='Output filter method')
    parser.add_argument('--attack', type=str, default='SynonymReplacementAttack', help='Attack method')
    parser.add_argument('--prompt', type=str, default='A happy Pikachu', help='Prompt for image generation')
    parser.add_argument('--team_name', type=str, default='TeamDefault', help='Your team name for the leaderboard')
    args = parser.parse_args()

    # Log the arguments
    logger.info(f"Arguments: {args}")

    # Load the FLUX.1-schnell model using FluxPipeline
    logger.info("Loading the FLUX.1-schnell model...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_id = "black-forest-labs/FLUX.1-schnell"

    # Ensure torch_dtype is set correctly
    torch_dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

    # Load the pipeline
    pipe = FluxPipeline.from_pretrained(
        model_id,
        torch_dtype=torch_dtype
    )

    # Optional: Offload model to CPU to save VRAM
    if not torch.cuda.is_available():
        pipe.enable_model_cpu_offload()

    pipe = pipe.to(device)

    # Apply Blue Team methods
    if args.team == 'blue':
        # Apply input filters
        InputFilterClass = getattr(input_filters_module, args.input_filter)
        input_filter = InputFilterClass()
        filtered_prompt = input_filter.apply(args.prompt)
        logger.info(f"Filtered prompt: {filtered_prompt}")
        # Apply model modifications
        model_modification = model_modifications_module.ModelModification()
        pipe = model_modification.apply(pipe)
    else:
        filtered_prompt = args.prompt
        logger.info(f"Using prompt: {filtered_prompt}")

    # Apply Red Team attacks
    if args.team == 'red':
        AttackClass = getattr(black_box_attack_module, args.attack)
        attack = AttackClass()
        filtered_prompt = attack.apply(filtered_prompt)
        logger.info(f"Attacked prompt: {filtered_prompt}")

    # Generate image
    logger.info(f"Generating image for prompt: {filtered_prompt}")
    generator = torch.Generator(device=device).manual_seed(0)

    # Adjust parameters
    guidance_scale = 0 # Changed from 0.0
    num_inference_steps = 4  # Increased from 4
    max_sequence_length = 256

    # Log the parameters
    logger.info(f"Using guidance_scale={guidance_scale}, num_inference_steps={num_inference_steps}")

    import pdb; pdb.set_trace()
    with torch.autocast(device.type):
        output = pipe(
            filtered_prompt,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            max_sequence_length=max_sequence_length,
            generator=generator
        )
        image = output.images[0]

    # Check for errors in image generation
    if image is None:
        logger.error("Image generation failed. The output image is None.")
        return

    # Save image
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    image_path = os.path.join(output_dir, f'{args.team_name}_generated_image.png')
    image.save(image_path)
    logger.info(f"Image saved as {image_path}")

    # Apply Output Filters (Blue Team)
    if args.team == 'blue':
        OutputFilterClass = getattr(output_filters_module, args.output_filter)
        output_filter = OutputFilterClass()
        image = output_filter.apply(image)
        # Save filtered image
        filtered_image_path = os.path.join(output_dir, f'{args.team_name}_filtered_image.png')
        image.save(filtered_image_path)
        logger.info(f"Filtered image saved as {filtered_image_path}")

    # Evaluate metrics
    performance_metric = performance_metrics_module.PerformanceMetric()
    performance_score = performance_metric.evaluate(pipe, filtered_prompt)
    content_detection_metric = content_detection_metrics_module.ContentDetectionMetric()
    content_score = content_detection_metric.evaluate(image)

    logger.info(f"Performance Score: {performance_score}")
    logger.info(f"Content Detection Score: {content_score}")

    # Update leaderboard
    from leaderboard.leaderboard import update_leaderboard
    update_leaderboard(args.team_name, content_score, performance_score)
    logger.info("Leaderboard updated.")

if __name__ == "__main__":
    main()
