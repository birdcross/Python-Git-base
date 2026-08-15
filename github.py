import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

DATA_FILE = "prompts.json"


def load_prompts():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


prompts = load_prompts()


def save_prompts():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(
            prompts,
            file,
            ensure_ascii=False,
            indent=4
        )

def refresh_list(data=None):
    tree.delete(*tree.get_children())

    target = prompts if data is None else data

    for i, prompt in enumerate(target):
        favorite = "⭐" if prompt["favorite"] else "☆"

        tree.insert(
            "",
            "end",
            iid=str(prompts.index(prompt)),
            values=(
                i + 1,
                prompt["category"],
                prompt["title"],
                favorite
            )
        )


def search_prompt():
    keyword = search_var.get().strip().lower()

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


def filter_category(event=None):
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


def show_favorites():
    result = [
        prompt
        for prompt in prompts
        if prompt["favorite"]
    ]

    refresh_list(result)


def toggle_favorite(event):
    selected = tree.identify_row(event.y)

    if not selected:
        return

    column = tree.identify_column(event.x)

    # 즐겨찾기 열 클릭
    if column == "#4":
        index = int(selected)

        prompts[index]["favorite"] = not prompts[index]["favorite"]

        refresh_list()


def show_detail(event):
    selected = tree.selection()

    if not selected:
        return

    index = int(selected[0])

    prompt = prompts[index]

    messagebox.showinfo(
        prompt["title"],
        f"""
카테고리 : {prompt['category']}

즐겨찾기 : {'⭐' if prompt['favorite'] else '☆'}

프롬프트 내용

{prompt['content']}
"""
    )


root = tk.Tk()

root.title("나만의 프롬프트 관리")
root.geometry("850x550")

title = tk.Label(
    root,
    text="나만의 프롬프트 관리",
    font=("맑은 고딕", 20, "bold")
)

title.pack(pady=20)


# 검색 영역
search_frame = tk.Frame(root)
search_frame.pack(pady=5)

search_var = tk.StringVar()

search_entry = tk.Entry(
    search_frame,
    textvariable=search_var,
    width=40
)

search_entry.pack(side="left", padx=5)

search_button = tk.Button(
    search_frame,
    text="검색",
    command=search_prompt
)

search_button.pack(side="left")


# 카테고리 영역
option_frame = tk.Frame(root)
option_frame.pack(pady=10)

category_var = tk.StringVar(value="전체")

category_combo = ttk.Combobox(
    option_frame,
    textvariable=category_var,
    state="readonly",
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

category_combo.pack(side="left", padx=10)

category_combo.bind(
    "<<ComboboxSelected>>",
    filter_category
)

favorite_button = tk.Button(
    option_frame,
    text="⭐ 즐겨찾기 목록",
    command=show_favorites
)

favorite_button.pack(side="left")


# 게시판 목록
columns = (
    "번호",
    "카테고리",
    "제목",
    "즐겨찾기"
)

tree = ttk.Treeview(
    root,
    columns=columns,
    show="headings",
    height=15
)

tree.heading("번호", text="번호")
tree.heading("카테고리", text="카테고리")
tree.heading("제목", text="프롬프트 제목")
tree.heading("즐겨찾기", text="즐겨찾기")

tree.column("번호", width=60, anchor="center")
tree.column("카테고리", width=130, anchor="center")
tree.column("제목", width=450)
tree.column("즐겨찾기", width=100, anchor="center")

tree.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=10
)

tree.bind(
    "<Button-1>",
    toggle_favorite
)

tree.bind(
    "<Double-1>",
    show_detail
)

refresh_list()

root.mainloop()