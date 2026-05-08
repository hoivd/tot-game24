# utils.py

def get_possible_next_states(nums):
    """Tự động sinh các trạng thái tiếp theo bằng code để đảm bảo chính xác"""
    states = []
    n = len(nums)
    for i in range(n):
        for j in range(n):
            if i == j: continue
            a, b = nums[i], nums[j]
            remaining = [nums[k] for k in range(n) if k != i and k != j]
            
            # Các phép toán cơ bản
            ops = {
                "+": a + b,
                "-": a - b,
                "*": a * b
            }
            if b != 0: ops["/"] = a / b
            
            for op_symbol, result in ops.items():
                new_state = remaining + [result]
                description = f"{a} {op_symbol} {b} = {result}"
                states.append((new_state, description))
    return states