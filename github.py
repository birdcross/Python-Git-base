import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont
import json
import os


DATA_FILE = "prompts.json"

# 현재 즐겨찾기 목록을 보고 있는지 여부
showing_favorites = False


# =========================================================
# JSON 데이터 불러오기
# =========================================================
def load_prompts():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        messagebox.showerror(
            "오류",
            "prompts.json 파일을 불러오는 중 오류가 발생했습니다."
        )
        return []


# =========================================================
# JSON 데이터 저장
# =========================================================
def save_prompts():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(
            prompts,
            file,
            ensure_ascii=False,
            indent=4
        )


# =========================================================
# 목록 새로고침
# =========================================================
def refresh_list(data=None):
    tree.delete(*tree.get_children())

    target = prompts if data is None else data

    for prompt in target:
        favorite = "⭐" if prompt["favorite"] else "☆"

        # 실제 prompts 리스트의 위치를 iid로 사용
        index = prompts.index(prompt)

        tree.insert(
            "",
            "end",
            iid=str(index),
            values=(
                index + 1,
                prompt["category"],
                prompt["title"],
                favorite
            )
        )


# =========================================================
# 검색
# =========================================================
def search_prompt():
    global showing_favorites

    keyword = search_var.get().strip().lower()

    # 검색하면 즐겨찾기 전용 화면 해제
    showing_favorites = False
    favorite_button.config(text="⭐ 즐겨찾기 목록")

    if not keyword:
        refresh_list()
        return

    result = []

    for prompt in prompts:
        if (
            keyword in prompt["title"].lower()
            or keyword in prompt["content"].lower()
        ):
            result.append(prompt)

    refresh_list(result)


# =========================================================
# 카테고리 필터
# =========================================================
def filter_category(event=None):
    global showing_favorites

    showing_favorites = False
    favorite_button.config(text="⭐ 즐겨찾기 목록")

    category = category_var.get()

    if category == "전체":
        refresh_list()
        return

    result = [
        prompt
        for prompt in prompts
        if prompt["category"] == category
    ]

    refresh_list(result)


# =========================================================
# 즐겨찾기 목록 / 전체 목록 토글
# =========================================================
def toggle_favorites():
    global showing_favorites

    if showing_favorites:
        # 즐겨찾기 목록 → 전체 목록
        showing_favorites = False

        favorite_button.config(
            text="⭐ 즐겨찾기 목록"
        )

        category_var.set("전체")
        refresh_list()

    else:
        # 전체 목록 → 즐겨찾기 목록
        showing_favorites = True

        favorite_button.config(
            text="☆ 즐겨찾기 목록 해제"
        )

        result = [
            prompt
            for prompt in prompts
            if prompt["favorite"]
        ]

        refresh_list(result)


# =========================================================
# 즐겨찾기 추가 / 해제
# =========================================================
def toggle_favorite(event):
    selected = tree.identify_row(event.y)

    if not selected:
        return

    column = tree.identify_column(event.x)

    # 즐겨찾기 열(#4)을 클릭했을 때만 실행
    if column == "#4":

        index = int(selected)

        # 즐겨찾기 상태 반전
        prompts[index]["favorite"] = not prompts[index]["favorite"]

        # JSON 저장
        save_prompts()

        # 메시지 출력
        if prompts[index]["favorite"]:

            messagebox.showinfo(
                "즐겨찾기",
                f"'{prompts[index]['title']}'\n\n"
                "즐겨찾기에 추가되었습니다."
            )

        else:

            messagebox.showinfo(
                "즐겨찾기",
                f"'{prompts[index]['title']}'\n\n"
                "즐겨찾기가 해제되었습니다."
            )

        # 현재 즐겨찾기 목록을 보고 있다면
        if showing_favorites:

            result = [
                prompt
                for prompt in prompts
                if prompt["favorite"]
            ]

            refresh_list(result)

        else:
            # 일반 목록
            refresh_list()


# =========================================================
# 상세 보기
# =========================================================
def show_detail(event=None):
    selected = tree.selection()

    if not selected:
        return

    index = int(selected[0])

    prompt = prompts[index]

    favorite_text = "⭐ 즐겨찾기" if prompt["favorite"] else "☆ 즐겨찾기 아님"

    messagebox.showinfo(
        prompt["title"],
        f"카테고리 : {prompt['category']}\n\n"
        f"즐겨찾기 : {favorite_text}\n\n"
        f"────────────────────────\n"
        f"프롬프트 내용\n"
        f"────────────────────────\n\n"
        f"{prompt['content']}"
    )


# =========================================================
# 메인 프로그램 창 생성
# =========================================================
root = tk.Tk()

root.title("나만의 프롬프트 관리")
root.geometry("950x650")
root.minsize(850, 550)


# =========================================================
# 전체 기본 폰트 설정
# 반드시 root 생성 후 실행해야 함
# =========================================================
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(
    family="맑은 고딕",
    size=11
)

