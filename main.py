import json
import os
from dotenv import load_dotenv

from classical_solver import ClassicalDFSSolver
from solver import ToTSolver
from experiment_logger import ExperimentLogger
from prompts import PROPOSE_PROMPT, VALUE_PROMPT

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")


def load_benchmark(path="benchmark.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_solver(logger, method, solver, nums, model=None):
    start = logger.start_case()

    result = solver.solve(nums)

    record = {
        "method": method,
        "model": model,
        "input": nums,
        **result
    }

    logger.end_case(record, start)

    return result

config = {
    "model": MODEL_NAME,
    "method": "tot_beam_search",
    "max_depth": 3,
    "proposal_limit": 15,
    "beam_width": 2,
    "max_nodes": 50,
    "prompts": {
        "propose_prompt": PROPOSE_PROMPT,
        "value_prompt": VALUE_PROMPT
    }
}

def main():
    benchmark_sets = load_benchmark()
    logger = ExperimentLogger(config=config)

    classical_solver = ClassicalDFSSolver()

    tot_solver = ToTSolver(
        api_key=API_KEY,
        model=MODEL_NAME,
        max_depth=3,
        proposal_limit=15,
        beam_width=2,
        max_nodes=50
    )

    for nums in benchmark_sets:
        print(f"\nInput: {nums}")

        classical_result = run_solver(
            logger=logger,
            method="classical_dfs",
            solver=classical_solver,
            nums=nums
        )

        tot_result = run_solver(
            logger=logger,
            method="tot_beam_search",
            solver=tot_solver,
            nums=nums,
            model=MODEL_NAME
        )

        print(
            "Classical:",
            classical_result["success"],
            classical_result["solution"]
        )

        print(
            "ToT Beam:",
            tot_result["success"],
            tot_result["solution"]
        )

    logger.save()

    print("\nSaved results to results.json")
    print("Saved debug logs to debug.log")


if __name__ == "__main__":
    main()