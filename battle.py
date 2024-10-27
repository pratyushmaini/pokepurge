import torch
from diffusers import FluxPipeline
from pathlib import Path
import logging
from PIL import Image
from importlib import import_module
from registry import BASELINE_METHODS, BASELINE_TEAMS, STUDENT_TEAMS

class BlueTeam:
    """Defender team implementing content filtering"""
    
    def __init__(self, team_config):
        self.config = team_config
        self.input_filter = self._load_method('input_filter', 'input_filters')
        self.output_filter = self._load_method('output_filter', 'output_filters')
    
    def _load_method(self, method_type, method_category):
        """Dynamically load method class from config"""
        if method_type not in self.config or self.config[method_type] is None:
            return None
            
        method_name = self.config[method_type]
        method_path = BASELINE_METHODS[method_category][method_name]
        module_path, class_name = method_path.rsplit('.', 1)
        module = import_module(module_path)
        return getattr(module, class_name)()
    
    def defend(self, prompt: str, model: FluxPipeline, image: Image = None):
        """Apply all defense layers"""
        # Input defense
        if self.input_filter:
            prompt = self.input_filter.apply(prompt)
            
        # Output defense
        if image and self.output_filter:
            image = self.output_filter.apply(image)
            
        return prompt, model, image

class RedTeam:
    """Attacker team implementing content generation"""
    
    def __init__(self, team_config):
        self.config = team_config
        self.attack_method = self._load_attack()
    
    def _load_attack(self):
        """Dynamically load attack method"""
        if 'attack' not in self.config or self.config['attack'] is None:
            return None
            
        attack_name = self.config['attack']
        attack_path = BASELINE_METHODS['attacks'][attack_name]
        module_path, class_name = attack_path.rsplit('.', 1)
        module = import_module(module_path)
        return getattr(module, class_name)()
    
    def run_attack(self, prompt: str):
        """Execute attack to modify prompt"""
        if self.attack_method:
            return self.attack_method.apply(prompt)
        return prompt

class Battle:
    """Manages battles between Red and Blue teams"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.model = self._setup_model()
        self.output_dir = Path('outputs')
        self.output_dir.mkdir(exist_ok=True)
    
    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)
    
    def _setup_model(self):
        pipe = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-schnell",
            torch_dtype=torch.bfloat16
        )
        pipe.enable_model_cpu_offload()
        return pipe
    
    def generate_image(self, prompt: str):
        """Generate image using model"""
        return self.model(
            prompt,
            guidance_scale=0.0,
            num_inference_steps=4,
            generator=torch.Generator("cpu").manual_seed(0)
        ).images[0]
    
    def run(self, red_team_name: str, blue_team_name: str, prompt: str):
        """Execute a battle between teams"""
        # Get team configs
        red_config = {**BASELINE_TEAMS, **STUDENT_TEAMS}.get(red_team_name)
        blue_config = {**BASELINE_TEAMS, **STUDENT_TEAMS}.get(blue_team_name)
        
        if not red_config or not blue_config:
            raise ValueError("Team not found in registry")
        
        # Initialize teams
        red_team = RedTeam(red_config)
        blue_team = BlueTeam(blue_config)
        
        # Battle sequence
        self.logger.info(f"Battle: {red_team_name} vs {blue_team_name}")
        self.logger.info(f"Initial prompt: {prompt}")
        
        # Red team attack
        attacked_prompt = red_team.run_attack(prompt)  # Changed from attack() to run_attack()
        self.logger.info(f"Red team modified prompt: {attacked_prompt}")
        
        # Blue team input & model defense
        defended_prompt, defended_model, _ = blue_team.defend(attacked_prompt, self.model)
        self.logger.info(f"Blue team filtered prompt: {defended_prompt}")
        
        # Generate image
        image = self.generate_image(defended_prompt)
        
        # Blue team output defense
        _, _, final_image = blue_team.defend(defended_prompt, defended_model, image)
        
        # Save results
        result_path = self.output_dir / f"{red_team_name}_vs_{blue_team_name}.png"
        final_image.save(result_path)
        
        return final_image