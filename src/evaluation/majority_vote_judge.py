from collections import Counter


class MajorityVoteJudge:
    def __init__(self, judge_llm, votes=5):
        self.judge_llm = judge_llm
        self.votes = votes

    def judge_truth(self, question, answer, statement):
        prompt = (
            "Question:\n"
            f"{question}\n\n"
            "Answer:\n"
            f"{answer}\n\n"
            "Statement:\n"
            f"{statement}\n\n"
            "Decide if the statement is true given the answer and question. "
            "Respond with only 'YES' or 'NO'."
        )
        decisions = []
        for _ in range(self.votes):
            decision = self.judge_llm.generate(prompt).strip().upper()
            decisions.append(
                "YES" if "YES" in decision and "NO" not in decision else "NO"
            )
        majority = Counter(decisions).most_common(1)[0][0]
        return majority == "YES"

    def score_comprehensiveness(self, question, answer):
        prompt = f"""You are grading the comprehensiveness of an answer.\n
Consider coverage of relevant vulnerabilities, clarity, and actionable detail.\n
Return only a number from 0 to 100.\n\n"
Question:\n
{question}\n\n
Answer:\n
{answer}\n\n
Score (0-100):"""
        scores = []
        for _ in range(self.votes):
            raw = self.judge_llm.generate(prompt).strip()
            num = "".join(ch for ch in raw if ch.isdigit())
            try:
                val = max(0, min(100, int(num))) if num else 0
            except Exception:
                val = 0
            scores.append(val)
        scores.sort()
        median = scores[len(scores) // 2]
        return float(median)
