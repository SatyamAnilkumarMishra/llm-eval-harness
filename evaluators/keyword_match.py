import re
from typing import List, Union
from evaluators.base import BaseEvaluator, EvalResult


class KeywordMatchEvaluator(BaseEvaluator):
    name = "keyword_match"

    def __init__(
        self,
        keywords: Union[List[str], str],
        match_all: bool = False,
        use_regex: bool = False,
    ):
        if isinstance(keywords, str):
            self.keywords = [keywords]
        else:
            self.keywords = keywords
        self.match_all = match_all
        self.use_regex = use_regex

    def evaluate(self, prediction: str, reference: str, **kwargs) -> EvalResult:
        text = prediction
        matches = 0
        details = []

        for kw in self.keywords:
            if self.use_regex:
                found = bool(re.search(kw, text, re.IGNORECASE))
            else:
                found = kw.lower() in text.lower()

            if found:
                matches += 1
            details.append(f"{kw}: {'found' if found else 'missing'}")

        if self.match_all:
            passed = matches == len(self.keywords)
        else:
            passed = matches > 0
        score = matches / len(self.keywords) if self.keywords else 0.0

        return EvalResult(
            score=score,
            passed=passed,
            reasoning="; ".join(details),
        )
