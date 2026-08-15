import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont

import json
import os
import re


# =========================================================
# 기본 설정
# =========================================================

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

# 현재 화면 상태
# all / search / category / favorites / top
current_mode = "all"


# =========================================================
# JSON 데이터 불러오기
# =========================================================

def load_prompts():

    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        # 기존 JSON에 views가 없어도 자동으로 0 추가
        for prompt in data:
            if "views" not in prompt:
                prompt["views"] = 0

            if "favorite" not in prompt:
                prompt["favorite"] = False

        return data

    except (json.JSONDecodeError, OSError):
        messagebox.showerror(
            "오류",
            "prompts.json 파일을 불러오는 중 오류가 발생했습니다."
        )

        return []


# =========================================================
# JSON 저장
# =========================================================

def save_prompts():

    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(
                prompts,
                file,
                ensure_ascii=False,
                indent=4
            )

    except OSError:
        messagebox.showerror(
            "저장 오류",
            "JSON 파일 저장 중 오류가 발생했습니다."
        )


# =========================================================
# 화면 모드 버튼 초기화
# =========================================================

def reset_view_buttons():

    favorite_button.config(
        text="⭐ 즐겨찾기 목록"
    )

    top_button.config(
        text="🔥 조회수 TOP"
    )


# =========================================================
# 목록 출력
# =========================================================

def refresh_list(indices=None):

    tree.delete(*tree.get_children())

    if indices is None:
        indices = list(range(len(prompts)))

    for index in indices:

        prompt = prompts[index]

        favorite = (
            "⭐"
            if prompt.get("favorite", False)
            else "☆"
        )

        views = prompt.get("views", 0)

        tree.insert(
            "",
            "end",

            # 실제 prompts 배열 index 저장
            iid=str(index),

            values=(
                index + 1,
                prompt["category"],
                prompt["title"],
                favorite,
                views
            )
        )

    status_var.set(
        f"현재 {len(indices)}개의 프롬프트가 표시되고 있습니다."
    )


# =========================================================
# 현재 화면 새로고침
# =========================================================

def refresh_current_view():

    if current_mode == "favorites":

        indices = [
            i
            for i, prompt in enumerate(prompts)
            if prompt.get("favorite", False)
        ]

        refresh_list(indices)


    elif current_mode == "top":

        indices = list(range(len(prompts)))

        indices.sort(
            key=lambda i: prompts[i].get("views", 0),
            reverse=True
        )

        refresh_list(indices)


    elif current_mode == "category":

        category = category_var.get()

        if category == "전체":

            refresh_list()

        else:

            indices = [
                i
                for i, prompt in enumerate(prompts)
                if prompt["category"] == category
            ]

            refresh_list(indices)


    elif current_mode == "search":

        keyword = search_var.get().strip().lower()

        indices = [
            i
            for i, prompt in enumerate(prompts)
            if (
                keyword in prompt["title"].lower()
                or keyword in prompt["content"].lower()
            )
        ]

        refresh_list(indices)


    else:

        refresh_list()


# =========================================================
# 전체 목록
# =========================================================

def show_all():

    global current_mode

    current_mode = "all"

    category_var.set("전체")
    search_var.set("")

    reset_view_buttons()

    refresh_list()


# =========================================================
# 검색
# =========================================================

def search_prompt():

    global current_mode

    keyword = search_var.get().strip().lower()

    category_var.set("전체")

    reset_view_buttons()

    if not keyword:

        current_mode = "all"
        refresh_list()
        return

    current_mode = "search"

    refresh_current_view()


# =========================================================
# 카테고리별 조회
# =========================================================

def filter_category(event=None):

    global current_mode

    search_var.set("")

    reset_view_buttons()

    category = category_var.get()

    if category == "전체":
        current_mode = "all"
    else:
        current_mode = "category"

    refresh_current_view()


# =========================================================
# 즐겨찾기 목록 토글
# =========================================================

def toggle_favorites():

    global current_mode

    search_var.set("")
    category_var.set("전체")

    if current_mode == "favorites":

        current_mode = "all"

        favorite_button.config(
            text="⭐ 즐겨찾기 목록"
        )

        refresh_list()

    else:

        current_mode = "favorites"

        favorite_button.config(
            text="📋 전체 목록"
        )

        top_button.config(
            text="🔥 조회수 TOP"
        )

        refresh_current_view()


# =========================================================
# 조회수 TOP 목록
# =========================================================

def toggle_top():

    global current_mode

    search_var.set("")
    category_var.set("전체")

    if current_mode == "top":

        current_mode = "all"

        top_button.config(
            text="🔥 조회수 TOP"
        )

        refresh_list()

    else:

        current_mode = "top"

        top_button.config(
            text="📋 전체 목록"
        )

        favorite_button.config(
            text="⭐ 즐겨찾기 목록"
        )

        refresh_current_view()


