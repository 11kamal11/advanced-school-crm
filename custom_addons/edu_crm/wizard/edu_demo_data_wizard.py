import random
from datetime import timedelta

from odoo import fields, models


FIRST_NAMES_M = ['Aarav', 'Vihaan', 'Reyansh', 'Arjun', 'Sai', 'Krishna', 'Ishaan', 'Rohan',
                  'Kabir', 'Aditya', 'Dev', 'Yuvraj', 'Karan', 'Rudra', 'Vivaan', 'Aryan']
FIRST_NAMES_F = ['Aanya', 'Diya', 'Myra', 'Anika', 'Ira', 'Kiara', 'Riya', 'Saanvi',
                  'Navya', 'Prisha', 'Zara', 'Aditi', 'Meera', 'Sara', 'Tara', 'Isha']
LAST_NAMES = ['Sharma', 'Verma', 'Gupta', 'Kumar', 'Singh', 'Rao', 'Nair', 'Iyer',
              'Mehta', 'Patel', 'Reddy', 'Joshi', 'Kapoor', 'Malhotra', 'Chatterjee', 'Bose']

TEACHER_FIRST = ['Asha', 'Priya', 'Neha', 'Sanjay', 'Vikram', 'Anjali', 'Ravi', 'Deepa',
                 'Manoj', 'Kavita']
SUBJECTS = [
    ('Mathematics', 'MATH', 'theory'),
    ('Science', 'SCI', 'both'),
    ('English', 'ENG', 'theory'),
    ('Social Studies', 'SOC', 'theory'),
    ('Computer Science', 'CS', 'both'),
    ('Art & Craft', 'ART', 'practical'),
    ('Physical Education', 'PE', 'practical'),
    ('Music', 'MUS', 'practical'),
]
PROGRAMS = [
    ('Primary Years', 'PRI', 'Grades 1-3, foundations that last a lifetime.',
     '<p>Our Primary Years program focuses on building strong literacy, numeracy, and social '
     'skills through a play-based, inquiry-driven curriculum.</p>'),
    ('Middle School', 'MID', 'Grades 4-6, building independence and curiosity.',
     '<p>Middle School students deepen their academic foundation while developing critical '
     'thinking, collaboration, and early specialization in subjects they love.</p>'),
    ('Senior Secondary', 'SEN', 'Grades 7-8, preparing for what comes next.',
     '<p>Our Senior Secondary program prepares students for board examinations and beyond, '
     'with dedicated subject teachers and regular assessments.</p>'),
]
ANNOUNCEMENTS = [
    ('Annual Sports Day', 'all', 'high', '<p>Join us for our Annual Sports Day on the school grounds. All families welcome!</p>'),
    ('Parent-Teacher Meeting', 'all', 'high', '<p>Parent-teacher meetings will be held this Friday. Please book your slot at the office.</p>'),
    ('Winter Break Notice', 'all', 'medium', '<p>The school will remain closed from Dec 20 to Jan 2 for winter break.</p>'),
    ('Library Week', 'students', 'low', '<p>Visit the library this week for a special reading challenge with prizes.</p>'),
    ('Fee Payment Reminder', 'all', 'medium', '<p>Quarterly fees are due by the end of this month. Please clear any pending dues.</p>'),
    ('Science Fair Submissions Open', 'students', 'medium', '<p>Submit your science fair project proposals by next Monday.</p>'),
]
LEAD_NAMES = [
    'Rakesh Malhotra', 'Sunita Bose', 'Amit Chatterjee', 'Pooja Reddy', 'Vikas Joshi',
    'Shalini Kapoor', 'Deepak Nair', 'Rina Iyer', 'Manish Patel', 'Geeta Rao',
    'Suresh Gupta', 'Nisha Singh', 'Anil Kumar', 'Preeti Verma', 'Rajesh Sharma',
]


