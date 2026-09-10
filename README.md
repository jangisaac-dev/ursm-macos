# URSM for macOS

한세대학교 학사행정 시스템 URSM(투비소프트 XPLATFORM 9.2, Windows 전용 네이티브 앱)을 macOS에서 Sikarugir/wine 포팅으로 실행한다. Windows, 가상머신, Parallels 없이 `install.sh` 한 줄로 설치하여 사용할 수 있다.

> 학교나 투비소프트의 공식 배포물이 아니다. 개인이 만든 설치 도구이며,
> 학교 시스템을 이용할 권한이 있는 사용자를 대상으로 한다. 무보증이다.

## 요구사항

- macOS. Apple Silicon(M 시리즈)에서 검증했다. Intel Mac은 검증하지 않았다.
- Apple Silicon Mac은 **Rosetta** 필수 (wine 바이너리가 x86_64 전용)
- 디스크 여유 공간 3GB 이상 (설치 완료 시 앱 번들 약 1.2GB, 다운로드 캐시 약 300MB)
- 인터넷 연결 (설치 중 원 배포처에서 약 290MB 다운로드)

## 설치

터미널에 다음 한 줄을 붙여넣는다.

```sh
curl -fsSL https://raw.githubusercontent.com/jangisaac-dev/ursm-macos/main/install.sh | sh
```

- 기본 설치 위치는 `~/Applications/URSM.app`이다.
- 최초 설치 시 다운로드 속도에 따라 약 10~20분 소요된다 (다운로드 캐시 재사용 시 설치 약 2분 20초).
- 설치 위치를 변경하려면 `URSM_DEST` 환경변수를 지정한다:

```sh
curl -fsSL https://raw.githubusercontent.com/jangisaac-dev/ursm-macos/main/install.sh \
  | URSM_DEST=/Applications/URSM.app sh
```

## 실행

설치가 끝나면 Finder에서 `~/Applications/URSM.app`을 실행한다.

- 첫 실행 시 내부 초기화 과정을 거쳐 약 20초 만에 로그인 화면이 나타난다.
- 이후 재실행은 약 5초다. 강제 종료 직후 곧바로 다시 열면 macOS가 아직 앱을
  종료 중이라 한 번 실패할 수 있다. 잠시 뒤 다시 열면 된다.

## 알려진 한계

- **OZ 리포트**: 조회 화면은 열리지만 현재 구성에서 리포트 내용이 표시되지 않는다. 뷰어 스크립트가 wine에 동봉된 gecko 엔진에서 실행되지 않는다.
- **엑셀 내보내기**: 지원되지 않는다. XPLATFORM의 엑셀 내보내기는 Windows에 설치된 Excel의 COM 인터페이스를 호출하는데 이 구성에는 Excel이 없다.
- 검증한 범위는 설치와 로그인 화면까지다. 로그인 이후의 개별 업무 화면은
  이 저장소에서 전수 확인하지 않았다.

## 문제 해결

### Apple Silicon에서 Rosetta가 없는 경우
Apple Silicon에서 Rosetta가 없으면 스크립트가 사전 점검에서 멈춘다. 터미널에서 다음 명령을 실행하여 Rosetta를 설치한 뒤 다시 시도한다.

```sh
softwareupdate --install-rosetta --agree-to-license
```

### 외장 볼륨(`/Volumes/...`)에 설치 시 창이 뜨지 않는 경우
외장 볼륨에 설치하면 Finder 실행 시 창이 뜨지 않고 멈추는 것이 관찰되었다. 원인은 규명하지 않았다(TCC 로그에는 관련 항목이 없었다). 터미널에서 `Contents/MacOS/URSM`을 직접 실행하면 정상적으로 뜬다. 기본 위치(`~/Applications/URSM.app`) 등 내부 디스크에 설치하는 것을 권장한다.

### 해시 불일치로 설치가 중단되는 경우
`install.sh`는 네 구성요소를 각 원 배포처에서 받아 SHA-256을 대조한 뒤에만 푼다. 배포처의 파일이 바뀌었거나 다운로드 중 손상된 경우 즉시 설치를 중단한다. 다운로드 손상이 의심되면 캐시를 지우고 다시 시도한다. 원 배포처의 파일 자체가 바뀐 경우라면 저장소 이슈를 확인해야 한다.

### 로그 확인
- **설치 로그**: `~/Library/Logs/URSM-install.log`
- **실행 로그**: `~/Library/Logs/URSM.log`

