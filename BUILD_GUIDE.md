# FnGuide 크롤러 exe 빌드 가이드

## 🚀 빠른 빌드 방법

### 1. 가상환경 활성화
```bash
# Windows
.venv\Scripts\activate

# 또는 새로운 가상환경 생성
python -m venv venv_new
venv_new\Scripts\activate
```

### 2. PyInstaller 설치
```bash
pip install pyinstaller
```

### 3. exe 파일 생성
```bash
# 방법 1: 간단한 빌드
pyinstaller --onefile --windowed --name FnGuide_Crawler run_GUI.py

# 방법 2: spec 파일 사용 (권장)
pyinstaller fnguide_crawler.spec --clean --noconfirm
```

### 4. 빌드 결과 확인
- `dist/FnGuide_Crawler.exe` 파일이 생성됩니다.
- `dist/FnGuide_Crawler_Package/` 폴더에 배포용 패키지가 생성됩니다.

## 📦 배포 패키지 구성

빌드 완료 후 다음 파일들이 포함됩니다:

```
FnGuide_Crawler_Package/
├── FnGuide_Crawler.exe          # 메인 실행 파일
├── config/                       # 설정 폴더
│   └── config.py
├── code.txt                     # 종목코드 예시 파일
├── data/                        # 데이터 저장 폴더 (빈 폴더)
├── README.md                    # 사용 설명서
└── 사용법.txt                   # 간단한 사용법
```

## 🔧 고급 빌드 옵션

### spec 파일 수정
`fnguide_crawler.spec` 파일에서 다음을 수정할 수 있습니다:

1. **아이콘 추가**:
   ```python
   icon='path/to/icon.ico'  # 아이콘 파일 경로
   ```

2. **버전 정보 추가**:
   ```python
   version_file='version_info.txt'  # 버전 정보 파일
   ```

3. **추가 파일 포함**:
   ```python
   datas = [
       ('additional_files/', 'additional_files/'),
       # 추가할 파일들
   ]
   ```

### 빌드 옵션 설명

- `--onefile`: 모든 파일을 하나의 exe로 묶기
- `--windowed`: 콘솔 창 숨기기 (GUI 앱용)
- `--clean`: 이전 빌드 파일 정리
- `--noconfirm`: 확인 없이 덮어쓰기

## 🐛 문제 해결

### 1. PyInstaller 설치 오류
```bash
# pip 업그레이드 후 재설치
python -m pip install --upgrade pip
pip install pyinstaller
```

### 2. 모듈을 찾을 수 없는 오류
- `hiddenimports`에 누락된 모듈 추가
- `fnguide_crawler.spec` 파일 수정

### 3. exe 파일이 실행되지 않는 경우
- `--console` 옵션으로 콘솔 창 표시하여 오류 확인
- 필요한 DLL 파일이 누락되었는지 확인

### 4. 파일 크기가 너무 큰 경우
- `--exclude-module` 옵션으로 불필요한 모듈 제외
- `--strip` 옵션으로 디버그 정보 제거

## 📋 빌드 체크리스트

- [ ] 가상환경 활성화
- [ ] PyInstaller 설치
- [ ] 필요한 파일들 확인 (run_GUI.py, config/, src/)
- [ ] 빌드 실행
- [ ] exe 파일 테스트
- [ ] 배포 패키지 확인

## 🎯 최종 확인

빌드 완료 후 다음을 확인하세요:

1. **exe 파일 실행**: `FnGuide_Crawler.exe` 더블클릭
2. **GUI 표시**: 프로그램 창이 정상적으로 열리는지 확인
3. **기능 테스트**: 종목코드 입력, 크롤링 시작 등
4. **데이터 저장**: 크롤링된 데이터가 정상적으로 저장되는지 확인

## 📞 지원

빌드 중 문제가 발생하면:
1. 오류 메시지를 자세히 확인
2. 가상환경 상태 확인
3. 필요한 패키지 설치 여부 확인
4. `--console` 옵션으로 상세 오류 확인