# =========================================================
# 즐겨찾기 추가 / 해제
# =========================================================

def toggle_favorite(event):

    selected = tree.identify_row(event.y)

    if not selected:
        return

    column = tree.identify_column(event.x)

    # 4번째 열 = 즐겨찾기
    if column != "#4":
        return

    index = int(selected)

    prompts[index]["favorite"] = (
        not prompts[index].get("favorite", False)
    )

    save_prompts()

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

    refresh_current_view()


# =========================================================
# 상세 보기 + 조회수 증가
# =========================================================

def show_detail(event=None):

    selected = tree.selection()

    if not selected:

        messagebox.showwarning(
            "선택",
            "상세 보기할 프롬프트를 선택해주세요."
        )

        return

    index = int(selected[0])

    prompt = prompts[index]

    # ★ 조회수 증가
    prompt["views"] = prompt.get("views", 0) + 1

    save_prompts()

    favorite_text = (
        "⭐ 즐겨찾기"
        if prompt.get("favorite", False)
        else "☆ 즐겨찾기 아님"
    )

    messagebox.showinfo(
        prompt["title"],

        f"제목 : {prompt['title']}\n\n"

        f"카테고리 : {prompt['category']}\n\n"

        f"즐겨찾기 : {favorite_text}\n\n"

        f"조회수 : {prompt['views']}회\n\n"

        f"──────────────────────────\n"
        f"프롬프트 내용\n"
        f"──────────────────────────\n\n"

        f"{prompt['content']}"
    )

    refresh_current_view()


# =========================================================
# 프롬프트 입력 팝업
# 추가 / 수정 공용
# =========================================================

def open_prompt_form(edit_index=None):

    window = tk.Toplevel(root)

    if edit_index is None:
        window.title("새 프롬프트 추가")
    else:
        window.title("프롬프트 수정")

    window.geometry("650x540")
    window.resizable(False, False)

    window.transient(root)
    window.grab_set()


    # 제목
    tk.Label(
        window,
        text="제목",
        font=("맑은 고딕", 11, "bold")
    ).pack(
        anchor="w",
        padx=30,
        pady=(25, 5)
    )


    title_entry = tk.Entry(
        window,
        font=("맑은 고딕", 11)
    )

    title_entry.pack(
        fill="x",
        padx=30,
        ipady=5
    )


    # 카테고리
    tk.Label(
        window,
        text="카테고리",
        font=("맑은 고딕", 11, "bold")
    ).pack(
        anchor="w",
        padx=30,
        pady=(20, 5)
    )


    category_form_var = tk.StringVar()

    category_box = ttk.Combobox(
        window,
        textvariable=category_form_var,
        values=CATEGORIES,
        font=("맑은 고딕", 11)
    )

    category_box.pack(
        fill="x",
        padx=30,
        ipady=3
    )


    # 내용
    tk.Label(
        window,
        text="프롬프트 내용",
        font=("맑은 고딕", 11, "bold")
    ).pack(
        anchor="w",
        padx=30,
        pady=(20, 5)
    )


    content_text = tk.Text(
        window,
        height=12,
        font=("맑은 고딕", 11),
        wrap="word"
    )

    content_text.pack(
        fill="both",
        expand=True,
        padx=30
    )


    # 수정이라면 기존 내용 표시
    if edit_index is not None:

        prompt = prompts[edit_index]

        title_entry.insert(
            0,
            prompt["title"]
        )

        category_form_var.set(
            prompt["category"]
        )

        content_text.insert(
            "1.0",
            prompt["content"]
        )


    # 저장 함수
    def save_form():

        title = title_entry.get().strip()
        category = category_form_var.get().strip()

        content = content_text.get(
            "1.0",
            "end"
        ).strip()


        if not title:

            messagebox.showwarning(
                "입력 확인",
                "제목을 입력해주세요.",
                parent=window
            )

            return


        if not category:

            messagebox.showwarning(
                "입력 확인",
                "카테고리를 입력해주세요.",
                parent=window
            )

            return


        if not content:

            messagebox.showwarning(
                "입력 확인",
                "프롬프트 내용을 입력해주세요.",
                parent=window
            )

            return


        # 새 프롬프트
        if edit_index is None:

            prompts.append(
                {
                    "title": title,
                    "content": content,
                    "category": category,
                    "favorite": False,
                    "views": 0
                }
            )

            save_prompts()

            messagebox.showinfo(
                "등록 완료",
                "새 프롬프트가 등록되었습니다.",
                parent=window
            )


        # 기존 프롬프트 수정
        else:

            prompts[edit_index]["title"] = title
            prompts[edit_index]["content"] = content
            prompts[edit_index]["category"] = category

            save_prompts()

            messagebox.showinfo(
                "수정 완료",
                "프롬프트가 수정되었습니다.",
                parent=window
            )


        window.destroy()

        show_all()


    # 버튼 영역
    button_frame = tk.Frame(window)

    button_frame.pack(
        pady=20
    )


    tk.Button(
        button_frame,
        text="취소",
        command=window.destroy,
        font=("맑은 고딕", 11),
        width=10
    ).pack(
        side="left",
        padx=5
    )


    tk.Button(
        button_frame,
        text="저장",
        command=save_form,
        font=("맑은 고딕", 11, "bold"),
        width=10
    ).pack(
        side="left",
        padx=5
    )


