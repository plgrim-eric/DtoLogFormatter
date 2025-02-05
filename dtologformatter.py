import sublime
import sublime_plugin

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
        # 괄호 내부 텍스트 추출
        start_idx = text.find('(')
        end_idx = text.rfind(')')
        
        if start_idx != -1 and end_idx != -1:
            prefix = text[:start_idx + 1]
            inner_text = text[start_idx + 1:end_idx]
            
            # 콤마로 분리
            pairs = inner_text.split(',')
            
            # 각 쌍을 처리
            result_pairs = []
            for pair in pairs:
                # 공백 제거 후 key=value 형태로 분리
                try:
                    key, value = pair.strip().split('=')
                    # 값이 있는 경우만 저장
                    if value.strip():
                        result_pairs.append("{}={}".format(key.strip(), value.strip()))
                except ValueError:
                    # 잘못된 형식은 무시
                    continue
            
            # 결과를 다시 조합
            return prefix + ', '.join(result_pairs) + ')'
        
        return text 