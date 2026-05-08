# solver.py
import openai
import re
from prompts import propose_prompt, value_prompt

class ToTSolver:
    def __init__(self, api_key, model="gpt-4.1-mini"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def propose(self, nums):
        """Sử dụng 1-shot propose_prompt để lấy các bước tiếp theo"""
        input_str = " ".join(map(str, nums))
        prompt = propose_prompt.format(input=input_str)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content.strip()

        print(f"Propose response:\n{response}\n")
        proposals = []
        # Tìm các dòng có định dạng: phép tính (left: số số số)
        lines = response.split('\n')
        for line in lines:
            if "left:" in line.lower():
                try:
                    # Regex tìm nội dung bên trong dấu ngoặc (left: ...)
                    match = re.search(r'\(left:\s*(.*?)\)', line, re.IGNORECASE)
                    if match:
                        nums_part = match.group(1).strip()
                        # Chuyển chuỗi số thành danh sách float
                        new_nums = [float(x) for x in nums_part.split()]
                        proposals.append((new_nums, line))
                except Exception as e:
                    continue
        return proposals

    def evaluate(self, nums):
        """Sử dụng value_prompt để dán nhãn trạng thái"""
        input_str = " ".join(map(str, nums))
        prompt = value_prompt.format(input=input_str)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
            ).choices[0].message.content.strip().lower()
        print(f"Evaluate response:{nums}\n{response}\n")
        # Lấy dòng cuối cùng của phản hồi vì LLM thường giải thích rồi mới kết luận
        lines = response.split('\n')
        last_line = lines[-1]
        
        if "sure" in last_line: return "sure"
        if "likely" in last_line: return "likely"
        return "impossible"

    def solve(self, nums, path=[]):
        # Kiểm tra mục tiêu
        if len(nums) == 1:
            if abs(nums[0] - 24) < 1e-6:
                return path
            return None

        print(f"Duyệt: {nums}")
        next_steps = self.propose(nums)
        
        # Sắp xếp để ưu tiên thử nhánh 'likely' hoặc 'sure' trước (nếu có)
        for next_nums, step_desc in next_steps:
            rating = self.evaluate(next_nums)
            print(f"  -> {step_desc} | Đánh giá: {rating}")
            
            if rating in ["sure", "likely"]:
                # DFS Backtracking thực thụ qua đệ quy
                result = self.solve(next_nums, path + [step_desc])
                if result:
                    return result
            else:
                print(f"     [!] Cắt tỉa (Impossible)")
        
        return None