# =========================================================
# 새 프롬프트
# =========================================================

def add_prompt():

    open_prompt_form()


# =========================================================
# 프롬프트 수정
# =========================================================

def edit_prompt():

    selected = tree.selection()

    if not selected:

        messagebox.showwarning(
            "선택",
            "수정할 프롬프트를 선택해주세요."
        )

        return

    index = int(selected[0])

    open_prompt_form(index)


# =========================================================
# 프롬프트 삭제
# =========================================================

def delete_prompt():

    selected = tree.selection()

    if not selected:

        messagebox.showwarning(
            "선택",
            "삭제할 프롬프트를 선택해주세요."
        )

        return

    index = int(selected[0])

    prompt = prompts[index]


    answer = messagebox.askyesno(
        "삭제 확인",
        f"'{prompt['title']}'\n\n"
        "프롬프트를 정말 삭제하시겠습니까?"
    )


    if not answer:
        return


    del prompts[index]

    save_prompts()

    messagebox.showinfo(
        "삭제 완료",
        "프롬프트가 삭제되었습니다."
    )

    show_all()


# =========================================================
# Markdown 내보내기
# =========================================================

def export_markdown():

    if not prompts:

        messagebox.showwarning(
            "내보내기",
            "내보낼 프롬프트가 없습니다."
        )

        return


    # 폴더 생성
    os.makedirs(
        EXPORT_FOLDER,
        exist_ok=True
    )


    # 현재 사용 중인 카테고리 찾기
    categories = sorted(
        set(
            prompt["category"]
            for prompt in prompts
        )
    )


    file_count = 0


    for category in categories:

        # Windows 파일명에서 사용할 수 없는 문자 제거
        safe_name = re.sub(
            r'[\\/:*?"<>|]',
            "_",
            category
        )


        file_path = os.path.join(
            EXPORT_FOLDER,
            f"{safe_name}.md"
        )


        category_prompts = [
            prompt
            for prompt in prompts
            if prompt["category"] == category
        ]


        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                f"# {category} 프롬프트\n\n"
            )

            file.write(
                f"총 {len(category_prompts)}개의 프롬프트\n\n"
            )


            for i, prompt in enumerate(
                category_prompts,
                start=1
            ):

                favorite = (
                    "⭐"
                    if prompt.get("favorite", False)
                    else "☆"
                )

                views = prompt.get(
                    "views",
                    0
                )


                file.write(
                    f"## {i}. {prompt['title']}\n\n"
                )

                file.write(
                    f"- 카테고리: {prompt['category']}\n"
                )

                file.write(
                    f"- 즐겨찾기: {favorite}\n"
                )

                file.write(
                    f"- 조회수: {views}회\n\n"
                )

                file.write(
                    "### 프롬프트\n\n"
                )

                file.write(
                    f"{prompt['content']}\n\n"
                )

                file.write(
                    "---\n\n"
                )


        file_count += 1


    messagebox.showinfo(
        "Markdown 내보내기 완료",

        f"카테고리별 Markdown 파일 생성이 완료되었습니다.\n\n"

        f"생성 파일: {file_count}개\n"

        f"저장 위치: {EXPORT_FOLDER}"
    )


# =========================================================
# 프로그램 창 생성
# =========================================================

root = tk.Tk()

root.title(
    "나만의 프롬프트 관리"
)

root.geometry(
    "1100x720"
)

root.minsize(
    950,
    650
)


# =========================================================
# 기본 폰트
# =========================================================

default_font = tkFont.nametofont(
    "TkDefaultFont"
)

default_font.configure(
    family="맑은 고딕",
    size=11
)


text_font = tkFont.nametofont(
    "TkTextFont"
)

text_font.configure(
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
    rowheight=36
)

style.configure(
    "Treeview.Heading",
    font=("맑은 고딕", 11, "bold")
)


# =========================================================
# 데이터 불러오기
# =========================================================

prompts = load_prompts()

# 기존 JSON에 views가 없었다면 저장해서 구조 업데이트
save_prompts()


# =========================================================
# 제목
# =========================================================

title = tk.Label(
    root,
    text="나만의 프롬프트 관리",
    font=("맑은 고딕", 23, "bold")
)

title.pack(
    pady=(20, 15)
)


