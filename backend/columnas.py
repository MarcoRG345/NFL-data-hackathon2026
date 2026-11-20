"""
Nombres reales de columnas y valores de texto del dataset NFL Big Data Bowl 2023.

Fuente: scratch/perfil-datos.md
Ningún otro archivo debe escribir estos textos a mano.
"""

# ============================================================================
# COLUMNAS — games.csv
# ============================================================================
COL_GAME_ID = "gameId"
COL_SEASON = "season"
COL_WEEK = "week"
COL_GAME_DATE = "gameDate"
COL_GAME_TIME_EASTERN = "gameTimeEastern"
COL_HOME_TEAM_ABBR = "homeTeamAbbr"
COL_VISITOR_TEAM_ABBR = "visitorTeamAbbr"

# ============================================================================
# COLUMNAS — plays.csv
# ============================================================================
COL_PLAY_ID = "playId"
COL_PLAY_DESCRIPTION = "playDescription"
COL_QUARTER = "quarter"
COL_DOWN = "down"
COL_YARDS_TO_GO = "yardsToGo"
COL_POSSESSION_TEAM = "possessionTeam"
COL_DEFENSIVE_TEAM = "defensiveTeam"
COL_YARDLINE_SIDE = "yardlineSide"
COL_YARDLINE_NUMBER = "yardlineNumber"
COL_GAME_CLOCK = "gameClock"
COL_PRESNAP_HOME_SCORE = "preSnapHomeScore"
COL_PRESNAP_VISITOR_SCORE = "preSnapVisitorScore"
COL_PASS_RESULT = "passResult"
COL_PENALTY_YARDS = "penaltyYards"
COL_PREPENALTY_PLAY_RESULT = "prePenaltyPlayResult"
COL_PLAY_RESULT = "playResult"
COL_FOUL_NAME_1 = "foulName1"
COL_FOUL_NFLID_1 = "foulNFLId1"
COL_FOUL_NAME_2 = "foulName2"
COL_FOUL_NFLID_2 = "foulNFLId2"
COL_FOUL_NAME_3 = "foulName3"
COL_FOUL_NFLID_3 = "foulNFLId3"
COL_ABSOLUTE_YARDLINE_NUMBER = "absoluteYardlineNumber"
COL_OFFENSE_FORMATION = "offenseFormation"
COL_PERSONNEL_O = "personnelO"
COL_DEFENDERS_IN_BOX = "defendersInBox"  # Nombre real verificado
COL_PERSONNEL_D = "personnelD"
COL_DROPBACK_TYPE = "dropBackType"  # Nombre real verificado (B mayúscula)
COL_PFF_PLAY_ACTION = "pff_playAction"
COL_PFF_PASS_COVERAGE = "pff_passCoverage"
COL_PFF_PASS_COVERAGE_TYPE = "pff_passCoverageType"

# ============================================================================
# COLUMNAS — players.csv
# ============================================================================
COL_NFL_ID = "nflId"
COL_HEIGHT = "height"
COL_WEIGHT = "weight"
COL_BIRTH_DATE = "birthDate"
COL_COLLEGE_NAME = "collegeName"
COL_OFFICIAL_POSITION = "officialPosition"
COL_DISPLAY_NAME = "displayName"

# ============================================================================
# COLUMNAS — pffScoutingData.csv
# ============================================================================
COL_PFF_ROLE = "pff_role"
COL_PFF_POSITION_LINED_UP = "pff_positionLinedUp"
COL_PFF_HIT = "pff_hit"
COL_PFF_HURRY = "pff_hurry"
COL_PFF_SACK = "pff_sack"
COL_PFF_BEATEN_BY_DEFENDER = "pff_beatenByDefender"
COL_PFF_HIT_ALLOWED = "pff_hitAllowed"
COL_PFF_HURRY_ALLOWED = "pff_hurryAllowed"
COL_PFF_SACK_ALLOWED = "pff_sackAllowed"
COL_PFF_NFLID_BLOCKED_PLAYER = "pff_nflIdBlockedPlayer"
COL_PFF_BLOCK_TYPE = "pff_blockType"
COL_PFF_BACKFIELD_BLOCK = "pff_backFieldBlock"