text_font = tkFont.nametofont("TkTextFont")
text_font.configure(
    family="맑은 고딕",
    size=11
)

fixed_font = tkFont.nametofont("TkFixedFont")
fixed_font.configure(
    family="맑은 고딕",
    size=11
)


# =========================================================
# Treeview 스타일
# =========================================================
style = ttk.Style()

style.configure(
    "Treeview",
    font=("맑은 고딕", 11),
    rowheight=35
)

style.configure(
    "Treeview.Heading",
    font=("맑은 고딕", 11, "bold")
)


# =========================================================
# JSON 데이터 불러오기
# =========================================================
prompts = load_prompts()


# =========================================================
# 제목
# =========================================================
title = tk.Label(
    root,
    text="나만의 프롬프트 관리",
    font=("맑은 고딕", 22, "bold")
)

title.pack(pady=(20, 15))


# =========================================================
# 검색 영역
# =========================================================
search_frame = tk.Frame(root)
search_frame.pack(pady=5)

search_var = tk.StringVar()

search_entry = tk.Entry(
    search_frame,
    textvariable=search_var,
    width=42,
    font=("맑은 고딕", 12)
)

search_entry.pack(
    side="left",
    padx=5,
    ipady=4
)

search_button = tk.Button(
    search_frame,
    text="🔍 검색",
    command=search_prompt,
    font=("맑은 고딕", 11),
    padx=12,
    pady=4
)

search_button.pack(
    side="left",
    padx=5
)

# Enter 키로 검색
search_entry.bind(
    "<Return>",
    lambda event: search_prompt()
)


# =========================================================
# 카테고리 / 즐겨찾기 영역
# =========================================================
option_frame = tk.Frame(root)
option_frame.pack(pady=10)

category_label = tk.Label(
    option_frame,
    text="카테고리",
    font=("맑은 고딕", 11, "bold")
)

category_label.pack(
    side="left",
    padx=(0, 5)
)

category_var = tk.StringVar(value="전체")

category_combo = ttk.Combobox(
    option_frame,
    textvariable=category_var,
    state="readonly",
    font=("맑은 고딕", 11),
    width=15,
    values=[
        "전체",
        "텍스트 생성",
        "이미지 생성",
        "영상 생성",
        "페르소나",
        "자동화",
        "기타"
    ]
)

category_combo.pack(
    side="left",
    padx=10,
    ipady=3
)

category_combo.bind(
    "<<ComboboxSelected>>",
    filter_category
)


favorite_button = tk.Button(
    option_frame,
    text="⭐ 즐겨찾기 목록",
    command=toggle_favorites,
    font=("맑은 고딕", 11),
    padx=12,
    pady=4
)

favorite_button.pack(
    side="left",
    padx=10
)


# =========================================================
# 사용 안내
# =========================================================
guide_label = tk.Label(
    root,
    text="※ 제목을 더블클릭하면 상세 내용을 볼 수 있으며, ☆/⭐를 클릭하면 즐겨찾기가 변경됩니다.",
    font=("맑은 고딕", 10),
    fg="#555555"
)

guide_label.pack(
    pady=(5, 0)
)


# =========================================================
# 게시판 영역
# =========================================================
tree_frame = tk.Frame(root)
tree_frame.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=10
)


columns = (
    "번호",
    "카테고리",
    "제목",
    "즐겨찾기"
)

tree = ttk.Treeview(
    tree_frame,
    columns=columns,
    show="headings",
    height=15
)


# 헤더
tree.heading(
    "번호",
    text="번호"
)

tree.heading(
    "카테고리",
    text="카테고리"
)

tree.heading(
    "제목",
    text="프롬프트 제목"
)

tree.heading(
    "즐겨찾기",
    text="즐겨찾기"
)


# 컬럼 크기
tree.column(
    "번호",
    width=70,
    anchor="center",
    stretch=False
)

tree.column(
    "카테고리",
    width=150,
    anchor="center",
    stretch=False
)

tree.column(
    "제목",
    width=520,
    anchor="w"
)

tree.column(
    "즐겨찾기",
    width=110,
    anchor="center",
    stretch=False
)


# =========================================================
# 스크롤바
# =========================================================
scrollbar = ttk.Scrollbar(
    tree_frame,
    orient="vertical",
    command=tree.yview
)

tree.configure(
    yscrollcommand=scrollbar.set
)

tree.pack(
    side="left",
    fill="both",
    expand=True
)

scrollbar.pack(
    side="right",
    fill="y"
)


# =========================================================
# 이벤트
# =========================================================

# 별 클릭
tree.bind(
    "<Button-1>",
    toggle_favorite
)

# 행 더블클릭 → 상세보기
tree.bind(
    "<Double-1>",
    show_detail
)


# =========================================================
# 처음 목록 표시
# =========================================================
refresh_list()


# =========================================================
# 프로그램 실행
# =========================================================
root.mainloop()