# =========================================================
# 검색
# =========================================================

search_frame = tk.Frame(root)

search_frame.pack(
    pady=5
)


search_var = tk.StringVar()


search_entry = tk.Entry(
    search_frame,
    textvariable=search_var,
    width=45,
    font=("맑은 고딕", 12)
)

search_entry.pack(
    side="left",
    padx=5,
    ipady=5
)


search_button = tk.Button(
    search_frame,
    text="🔍 검색",
    command=search_prompt,
    font=("맑은 고딕", 11),
    padx=15,
    pady=4
)

search_button.pack(
    side="left",
    padx=5
)


search_entry.bind(
    "<Return>",
    lambda event: search_prompt()
)


# =========================================================
# 조회 조건
# =========================================================

option_frame = tk.Frame(root)

option_frame.pack(
    pady=10
)


tk.Label(
    option_frame,
    text="카테고리",
    font=("맑은 고딕", 11, "bold")
).pack(
    side="left",
    padx=(0, 5)
)


category_var = tk.StringVar(
    value="전체"
)


category_combo = ttk.Combobox(
    option_frame,
    textvariable=category_var,
    state="readonly",
    font=("맑은 고딕", 11),
    width=14,
    values=[
        "전체"
    ] + CATEGORIES
)

category_combo.pack(
    side="left",
    padx=8,
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
    padx=5
)


top_button = tk.Button(
    option_frame,
    text="🔥 조회수 TOP",
    command=toggle_top,
    font=("맑은 고딕", 11),
    padx=12,
    pady=4
)

top_button.pack(
    side="left",
    padx=5
)


all_button = tk.Button(
    option_frame,
    text="📋 전체",
    command=show_all,
    font=("맑은 고딕", 11),
    padx=12,
    pady=4
)

all_button.pack(
    side="left",
    padx=5
)


# =========================================================
# CRUD / 내보내기 버튼
# =========================================================

action_frame = tk.Frame(root)

action_frame.pack(
    pady=(0, 10)
)


add_button = tk.Button(
    action_frame,
    text="＋ 새 프롬프트",
    command=add_prompt,
    font=("맑은 고딕", 11, "bold"),
    padx=14,
    pady=5
)

add_button.pack(
    side="left",
    padx=5
)


edit_button = tk.Button(
    action_frame,
    text="✏ 수정",
    command=edit_prompt,
    font=("맑은 고딕", 11),
    padx=14,
    pady=5
)

edit_button.pack(
    side="left",
    padx=5
)


delete_button = tk.Button(
    action_frame,
    text="🗑 삭제",
    command=delete_prompt,
    font=("맑은 고딕", 11),
    padx=14,
    pady=5
)

delete_button.pack(
    side="left",
    padx=5
)


export_button = tk.Button(
    action_frame,
    text="📄 Markdown 내보내기",
    command=export_markdown,
    font=("맑은 고딕", 11),
    padx=14,
    pady=5
)

export_button.pack(
    side="left",
    padx=5
)


# =========================================================
# 안내 문구
# =========================================================

guide_label = tk.Label(
    root,
    text=(
        "※ 프롬프트를 더블클릭하면 상세 내용을 볼 수 있습니다. "
        "☆/⭐ 클릭 시 즐겨찾기가 변경됩니다."
    ),
    font=("맑은 고딕", 10),
    fg="#555555"
)

guide_label.pack(
    pady=(0, 5)
)


# =========================================================
# 게시판
# =========================================================

tree_frame = tk.Frame(root)

tree_frame.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=5
)


columns = (
    "번호",
    "카테고리",
    "제목",
    "즐겨찾기",
    "조회수"
)


tree = ttk.Treeview(
    tree_frame,
    columns=columns,
    show="headings",
    height=14
)


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

tree.heading(
    "조회수",
    text="조회수"
)


tree.column(
    "번호",
    width=65,
    anchor="center",
    stretch=False
)

tree.column(
    "카테고리",
    width=145,
    anchor="center",
    stretch=False
)

tree.column(
    "제목",
    width=560,
    anchor="w"
)

tree.column(
    "즐겨찾기",
    width=100,
    anchor="center",
    stretch=False
)

tree.column(
    "조회수",
    width=90,
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
# 상태 표시
# =========================================================

status_var = tk.StringVar()


status_label = tk.Label(
    root,
    textvariable=status_var,
    font=("맑은 고딕", 10),
    anchor="w"
)

status_label.pack(
    fill="x",
    padx=35,
    pady=(0, 15)
)


# =========================================================
# 이벤트
# =========================================================

tree.bind(
    "<Button-1>",
    toggle_favorite
)

tree.bind(
    "<Double-1>",
    show_detail
)


# =========================================================
# 첫 목록 표시
# =========================================================

refresh_list()


# =========================================================
# 실행
# =========================================================

root.mainloop()