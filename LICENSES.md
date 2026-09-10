# 라이선스

이 저장소에는 `install.sh`, 문서, 그리고 아래 `licenses/` 의 원문만 들어 있다.
프로그램 바이너리는 재배포하지 않는다. 설치 시점에 각 원 배포처에서 직접 받는다.

## install.sh 및 문서

MIT License.

```
Copyright (c) 2026 jangisaac-dev

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 내려받는 구성요소

이 저장소는 어떠한 바이너리도 담지 않는다. `install.sh`가 설치 시점에 아래 구성요소를 각 원 배포처에서 직접 내려받아 SHA-256 해시를 대조한 뒤에만 사용한다.

### 굴림 (Gulim)
- **출처**: github.com/googlefonts/gulim (커밋 고정)
- **라이선스**: SIL Open Font License 1.1
- **라이선스 전문**: [licenses/GULIM-OFL.txt](licenses/GULIM-OFL.txt)
- **저자 정보**: [licenses/GULIM-AUTHORS.txt](licenses/GULIM-AUTHORS.txt)
- **비고**: 설치 스크립트는 원본 `gulim-Regular.ttc`를 수정 없이 그대로 넣으며, OFL이 금지하는 이름 재사용을 하지 않는다.

### wine 엔진 (WS12WineCX24.0.7_7)
- **출처**: github.com/Sikarugir-App/Engines
- **라이선스**: wine 본체는 LGPL-2.1-or-later다. 다만 이 아카이브는 CrossOver
  24.0.7 기반 빌드로, 함께 담긴 구성요소들이 모두 같은 라이선스인지는 확인하지
  않았다. 정확한 조건은 아카이브 안의 라이선스 파일을 따른다.
- **비고**: 원 배포처의 릴리스 아카이브를 직접 내려받아 사용한다.

### Sikarugir Wrapper (Template-1.0.15)
- **출처**: github.com/Sikarugir-App/Wrapper
- **라이선스**: Wineskin 계열 macOS 앱 래퍼. 동봉 라이브러리(GStreamer, gnutls, freetype, ICU 등)는 각자의 LGPL/MIT/BSD 라이선스를 따르며, 배포본 안에 원문이 함께 들어 있다.
- **비고**: 원 배포처의 릴리스 아카이브를 직접 내려받아 사용한다.

### XPLATFORM 9.2 런타임
- **출처**: 한세대학교 공식 배포 (`ims.hansei.ac.kr:448`)
- **라이선스**: 투비소프트(TOBESOFT)의 독점 소프트웨어
- **비고**: 제3자 재배포 허락을 확인하지 않았으므로 이 저장소는 파일을 담지 않고, 설치 시 학교 공식 배포 주소에서 직접 받는다. 사용은 학교와 투비소프트의 이용 조건을 따른다.
