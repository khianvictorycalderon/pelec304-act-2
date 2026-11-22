from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand

from myapp.models import Section, Student


class Command(BaseCommand):
    help = "Create sample sections and students for demo purposes."

    def handle(self, *args, **opts):
        a, _ = Section.objects.get_or_create(name="BSIT 3-A", school_year="2026-2027", defaults=dict(
            program="BS Information Technology", year_level="3rd Year", adviser="Prof. Maria Reyes"))
        b, _ = Section.objects.get_or_create(name="BSIT 3-B", school_year="2026-2027", defaults=dict(
            program="BS Information Technology", year_level="3rd Year", adviser="Prof. Jose Villanueva"))

        E, P, D = Student.Status.ENROLLED, Student.Status.PENDING, Student.Status.DROPPED
        rows = [
            ("2023-0001", a, E, "Angela", "Mae", "Santos", "F", date(2004, 3, 14), "Biñan, Laguna", "Catholic", "Jose Santos", "Maria Santos", "Mother", "Sta. Rosa Integrated High School", Decimal("93.40"), "With High Honors"),
            ("2023-0002", a, E, "Miguel", "Luis", "Dela Cruz", "M", date(2003, 11, 2), "Calamba, Laguna", "Catholic", "Ramon Dela Cruz", "Liza Dela Cruz", "Father", "Calamba Science High School", Decimal("90.10"), "With Honors"),
            ("2023-0003", a, E, "Kristine", "", "Bautista", "F", date(2004, 7, 21), "Manila", "Iglesia ni Cristo", "Eduardo Bautista", "Rowena Bautista", "Father", "Manila Central High", Decimal("88.75"), ""),
            ("2023-0004", a, P, "John Paul", "Reyes", "Garcia", "M", date(2004, 1, 9), "San Pedro, Laguna", "Catholic", "Paulo Garcia", "Nena Garcia", "Mother", "San Pedro National High School", Decimal("85.00"), ""),
            ("2023-0005", b, E, "Patricia", "Ann", "Mendoza", "F", date(2003, 5, 30), "Cabuyao, Laguna", "Born Again Christian", "Arnel Mendoza", "Cecilia Mendoza", "Mother", "Cabuyao Integrated School", Decimal("91.20"), "With Honors"),
            ("2023-0006", b, E, "Carlo", "James", "Ramos", "M", date(2004, 9, 18), "Biñan, Laguna", "Catholic", "Ben Ramos", "Joy Ramos", "Father", "Biñan City Science High", Decimal("94.80"), "Valedictorian"),
            ("2023-0007", b, D, "Jasmine", "", "Torres", "F", date(2003, 12, 25), "Quezon City", "Catholic", "Ricky Torres", "Amy Torres", "Mother", "QC National High School", Decimal("82.30"), ""),
            ("2023-0008", b, P, "Nathaniel", "Cruz", "Aquino", "M", date(2004, 4, 6), "Los Baños, Laguna", "Muslim", "Hassan Aquino", "Fatima Aquino", "Father", "UPLB Integrated School", Decimal("89.90"), "With Honors"),
        ]
        created = 0
        for no, sec, st, fn, mn, ln, sex, bd, bp, rel, fa, mo, gr, prev, avg, hon in rows:
            _, new = Student.objects.get_or_create(student_no=no, defaults=dict(
                section=sec, status=st, first_name=fn, middle_name=mn, last_name=ln, sex=sex,
                birth_date=bd, birth_place=bp, religion=rel, email=f"{fn.split()[0].lower()}.{ln.split()[-1].lower()}@example.com",
                phone="0917 555 01%02d" % (created + 1), address=f"Blk {created+1} Lot {created+3}, {bp.split(',')[0]}, Laguna",
                father_name=fa, mother_name=mo, guardian_name=fa if gr == "Father" else mo, guardian_relationship=gr,
                guardian_phone="0928 555 02%02d" % (created + 1), guardian_occupation="Self-employed",
                previous_school=prev, previous_school_address="Laguna, Philippines", last_level_completed="Grade 12",
                general_average=avg, honors=hon, date_enrolled=date(2026, 6, 10) if st != P else None,
                notes="Submitted all requirements." if st == E else ("Missing Form 137." if st == P else "Withdrew after first term."),
            ))
            created += new
        self.stdout.write(self.style.SUCCESS(f"Seeded {created} new student(s)."))