# ============================================================================
# COLUMNAS — tracking_<gameId>.csv (un archivo por partido)
# ============================================================================
COL_FRAME_ID = "frameId"
COL_TIME = "time"
COL_JERSEY_NUMBER = "jerseyNumber"
COL_TEAM = "team"  # Nombre real verificado (no "club")
COL_PLAY_DIRECTION = "playDirection"
COL_X = "x"
COL_Y = "y"
COL_S = "s"
COL_A = "a"
COL_DIS = "dis"
COL_O = "o"
COL_DIR = "dir"
COL_EVENT = "event"

# ============================================================================
# COLUMNAS — derivadas (normalizacion.py)
# ============================================================================
COL_NORMALIZADO = "normalizado"
COL_LINEA_GOLPEO = "linea_golpeo"
COL_FUENTE_LINEA = "fuente_linea"
COL_MARCADA = "marcada"
COL_DIFF_CPRIME_D = "diff_cprime_D"

# ============================================================================
# VALORES — pff_role (verificados, mayúsculas exactas)
# ============================================================================
ROLE_PASS = "Pass"
ROLE_PASS_BLOCK = "Pass Block"
ROLE_PASS_ROUTE = "Pass Route"
ROLE_PASS_RUSH = "Pass Rush"
ROLE_COVERAGE = "Coverage"

# Roles que se conservan en el tracking recortado (más el balón). Pass Block se descarta.
ROLES_A_CONSERVAR = {ROLE_PASS, ROLE_PASS_ROUTE, ROLE_PASS_RUSH, ROLE_COVERAGE}
ROL_BALON = "_balon"  # marcador para el balón (team = "football")

# ============================================================================
# VALORES — event (verificados en el tracking; "None" = sin evento, pandas lo lee como NaN)
# ============================================================================
EVENT_BALL_SNAP = "ball_snap"
EVENT_PASS_FORWARD = "pass_forward"
EVENT_QB_SACK = "qb_sack"
EVENT_QB_STRIP_SACK = "qb_strip_sack"
EVENT_AUTO_BALLSNAP = "autoevent_ballsnap"        # respaldo de ball_snap
EVENT_AUTO_PASSFORWARD = "autoevent_passforward"  # respaldo de pass_forward
# pass_arrived NO se usa: casi no existe en estos datos.

# ============================================================================
# VALORES — passResult
# ============================================================================
RESULT_C = "C"  # Completo
RESULT_I = "I"  # Incompleto
RESULT_S = "S"  # Sack
RESULT_R = "R"  # Scramble
RESULT_IN = "IN"  # Intercepción

# ============================================================================
# VALORES — team (balón)
# ============================================================================
TEAM_FOOTBALL = "football"

# ============================================================================
# VALORES — playDirection
# ============================================================================
PLAY_DIRECTION_LEFT = "left"
PLAY_DIRECTION_RIGHT = "right"

# ============================================================================
# VALORES — dropBackType a excluir en Q4 (rollouts diseñados y carreras)
# ============================================================================
DROPBACK_DESIGNED_ROLLOUT_RIGHT = "DESIGNED_ROLLOUT_RIGHT"
DROPBACK_DESIGNED_ROLLOUT_LEFT = "DESIGNED_ROLLOUT_LEFT"
DROPBACK_DESIGNED_RUN = "DESIGNED_RUN"

DROPBACK_EXCLUIR_Q4 = [
    DROPBACK_DESIGNED_ROLLOUT_RIGHT,
    DROPBACK_DESIGNED_ROLLOUT_LEFT,
    DROPBACK_DESIGNED_RUN,
]
