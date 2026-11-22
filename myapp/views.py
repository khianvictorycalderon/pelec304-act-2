import hmac
from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import StudentForm
from .models import Section, Student

SESSION_KEY = "console_admin"
MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 300


def admin_required(view):
    """Redirect to the login page unless the session is signed in as admin."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.session.get(SESSION_KEY):
            return redirect(f"{reverse('login')}?next={request.get_full_path()}")
        return view(request, *args, **kwargs)
    return wrapper


def _client_ip(request):
    return request.META.get("REMOTE_ADDR", "unknown")


def _credentials_match(username, password):
    # constant-time comparison against the values from the environment
    ok_user = hmac.compare_digest(username.encode(), settings.ADMIN_DEFAULT_USERNAME.encode())
    ok_pass = hmac.compare_digest(password.encode(), settings.ADMIN_DEFAULT_PASSWORD.encode())
    return ok_user and ok_pass


def root(request):
    return render(request, "console/home.html", {"is_admin": bool(request.session.get(SESSION_KEY))})


def login_view(request):
    if request.session.get(SESSION_KEY):
        return redirect("students")

    next_url = request.POST.get("next") or request.GET.get("next") or ""
    error = None
    attempts_key = f"login-attempts:{_client_ip(request)}"

    if request.method == "POST":
        attempts = cache.get(attempts_key, 0)
        if attempts >= MAX_ATTEMPTS:
            error = "Too many failed attempts. Please try again in a few minutes."
        elif _credentials_match(request.POST.get("username", "").strip(), request.POST.get("password", "")):
            cache.delete(attempts_key)
            request.session.cycle_key()
            request.session[SESSION_KEY] = True
            if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}):
                return redirect(next_url)
            return redirect("students")
        else:
            cache.set(attempts_key, attempts + 1, LOCKOUT_SECONDS)
            error = "Invalid username or password."

    return render(request, "console/login.html", {"error": error, "next": next_url})


@require_POST
def logout_view(request):
    request.session.flush()
    return redirect("login")


@admin_required
def students(request, pk=None):
    q = request.GET.get("q", "").strip()
    section_id = request.GET.get("section", "")
    status = request.GET.get("status", "")

    qs = Student.objects.select_related("section")
    if q:
        qs = qs.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q)
            | Q(middle_name__icontains=q) | Q(student_no__icontains=q)
        )
    if section_id.isdigit():
        qs = qs.filter(section_id=section_id)
    if status in Student.Status.values:
        qs = qs.filter(status=status)

    selected = get_object_or_404(Student.objects.select_related("section"), pk=pk) if pk else None

    return render(request, "console/students.html", {
        "student_list": qs,
        "selected": selected,
        "sections": Section.objects.all(),
        "statuses": Student.Status.choices,
        "q": q,
        "section_id": section_id,
        "status": status,
        "querystring": request.GET.urlencode(),
        "total": Student.objects.count(),
    })


ADD_MAX_PER_HOUR = 10


def _next_student_no():
    prefix = str(timezone.now().year)
    last = (Student.objects.filter(student_no__startswith=f"{prefix}-")
            .order_by("-student_no").values_list("student_no", flat=True).first())
    n = int(last.split("-")[1]) + 1 if last and last.split("-")[1].isdigit() else 1
    return f"{prefix}-{n:04d}"


def add_student(request):
    """Public page: anyone (signed in or not) can submit a student."""
    key = f"add-student:{_client_ip(request)}"
    form = StudentForm(request.POST or None)
    error = None

    if request.method == "POST":
        if cache.get(key, 0) >= ADD_MAX_PER_HOUR:
            error = "Too many submissions from your network. Please try again later."
        elif form.is_valid():
            student = form.save(commit=False)
            student.status = Student.Status.PENDING  # public submissions always start as pending
            for _ in range(5):  # retry if two people grab the same number at once
                student.student_no = _next_student_no()
                try:
                    with transaction.atomic():
                        student.save()
                    break
                except IntegrityError:
                    continue
            else:
                error = "Something went wrong saving the record. Please try again."
            if not error:
                cache.set(key, cache.get(key, 0) + 1, 3600)
                request.session["added_student"] = [student.display_name, student.student_no]
                return redirect("add_student_done")

    return render(request, "console/add.html", {
        "form": form, "error": error, "is_admin": bool(request.session.get(SESSION_KEY)),
    })


def add_student_done(request):
    info = request.session.pop("added_student", None)
    if not info:
        return redirect("add_student")
    return render(request, "console/add_done.html", {
        "name": info[0], "student_no": info[1], "is_admin": bool(request.session.get(SESSION_KEY)),
    })
