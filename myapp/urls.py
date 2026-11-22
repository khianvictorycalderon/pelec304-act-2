from django.urls import path

from . import views

urlpatterns = [
    path("", views.root, name="root"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("add/", views.add_student, name="add_student"),
    path("add/done/", views.add_student_done, name="add_student_done"),
    path("students/", views.students, name="students"),
    path("students/<int:pk>/", views.students, name="student_detail"),
]
