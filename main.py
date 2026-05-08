# main.py
from solver import ToTSolver

API_KEY = ""

def main():
    benchmark_sets = [
        [4, 7, 8, 8],
        [1, 5, 5, 5],
        [3, 3, 8, 8],
        [4, 9, 10, 13]
    ]

    solver = ToTSolver(api_key=API_KEY)

    for nums in benchmark_sets:
        print(f"\n--- Đang giải bộ số: {nums} ---")
        solution = solver.solve(nums)
        if solution:
            print("Thành công!")
            for i, step in enumerate(solution):
                print(f"  Bước {i+1}: {step}")
        else:
            print("Không tìm thấy lời giải.")

if __name__ == "__main__":
    main()