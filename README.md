# VOIDOC API
비대면 진료 솔루션 "VOIDOC"의 주요 기능을 구현한 백엔드 API입니다.
<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li><a href="#project-structure">Project Structure</a></li>
  </ol>
</details>

<br>

<!-- ABOUT THE PROJECT -->
## About The Project

"PuzzleAI" 와 기업협업 간 진행한 프로젝트로,

아래와 같은 비대면 진료 솔루션 **VOIDOC**의 주요 기능 API 구현 및 배포하였습니다.
- 회원가입 & 로그인 기능
- 예약 관련 기능 (예약 생성, 취소, 변경)

<br>

### Built With

- ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
- ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
- ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
- ![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)

<br>

<!-- Project Structure -->
## Project Structure
```
├── appointments
│   └── views.py
├── users
│   └── views.py
│   └── utils.py
├── media
│   └── department_thumbnail
│   └── doctor_profile_img
│   └── wound_img
├── voidoc
│   └── settings.py
├── manage.py
├── Dockerfile
├── requirements.txt
└── requirements-dev.txt

```
- `appointments`: 진료과목 및 의사 정보, 예약 관리 기능
- `users`: 사용자(환자, 의사) 정보 관리 (회원가입, 로그인)
- `media`: 로컬 서버 저장소(진료과목 이미지, 의사 프로필 사진, 환자 환부사진)
