# Available baseline methods that are actually implemented
BASELINE_METHODS = {
    'input_filters': {
        'NoInputFilter': 'methods.input_filters.InputFilter',
        'BaseRegexFilter': 'methods.input_filters.RegexFilter',
        'BaseWordFilter': 'methods.input_filters.SimpleWordFilter',
        'EmbeddingFilter': 'methods.ppp_input_filters.EmbeddingFilter'
    },
    'output_filters': {
        'NoOutputFilter': 'methods.output_filters.OutputFilter',
        'BaseContentDetector': 'methods.output_filters.ContentDetectorFilter',
        'ContentClassificationFilter': 'methods.ppp_output_filters.ContentClassificationFilter'
    },
    # 'model_mods': {
    #     'BaseModelPatch': 'methods.model_modifications.ModelPatch'
    # },
    'attacks': {
        'RandomizedDupAndCombAttack': 'attacks.ppp_attack.RandomizedDupAndCombAttack',
        'SynonymReplacementAttack': 'attacks.ppp_attack.SynonymReplacementAttack',
        'PermutationAttack': 'attacks.ppp_attack.PermutationAttack',
        'PermuteAndJoinAttack': 'attacks.ppp_attack.PermuteAndJoinAttack',
        'MisspellJoinInjectAttack': 'attacks.ppp_attack.MisspellJoinInjectAttack',
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
} 
