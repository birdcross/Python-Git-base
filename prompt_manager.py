import json
import os
import re

DATA_FILE = "prompts.json"
EXPORT_FOLDER = "export_markdown"

CATEGORIES = [
    "텍스트 생성",
    "이미지 생성",
    "영상 생성",
    "페르소나",
    "자동화",
    "기타"
]

DEFAULT_PROMPTS = [
    {
        "title": "블로그 글 작성 도우미",
        "content": "당신은 10년 경력의 전문 블로거입니다. 주어진 주제에 대해 SEO에 최적화된 블로그 글을 작성해주세요. 서론, 본론, 결론 구조를 갖추고 독자의 관심을 끄는 제목을 3개 제안해주세요.",
        "category": "텍스트 생성",
        "favorite": True,
        "views": 0
    },
    {
        "title": "제품 썸네일 생성",
        "content": "다음 제품의 특징이 잘 드러나는 매력적인 썸네일 이미지를 생성해주세요. 제품을 중앙에 배치하고 깔끔한 상업 광고 스타일로 표현해주세요.",
        "category": "이미지 생성",
        "favorite": False,
        "views": 0
    },
    {
        "title": "IT 컨설턴트 페르소나",
        "content": "당신은 10년 경력의 IT 컨설턴트입니다. 사용자의 문제를 분석하고 원인, 해결방안, 기대효과 순서로 전문적으로 답변해주세요.",
        "category": "페르소나",
        "favorite": False,
        "views": 0
    },
    {
        "title": "뉴스 요약 프롬프트",
        "content": "다음 뉴스 내용을 핵심 사실, 주요 인물, 핵심 이슈, 한 줄 요약으로 정리해주세요.",
        "category": "자동화",
        "favorite": True,
        "views": 0
    },
    {
        "title": "광고 스크립트 작성",
        "content": "제품의 핵심 장점을 강조하는 10초 분량의 광고 영상 스크립트를 작성해주세요. 도입, 제품 등장, 핵심 메시지, 엔딩 순서로 구성해주세요.",
        "category": "영상 생성",
        "favorite": False,
        "views": 0
    }
]


# =========================================================
# 데이터 저장 / 불러오기
# =========================================================

def create_default_data():
    return [prompt.copy() for prompt in DEFAULT_PROMPTS]


def load_prompts():
    if not os.path.exists(DATA_FILE):
        return create_default_data()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        for prompt in data:
            prompt.setdefault("favorite", False)
            prompt.setdefault("views", 0)

        return data

    except (json.JSONDecodeError, OSError):
        print("[WARNING] prompts.json 파일을 읽을 수 없어 기본 데이터로 시작합니다.")
        return create_default_data()


def save_prompts(prompts):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(prompts, file, ensure_ascii=False, indent=4)
    except OSError:
        print("[ERROR] prompts.json 파일 저장 중 오류가 발생했습니다.")


# =========================================================
# 공통 함수
# =========================================================

def print_line():
    print("-" * 60)


def input_not_empty(message):
    while True:
        value = input(message).strip()

        if value:
            return value

        print("입력값이 비어있습니다. 다시 입력해주세요.")


def show_menu():
    print()
    print("=" * 60)
    print("              나만의 프롬프트 관리")
    print("=" * 60)
    print("1. 프롬프트 추가")
    print("2. 프롬프트 목록")
    print("3. 카테고리별 조회")
    print("4. 프롬프트 검색")
    print("5. 프롬프트 상세 보기")
    print("6. 즐겨찾기 관리")
    print("7. 즐겨찾기 목록")
    print("8. 프롬프트 수정")
    print("9. 프롬프트 삭제")
    print("10. 조회수 TOP 목록")
    print("11. Markdown 내보내기")
    print("0. 종료")
    print("=" * 60)


def print_prompt_item(index, prompt):
    star = " ⭐" if prompt.get("favorite", False) else ""

    print(
        f"{index}. "
        f"[{prompt['category']}] "
        f"{prompt['title']}{star} "
        f"(조회수: {prompt.get('views', 0)})"
    )


# =========================================================
# 1. 프롬프트 추가
# =========================================================

def add_prompt(prompts):
    print()
    print("=== 프롬프트 추가 ===")

    title = input_not_empty("제목: ")
    content = input_not_empty("내용: ")

    print()
    print("카테고리 선택")

    for i, category in enumerate(CATEGORIES, start=1):
        print(f"{i}) {category}")

    print(f"{len(CATEGORIES) + 1}) 직접 입력")

    while True:
        choice = input("선택: ").strip()

        if choice.isdigit():
            choice_num = int(choice)

            if 1 <= choice_num <= len(CATEGORIES):
                category = CATEGORIES[choice_num - 1]
                break

            if choice_num == len(CATEGORIES) + 1:
                category = input_not_empty("카테고리 직접 입력: ")
                break

        print("올바른 번호를 입력해주세요.")

    new_prompt = {
        "title": title,
        "content": content,
        "category": category,
        "favorite": False,
        "views": 0
    }

    prompts.append(new_prompt)
    save_prompts(prompts)

    print()
    print("프롬프트가 추가되었습니다!")


