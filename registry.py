# Available baseline methods that are actually implemented
BASELINE_METHODS = {
    'input_filters': {
        'NoInputFilter': 'methods.input_filters.InputFilter',
        'BaseRegexFilter': 'methods.input_filters.RegexFilter',
        'BaseWordFilter': 'methods.input_filters.SimpleWordFilter',
        'EmbeddingFilter': 'methods.ppp_input_filters.EmbeddingFilter'
        'CaptionFilter': 'methods.input_filters.CaptionFilter',
    },
    'output_filters': {
        'NoOutputFilter': 'methods.output_filters.OutputFilter',
        'BaseContentDetector': 'methods.output_filters.ContentDetectorFilter',
        'ContentClassificationFilter': 'methods.ppp_output_filters.ContentClassificationFilter'
    },
    'model_mods': {
        'BaseModelPatch': 'methods.model_modifications.ModelPatch',
        'EmeraldConceptEditing': 'methods.model_modifications.ConceptEditing',
    },
    'attacks': {
        'RandomizedDupAndCombAttack': 'attacks.ppp_attack.RandomizedDupAndCombAttack',
        'SynonymReplacementAttack': 'attacks.ppp_attack.SynonymReplacementAttack',
        'PermutationAttack': 'attacks.ppp_attack.PermutationAttack',
        'PermuteAndJoinAttack': 'attacks.ppp_attack.PermuteAndJoinAttack',
        'MisspellJoinInjectAttack': 'attacks.ppp_attack.MisspellJoinInjectAttack',
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
   },
    'PrefixSuffixTeam': {
       'type': 'red',
       'attack': 'InjectPrefixAndSuffix'
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
    },
    # 'TeamRocket': {
    #     'type': 'red',
    #     'attack': 'CustomHomographAttack'
    # }
    'PichuPixelPatrolBlue': {
       'type': 'blue',
       'input_filter': 'EmbeddingFilter',
       'output_filter': 'ContentClassificationFilter'
   },

   'PichuPixelPatrolRed_DupOrComb': {
       'type': 'red',
       'attack': 'RandomizedDupAndCombAttack'
   },

   'PichuPixelPatrolRed_Synonym': {
       'type': 'red',
       'attack': 'SynonymReplacementAttack'
   },

   'PichuPixelPatrolRed_Permutation': {
       'type': 'red',
       'attack': 'PermutationAttack'
   },

   'PichuPixelPatrolRed_Inject': {
       'type': 'red',
       'attack': 'MisspellJoinInjectAttack'
   },

   'PichuPixelPatrolRed_Permute': {
       'type': 'red',
       'attack': 'PermuteAndJoinAttack'
   },
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
