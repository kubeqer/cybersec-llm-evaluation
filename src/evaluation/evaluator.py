from pathlib import Path

from deepeval.metrics import AnswerRelevancyMetric, GEval  # type: ignore
from deepeval.test_case import LLMTestCase  # type: ignore
from loguru import logger

from src.core.decorators.error_handling import error_handling
from src.core.decorators.log_calls import log_calls
from src.evaluation.majority_vote_judge import MajorityVoteJudge
from src.evaluation.schema import EvalResult


class Evaluator:
    def __init__(self, models, judge_llm, results_dir: Path):
        self.models = models
        self.judge = MajorityVoteJudge(judge_llm, votes=5)
        self.results_dir = results_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)

    @error_handling
    @log_calls
    def evaluate(self, samples):
        results = []
        for model in self.models:
            model_name = getattr(model, "model_config", None)
            model_name = (
                getattr(model_name, "model_name", None) or model.__class__.__name__
            )
            logger.info(f"Evaluating model: {model_name}")
            correct = 0
            total = 0
            comp_sum = 0.0
            relevancy_metric = AnswerRelevancyMetric(threshold=0.5)  # score in [0,1]
            comprehensiveness_metric = GEval(
                name="Comprehensiveness",
                criteria="Evaluate coverage of relevant vulnerabilities, clarity, and actionable detail.",  # noqa: E501
                evaluation_steps=[
                    "Check if the answer identifies the correct vulnerability types",
                    "Assess clarity and structure",
                    "Assess presence of actionable remediation details",
                ],
                threshold=0.5,
                evaluation_params={
                    "rubric": (
                        "High score if the answer correctly identifies vulnerability "
                        "types relevant to the question/code, "
                        "explains why, and provides concrete remediation or "
                        "best practices."
                        "Penalize missing key issues, "
                        "vague guidance, or inaccuracies."
                    )
                },
            )

            for s in samples:
                question = (
                    s.get("question") or s.get("prompt") or s.get("description") or ""
                )
                context_code = s.get("code") or s.get("vulnerable_code") or ""
                if context_code:
                    question = (
                        question
                        or "What types of vulnerabilities are seen in this code?"
                    )
                    full_question = f"{question}\n\n{context_code}"
                else:
                    full_question = question or "What security issue is described?"
                try:
                    answer = model.generate(
                        full_question, eval_type=getattr(s, "eval_type", None) or None
                    )
                except TypeError:
                    answer = model.generate(full_question)
                vuln_type = s.get("type") or s.get("vulnerability") or ""
                expected_statement = (
                    f"Answer recalls about vulnerability {vuln_type}".strip()
                )

                tc = LLMTestCase(
                    input=full_question,
                    actual_output=answer,
                    expected_output=expected_statement,
                )
                relevancy_metric.measure(tc)
                comprehensiveness_metric.measure(tc)
                is_true = bool(getattr(relevancy_metric, "passed", False))
                comp_score_0_1 = float(getattr(comprehensiveness_metric, "score", 0.0))
                comp = max(0.0, min(100.0, comp_score_0_1 * 100.0))

                total += 1
                if is_true:
                    correct += 1
                comp_sum += comp

            incorrect = total - correct
            avg_comp = (comp_sum / total) if total else 0.0
            results.append(
                EvalResult(
                    model_name=model_name,
                    total=total,
                    correct=correct,
                    incorrect=incorrect,
                    avg_comprehensiveness=avg_comp,
                )
            )
            logger.info(
                f"{model_name}: total={total}, correct={correct}, "
                f"incorrect={incorrect}, avg_comp={avg_comp:.1f}%"
            )

        self._persist(results)
        return results

    def _persist(self, results):
        out = self.results_dir / "evaluation_summary.csv"
        header = "model_name,total,correct,incorrect,avg_comprehensiveness\n"
        if not out.exists():
            out.write_text(header, encoding="utf-8")
        lines = []
        for r in results:
            lines.append(
                f"{r.model_name},{r.total},{r.correct},{r.incorrect},{r.avg_comprehensiveness:.1f}\n"
            )
        with out.open("a", encoding="utf-8") as f:
            f.writelines(lines)
        logger.info(f"Saved results to {out}")
