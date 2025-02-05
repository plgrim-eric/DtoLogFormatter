# DTO Log Formatter

Tomcat 로그 중 DTO 값이 있는 컬럼만 추출하여 보여주는 Sublime Text 패키지입니다.

## 기능
- DTO 로그에서 값이 있는 컬럼만 추출
- 드래그로 선택된 텍스트 또는 현재 커서가 있는 줄 처리
- 간단한 명령어로 실행 (Ctrl+Shift+P -> "DtoLogFormatter")

## 설치
1. Sublime Text 설치 폴더의 \Data\Packages 로 이동합니다.
2. 패키지 폴더(DtoLogFormatter)를 생성합니다.
3. 패키지 폴더 내에 파일을 복사합니다.

** Package Control 사용 시 **
- Preferences -> Package Settings -> Package Control -> Settings - User 에 아래 내용 추가
	"installed_packages": [
        // 기존 패키지 목록
        ...
        "DtoLogFormatter"
	],

4. Sublime Text 재시작

## 사용 방법
1. 텍스트 선택 (보통 한줄로 찍히므로 선택 없으면 현재 줄 전체 처리)
2. Ctrl+Shift+P 로 명령어 팔레트 열기
3. "dtologformatter" 입력 

## 예시
AbcDto(a=1, b=, c=3, n=, x=이름, y=)

결과: AbcDto(a=1, c=3, x=이름)
