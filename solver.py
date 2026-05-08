import os
import re
from openai import OpenAI

from prompts import PROPOSE_PROMPT, VALUE_PROMPT
from logger_config import setup_logger

TARGET = 24
EPS = 1e-6
DEFAULT_MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")


class ToTSolver:
    def __init__(
        self,
        api_key,
        model=DEFAULT_MODEL,
        max_depth=3,
        proposal_limit=20,
        beam_width=20,
        max_nodes=50
    ):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_depth = max_depth
        self.proposal_limit = proposal_limit
        self.beam_width = beam_width
        self.max_nodes = max_nodes
        self.logger = setup_logger()

        self.reset()

    def reset(self):
        self.api_calls = 0
        self.nodes_expanded = 0
        self.pruned = 0
        self.trace = []
        self.visited = set()

    @staticmethod
    def _state_key(nums):
        return tuple(sorted(round(float(x), 6) for x in nums))

    @staticmethod
    def _score_label(label):
        return {
            "sure": 20,
            "likely": 1,
            "impossible": 0.001
        }.get(label, 0.001)

    @staticmethod
    def _format_nums(nums):
        return " ".join(
            str(int(x)) if float(x).is_integer() else str(round(float(x), 6))
            for x in nums
        )

    def _chat(self, prompt, temperature=0):
        self.api_calls += 1

        self.logger.debug("=" * 80)
        self.logger.debug(f"API CALL #{self.api_calls}")
        self.logger.debug(f"MODEL: {self.model}")
        self.logger.debug(f"TEMPERATURE: {temperature}")
        # self.logger.debug("PROMPT:")
        # self.logger.debug(prompt)

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.choices[0].message.content.strip()
        self.logger.debug("RAW RESPONSE:")
        self.logger.debug(content)
        self.logger.debug("=" * 80)

        return content

    def propose(self, nums):
        input_str = self._format_nums(nums)
        prompt = PROPOSE_PROMPT.format(input=input_str)

        response = self._chat(prompt, temperature=0)

        proposals = []
        seen_states = set()

        self.logger.info(f"[PROPOSE] state={nums}")

        for line in response.splitlines():
            line = line.strip()

            if not line:
                continue

            match = re.search(r"\(left:\s*([^)]+)\)", line, re.I)

            if not match:
                self.logger.debug(f"[SKIP] no left state: {line}")
                continue

            nums_part = match.group(1)

            try:
                numbers = re.findall(r"-?\d+(?:\.\d+)?", nums_part)
                new_nums = [float(x) for x in numbers]

                if len(new_nums) != len(nums) - 1:
                    self.pruned += 1
                    self.logger.debug(f"[SKIP] invalid length: {line}")
                    continue

                key = self._state_key(new_nums)

                if key in seen_states:
                    self.pruned += 1
                    self.logger.debug(f"[SKIP] duplicate proposal: {line}")
                    continue

                seen_states.add(key)
                proposals.append((new_nums, line))

                self.logger.debug(f"[PARSED] {new_nums} | {line}")

            except Exception as e:
                self.pruned += 1
                self.logger.error(f"[PARSE ERROR] {e} | line={line}")

        self.trace.append({
            "type": "propose",
            "state": nums,
            "raw_response": response,
            "parsed_count": len(proposals),
            "parsed_proposals": proposals
        })

        self.logger.info(f"[PROPOSE COUNT] {len(proposals)}")

        return proposals[:self.proposal_limit]

    def evaluate(self, nums):
        input_str = self._format_nums(nums)
        prompt = VALUE_PROMPT.format(input=input_str)

        response = self._chat(prompt, temperature=0)
        text = response.lower().strip()

        last_line = text.splitlines()[-1] if text else ""

        if "sure" in last_line:
            label = "sure"
        elif "likely" in last_line:
            label = "likely"
        elif "impossible" in last_line:
            label = "impossible"
        elif "sure" in text:
            label = "sure"
        elif "likely" in text:
            label = "likely"
        else:
            label = "impossible"

        value = self._score_label(label)

        self.trace.append({
            "type": "evaluate",
            "state": nums,
            "raw_response": response,
            "label": label,
            "value": value
        })

        self.logger.info(
            f"[EVALUATE] state={nums} -> label={label}, value={value}"
        )

        return label, value

    def solve(self, nums):
        self.reset()

        solution = self._beam_search([float(n) for n in nums])

        return {
            "success": solution is not None,
            "solution": solution,
            "nodes_expanded": self.nodes_expanded,
            "api_calls": self.api_calls,
            "pruned": self.pruned,
            "trace": self.trace
        }

    def _beam_search(self, nums):
        frontier = [
            {
                "state": nums,
                "path": []
            }
        ]

        for depth in range(self.max_depth):
            self.logger.info("=" * 60)
            self.logger.info(
                f"[BEAM DEPTH] depth={depth}, frontier_size={len(frontier)}"
            )

            candidates = []

            for item in frontier:
                if self.nodes_expanded >= self.max_nodes:
                    self.logger.info("[STOP] max_nodes reached")
                    return None

                state = item["state"]
                path = item["path"]

                key = self._state_key(state)

                if key in self.visited:
                    self.pruned += 1
                    self.logger.info(f"[PRUNE] visited state={state}")
                    continue

                self.visited.add(key)
                self.nodes_expanded += 1

                self.logger.info(
                    f"[EXPAND] node={self.nodes_expanded}, state={state}"
                )

                if len(state) == 1:
                    if abs(state[0] - TARGET) < EPS:
                        self.logger.info("[SUCCESS] found 24")
                        return path

                    self.pruned += 1
                    continue

                proposals = self.propose(state)

                for next_nums, step_desc in proposals:
                    new_path = path + [step_desc]

                    # Nếu state còn 1 số, kiểm tra bằng code, không gọi LLM evaluate
                    if len(next_nums) == 1:
                        if abs(next_nums[0] - TARGET) < EPS:
                            self.logger.info(
                                f"[SUCCESS] final_state={next_nums}, step={step_desc}"
                            )
                            return new_path

                        self.pruned += 1
                        self.logger.info(
                            f"[PRUNE] final_state_not_24={next_nums}, step={step_desc}"
                        )
                        continue

                    label, value = self.evaluate(next_nums)

                    if label == "impossible":
                        self.pruned += 1

                    candidate = {
                        "state": next_nums,
                        "path": new_path,
                        "value": value,
                        "label": label,
                        "step": step_desc
                    }

                    candidates.append(candidate)

                    self.logger.info(
                        f"[CANDIDATE] value={value}, label={label}, step={step_desc}"
                    )

            if not candidates:
                self.logger.info("[STOP] no candidates")
                return None

            candidates.sort(key=lambda x: x["value"], reverse=True)

            selected = candidates[:self.beam_width]

            self.trace.append({
                "type": "select",
                "depth": depth,
                "num_candidates": len(candidates),
                "selected": [
                    {
                        "state": item["state"],
                        "value": item["value"],
                        "label": item["label"],
                        "step": item["step"]
                    }
                    for item in selected
                ]
            })

            self.logger.info("[SELECTED FRONTIER]")
            for i, item in enumerate(selected, start=1):
                self.logger.info(
                    f"{i}. value={item['value']} label={item['label']} state={item['state']}"
                )

            for item in selected:
                if len(item["state"]) == 1 and abs(item["state"][0] - TARGET) < EPS:
                    self.logger.info("[SUCCESS] found 24 in selected frontier")
                    return item["path"]

            frontier = [
                {
                    "state": item["state"],
                    "path": item["path"]
                }
                for item in selected
            ]

        return None