class EduDemoDataWizard(models.TransientModel):
    _name = 'edu.demo.data.wizard'
    _description = 'Generate Sample Data'

    note = fields.Char(
        default='This will add sample teachers, classes, students, fees, exams, leads and '
                'announcements. Safe to run multiple times -- it always adds new records, '
                'it never deletes anything.',
        readonly=True,
    )

    def _rand_date(self, days_back_min, days_back_max):
        today = fields.Date.context_today(self)
        return today - timedelta(days=random.randint(days_back_min, days_back_max))

    def action_generate(self):
        self.ensure_one()
        env = self.env

        academic_year = env['edu.academic.year'].search([], limit=1)
        if not academic_year:
            academic_year = env['edu.academic.year'].create({
                'name': '2026-2027', 'date_start': '2026-06-01', 'date_end': '2027-04-30',
            })

        # --- Subjects ---
        subjects = env['edu.subject']
        for name, code, subj_type in SUBJECTS:
            existing = env['edu.subject'].search([('code', '=', code)], limit=1)
            subjects |= existing or env['edu.subject'].create({
                'name': name, 'code': code, 'subject_type': subj_type,
                'credit_hours': random.randint(2, 5),
            })

        # --- Teachers ---
        teachers = env['edu.teacher']
        for i, first in enumerate(TEACHER_FIRST):
            last = random.choice(LAST_NAMES)
            email = f'{first.lower()}.{last.lower()}@sampleschool.example.com'
            existing = env['edu.teacher'].search([('email', '=', email)], limit=1)
            if existing:
                teachers |= existing
                continue
            teacher = env['edu.teacher'].create({
                'name': f'{first} {last}',
                'email': email,
                'phone': f'9{random.randint(100000000, 999999999)}',
                'gender': random.choice(['male', 'female']),
                'qualification': random.choice(['M.Sc', 'M.A', 'B.Ed', 'M.Ed', 'Ph.D']),
                'experience_years': random.randint(2, 20),
                'specialization': random.choice(subjects.mapped('name')),
                'subject_ids': [(6, 0, random.sample(subjects.ids, k=min(2, len(subjects))))],
            })
            if i < 6:
                teacher.write({
                    'bio': f'<p>{teacher.name} has {teacher.experience_years} years of teaching '
                           f'experience and specializes in {teacher.specialization}.</p>',
                })
            teachers |= teacher

        # --- Programs ---
        programs = []
        for name, code, tagline, description in PROGRAMS:
            existing = env['edu.program'].search([('code', '=', code)], limit=1)
            program = existing or env['edu.program'].create({
                'name': name, 'code': code, 'tagline': tagline, 'description': description,
                'sequence': len(programs) * 10,
            })
            programs.append(program)

        # --- Classes (Grade 1-8) ---
        classes = env['edu.class']
        for grade in range(1, 9):
            program = programs[0] if grade <= 3 else programs[1] if grade <= 6 else programs[2]
            name = f'Grade {grade}'
            existing = env['edu.class'].search([
                ('name', '=', name), ('section', '=', 'A'), ('academic_year_id', '=', academic_year.id),
            ], limit=1)
            if existing:
                classes |= existing
                continue
            klass = env['edu.class'].create({
                'name': name, 'code': f'G{grade}A', 'section': 'A',
                'academic_year_id': academic_year.id,
                'class_teacher_id': random.choice(teachers.ids),
                'program_id': program.id,
                'subject_ids': [(6, 0, subjects.ids)],
                'capacity': 30,
            })
            classes |= klass

        # --- Students + Guardians ---
        students = env['edu.student']
        for klass in classes:
            grade_num = int(''.join(c for c in klass.code if c.isdigit()) or 5)
            age_years = grade_num + 5  # Grade 1 ~ age 6, Grade 8 ~ age 13
            for roll in range(1, random.randint(6, 10)):
                is_male = random.random() < 0.5
                first = random.choice(FIRST_NAMES_M if is_male else FIRST_NAMES_F)
                last = random.choice(LAST_NAMES)
                name = f'{first} {last}'
                if env['edu.student'].search_count([('name', '=', name), ('class_id', '=', klass.id)]):
                    continue
                guardian_first = random.choice(['Rakesh', 'Sunita', 'Amit', 'Pooja', 'Vikas', 'Shalini'])
                partner = env['res.partner'].create({
                    'name': f'{guardian_first} {last}',
                    'email': f'{guardian_first.lower()}.{last.lower()}{random.randint(1,999)}@example.com',
                    'phone': f'9{random.randint(100000000, 999999999)}',
                })
                guardian = env['edu.guardian'].create({
                    'partner_id': partner.id,
                    'relationship': random.choice(['father', 'mother', 'guardian']),
                })
                student = env['edu.student'].create({
                    'name': name,
                    'class_id': klass.id,
                    'roll_number': roll,
                    'academic_year_id': academic_year.id,
                    'gender': 'male' if is_male else 'female',
                    'date_of_birth': self._rand_date(365 * age_years - 90, 365 * age_years + 90),
                    'blood_group': random.choice(['a+', 'b+', 'o+', 'ab+']),
                    'admission_date': self._rand_date(30, 700),
                    'guardian_ids': [(4, guardian.id)],
                    'state': 'active',
                })
                students |= student

        # --- Attendance (last 10 school days per class) ---
        for klass in classes:
            for day_offset in range(1, 11):
                date_ = self._rand_date(day_offset, day_offset)
                if env['edu.attendance'].search_count([('class_id', '=', klass.id), ('date', '=', date_)]):
                    continue
                attendance = env['edu.attendance'].create({
                    'class_id': klass.id, 'date': date_, 'teacher_id': klass.class_teacher_id.id,
                    'line_ids': [
                        (0, 0, {'student_id': s.id, 'status': random.choices(
                            ['present', 'absent', 'late'], weights=[85, 10, 5])[0]})
                        for s in klass.student_ids
                    ],
                })
                attendance.action_confirm()

        # --- Exams + Results ---
        for klass in classes:
            for subject in klass.subject_ids[:2]:
                exam_name = f'{subject.name} Unit Test'
                if env['edu.exam'].search_count([('name', '=', exam_name), ('class_id', '=', klass.id)]):
                    continue
                exam = env['edu.exam'].create({
                    'name': exam_name, 'exam_type': 'unit_test', 'class_id': klass.id,
                    'subject_id': subject.id, 'academic_year_id': academic_year.id,
                    'exam_date': self._rand_date(5, 60), 'max_marks': 100, 'passing_marks': 35,
                })
                for student in klass.student_ids:
                    env['edu.exam.result'].create({
                        'exam_id': exam.id, 'student_id': student.id,
                        'marks_obtained': random.randint(20, 100),
                    })
                exam.action_complete()

        # --- Fees + Payments ---
        for student in students:
            for fee_type, amount in [('tuition', 15000.0), ('transport', 3000.0)]:
                if env['edu.fee'].search_count([('student_id', '=', student.id), ('fee_type', '=', fee_type)]):
                    continue
                fee = env['edu.fee'].create({
                    'student_id': student.id, 'fee_type': fee_type, 'amount': amount,
                    'due_date': self._rand_date(-30, 60), 'academic_year_id': academic_year.id,
                })
                roll = random.random()
                if roll < 0.6:
                    env['edu.fee.payment'].create({
                        'fee_id': fee.id, 'amount': fee.net_amount,
                        'payment_date': self._rand_date(1, 30),
                        'payment_method': random.choice(['cash', 'bank', 'online', 'upi']),
                    })
                elif roll < 0.8:
                    env['edu.fee.payment'].create({
                        'fee_id': fee.id, 'amount': round(fee.net_amount * 0.5, 2),
                        'payment_date': self._rand_date(1, 15),
                        'payment_method': random.choice(['cash', 'bank']),
                    })
        env['edu.fee']._cron_check_overdue()

        # --- Leave requests ---
        for student in random.sample(list(students), k=min(8, len(students))):
            date_from = self._rand_date(5, 40)
            leave = env['edu.leave.request'].create({
                'applicant_type': 'student', 'student_id': student.id,
                'leave_type': random.choice(['sick', 'personal', 'family']),
                'date_from': date_from, 'date_to': date_from + timedelta(days=random.randint(1, 3)),
                'reason': 'Sample leave request for demo purposes.',
            })
            outcome = random.choice(['submitted', 'approved', 'rejected'])
            leave.action_submit()
            if outcome == 'approved':
                leave.action_approve()
            elif outcome == 'rejected':
                leave.write({'rejection_reason': 'Insufficient supporting documents.'})
                leave.action_reject()

        # --- Announcements ---
        for name, audience, priority, body in ANNOUNCEMENTS:
            if env['edu.announcement'].search_count([('name', '=', name)]):
                continue
            env['edu.announcement'].create({
                'name': name, 'audience': audience, 'priority': priority, 'body': body,
                'is_portal_visible': True,
                'class_ids': [(6, 0, random.sample(classes.ids, k=2))] if audience == 'students' else False,
            })

        # --- CRM leads across every pipeline stage ---
        stages = env['edu.crm.stage'].search([], order='sequence')
        website_source = env.ref('edu_crm.utm_source_website', raise_if_not_found=False)
        for i, contact_name in enumerate(LEAD_NAMES):
            if env['edu.lead'].search_count([('contact_name', '=', contact_name)]):
                continue
            stage = stages[i % len(stages)]
            lead = env['edu.lead'].create({
                'contact_name': contact_name,
                'phone': f'9{random.randint(100000000, 999999999)}',
                'email': f'{contact_name.lower().replace(" ", ".")}@example.com',
                'student_name': f"{random.choice(FIRST_NAMES_M + FIRST_NAMES_F)} {contact_name.split()[-1]}",
                'class_applying_id': random.choice(classes.ids),
                'stage_id': stage.id,
                'priority': random.choice(['low', 'medium', 'high']),
                'is_from_website': bool(website_source) and random.random() < 0.4,
                'source_id': website_source.id if website_source else False,
            })
            if stage.name == 'Contacted':
                lead.write({'state': 'contacted'})
            elif stage.name in ('Qualified', 'Application Requested'):
                lead.write({'state': 'qualified'})
            elif stage.name == 'Converted' and not lead.applicant_id:
                lead.write({'state': 'converted'})
                env['edu.applicant'].create({
                    'lead_id': lead.id, 'student_name': lead.student_name,
                    'class_applying_id': lead.class_applying_id.id,
                    'guardian_name': lead.contact_name, 'guardian_phone': lead.phone,
                    'guardian_email': lead.email, 'state': random.choice(
                        ['submitted', 'document_verification', 'interview', 'approved']),
                })

        return {'type': 'ir.actions.client', 'tag': 'reload'}
