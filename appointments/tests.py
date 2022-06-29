import jwt

from django.test import TestCase, Client
from django.conf import settings

from users.models import CustomUser, Department, Hospital, Doctor

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
                        "thumbnail": "127.0.0.1:8000/media/department_thumbnail/family_medicine.png"
                    }
                ],
                "user_name": "kevin"
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
                        "name"       : "doctor",
                        "department" : "가정의학과",
                        "hospital"   : "퍼즐AI병원",
                        "profile_img": "127.0.0.1:8000/media/doctor_profile_img/doctor_profile.png"
                    }
                ]
            }
        )