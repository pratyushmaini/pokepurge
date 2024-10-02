# Pokémon Purge Challenge

Welcome to the **Pokémon Purge Challenge**! This is an exciting and educational exercise designed to explore model unlearning, content filtering, and model robustness using state-of-the-art diffusion models. You'll be working in teams to either protect or generate specific content, all while maintaining overall model performance.

---

## Table of Contents

- [Introduction](#introduction)
- [Objectives](#objectives)
- [Team Roles](#team-roles)
  - [Blue Team](#blue-team)
  - [Red Team](#red-team)
- [Rules and Guidelines](#rules-and-guidelines)
- [Evaluation Criteria](#evaluation-criteria)
- [Getting Started](#getting-started)
  - [Repository Structure](#repository-structure)
  - [Setup Instructions](#setup-instructions)
- [Code Structure](#code-structure)
  - [Methods Module](#methods-module)
  - [Metrics Module](#metrics-module)
  - [Attacks Module](#attacks-module)
- [Automated Leaderboard](#automated-leaderboard)
- [How to Submit](#how-to-submit)
- [Resources](#resources)
- [License](#license)

---

## Introduction

In this challenge, we will use the **FLUX.1-schnell** diffusion model ([Hugging Face Repository](https://huggingface.co/black-forest-labs/FLUX.1-schnell)) to explore the concepts of model unlearning and content filtering. Our case study focuses on the generation of Pokémon characters.

---

## Objectives

- **Blue Team**: Implement methods to prevent the generation of the top 100 Pokémon characters using input/output filters or model unlearning techniques.
- **Red Team**: Develop strategies to generate high-quality images of the top 100 Pokémon characters, overcoming the Blue Team's defenses.
- **Both Teams**: Ensure that any modifications or strategies do not degrade the overall performance of the diffusion model below an acceptable threshold.

---

## Team Roles

### Blue Team

- **Goal**: Prevent the diffusion model from generating images of the top 100 Pokémon characters.
- **Strategies**:
  - Implement input/output filters.
  - Apply model unlearning techniques.
  - Modify the model to avoid specific content generation.

### Red Team

- **Goal**: Successfully generate high-quality images of the top 100 Pokémon characters.
- **Approaches**:
  - **Black Box Access**: Interact with the model through its input and output without internal modifications.
  - **White Box Access**: Analyze and modify the model's internal mechanisms to bypass the Blue Team's defenses.

---

## Rules and Guidelines

- **Ethical Considerations**: All strategies must comply with ethical guidelines and avoid infringing on any intellectual property rights.
- **Model Integrity**: Any modifications should not degrade the model's performance below the specified threshold.
- **Collaboration**: Teams are encouraged to collaborate within their groups but not across teams.
- **Documentation**: Keep detailed records of your methodologies and reasoning.
- **Standardization**: Follow the provided code structure to ensure consistency across all submissions.

---

## Evaluation Criteria

1. **Success Rate**:
   - **Blue Team**: Number of prevented generations of the top 100 Pokémon.
   - **Red Team**: Number of successful generations of the top 100 Pokémon.
2. **Model Performance**:
   - Overall performance on a held-out set of tasks to ensure the model remains effective.
   - Models that fall below the performance threshold will be rejected.
3. **Innovation**:
   - Creativity and effectiveness of the strategies employed.
4. **Compliance**:
   - Adherence to ethical guidelines and rules.

---

## Getting Started

### Repository Structure

Students should **fork** this repository and work on their own copies. The repository is structured as follows:

```
pokemon-purge-challenge/
├── README.md
├── requirements.txt
├── main.py
├── methods/
│   ├── __init__.py
│   ├── base_method.py
│   ├── input_filters.py
│   ├── output_filters.py
│   └── model_modifications.py
├── metrics/
│   ├── __init__.py
│   ├── base_metric.py
│   ├── performance_metrics.py
│   └── content_detection_metrics.py
├── attacks/
│   ├── __init__.py
│   ├── base_attack.py
│   ├── black_box_attack.py
│   └── white_box_attack.py
├── leaderboard/
│   └── leaderboard.py
├── data/
│   ├── held_out_tasks.json
│   └── top_100_pokemon.txt
└── .gitignore
```

### Setup Instructions

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-username/pokemon-purge-challenge.git
   ```

2. **Navigate to the Directory**:

   ```bash
   cd pokemon-purge-challenge
   ```

3. **Install the Required Packages**:

   ```bash
   conda create -n pokepurge python=3.12
   pip install -r requirements.txt
   ```

4. **Download the FLUX.1-schnell Model**:

   The model will be automatically downloaded when you run the code for the first time.

---

## Code Structure

### Methods Module

This module contains the base classes and implementations for input filters, output filters, and model modifications.

- **`methods/base_method.py`**: Defines the `BaseMethod` class.
- **`methods/input_filters.py`**: Implements input filtering methods.
- **`methods/output_filters.py`**: Implements output filtering methods.
- **`methods/model_modifications.py`**: Implements methods for modifying the model.

### Metrics Module

This module contains the base classes and implementations for performance metrics and content detection metrics.

- **`metrics/base_metric.py`**: Defines the `BaseMetric` class.
- **`metrics/performance_metrics.py`**: Implements performance evaluation metrics.
- **`metrics/content_detection_metrics.py`**: Implements content detection metrics to check for Pokémon generation.

### Attacks Module

This module contains the base class and implementations for red team attacks.

- **`attacks/base_attack.py`**: Defines the `BaseAttack` class.
- **`attacks/black_box_attack.py`**: Implements black box attack strategies.
- **`attacks/white_box_attack.py`**: Implements white box attack strategies.

### Leaderboard Module

This module contains the script to generate an automated leaderboard based on submissions.

- **`leaderboard/leaderboard.py`**: Generates and updates the leaderboard.

---

## Automated Leaderboard

The leaderboard will be automatically generated based on the evaluation metrics. It will rank teams based on their success rates and adherence to the performance thresholds.

---

## How to Submit

1. **Fork the Repository**: Create a fork of this repository in your own GitHub account.

2. **Implement Your Strategies**: Add your methods and modifications in the appropriate modules.

3. **Update the README**: Include a section in your forked repository's README detailing your approach.

4. **Pull Request**: Submit a pull request to the original repository for evaluation.

---

## Resources

- **FLUX.1-schnell Model**: [Hugging Face Repository](https://huggingface.co/black-forest-labs/FLUX.1-schnell)
- **Relevant Paper**: ["Selective Amnesia: On Efficiently Forgetting Transformers"](https://arxiv.org/abs/2303.07345)
- **Diffusers Library**: [Hugging Face Diffusers](https://github.com/huggingface/diffusers)
- **Top 100 Pokémon List**: Provided in `data/top_100_pokemon.txt`

---

## License

This project is licensed under the MIT License.

---

Let's make this challenge exciting and insightful! Good luck to all teams!

---

# Additional Instructions

- **Students** should implement their strategies within the provided classes and modules.
- **Blue Team** members should focus on enhancing the methods in `methods/` to prevent forbidden content generation.
- **Red Team** members should focus on implementing attack strategies in `attacks/` to generate the forbidden content.
- **Metrics** for evaluation are to be implemented or extended in `metrics/`.
- **Leaderboard** updates are handled by `leaderboard/leaderboard.py`.

# How to Extend the Base Classes

## For Blue Team

- **Input Filters**: Extend `InputFilter` to implement more sophisticated input filtering.
- **Output Filters**: Extend `OutputFilter` with advanced content detection models.
- **Model Modifications**: Implement `apply()` in `ModelModification` to modify the model weights or architecture.

## For Red Team

- **Black Box Attacks**: Enhance `BlackBoxAttack` with prompt engineering or adversarial examples.
- **White Box Attacks**: Modify `WhiteBoxAttack` to manipulate the model's internal layers or parameters.

---

# Leaderboard Generation

The leaderboard is automatically updated each time `main.py` is run. It reads from and writes to `leaderboard/leaderboard.json`. Ensure that your team's name is unique to avoid overwriting another team's score.

---

# Final Notes

- **Standardization**: Please adhere to the code structure and naming conventions to ensure consistency.
- **Documentation**: Comment your code thoroughly to explain your implementations.
- **Ethical Compliance**: Do not include any disallowed or unethical content in your code or submissions.
- **Testing**: Test your code thoroughly before submitting to ensure it runs without errors.

---

# Let's Get Started!

Fork this repository, choose your team, and start implementing your strategies. May the best team win!

---