import sublime
import sublime_plugin
import re

class DtologformatterCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # 선택된 영역 가져오기
        selections = self.view.sel()

        for sel in selections:
            # 선택된 텍스트가 없으면 현재 줄 전체를 대상으로
            if sel.empty():
                line = self.view.line(sel)
                text = self.view.substr(line)
            else:
                text = self.view.substr(sel)

            # 텍스트 처리
            formatted_text = self.process_text(text)

            # 결과 적용
            if sel.empty():
                self.view.replace(edit, line, formatted_text)
            else:
                self.view.replace(edit, sel, formatted_text)

    def process_text(self, text):
        """
        입력 텍스트 내의 DTO 구조(예: MainDto(...), SubDto.Data(...), ChildDto(...) 등)를
        찾아서 내부의 key=value 항목 중 value가 'null' 또는 'NULL'인 것은 제거하며,
        보기 좋게 줄바꿈 및 들여쓰기(기본 2칸, 내부 DTO마다 추가 2칸)를 적용하여 재조립합니다.
        """

        indent_str = "  "  # 들여쓰기는 2칸

        def find_matching_parenthesis(s, start_idx):
            """s[start_idx]의 '('에 대응하는 닫는 괄호 인덱스를 반환합니다."""
            count = 1
            i = start_idx + 1
            while i < len(s) and count > 0:
                if s[i] == '(':
                    count += 1
                elif s[i] == ')':
                    count -= 1
                i += 1
            return i - 1 if count == 0 else -1

        def split_arguments(s):
            """
            s 문자열을 괄호 중첩을 고려하여 쉼표(,) 기준으로 분리합니다.
            예)
            "key1=val1, key2=SomeDto(val=null, a=b)" →
              ["key1=val1", "key2=SomeDto(val=null, a=b)"]
            """
            parts = []
            current = ''
            level = 0
            for char in s:
                if char == '(':
                    level += 1
                    current += char
                elif char == ')':
                    level -= 1
                    current += char
                elif char == ',' and level == 0:
                    parts.append(current.strip())
                    current = ''
                else:
                    current += char
            if current:
                parts.append(current.strip())
            return parts

        # DTO 패턴 : 단어(및 점 포함) 바로 뒤에 '('가 오는 패턴 (예: MainDto(, SubDto.Data( 등)
        dto_pattern = re.compile(r'([\w\.]+)\(')

        def process_all_dto(s, indent_level):
            """
            s 문자열 내에서 DTO 패턴을 찾아 내부 인자들을 process_arguments()로 가공한 후,
            DTO를 아래와 같이 재조립합니다.
              DTOName(
                첫번째 인자
              , 이후 인자...
              )
            indent_level에 따라 들여쓰기를 적용합니다.
            """
            result = ""
            pos = 0
            while True:
                m = dto_pattern.search(s, pos)
                if not m:
                    result += s[pos:]
                    break
                # DTO 패턴 이전의 문자열은 그대로 추가
                result += s[pos:m.start()]
                dto_name = m.group(1)
                open_idx = m.end() - 1  # '(' 의 위치
                close_idx = find_matching_parenthesis(s, open_idx)
                if close_idx == -1:
                    result += s[m.start():]
                    break
                # 괄호 안의 내용
                inner = s[open_idx + 1:close_idx]
                # 내부 인자는 indent_level보다 한단계 더 들여쓰도록 처리
                formatted_inner = process_arguments(inner, indent_level + 1)
                # DTO 재조립: dto_name( + "\n" + 내부인자 + "\n" + 현재 indent + ")"
                dto_block = dto_name + "(\n" + formatted_inner + "\n" + (indent_str * indent_level) + ")"
                result += dto_block
                pos = close_idx + 1
            return result

        def process_arguments(arg_text, indent_level):
            """
            DTO 내부 인자 문자열을 split_arguments()로 분리한 뒤,
            각 항목에 대해 재귀적으로 내부 DTO 처리를 진행합니다.
            또한 key=value 항목에서 value가 null (대소문자 무관)이면 해당 항목을 출력하지 않습니다.
            모든 항목은 현재 indent_level + 1 만큼 들여쓰기를 적용하고,
            두 번째 항목부터는 ", "를 포함하여 현재 indent_level만큼 들여쓰기를 적용합니다.
            """
            items = split_arguments(arg_text)
            processed_items = []
            for item in items:
                processed_item = process_all_dto(item, indent_level)
                # key=value 형태일 경우 value가 "null" (대소문자)라면 출력하지 않음
                if "=" in processed_item:
                    key, value = processed_item.split("=", 1)
                    if value.strip().lower() == "null":
                        continue
                processed_items.append(processed_item)

            lines = []
            base_indent = indent_str * indent_level
            first_indent = indent_str * (indent_level + 1)  # 첫 항목은 한 단계 더 들여쓰기
            
            for i, itm in enumerate(processed_items):
                if i == 0:
                    lines.append(first_indent + itm)  # 첫 항목은 추가 들여쓰기 적용
                else:
                    lines.append(base_indent + ", " + itm)  # 이후 항목은 기본 들여쓰기 + 콤마
            return "\n".join(lines)

        return process_all_dto(text, 0)
