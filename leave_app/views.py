import os
from functools import lru_cache

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from loaders import load_pdfs
from splitter import split_documents
from embeddings_store import create_vectorstore
from qa_chain import build_qa_chain
from employee_data import get_employee_by_id, signup_employee_excel
from auth_db import create_user, verify_user


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEAVE_PDF_PATH = os.path.join(BASE_DIR, "data", "leave.pdf")


@lru_cache(maxsize=1)
def load_chain():
    docs = load_pdfs([LEAVE_PDF_PATH])
    split_docs = split_documents(docs)
    vectorstore = create_vectorstore(split_docs)
    return build_qa_chain(vectorstore)


def _get_employee_from_session(request):
    employee_id = request.session.get("employee_id")
    if not employee_id:
        return None
    return get_employee_by_id(employee_id)


def _build_full_query(employee_data, query):
    return f"""
Employee Information:
Employee ID: {employee_data['employee_id']}
Name: {employee_data['name']}
Grade/Band: {employee_data['grade']}
PL Taken: {employee_data['PL_taken']}
CL Taken: {employee_data['CL_taken']}
SL Taken: {employee_data['SL_taken']}

User Question:
{query}
"""


def _get_chat_title(chat_messages):
    for msg in chat_messages:
        if msg.get("role") == "user":
            title = msg.get("content", "").strip()
            return title[:32] + "..." if len(title) > 32 else title
    return "New Chat"


@require_http_methods(["GET", "POST"])
def login_page(request):
    if request.method == "POST":
        employee_id = request.POST.get("employee_id", "").strip()
        password = request.POST.get("password", "").strip()

        if not employee_id or not password:
            messages.error(request, "Employee ID and password are required.")
            return redirect("login")

        if not verify_user(employee_id, password):
            messages.error(request, "Invalid Employee ID or Password.")
            return redirect("login")

        employee_data = get_employee_by_id(employee_id)
        if employee_data is None:
            messages.error(request, "Employee data not found in Excel.")
            return redirect("login")

        request.session["employee_id"] = employee_id
        request.session["chat_messages"] = []
        request.session.setdefault("chat_history", [])
        request.session.pop("opened_history_index", None)
        request.session.modified = True

        return redirect("chat")

    return render(request, "leave_app/login.html")


@require_http_methods(["GET", "POST"])
def signup_page(request):
    fetched_employee = None

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "fetch":
            fetch_id = request.POST.get("fetch_id", "").strip()
            fetched_employee = get_employee_by_id(fetch_id)

            if fetched_employee is None:
                messages.warning(
                    request,
                    "Employee not found in Excel. You can create a new signup."
                )
            else:
                messages.success(request, "Employee data fetched from Excel.")

        if action == "signup":
            employee_id = request.POST.get("employee_id", "").strip()
            password = request.POST.get("password", "").strip()
            name = request.POST.get("name", "").strip()
            grade = request.POST.get("grade", "").strip()
            joining_date = request.POST.get("joining_date", "").strip()
            pl_taken = int(request.POST.get("pl_taken") or 0)
            cl_taken = int(request.POST.get("cl_taken") or 0)
            sl_taken = int(request.POST.get("sl_taken") or 0)

            if not all([employee_id, password, name, grade]):
                messages.error(
                    request,
                    "Employee ID, password, name, and grade are required."
                )
                return redirect("signup")

            auth_success, auth_message = create_user(employee_id, password)
            if not auth_success:
                messages.error(request, auth_message)
                return redirect("signup")

            excel_success, excel_message = signup_employee_excel(
                employee_id,
                name,
                grade,
                joining_date,
                pl_taken,
                cl_taken,
                sl_taken
            )

            if not excel_success:
                messages.error(request, excel_message)
                return redirect("signup")

            messages.success(request, "Signup successful. Please login.")
            return redirect("login")

    return render(
        request,
        "leave_app/signup.html",
        {"fetched_employee": fetched_employee}
    )


@require_http_methods(["GET", "POST"])
def chat_page(request):
    employee_data = _get_employee_from_session(request)

    if employee_data is None:
        return redirect("login")

    current_chat = request.session.get("chat_messages", [])
    chat_history = request.session.get("chat_history", [])

    action = request.GET.get("action")
    history_index = request.GET.get("history")

    # NEW CHAT:
    # If current chat is normal chat, save it in history.
    # If current chat is opened from history, do not duplicate it.
    if action == "new_chat":
        opened_index = request.session.get("opened_history_index")

        if current_chat and opened_index is None:
            chat_history.insert(0, {
                "title": _get_chat_title(current_chat),
                "messages": current_chat.copy()
            })

        request.session["chat_history"] = chat_history
        request.session["chat_messages"] = []
        request.session.pop("opened_history_index", None)
        request.session.modified = True

        return redirect("chat")

    # CLEAR CHAT:
    # If current chat is normal chat -> only clear current chat.
    # If current chat is opened history chat -> remove only that chat from history also.
    if action == "clear_chat":
        opened_index = request.session.get("opened_history_index")

        if opened_index is not None:
            try:
                opened_index = int(opened_index)

                if 0 <= opened_index < len(chat_history):
                    chat_history.pop(opened_index)

                request.session["chat_history"] = chat_history

            except Exception:
                pass

        request.session["chat_messages"] = []
        request.session.pop("opened_history_index", None)
        request.session.modified = True

        return redirect("chat")

    # CLEAR ALL HISTORY
    if action == "clear_history":
        request.session["chat_history"] = []
        request.session["chat_messages"] = []
        request.session.pop("opened_history_index", None)
        request.session.modified = True

        return redirect("chat")

    # OPEN HISTORY CHAT
    if history_index is not None:
        try:
            index = int(history_index)
            selected_chat = chat_history[index]

            if isinstance(selected_chat, dict):
                request.session["chat_messages"] = selected_chat.get("messages", [])
            else:
                request.session["chat_messages"] = selected_chat

            request.session["opened_history_index"] = index
            request.session.modified = True

            return redirect("chat")

        except Exception:
            messages.error(request, "Unable to open selected chat.")
            return redirect("chat")

    # ASK QUESTION
    if request.method == "POST":
        query = request.POST.get("query", "").strip()

        if query:
            current_chat.append({
                "role": "user",
                "content": query
            })

            full_query = _build_full_query(employee_data, query)

            try:
                response = load_chain().invoke({"query": full_query})
                answer = response["result"].replace("**", "")

            except Exception as exc:
                answer = f"Error while generating answer: {exc}"

            current_chat.append({
                "role": "assistant",
                "content": answer
            })

            request.session["chat_messages"] = current_chat

            # If this chat came from history, update only that same history item
            opened_index = request.session.get("opened_history_index")
            if opened_index is not None:
                try:
                    opened_index = int(opened_index)

                    if 0 <= opened_index < len(chat_history):
                        chat_history[opened_index] = {
                            "title": _get_chat_title(current_chat),
                            "messages": current_chat.copy()
                        }

                        request.session["chat_history"] = chat_history

                except Exception:
                    pass

            request.session.modified = True

        return redirect("chat")

    return render(
        request,
        "leave_app/chat.html",
        {
            "employee": employee_data,
            "chat_messages": current_chat,
            "chat_history": chat_history,
        },
    )


def logout_page(request):
    request.session.flush()
    return redirect("login")