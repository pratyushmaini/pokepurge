# Available baseline methods that are actually implemented
BASELINE_METHODS = {
    'input_filters': {
        'BaseRegexFilter': 'methods.input_filters.RegexFilter',
        'BaseWordFilter': 'methods.input_filters.WordFilter'
    },
    'output_filters': {
        'BaseContentDetector': 'methods.output_filters.ContentDetectorFilter'
    },
    # 'model_mods': {
    #     'BaseModelPatch': 'methods.model_modifications.ModelPatch'
    # },
    'attacks': {
        'BaseHomographAttack': 'attacks.black_box_attack.HomographAttack',
        'BasePromptInjection': 'attacks.black_box_attack.PromptInjection'
    }
}

# Baseline team configurations using only implemented methods
BASELINE_TEAMS = {
    'BaseDefenseTeam': {
        'type': 'blue',
        'input_filter': 'BaseRegexFilter',
        'output_filter': 'BaseContentDetector',
        # 'model_mod': 'BaseModelPatch'
    },
    'BaseAttackTeam': {
        'type': 'red',
        'attack': 'BaseHomographAttack'
    }
}

# Students can register their teams here
STUDENT_TEAMS = {
    # Example:
    # 'TeamRocket': {
    #     'type': 'red',
    #     'attack': 'CustomHomographAttack'
    # }
}