# =========================================================
# 2. 프롬프트 목록
# =========================================================

def show_list(prompts):
    print()
    print("=== 프롬프트 목록 ===")

    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return

    for index, prompt in enumerate(prompts, start=1):
        print_prompt_item(index, prompt)

    print()
    print(f"총 {len(prompts)}개의 프롬프트")


# =========================================================
# 3. 카테고리별 조회
# =========================================================

def show_by_category(prompts):
    print()
    print("=== 카테고리별 조회 ===")

    for i, category in enumerate(CATEGORIES, start=1):
        print(f"{i}) {category}")

    while True:
        choice = input("선택: ").strip()

        if choice.isdigit() and 1 <= int(choice) <= len(CATEGORIES):
            category = CATEGORIES[int(choice) - 1]
            break

        print("올바른 번호를 입력해주세요.")

    result = [
        (index, prompt)
        for index, prompt in enumerate(prompts, start=1)
        if prompt["category"] == category
    ]

    print()
    print(f"[{category}] 카테고리 프롬프트:")

    if not result:
        print("해당 카테고리에 등록된 프롬프트가 없습니다.")
        return

    for index, prompt in result:
        print_prompt_item(index, prompt)

    print()
    print(f"총 {len(result)}개의 프롬프트")


# =========================================================
# 4. 프롬프트 검색
# =========================================================

def search_prompt(prompts):
    print()
    print("=== 프롬프트 검색 ===")

    keyword = input_not_empty("검색어: ").lower()

    result = [
        (index, prompt)
        for index, prompt in enumerate(prompts, start=1)
        if (
            keyword in prompt["title"].lower()
            or keyword in prompt["content"].lower()
        )
    ]

    print()
    print("검색 결과:")

    if not result:
        print("검색 결과가 없습니다.")
        return

    for index, prompt in result:
        print_prompt_item(index, prompt)

    print()
    print(f"{len(result)}개의 프롬프트를 찾았습니다.")


# =========================================================
# 5. 프롬프트 상세 보기
# =========================================================

def show_detail(prompts):
    print()
    print("=== 프롬프트 상세 보기 ===")

    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return

    number = input("번호 입력: ").strip()

    if not number.isdigit():
        print("잘못된 번호입니다.")
        return

    index = int(number) - 1

    if index < 0 or index >= len(prompts):
        print("잘못된 번호입니다.")
        return

    prompt = prompts[index]

    # 보너스: 상세 보기 시 조회수 증가
    prompt["views"] = prompt.get("views", 0) + 1
    save_prompts(prompts)

    print()
    print_line()
    print(f"제목: {prompt['title']}")
    print(f"카테고리: {prompt['category']}")
    print(
        "즐겨찾기:",
        "⭐" if prompt.get("favorite", False) else "☆"
    )
    print(f"조회수: {prompt['views']}회")
    print_line()
    print("내용:")
    print(prompt["content"])
    print_line()


# =========================================================
# 6. 즐겨찾기 관리
# =========================================================

def manage_favorite(prompts):
    print()
    print("=== 즐겨찾기 관리 ===")

    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return

    show_list(prompts)

    number = input("프롬프트 번호 입력: ").strip()

    if not number.isdigit():
        print("잘못된 번호입니다.")
        return

    index = int(number) - 1

    if index < 0 or index >= len(prompts):
        print("잘못된 번호입니다.")
        return

    prompt = prompts[index]

    prompt["favorite"] = not prompt.get("favorite", False)

    save_prompts(prompts)

    if prompt["favorite"]:
        print(f"'{prompt['title']}' 프롬프트를 즐겨찾기에 추가했습니다!")
    else:
        print(f"'{prompt['title']}' 프롬프트의 즐겨찾기를 해제했습니다!")


# =========================================================
# 7. 즐겨찾기 목록
# =========================================================

def show_favorites(prompts):
    print()
    print("=== 즐겨찾기 목록 ===")

    result = [
        (index, prompt)
        for index, prompt in enumerate(prompts, start=1)
        if prompt.get("favorite", False)
    ]

    if not result:
        print("즐겨찾기된 프롬프트가 없습니다.")
        return

    for index, prompt in result:
        print_prompt_item(index, prompt)

    print()
    print(f"총 {len(result)}개의 즐겨찾기")


# =========================================================
# 8. 프롬프트 수정
# =========================================================

