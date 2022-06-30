import jwt

from datetime import datetime

from django.test import TestCase, Client
from django.conf import settings

from users.models import CustomUser, Department, Hospital, Doctor, WorkingDay, WorkingTime
from appointments.models import Appointment, State, UserAppointment

class DepartmentsListTest(TestCase):
    def setUp(self):
        CustomUser.objects.create_user(
            name      = 'kevin',
            email     = 'kevin@gmail.com',
            password  = 'kevin1123',
            is_doctor = 'False'
        )

        Department.objects.create(
            id        = 1,
            name      = "가정의학과",
            thumbnail = "family_medicine.png"
        )

        Hospital.objects.create(
            id   = 1,
            name = "퍼즐AI병원"
        )

        self.token = jwt.encode({"user_id" : CustomUser.objects.get(is_doctor=False).id}, settings.SECRET_KEY, algorithm = settings.ALGORITHM)
        
    def tearDown(self):
        CustomUser.objects.all().delete()
        Department.objects.all().delete()
        Hospital.objects.all().delete()

    def test_sucess_department_list(self):
        client = Client()
        headers = {"HTTP_Authorization" : self.token}
        response = client.get('/appointments/departments', **headers, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                "result": [
                    {
                        "id"       : 1,
                        "name"     : "가정의학과",
                        "thumbnails": "127.0.0.1:8000/media/department_thumbnail/family_medicine.png"
                    }
                ]
            }
        )

class DoctorListTest(TestCase):
    def setUp(self):
        CustomUser.objects.create_user(
            name      = 'kevin',
            email     = 'kevin@gmail.com',
            password  = 'kevin1123',
            is_doctor = 'False'
        )
        
        CustomUser.objects.create_user(
            name      = 'doctor',
            email     = 'doctor@gmail.com',
            password  = 'doctor123',
            is_doctor = 'True'
        )

        Department.objects.create(
            id        = 1,
            name      = "가정의학과",
            thumbnail = "family_medicine.png"
        )

        Hospital.objects.create(
            id   = 1,
            name = "퍼즐AI병원"
        )

        Doctor.objects.create(
            id            = 1,
            user_id       = CustomUser.objects.get(is_doctor=True).id,
            department_id = Department.objects.get(name="가정의학과").id,
            hospital_id   = Hospital.objects.get(name="퍼즐AI병원").id,
            profile_img   = "doctor_profile.png"
        )
        self.token = jwt.encode({"user_id" : CustomUser.objects.get(is_doctor=False).id}, settings.SECRET_KEY, algorithm = settings.ALGORITHM)
        
    def tearDown(self):
        CustomUser.objects.all().delete()
        Department.objects.all().delete()
        Hospital.objects.all().delete()
        Doctor.objects.all().delete()

    def test_sucess_doctor_list(self):
        client = Client()
        headers = {"HTTP_Authorization" : self.token}
        response = client.get('/appointments/departments/1', **headers, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 
            {
                "result": [
                    {
                        "id"         : 1,
                        "names"       : "doctor",
                        "departments" : "가정의학과",
                        "hospitals"   : "퍼즐AI병원",
                        "profile_imgs": "127.0.0.1:8000/media/doctor_profile_img/doctor_profile.png"
                    }
                ]
            }
        )

