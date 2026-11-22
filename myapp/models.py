from datetime import date

from django.db import models


class Section(models.Model):
    name = models.CharField(max_length=50)
    program = models.CharField(max_length=100)
    year_level = models.CharField(max_length=30)
    school_year = models.CharField(max_length=9, default="2026-2027")
    adviser = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["program", "year_level", "name"]
        unique_together = ("name", "school_year")

    def __str__(self):
        return f"{self.name} · {self.school_year}"


class Student(models.Model):
    class Sex(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"

    class Status(models.TextChoices):
        ENROLLED = "enrolled", "Enrolled"
        PENDING = "pending", "Pending"
        DROPPED = "dropped", "Dropped"

    # Enrollment
    student_no = models.CharField("Student No.", max_length=20, unique=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name="students")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    date_enrolled = models.DateField(null=True, blank=True)

    # Personal info
    first_name = models.CharField(max_length=60)
    middle_name = models.CharField(max_length=60, blank=True)
    last_name = models.CharField(max_length=60)
    sex = models.CharField(max_length=1, choices=Sex.choices)
    birth_date = models.DateField()
    birth_place = models.CharField(max_length=120, blank=True)
    nationality = models.CharField(max_length=60, default="Filipino")
    religion = models.CharField(max_length=60, blank=True)

    # Contact info
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)

    # Family / guardian
    father_name = models.CharField(max_length=120, blank=True)
    mother_name = models.CharField(max_length=120, blank=True)
    guardian_name = models.CharField(max_length=120, blank=True)
    guardian_relationship = models.CharField(max_length=60, blank=True)
    guardian_phone = models.CharField(max_length=30, blank=True)
    guardian_occupation = models.CharField(max_length=100, blank=True)

    # Background / academic history
    previous_school = models.CharField(max_length=150, blank=True)
    previous_school_address = models.CharField(max_length=255, blank=True)
    last_level_completed = models.CharField(max_length=60, blank=True)
    general_average = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    honors = models.CharField(max_length=150, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f"{self.last_name}, {self.first_name} {self.middle_name}".strip()

    @property
    def display_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def initials(self):
        return (self.first_name[:1] + self.last_name[:1]).upper()

    @property
    def age(self):
        today = date.today()
        b = self.birth_date
        return today.year - b.year - ((today.month, today.day) < (b.month, b.day))
