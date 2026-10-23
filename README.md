# URSM for macOS

맥에서 한세대학교 학사정보시스템(URSM)을 쓸 수 있게 해줍니다.

> 학교나 투비소프트의 공식 배포물이 아닙니다. 개인이 만든 비공식 도구이며, 학교 시스템 이용 권한이 있는 분을 위한 안내입니다.

## 설치하기

1. **터미널 열기**  
   키보드에서 `command` + `space`를 눌러 Spotlight를 띄운 뒤, `터미널`을 입력하고 엔터를 누릅니다.

2. **명령어 붙여넣기**  
   터미널 창에 아래 명령어를 복사해 붙여넣고 엔터를 누릅니다.
   ```sh
   curl -fsSL https://raw.githubusercontent.com/jangisaac-dev/ursm-macos/main/install.sh | sh
   ```

   > **붙여넣을 때 macOS 보안 경고가 나타날 수 있습니다.**
   > macOS(Tahoe 26.4 이후)는 터미널에 붙여넣은 명령이 위험해 보이면 경고를 띄웁니다. 사람을 속여 악성 명령을 붙여넣게 하는 수법이 많아서 생긴 장치입니다.
   > 이 명령은 이 저장소의 [`install.sh`](install.sh)를 받아 실행합니다. 무엇을 하는지는 그 파일에서 누구나 확인할 수 있습니다.
   > 명령을 **이 페이지(github.com/jangisaac-dev/ursm-macos)에서 직접 복사했는지** 확인하세요. 다른 곳에서 받은 비슷한 명령은 붙여넣지 마세요.
   > 이 안내는 터미널 붙여넣기 경고에 대한 것입니다. 설치한 URSM 앱을 열 때 "악성 코드" 경고가 뜬다면 정상이 아니므로 열지 말고 [Issues](https://github.com/jangisaac-dev/ursm-macos/issues)에 알려 주세요.

3. **설치 완료 기다리기**  
   필요한 파일을 자동으로 내려받아 설치를 마칩니다. 인터넷 속도에 따라 2분에서 20분 정도 걸리며, 설치가 끝나면 앱이 저절로 열립니다.

- 앱 크기는 약 1.2GB이며, 3GB 이상의 디스크 여유 공간이 필요합니다.
- Apple Silicon(M1/M2/M3/M4) 맥에서 확인했습니다. 인텔 맥은 확인하지 않았습니다.
- 실행에 필요한 Rosetta가 없으면 설치 스크립트가 물어보고 대신 설치해 줍니다.

## 쓰는 법

설치가 끝난 뒤에는 일반 맥 앱처럼 실행하시면 됩니다.

- Launchpad나 Finder의 `응용 프로그램` 폴더에서 `URSM`을 찾아 엽니다.
- 첫 실행 시 내부 준비로 약 20초 정도 걸릴 수 있으며, 이후에는 5초 내외로 빠르게 열립니다.

## 출력과 엑셀 기능

- **OZ 출력**: 맥 기본 브라우저에서 열립니다. 브라우저에서 인쇄하거나 PDF로 저장할 수 있습니다.
- **엑셀 내보내기**: `~/Downloads`에 xlsx 파일로 저장되어 열립니다. 머리글 병합과 셀 서식은 보존되지 않습니다.
- 두 기능을 쓰려면 Apple Command Line Tools가 필요합니다. 설치기가 없음을 확인하면 설치 창을 열지 묻습니다.
- **확인한 범위**: 로그인, 강의계획서·수업시간표 출력, 수업시간표 엑셀 내보내기를 직접 확인했습니다. 다른 업무 화면은 모두 확인하지는 않았습니다.

## 업데이트

- 앱은 하루 한 번 새 버전을 확인해 받아 두고, 다음 실행 때 적용합니다. 적용되면 "새 버전(v1.1.0)으로 업데이트했습니다"처럼 알림이 뜹니다. 로그인 기록은 유지됩니다.
- 버전마다 바뀐 점은 [Releases](https://github.com/jangisaac-dev/ursm-macos/releases)에 정리합니다.
- **v1.0.0(2026년 9월)으로 설치하셨다면** 위 설치 명령을 한 번 다시 실행한 뒤 `[U] 업데이트`를 고르세요. 로그인 기록은 그대로 두고 출력·엑셀 기능과 자동 업데이트가 들어갑니다. 그다음부터는 자동으로 업데이트됩니다.
- **이전 버전으로 되돌리기**: 아래 명령을 실행하고 `[U] 업데이트`를 고르면 로그인 기록을 유지한 채 해당 버전으로 고정합니다. 자동 업데이트는 꺼진 상태로 유지됩니다. 선택할 버전은 [Releases](https://github.com/jangisaac-dev/ursm-macos/releases)에서 확인하세요. 선택 가능한 가장 오래된 버전은 `v1.1.0`입니다.
  ```sh
  curl -fsSL https://raw.githubusercontent.com/jangisaac-dev/ursm-macos/main/install.sh | URSM_VERSION=v1.1.0 sh
  ```
  최신 버전으로 바꾸려면 위의 일반 설치 명령을 다시 실행하고 `[U] 업데이트`를 고르세요.
- **v1.0.0(2026년 9월 버전)으로 되돌리기**: `v1.1.0`으로도 안 되면 아래 명령으로 v1.0.0을 새로 설치하세요. "지우고 새로 설치할까요?"에 `y`를 누르면 앱을 지우고 다시 만들기 때문에 로그인 기록이 지워지고, 출력·엑셀 기능도 빠집니다. v1.0.0은 스스로 업데이트하지 않습니다.
  ```sh
  curl -fsSL https://raw.githubusercontent.com/jangisaac-dev/ursm-macos/v1.0.0/install.sh | sh
  ```

## 잘 안 될 때

- **설치가 중간에 멈췄어요**  
  인터넷 연결이 끊겼거나 다운로드가 중단된 경우일 수 있습니다. 터미널에 설치 명령어를 다시 붙여넣고 실행해 보세요.

- **창이 안 떠요**  
  외장 디스크에 설치하면 창이 뜨지 않는 현상이 있습니다. 기본 위치(맥 내부 "응용 프로그램" 폴더)에 설치해 주세요.  
  앱을 닫은 직후 바로 다시 열면 맥이 이전 작업을 정리 중이라 안 열릴 수 있으니 잠시 후 다시 열어보세요.

- **오류 확인이 필요할 때**  
  문제가 계속되면 설치 로그(`~/Library/Logs/URSM-install.log`), 실행 로그(`~/Library/Logs/URSM.log`), 업데이트 로그(`~/Library/Logs/URSM-update.log`), OZ 출력 로그(`~/Library/Logs/URSM-oz.log`)를 확인해 보세요.

## 개인정보 주의 및 지우기

- **개인정보 주의**: 앱 안에 로그인 이력과 학사 정보가 남습니다. 설치된 앱이나 백업 파일을 다른 사람에게 건네지 마세요.
- **지우고 싶으면**: 터미널에 아래 명령어를 복사해 실행하시면 앱, 캐시, 로그가 모두 삭제됩니다.
  ```sh
  rm -rf ~/Applications/URSM.app ~/Library/Caches/URSM-install ~/Library/Logs/URSM*.log
  ```

---

## 기술 정보 (개발자용)

여기부터는 동작 원리와 기술적인 세부 사항을 다룬다.

### 이 저장소가 담는 것과 담지 않는 것

이 저장소는 바이너리를 담지 않는다. `install.sh`가 네 구성요소를 각 원 배포처에서 받아 SHA-256을 대조한 뒤에만 푼다. 앱 코드(`app/`)는 최신 릴리즈 태그의 것을 받아 설치한다.

| 구성요소 | 용량 | 출처 및 비고 |
|---|---|---|
| 앱 뼈대 (`Template-1.0.15.tar.xz`) | 87MB | github.com/Sikarugir-App/Wrapper |
| wine 엔진 (`WS12WineCX24.0.7_7.tar.xz`) | 172MB | github.com/Sikarugir-App/Engines (CrossOver 24.0.7 기반 wine-9.0) |
| XPLATFORM 9.2 런타임 (`XPLATFORM9.2_SetupEngine.exe`) | 14.6MB | ims.hansei.ac.kr:448 (학교 공식 배포, 투비소프트 독점 소프트웨어, 재배포 허락 미확인) |
| 굴림 (`GULIM.TTC`) | 18MB | github.com/googlefonts/gulim (OFL 1.1, 커밋 고정) |

### 굴림을 따로 넣는 이유

XPLATFORM UI는 글꼴을 `System`, `MS Sans Serif`, `Arial` 세 패밀리로만 요청한다. wine의 기본 `FontLink\SystemLink`에는 이 셋에 대한 한글 대체가 없어서 한글이 비트맵 글꼴로 떨어진다. 비트맵 글꼴은 안티앨리어싱이 걸리지 않아 글자가 거칠게 뭉개진다. `install.sh`는 굴림(`GULIM.TTC`)을 넣고 이 세 줄만 굴림으로 연결한다. `Tahoma`, `Microsoft Sans Serif` 등 나머지는 wine 기본값이 이미 `GULIM.TTC`를 가리키므로 파일만 있으면 저절로 동작한다.

prefix를 한국어 로케일(`ko_KR.UTF-8`)로 만들기 때문에 wine이 코드페이지 949와 `FontSubstitutes`(`MS Shell Dlg` → `Gulim`)를 스스로 잡는다. 백묵(Baekmuk) 폰트는 필요 없다 — 없이도 글꼴 파일과 관련 레지스트리 값이 기존에 손으로 맞춰 둔 설치본과 같은 상태로 재현된다.

### gecko를 직접 등록하는 이유

출력·리포트 화면은 `Shell.Explorer.2`(IE 웹브라우저 컨트롤)로 뜨고, 그 실체가 `mshtml`이며 `mshtml`은 gecko 엔진을 `GeckoPath` 레지스트리로 찾는다. 이 wine 빌드는 gecko를 `.msi`가 아니라 이미 풀린 디렉터리로 담고 있어서 `wineboot`이 자동 등록하지 않는다. `install.sh`가 `GeckoPath`를 직접 등록한다. 등록하지 않으면 그 화면이 빈 흰 창이 된다.

### 출력과 엑셀 기능의 우회 경로

런처는 `app/ozcap.py`가 여는 `127.0.0.1:18766` 로컬 프록시로 요청을 중계한다. 출력 요청은 맥 기본 브라우저에서 열고, 그리드의 엑셀 내보내기는 xlsx로 변환해 `~/Downloads`에 저장한다. 요청 본문은 기록하지 않는다.

### 자동 업데이트

버전은 이 저장소의 릴리즈 태그(`vX.Y.Z`)다. 런처는 하루 한 번 `releases/latest`가 가리키는 태그를 확인하고(GitHub API를 쓰지 않아 호출 한도가 없다), 설치된 버전과 다르면 그 태그의 `app/URSM`, `app/ozcap.py`를 받아 두었다가 다음 실행 때 적용한다. `main`에 push만 해서는 배포되지 않고, 릴리즈를 만들어야 배포된다. 바뀌는 파일은 URSM 런처, `ozcap.py`, `ursm-version` 세 개뿐이고, 이전 버전은 `Contents/Resources/.prev/`에 보존한다. 따라서 이 저장소의 최신 릴리즈에 담긴 코드가 사용자 Mac에서 실행된다.

`URSM_VERSION`을 지정하면 해당 릴리즈 태그로 고정하고 `ursm-version` 파일을 두지 않아 런처가 자동 업데이트 확인을 건너뛴다.

### 통신 경로

앱은 실행 시 `http://ims.hansei.ac.kr/URSM.xadl`에서 화면 정의를 받는다. 설치 파일 네 개는 SHA-256으로 검증하지만, 그 검증은 실행 이후 앱이 받아오는 화면 정의와 리소스에는 적용되지 않는다. 화면 정의 안에도 `http://` 주소가 들어 있다. 학교 서버가 `https://ims.hansei.ac.kr:448`로 같은 파일을 주는 것은 확인했으나, 바꿨을 때 리소스 해석이 어떻게 되는지는 검증하지 않아 기본값을 그대로 두었다.

### 개인정보 주의

앱 번들 안의 wine prefix에 로그인 이력과 학사자료 캐시가 남는다. 번들을 그대로 남에게 주거나 백업을 공유하면 안 된다.

### 라이선스

설치 스크립트 및 문서는 MIT License를 따른다. 스크립트가 내려받는 각 구성요소는 각 원 배포처의 라이선스를 따른다. 자세한 내용은 [LICENSES.md](LICENSES.md)를 참고한다.
