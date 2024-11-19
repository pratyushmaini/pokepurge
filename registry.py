# Available baseline methods that are actually implemented
BASELINE_METHODS = {
    'input_filters': {
        'BaseRegexFilter': 'methods.input_filters.RegexFilter',
        'BaseWordFilter': 'methods.input_filters.WordFilter',
        'EmeraldPerplexityFilter': 'methods.input_filters.PerplexityFilter'
        'CaptionFilter': 'methods.input_filters.CaptionFilter',
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
        'SynonymReplacementAttack': 'attacks.black_box_attack.SynonymReplacementAttack',
        'PezAttack': 'attacks.black_box_attack.PezAttack',
        'CubismStyleAttack': 'attacks.black_box_attack.CubismStyleAttack',
        'TransformerAttack': 'attacks.black_box_attack.TransformerAttack',
        'SimilarTextEmbeddingAttack': 'attacks.black_box_attack.SimilarTextEmbeddingAttack'
        'TeamPikaAttack1': 'attacks.black_box_attack.TeamPikaAttack1',
        'TeamPikaAttack2': 'attacks.black_box_attack.TeamPikaAttack2',
        'TeamPikaAttack3': 'attacks.black_box_attack.TeamPikaAttack3',
        'TeamPikaAttack4': 'attacks.black_box_attack.TeamPikaAttack4',
        'TeamPikaAttack5': 'attacks.black_box_attack.TeamPikaAttack5',
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
    'EmeraldDefenseTeam': {
        'type': 'blue',
        'input_filter': 'EmeraldPerplexityFilter',
        'output_filter': None,
        'model_mods': 'EmeraldConceptEditing'
    },
    'EmeraldAttackTeam1': {
        'type': 'red',
        'attack': 'SynonymReplacementAttack'
    },
    'EmeraldAttackTeam2': {
        'type': 'red',
        'attack': 'PezAttack'
    },
    'EmeraldAttackTeam3': {
        'type': 'red',
        'attack': 'TransformerAttack'
    },
    'EmeraldAttackTeam4': {
        'type': 'red',
        'attack': 'SimilarTextEmbeddingAttack'
    }, 
    'EmeraldAttackTeam5': {
        'type': 'red',
        'attack': 'CubismStyleAttack'
    }
}
    # 'TeamRocket': {
    #     'type': 'red',
    #     'attack': 'CustomHomographAttack'
    # }
    'TeamPikaDefense': {
        'type': 'blue',
        'input_filter': 'CaptionFilter',
        'output_filter': None,
        'generate_image_in_input_filter': True
    },
    'TeamPikaAttack1': {
        'type': 'red',
        'attack': 'TeamPikaAttack1'
    },
    'TeamPikaAttack2': {
        'type': 'red',
        'attack': 'TeamPikaAttack2'
    },
    'TeamPikaAttack3': {
        'type': 'red',
        'attack': 'TeamPikaAttack3'
    },
    'TeamPikaAttack4': {
        'type': 'red',
        'attack': 'TeamPikaAttack4'
    },
    'TeamPikaAttack5': {
        'type': 'red',
        'attack': 'TeamPikaAttack5'
    },
}