def edit_prompt(prompts):
    print()
    print("=== 프롬프트 수정 ===")

    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return

    show_list(prompts)

    number = input("수정할 프롬프트 번호: ").strip()

    if not number.isdigit():
        print("잘못된 번호입니다.")
        return

    index = int(number) - 1

    if index < 0 or index >= len(prompts):
        print("잘못된 번호입니다.")
        return

    prompt = prompts[index]

    print()
    print("수정하지 않을 항목은 Enter를 누르세요.")

    title = input(f"제목 [{prompt['title']}]: ").strip()
    content = input(f"내용 [{prompt['content']}]: ").strip()
    category = input(f"카테고리 [{prompt['category']}]: ").strip()

    if title:
        prompt["title"] = title

    if content:
        prompt["content"] = content

    if category:
        prompt["category"] = category

    save_prompts(prompts)

    print("프롬프트가 수정되었습니다.")


# =========================================================
# 9. 프롬프트 삭제
# =========================================================

def delete_prompt(prompts):
    print()
    print("=== 프롬프트 삭제 ===")

    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return

    show_list(prompts)

    number = input("삭제할 프롬프트 번호: ").strip()

    if not number.isdigit():
        print("잘못된 번호입니다.")
        return

    index = int(number) - 1

    if index < 0 or index >= len(prompts):
        print("잘못된 번호입니다.")
        return

    prompt = prompts[index]

    confirm = input(
        f"'{prompt['title']}' 프롬프트를 정말 삭제하시겠습니까? (y/n): "
    ).strip().lower()

    if confirm != "y":
        print("삭제를 취소했습니다.")
        return

    del prompts[index]

    save_prompts(prompts)

    print("프롬프트가 삭제되었습니다.")


# =========================================================
# 10. 조회수 TOP 목록
# =========================================================

def show_top(prompts):
    print()
    print("=== 조회수 TOP 목록 ===")

    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return

    sorted_prompts = sorted(
        enumerate(prompts, start=1),
        key=lambda item: item[1].get("views", 0),
        reverse=True
    )

    for rank, (original_index, prompt) in enumerate(
        sorted_prompts,
        start=1
    ):
        star = " ⭐" if prompt.get("favorite", False) else ""

        print(
            f"{rank}위. "
            f"[{prompt['category']}] "
            f"{prompt['title']}{star} "
            f"- 조회수 {prompt.get('views', 0)}회 "
            f"(원본 번호: {original_index})"
        )


# =========================================================
# 11. Markdown 내보내기
# =========================================================

def export_markdown(prompts):
    print()
    print("=== Markdown 내보내기 ===")

    if not prompts:
        print("내보낼 프롬프트가 없습니다.")
        return

    os.makedirs(EXPORT_FOLDER, exist_ok=True)

    categories = sorted(
        set(prompt["category"] for prompt in prompts)
    )

    file_count = 0

    for category in categories:
        safe_name = re.sub(r'[\\/:*?"<>|]', "_", category)

        file_path = os.path.join(
            EXPORT_FOLDER,
            f"{safe_name}.md"
        )

        category_prompts = [
            prompt
            for prompt in prompts
            if prompt["category"] == category
        ]

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(f"# {category} 프롬프트\n\n")
            file.write(
                f"총 {len(category_prompts)}개의 프롬프트\n\n"
            )

            for index, prompt in enumerate(
                category_prompts,
                start=1
            ):
                favorite = (
                    "⭐"
                    if prompt.get("favorite", False)
                    else "☆"
                )

                file.write(
                    f"## {index}. {prompt['title']}\n\n"
                )
                file.write(
                    f"- 카테고리: {prompt['category']}\n"
                )
                file.write(
                    f"- 즐겨찾기: {favorite}\n"
                )
                file.write(
                    f"- 조회수: {prompt.get('views', 0)}회\n\n"
                )
                file.write("### 프롬프트 내용\n\n")
                file.write(f"{prompt['content']}\n\n")
                file.write("---\n\n")

        file_count += 1

    print(
        f"카테고리별 Markdown 파일 "
        f"{file_count}개를 생성했습니다."
    )
    print(f"저장 폴더: {EXPORT_FOLDER}")


# =========================================================
# 메인 프로그램
# =========================================================

def main():
    prompts = load_prompts()

    while True:
        show_menu()

        choice = input("선택: ").strip()

        if choice == "1":
            add_prompt(prompts)

        elif choice == "2":
            show_list(prompts)

        elif choice == "3":
            show_by_category(prompts)

        elif choice == "4":
            search_prompt(prompts)

        elif choice == "5":
            show_detail(prompts)

        elif choice == "6":
            manage_favorite(prompts)

        elif choice == "7":
            show_favorites(prompts)

        elif choice == "8":
            edit_prompt(prompts)

        elif choice == "9":
            delete_prompt(prompts)

        elif choice == "10":
            show_top(prompts)

        elif choice == "11":
            export_markdown(prompts)

        elif choice == "0":
            print()
            print("프로그램을 종료합니다.")
            break

        else:
            print()
            print("잘못된 번호입니다. 다시 선택해주세요.")

        print()
        input("Enter 키를 누르면 메뉴로 돌아갑니다...")


if __name__ == "__main__":
    main()
