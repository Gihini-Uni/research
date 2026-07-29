# surveys/hmsam.py
# HMSAM Questionnaire Template
# Based on Lowry et al. (2013)
# Measured on a 5-point Likert scale:
# 1 = Strongly Disagree, 2 = Disagree, 3 = Neutral,
# 4 = Agree, 5 = Strongly Agree

HMSAM_QUESTIONS = [

    # Perceived Ease of Use (PEU)
    ('peou', 'PEU1', 'I find it easy to learn how to use the features of this application / software.'),
    ('peou', 'PEU2', 'I find it easy to operate features of this application / software as I need.'),
    ('peou', 'PEU3', 'I find the display and instructions clear and understandable.'),
    ('peou', 'PEU4', 'I find navigation of this application / software simple.'),
    ('peou', 'PEU5', 'I find myself quickly getting used to the navigation of this app / software.'),
    ('peou', 'PEU6', 'I find features of this app / software easy to use.'),

    # Perceived Usefulness (PU)
    ('pu', 'PU1', 'I find this application / software useful for entertainment.'),
    ('pu', 'PU2', 'I find this application / software useful for relaxation.'),
    ('pu', 'PU3', 'I find this application / software provides the information I need.'),
    ('pu', 'PU4', 'I find this application / software useful in my daily life.'),
    ('pu', 'PU5', 'I find this application / software helps me spend my leisure time.'),
    ('pu', 'PU6', 'I find this application / software useful for expanding my social connections.'),

    # Joy (JOY)
    ('joy', 'JOY1', 'I find using this application / software enjoyable.'),
    ('joy', 'JOY2', 'I find this application / software entertaining.'),
    ('joy', 'JOY3', 'I find myself truly enjoying this application / software.'),
    ('joy', 'JOY4', 'I find myself satisfied after using this application / software.'),
    ('joy', 'JOY5', 'I find the this application / software experience pleasant.'),

    # Curiosity (CUR)
    ('curiosity', 'CUR1', 'I find myself curious to keep exploring this application / software.'),
    ('curiosity', 'CUR2', 'I find myself eager to discover new things through this application / software.'),
    ('curiosity', 'CUR3', 'I find myself driven to learn new things from this application / software.'),
    ('curiosity', 'CUR4', 'I find this application / software stimulates my curiosity.'),
    ('curiosity', 'CUR5', 'I find myself interested in this application / software\'s features.'),

    # Control (CTR)
    ('control', 'CTR1', 'I find I am free to use this application / software as per my free will without being influenced by other forces.'),
    ('control', 'CTR2', 'I find I can manage my time whenever I\'m using this application / software.'),
    ('control', 'CTR3', 'I find I have full control over how I use this application / software.'),
    ('control', 'CTR4', 'I find I can manage my interactions while using this application / software.'),
    ('control', 'CTR5', 'I find I can use this application / software according to my own preferences.'),

    # Focused Immersion (IMM)
    ('fi', 'IMM1', 'I find myself fully focused when using this application / software.'),
    ('fi', 'IMM2', 'I find myself absorbed when using this application / software.'),
    ('fi', 'IMM3', 'I find myself losing track of time while using this application / software.'),
    ('fi', 'IMM4', 'I find myself feeling present in this application / software.'),
    ('fi', 'IMM5', 'I find my full attention absorbed in this application / software.'),
    ('fi', 'IMM6', 'I find this application / software usage makes me immersed.'),

    # Behavioural Intention to Use (BIU)
    ('biu', 'BIU1', 'I intend to keep using this application / software.'),
    ('biu', 'BIU2', 'I plan to use this application / software more often.'),
    ('biu', 'BIU3', 'I want to continue using this application / software long-term.'),
    ('biu', 'BIU4', 'I want to recommend this application / software to others.'),
    ('biu', 'BIU5', 'I want to make this application / software usage a habit.'),
]

# Likert scale labels used across the entire questionnaire
LIKERT_SCALE = [
    (1, 'Strongly Disagree'),
    (2, 'Disagree'),
    (3, 'Neutral'),
    (4, 'Agree'),
    (5, 'Strongly Agree'),
]

# Construct display names — used in dashboard and analytics
CONSTRUCT_LABELS = {
    'peou':     'Perceived Ease of Use',
    'pu':       'Perceived Usefulness',
    'joy':      'Joy',
    'curiosity':'Curiosity',
    'control':  'Control',
    'fi':       'Focused Immersion',
    'biu':      'Behavioural Intention to Use',
}