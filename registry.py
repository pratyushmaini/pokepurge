# Available baseline methods that are actually implemented
BASELINE_METHODS = {
    'input_filters': {
        'BaseRegexFilter': 'methods.input_filters.RegexFilter',
        'BaseWordFilter': 'methods.input_filters.WordFilter',
        'EmeraldPerplexityFilter': 'methods.input_filters.PerplexityFilter'
    },
    'output_filters': {
        'BaseContentDetector': 'methods.output_filters.ContentDetectorFilter',
        'EmeraldContentDetector': 'methods.output_filters.ContentDetectorFilter2'
    },
    'model_mods': {
        'BaseModelPatch': 'methods.model_modifications.ModelPatch',
        'EmeraldConceptEditing': 'methods.model_modifications.ConceptEditing',
    },
    'attacks': {
        'BaseHomographAttack': 'attacks.black_box_attack.HomographAttack',
        'BasePromptInjection': 'attacks.black_box_attack.PromptInjection',
    }
}

# Baseline team configurations using only implemented methods
BASELINE_TEAMS = {
   'BaseDefenseTeam': {
       'type': 'blue',
       'input_filter': 'BaseRegexFilter',
       'output_filter': 'BaseContentDetector'
   },
   'NoDefenseTeam': {
       'type': 'blue',
       'input_filter': None,
       'output_filter': None
   },
   'BaseAttackTeam': {
       'type': 'red',
       'attack': 'BaseHomographAttack'
   },
   'NoAttackTeam': {
       'type': 'red',
       'attack': None
   }
}


# Students can register their teams here
STUDENT_TEAMS = {
    # Example:
    'TeamEmerald': {
        'type': 'blue',
        'input_filter': 'EmeraldPerplexityFilter',
        'output_filter': 'EmeraldContentDetector',
        'model_mods': 'EmeraldConceptEditing'
    }
}