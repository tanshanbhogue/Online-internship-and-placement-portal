# ==============================================================================
# FILE   : backend/app/modules/practice/code_evaluator.py
# STORY  : #22 Practice Test Scoring  [FR-003; SEC-06, SEC-12]
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 5
# ==============================================================================
#
# PURPOSE
#   Extension point for evaluating coding answers. The real sandbox (SEC-17, 'Code Evaluation Sandbox' external system) is a later story, so this
#   sprint ships only a safe placeholder.
#
# EXPOSES
#   class CodeEvaluator(Protocol): evaluate(question, code: str) -> EvaluationResult(is_correct: bool | None, status: EvaluationStatus)
#   class PendingCodeEvaluator: returns (None, PENDING). It must NEVER execute, import or eval submitted code.
#   get_code_evaluator() -> CodeEvaluator   # returns PendingCodeEvaluator; later swapped by config
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
