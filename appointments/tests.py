import jwt

from datetime import datetime, timedelta, date, time

from django.test                    import TestCase, Client
from django.conf                    import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from users.models        import CustomUser, Department, Hospital, Doctor, WorkingDay, WorkingTime
from appointments.models import Appointment, AppointmentImage, State, UserAppointment

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

    def test_success_department_list(self):
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
                        "thumbnails": f'{settings.LOCAL_PATH}/department_thumbnail/family_medicine.png'
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

    def test_success_doctor_list(self):
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
                        "profile_imgs": f"{settings.LOCAL_PATH}/doctor_profile_img/doctor_profile.png"
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

    def test_success_working_time_list(self):
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

class CancellationTest(TestCase):
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

        five_days_after    = datetime.now() + timedelta(days=5)
        two_days_after     = datetime.now() + timedelta(days=2)
        less_an_hour_after = datetime.now() + timedelta(seconds=1500)

        Appointment.objects.bulk_create([
            Appointment(            
                id         = 1,
                symptom    = "아파요",
                opinion    = "괜찮아요",
                date       = five_days_after.date(),
                time       = five_days_after.time(),
                state_id   = 1
            ),
            Appointment(            
                id         = 2,
                symptom    = "아파요",
                opinion    = "괜찮아요",
                date       = less_an_hour_after.date(),
                time       = less_an_hour_after.time(),
                state_id   = 1
            ),
            Appointment(            
                id         = 3,
                symptom    = "아파요",
                opinion    = "괜찮아요",
                date       = two_days_after.date(),
                time       = two_days_after.time(),
                state_id   = 2
            )
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

        self.token = jwt.encode({"user_id" : CustomUser.objects.get(is_doctor=False).id}, settings.SECRET_KEY, algorithm = settings.ALGORITHM)
        
    def tearDown(self):
        CustomUser.objects.all().delete()
        Department.objects.all().delete()
        Hospital.objects.all().delete()
        Doctor.objects.all().delete()
        Appointment.objects.all().delete()
        UserAppointment.objects.all().delete()

    def test_success_cancellation(self):
        client  = Client()
        headers = {"HTTP_Authorization" : self.token}
        appointment_id = Appointment.objects.get(id=1).id

        response = client.patch(f'/appointments/{appointment_id}/cancellation', **headers, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message' : 'APPOINTMENT_HAS_BEEN_CANCELED'})

    def test_fail_cancellation_an_hour_prior_to(self):
        client  = Client()
        headers = {"HTTP_Authorization" : self.token}
        appointment_id = Appointment.objects.get(id=2).id

        response = client.patch(f'/appointments/{appointment_id}/cancellation', **headers, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'APPOINTMENTS_CAN_BE_CANCELLED_ONLY_AN_HOUR_PRIOR_TO_THE_SCHEDULED_TIME'})
    
    def test_fail_cancellation_already_canceled_or_closed(self):
        client  = Client()
        headers = {"HTTP_Authorization" : self.token}
        appointment_id = Appointment.objects.get(id=3).id

        response = client.patch(f'/appointments/{appointment_id}/cancellation', **headers, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'ALREADY_CANCELED_OR_CLOSED_APPOINTMENT'})

    def test_fail_cancellation_does_not_exist(self):
        client  = Client()
        headers = {"HTTP_Authorization" : self.token}
        appointment_id = 4

        response = client.patch(f'/appointments/{appointment_id}/cancellation', **headers, content_type='application/json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'message' : 'APPOINTMENT_DOES_NOT_EXIST'})

class AppointmentCreationTest(TestCase):
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

        five_days_after    = datetime.now() + timedelta(days=5)

        Appointment.objects.bulk_create([
            Appointment(            
                id         = 1,
                symptom    = "아파요",
                opinion    = "괜찮아요",
                date       = five_days_after.date(),
                time       = five_days_after.time(),
                state_id   = 1
            ),
            Appointment(            
                id         = 2,
                symptom    = "아파요",
                opinion    = "괜찮아요",
                date       = date(2023, 1, 1),
                time       = time(13, 0),
                state_id   = 1
            )
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

    def test_success_appointment_creation(self):
        client  = Client()
        headers = {"HTTP_Authorization" : self.token}
        doctor  = Doctor.objects.get(id=1)
        patient = CustomUser.objects.get(is_doctor=False)

        test_date  = datetime.now() + timedelta(days=2)
        test_year  = test_date.year
        test_month = test_date.month
        test_day   = test_date.day
        test_time  = test_date.hour

        image_mock = SimpleUploadedFile('testcode_image.png', b'')

        form_data = {
            'patient_id': patient.id,
            'doctor_id' : doctor.id,
            'year'      : test_year,
            'month'     : test_month,
            'day'       : test_day,
            'time'      : test_time,
            'symptom'   : "symptom",
            'image'     : [image_mock]
        }

        response = client.post('/appointments/create', form_data, **headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'message' : 'YOUR_APPOINTMENT_IS_CREATED'})

    def test_fail_appointment_creation_key_error(self):
        client  = Client()
        headers = {"HTTP_Authorization" : self.token}
        doctor  = Doctor.objects.get(id=1)
        patient = CustomUser.objects.get(is_doctor=False)

        test_date  = datetime.now() + timedelta(days=2)
        test_year  = test_date.year
        test_month = test_date.month
        test_day   = test_date.day
        test_time  = test_date.hour

        image_mock = SimpleUploadedFile('testcode_image.png', b'')

        form_data = {
            'patient_id': patient.id,
            'doctor_id' : doctor.id,
            'years'     : test_year,
            'months'    : test_month,
            'days'      : test_day,
            'time'      : test_time,
            'symptom'   : "symptom",
            'image'     : [image_mock]
        }

        response = client.post('/appointments/create', form_data, **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'KEY_ERROR'})

    def test_fail_creation_image_limitation(self):
        client  = Client()
        headers = {"HTTP_Authorization" : self.token}
        doctor  = Doctor.objects.get(id=1)
        patient = CustomUser.objects.get(is_doctor=False)

        test_date  = datetime.now() + timedelta(days=2)
        test_year  = test_date.year
        test_month = test_date.month
        test_day   = test_date.day
        test_time  = test_date.hour

        image_mock = SimpleUploadedFile('testcode_image.png', b'')

        form_data = {
            'patient_id': patient.id,
            'doctor_id' : doctor.id,
            'year'      : test_year,
            'month'     : test_month,
            'day'       : test_day,
            'time'      : test_time,
            'symptom'   : "symptom",
            'image'     : [image_mock, image_mock, image_mock, image_mock, image_mock, image_mock, image_mock]
        }

        response = client.post('/appointments/create', form_data, **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'DO_NOT_ALLOW_TO_UPLOAD_IMAGES_MORE_THAN_6'})

class AppointmentChangeTest(TestCase):
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

        five_days_after    = datetime.now() + timedelta(days=5)
        less_an_hour_after = datetime.now() + timedelta(seconds=1500)

        Appointment.objects.bulk_create([
            Appointment(            
                id         = 1,
                symptom    = "아파요",
                opinion    = "괜찮아요",
                date       = five_days_after.date(),
                time       = five_days_after.time(),
                state_id   = 1
            ),
            Appointment(            
                id         = 2,
                symptom    = "아파요",
                opinion    = "괜찮아요",
                date       = less_an_hour_after.date(),
                time       = less_an_hour_after.time(),
                state_id   = 1
            )
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
            )
        ])

        AppointmentImage.objects.bulk_create([
            AppointmentImage(
                id = 1,
                wound_img = "image1.png",
                appointment_id = 1,
            ),
            AppointmentImage(
                id = 2,
                wound_img = "image2.png",
                appointment_id = 1,
            ),
            AppointmentImage(
                id = 3,
                wound_img = "image3.png",
                appointment_id = 2,
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
        AppointmentImage.objects.all().delete()

    def test_success_appointment_change(self):
        client  = Client()
        headers = {"HTTP_Authorization" : self.token}

        doctor         = Doctor.objects.get(id=1)
        test_date      = datetime.now() + timedelta(days=2)
        test_year      = test_date.year
        test_month     = test_date.month
        test_day       = test_date.day
        test_time      = test_date.hour
        image_mock     = SimpleUploadedFile('testcode_image.png', b'')
        appointment_id = 1

        form_data = {
            'doctor_id' : doctor.id,
            'year'      : test_year,
            'month'     : test_month,
            'day'       : test_day,
            'time'      : test_time,
            'symptom'   : "symptom",
            'image'     : [image_mock]
        }

        response = client.post(f'/appointments/{appointment_id}/change', form_data, **headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'message' : 'YOUR_APPOINTMENT_HAS_BEEN_CHANGED'})

    def test_fail_key_error_appointment_change(self):
        client  = Client()
        headers = {"HTTP_Authorization" : self.token}
        
        doctor         = Doctor.objects.get(id=1)
        test_date      = datetime.now() + timedelta(days=2)
        test_year      = test_date.year
        test_month     = test_date.month
        test_day       = test_date.day
        test_time      = test_date.hour
        image_mock     = SimpleUploadedFile('testcode_image.png', b'')
        appointment_id = 1

        form_data = {
            'doctor_id' : doctor.id,
            'years'      : test_year,
            'month'     : test_month,
            'day'       : test_day,
            'time'      : test_time,
            'symptom'   : "symptom",
            'image'     : [image_mock]
        }

        response = client.post(f'/appointments/{appointment_id}/change', form_data, **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'KEY_ERROR'})

    def test_fail_does_not_exist_appointment_change(self):
        client  = Client()
        headers = {"HTTP_Authorization" : self.token}
        
        doctor         = Doctor.objects.get(id=1)
        test_date      = datetime.now() + timedelta(days=2)
        test_year      = test_date.year
        test_month     = test_date.month
        test_day       = test_date.day
        test_time      = test_date.hour
        image_mock     = SimpleUploadedFile('testcode_image.png', b'')
        appointment_id = 5

        form_data = {
            'doctor_id' : doctor.id,
            'year'      : test_year,
            'month'     : test_month,
            'day'       : test_day,
            'time'      : test_time,
            'symptom'   : "symptom",
            'image'     : [image_mock]
        }

        response = client.post(f'/appointments/{appointment_id}/change', form_data, **headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'message' : 'APPOINTMENT_DOES_NOT_EXIST'})

    def test_fail_appointment_change_an_hour_prior_to(self):
        client  = Client()
        headers = {"HTTP_Authorization" : self.token}

        doctor         = Doctor.objects.get(id=1)
        test_date      = datetime.now() + timedelta(days=2)
        test_year      = test_date.year
        test_month     = test_date.month
        test_day       = test_date.day
        test_time      = test_date.hour
        image_mock     = SimpleUploadedFile('testcode_image.png', b'')
        appointment_id = 2
        
        form_data = {
            'doctor_id' : doctor.id,
            'year'      : test_year,
            'month'     : test_month,
            'day'       : test_day,
            'time'      : test_time,
            'symptom'   : "symptom",
            'image'     : [image_mock]
        }

        response = client.post(f'/appointments/{appointment_id}/change', form_data, **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'NOT_ALLOW_TO_RESCHEDULE_YOUR_APPOINTMENT_AN_HOUR_PRIOR_TO_YOUR_SCHEDULED_TIME'})

    def test_fail_image_limitation_appointment_change(self):
        client  = Client()
        headers = {"HTTP_Authorization" : self.token}

        doctor         = Doctor.objects.get(id=1)
        test_date      = datetime.now() + timedelta(days=2)
        test_year      = test_date.year
        test_month     = test_date.month
        test_day       = test_date.day
        test_time      = test_date.hour
        image_mock     = SimpleUploadedFile('testcode_image.png', b'')
        appointment_id = 1

        form_data = {
            'doctor_id' : doctor.id,
            'year'      : test_year,
            'month'     : test_month,
            'day'       : test_day,
            'time'      : test_time,
            'symptom'   : "symptom",
            'image'     : [image_mock, image_mock, image_mock, image_mock, image_mock, image_mock, image_mock]
        }

        response = client.post(f'/appointments/{appointment_id}/change', form_data, **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message' : 'NOT_ALLOW_TO_UPLOAD_IMAGES_MORE_THAN_6'})