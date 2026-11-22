from django import forms

from .models import Student

SECTIONS = [
    ("Personal Information", ["first_name", "middle_name", "last_name", "sex", "birth_date", "birth_place", "nationality", "religion"]),
    ("Contact Information", ["email", "phone", "address"]),
    ("Family & Guardian", ["father_name", "mother_name", "guardian_name", "guardian_relationship", "guardian_phone", "guardian_occupation"]),
    ("Background Information", ["previous_school", "previous_school_address", "last_level_completed", "general_average", "honors"]),
    ("Enrollment", ["section"]),
]


class StudentForm(forms.ModelForm):
    # Honeypot: real people never see or fill this; bots usually do.
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))

    class Meta:
        model = Student
        fields = [f for _, names in SECTIONS for f in names]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "email": forms.EmailInput(),
            "general_average": forms.NumberInput(attrs={"step": "0.01", "min": "0", "max": "100"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["section"].required = False
        self.fields["section"].empty_label = "Not sure yet"

    def clean_birth_date(self):
        from datetime import date
        d = self.cleaned_data["birth_date"]
        if d > date.today():
            raise forms.ValidationError("Birth date can't be in the future.")
        return d

    def clean_general_average(self):
        v = self.cleaned_data.get("general_average")
        if v is not None and not (0 <= v <= 100):
            raise forms.ValidationError("Enter a value between 0 and 100.")
        return v

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("website"):
            raise forms.ValidationError("Submission rejected.")
        return cleaned

    def visible_sections(self):
        return [(title, [self[n] for n in names]) for title, names in SECTIONS]