### 다시 설치하는 법
이미 설치된 앱이 있는 상태에서 `install.sh`를 실행하면 기존 앱을 삭제하고 다시 설치할지 묻는다(`[y/N]`). 캐시(`~/Library/Caches/URSM-install`)가 남아 있다면 다운로드를 건너뛰고 약 2분 20초 만에 재설치된다.

## 이 저장소가 담는 것과 담지 않는 것

이 저장소는 바이너리를 담지 않는다. `install.sh`가 네 구성요소를 각 원 배포처에서 받아 SHA-256을 대조한 뒤에만 푼다. 불일치면 즉시 중단한다.

| 구성요소 | 용량 | 출처 및 비고 |
|---|---|---|
| 앱 뼈대 (`Template-1.0.15.tar.xz`) | 87MB | github.com/Sikarugir-App/Wrapper |
| wine 엔진 (`WS12WineCX24.0.7_7.tar.xz`) | 172MB | github.com/Sikarugir-App/Engines (CrossOver 24.0.7 기반 wine-9.0) |
| XPLATFORM 9.2 런타임 (`XPLATFORM9.2_SetupEngine.exe`) | 14.6MB | ims.hansei.ac.kr:448 (학교 공식 배포, 투비소프트 독점 소프트웨어로 재배포 권한 없음) |
| 굴림 (`GULIM.TTC`) | 18MB | github.com/googlefonts/gulim (OFL 1.1, 커밋 고정) |

## 기술적 배경

### 굴림을 따로 넣는 이유
XPLATFORM UI는 글꼴을 `System`, `MS Sans Serif`, `Arial` 세 패밀리로만 요청한다. wine의 기본 `FontLink\SystemLink`에는 이 셋에 대한 한글 대체가 없어서 한글이 비트맵 글꼴로 떨어진다. 비트맵 글꼴은 안티앨리어싱이 걸리지 않아 글자가 거칠게 뭉개진다. `install.sh`는 굴림(`GULIM.TTC`)을 넣고 이 세 줄만 굴림으로 연결한다. `Tahoma`, `Microsoft Sans Serif` 등 나머지는 wine 기본값이 이미 `GULIM.TTC`를 가리키므로 파일만 있으면 저절로 동작한다.

prefix를 한국어 로케일(`ko_KR.UTF-8`)로 만들기 때문에 wine이 코드페이지 949와 `FontSubstitutes`(`MS Shell Dlg` → `Gulim`)를 스스로 잡는다. 백묵(Baekmuk) 폰트는 필요 없다 — 없이도 글꼴 파일과 관련 레지스트리 값이 기존에 손으로 맞춰 둔 설치본과 같은 상태로 재현된다.

### gecko를 직접 등록하는 이유
출력·리포트 화면은 `Shell.Explorer.2`(IE 웹브라우저 컨트롤)로 뜨고, 그 실체가 `mshtml`이며 `mshtml`은 gecko 엔진을 `GeckoPath` 레지스트리로 찾는다. 이 wine 빌드는 gecko를 `.msi`가 아니라 이미 풀린 디렉터리로 담고 있어서 `wineboot`이 자동 등록하지 않는다. `install.sh`가 `GeckoPath`를 직접 등록한다. 등록하지 않으면 그 화면이 빈 흰 창이 된다.

## 통신 경로

앱은 실행 시 `http://ims.hansei.ac.kr/URSM.xadl`에서 화면 정의를 받는다. 설치
파일 네 개는 SHA-256으로 검증하지만, 그 검증은 실행 이후 앱이 받아오는 화면
정의와 리소스에는 적용되지 않는다. 화면 정의 안에도 `http://` 주소가 들어 있다.
학교 서버가 `https://ims.hansei.ac.kr:448`로 같은 파일을 주는 것은 확인했으나,
바꿨을 때 리소스 해석이 어떻게 되는지는 검증하지 않아 기본값을 그대로 두었다.

## 개인정보 주의 및 지우기

### 개인정보 주의
앱 번들 안의 wine prefix에 로그인 이력과 학사자료 캐시가 남는다. 번들을 그대로 남에게 주거나 백업을 공유하면 안 된다.

### 지우는 법
터미널에서 다음 명령을 실행하여 앱, 캐시, 로그를 모두 삭제한다.

```sh
rm -rf ~/Applications/URSM.app ~/Library/Caches/URSM-install ~/Library/Logs/URSM*.log
```

## 라이선스

설치 스크립트 및 문서는 MIT License를 따른다. 스크립트가 내려받는 각 구성요소는 각 원 배포처의 라이선스를 따른다. 자세한 내용은 [LICENSES.md](LICENSES.md)를 참고한다.