class WorkingDayTest(TestCase):
    def setUp(self):
        CustomUser.objects.create_user(
            name      = 'kevin',
            email     = 'kevin@gmail.com',
            password  = 'kevin1123',
            is_doctor = 'False'
        )
        
        CustomUser.objects.create_user(
            name      = 'doctor',
            email     = 'doctor@gmail.com',
            password  = 'doctor123',
            is_doctor = 'True'
        )

        doc     = CustomUser.objects.get(is_doctor=True)
        patient = CustomUser.objects.get(is_doctor=False)

        Department.objects.create(
            id        = 1,
            name      = "가정의학과",
            thumbnail = "family_medicine.png"
        )

        Hospital.objects.create(
            id   = 1,
            name = "퍼즐AI병원"
        )

        department = Department.objects.get(name="가정의학과")
        hospital   = Hospital.objects.get(name="퍼즐AI병원")

        Doctor.objects.create(
            id            = 1,
            user_id       = doc.id,
            department_id = department.id,
            hospital_id   = hospital.id,
            profile_img   = "doctor_profile.png"
        )

        doctor = Doctor.objects.get(id=1)

        State.objects.create(
            id   = 1,
            name = "진료대기"
        )

        current = datetime.strptime((datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")

        Appointment.objects.create(
            id         = 1,
            symptom    = "아파요",
            opinion    = "괜찮아요",
            date       = current,
            time       = "12:00:00.000000",
            created_at = "2022-06-28 13:34:40.769922",
            updated_at = "2022-06-28 13:34:40.769922",
            state_id   = 1
        )

        UserAppointment.objects.create(
            id             = 1,
            appointment_id = 1,
            doctor_id      = doctor.id,
            patient_id     = patient.id
        )

        WorkingDay.objects.create(
            id        = 1,
            date      = current,
            doctor_id = doctor.id
        )

        self.token = jwt.encode({"user_id" : CustomUser.objects.get(is_doctor=False).id}, settings.SECRET_KEY, algorithm = settings.ALGORITHM)
        
    def tearDown(self):
        CustomUser.objects.all().delete()
        Department.objects.all().delete()
        Hospital.objects.all().delete()
        Doctor.objects.all().delete()
        Appointment.objects.all().delete()
        UserAppointment.objects.all().delete()
        WorkingDay.objects.all().delete()

    def test_success_working_day_list(self): 
        client  = Client()
        headers = {"HTTP_Authorization" : self.token}

        doctor                = CustomUser.objects.get(is_doctor=True)
        doctor_id             = Doctor.objects.get(user_id = doctor.id).id
        test_date             = datetime.strptime((datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")
        year                  = test_date.year
        month                 = test_date.month

        response = client.get(f'/appointments/doctor/{doctor_id}/workingday?year={year}&month={month}', **headers, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                "result": [
                    test_date.day
                ]
            }
        )

class WorkingTimeTest(TestCase):
    def setUp(self):
        CustomUser.objects.create_user(
            name      = 'kevin',
            email     = 'kevin@gmail.com',
            password  = 'kevin1123',
            is_doctor = 'False'
        )
        
        CustomUser.objects.create_user(
            name      = 'doctor',
            email     = 'doctor@gmail.com',
            password  = 'doctor123',
            is_doctor = 'True'
        )

        doc     = CustomUser.objects.get(is_doctor=True)
        patient = CustomUser.objects.get(is_doctor=False)

        Department.objects.create(
            id        = 1,
            name      = "가정의학과",
            thumbnail = "family_medicine.png"
        )

        Hospital.objects.create(
            id   = 1,
            name = "퍼즐AI병원"
        )

        department = Department.objects.get(name="가정의학과")
        hospital = Hospital.objects.get(name="퍼즐AI병원")

        Doctor.objects.create(
            id            = 1,
            user_id       = doc.id,
            department_id = department.id,
            hospital_id   = hospital.id,
            profile_img   = "doctor_profile.png"
        )

        doctor = Doctor.objects.get(id=1)

        State.objects.bulk_create([
            State(
                id   = 1,
                name = "진료대기"
            ),
            State(
                id   = 2,
                name = "진료취소"
            ),
            State(
                id   = 3,
                name = "진료완료"
            )
        ])

        Appointment.objects.bulk_create([
            Appointment(            
                id         = 1,
                symptom    = "아파요",
                opinion    = "괜찮아요",
                date       = "2023-07-01",
                time       = "12:00:00.000000",
                created_at = "2022-06-28 13:34:40.769922",
                updated_at = "2022-06-28 13:34:40.769922",
                state_id   = 1
            ),
            Appointment(            
                id         = 2,
                symptom    = "아파요",
                opinion    = "괜찮아요",
                date       = datetime.strptime((datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d"),
                time       = "12:00:00.000000",
                created_at = "2022-06-28 13:34:40.769922",
                updated_at = "2022-06-28 13:34:40.769922",
                state_id   = 1
            ),
            Appointment(            
                id         = 3,
                symptom    = "아파요",
                opinion    = "괜찮아요",
                date       = "2022-05-01",
                time       = "12:00:00.000000",
                created_at = "2022-04-28 13:34:40.769922",
                updated_at = "2022-04-28 13:34:40.769922",
                state_id   = 1
            ),
            Appointment(            
                id         = 4,
                symptom    = "아파요",
                opinion    = "괜찮아요",
                date       = "2023-07-01",
                time       = "10:00:00.000000",
                created_at = "2022-04-28 13:34:40.769922",
                updated_at = "2022-04-28 13:34:40.769922",
                state_id   = 3
            ),
        ])

        UserAppointment.objects.bulk_create([
            UserAppointment(
                id             = 1,
                appointment_id = 1,
                doctor_id      = doctor.id,
                patient_id     = patient.id
            ),
            UserAppointment(
                id             = 2,
                appointment_id = 2,
                doctor_id      = doctor.id,
                patient_id     = patient.id
            ),
            UserAppointment(
                id             = 3,
                appointment_id = 3,
                doctor_id      = doctor.id,
                patient_id     = patient.id
            )
        ])

        WorkingDay.objects.bulk_create([
            WorkingDay(
                id        = 1,
                date      = "2023-07-01",
                doctor_id = doctor.id
            ),
            WorkingDay(
                id        = 2,
                date      = datetime.strptime((datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d"),
                doctor_id = doctor.id
            ),
            WorkingDay(
                id        = 3,
                date      = "2022-05-01",
                doctor_id = doctor.id
            )
        ])

        WorkingTime.objects.bulk_create([
            WorkingTime(
                id             = 1,
                time           = "12:00:00.000000",
                working_day_id = 1
                ),
            WorkingTime(
                id             = 2,
                time           = "13:00:00.000000",
                working_day_id = 1
            )
        ])

        self.token = jwt.encode({"user_id" : CustomUser.objects.get(is_doctor=False).id}, settings.SECRET_KEY, algorithm = settings.ALGORITHM)
        
    def tearDown(self):
        CustomUser.objects.all().delete()
        Department.objects.all().delete()
        Hospital.objects.all().delete()
        Doctor.objects.all().delete()
        Appointment.objects.all().delete()
        UserAppointment.objects.all().delete()
        WorkingDay.objects.all().delete()
        WorkingTime.objects.all().delete()

    def test_sucess_working_time_list(self):
        client  = Client()
        headers = {"HTTP_Authorization" : self.token}

        doctor    = CustomUser.objects.get(is_doctor=True)
        doctor_id = Doctor.objects.get(user_id = doctor.id).id
        test_date = datetime(2023, 7, 1)
        year      = test_date.year
        month     = test_date.month
        day       = test_date.day

        response = client.get(f'/appointments/doctor/{doctor_id}/workingtime?year={year}&month={month}&day={day}', **headers, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                'appointmented_time': ['12:00'],
                'working_time'      : ['12:00', '13:00']
            }
        )

    def test_error_appointment_for_past_dates(self):
        client  = Client()
        headers = {"HTTP_Authorization" : self.token}

        doctor    = CustomUser.objects.get(is_doctor=True)
        doctor_id = Doctor.objects.get(user_id = doctor.id).id
        test_date = datetime(2022, 5, 1)
        year      = test_date.year
        month     = test_date.month
        day       = test_date.day

        response = client.get(f'/appointments/doctor/{doctor_id}/workingtime?year={year}&month={month}&day={day}', **headers, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                'message': 'CANNOT_MAKE_AN_APPOINTMENT_FOR PAST_DATES'
            }
        )

    def test_error_appointment_on_the_day(self):
        client  = Client()
        headers = {"HTTP_Authorization" : self.token}

        doctor    = CustomUser.objects.get(is_doctor=True)
        doctor_id = Doctor.objects.get(user_id = doctor.id).id
        test_date = datetime.strptime((datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")
        year      = test_date.year
        month     = test_date.month
        day       = test_date.day

        response = client.get(f'/appointments/doctor/{doctor_id}/workingtime?year={year}&month={month}&day={day}', **headers, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                'message': 'NOT_AVAILABLE_ON_THE_DAY_OF_MAKING_AN_APPOINTMENT'
            }
        )