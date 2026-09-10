#!/bin/sh
# URSM (한세대 XPLATFORM 9.2) macOS 설치기.
#   curl -fsSL <raw url>/install.sh | sh
# 재배포 권한이 없는 바이너리는 하나도 담지 않는다. 전부 원 배포처에서 받아
# SHA-256 을 대조한 뒤에만 푼다. 해시가 다르면 즉시 중단한다.
set -eu

DEST="${URSM_DEST:-$HOME/Applications/URSM.app}"
CACHE="${URSM_CACHE:-$HOME/Library/Caches/URSM-install}"
LOG="$HOME/Library/Logs/URSM-install.log"

# --- 고정 구성요소 --------------------------------------------------------
WRAPPER_URL="https://github.com/Sikarugir-App/Wrapper/releases/download/v1.0/Template-1.0.15.tar.xz"
WRAPPER_SHA="34273bcce885ce5a7fd6937af9ea344bb9961de7d55d6193f7413142e835c8c3"
ENGINE_URL="https://github.com/Sikarugir-App/Engines/releases/download/v1.0/WS12WineCX24.0.7_7.tar.xz"
ENGINE_SHA="203f9e9fd6c2cc77e6525d798a434ced326145db34a356355e05659d3445fd1c"
XPLAT_URL="https://ims.hansei.ac.kr:448/platform/newInstall/Download/XPLATFORM9.2_SetupEngine.exe"
XPLAT_SHA="b6e92d5c9663ca9ff6af887e08006e57caa5f3d70944efaf3fc13ab2c44693d1"
# 커밋 고정. main 이 움직여도 해시 대조에서 걸린다.
GULIM_URL="https://raw.githubusercontent.com/googlefonts/gulim/012723a8d5b6a6dc920330f26d165422c3014fd6/fonts/ttc/gulim-Regular.ttc"
GULIM_SHA="e658caecd9723d87bb0660de2d24b8310c8b11d27d812e2587e9c46c6e48abdd"

APPKEY="URSM"
XADL="http://ims.hansei.ac.kr/URSM.xadl"

mkdir -p "${LOG%/*}" "$CACHE"
log() { printf '%s  %s\n' "$(date '+%H:%M:%S')" "$*" | tee -a "$LOG"; }
die() { printf '\n실패: %s\n로그: %s\n' "$*" "$LOG" >&2; exit 1; }

# --- 0. 사전 점검 ---------------------------------------------------------
[ "$(uname -s)" = "Darwin" ] || die "macOS 전용이다."
for c in curl tar shasum plutil xattr; do
  command -v "$c" >/dev/null || die "$c 가 없다."
done
# wine 은 x86_64 전용이다. Apple Silicon 에서는 Rosetta 가 있어야 한 줄도 못 뗀다.
# 사용자가 따로 명령을 찾아 치게 하지 않고 여기서 대신 깔아 준다.
if [ "$(uname -m)" = arm64 ] && ! /usr/bin/arch -x86_64 /usr/bin/true 2>/dev/null; then
  echo
  echo "이 맥에는 Rosetta 가 필요합니다. 애플이 제공하는 구성 요소입니다."
  printf "지금 설치할까요? [Y/n] "
  read -r r </dev/tty || r=n
  case "$r" in
    [nN]*) die "Rosetta 없이는 설치할 수 없습니다." ;;
  esac
  echo "Rosetta 를 설치합니다. 암호를 물어볼 수 있습니다."
  softwareupdate --install-rosetta --agree-to-license </dev/tty \
    || sudo softwareupdate --install-rosetta --agree-to-license </dev/tty \
    || die "Rosetta 설치에 실패했습니다. 터미널에 아래를 붙여넣어 직접 설치한 뒤
다시 시도해 주세요.

  softwareupdate --install-rosetta --agree-to-license"
  /usr/bin/arch -x86_64 /usr/bin/true 2>/dev/null \
    || die "Rosetta 설치를 확인하지 못했습니다. 맥을 다시 시작한 뒤 시도해 주세요."
fi

# rm -rf 의 대상이 되므로 형태를 검사한다. URSM_DEST 를 잘못 주면
# 엉뚱한 디렉터리가 통째로 날아간다.
case "$DEST" in
  /*.app|/*/*.app) : ;;
  *) die "설치 경로는 .app 으로 끝나는 절대경로여야 한다: $DEST" ;;
esac

# 앱 1.2GB + 캐시 300MB. 여유 3GB 를 요구한다.
avail=$(df -k "${DEST%/*}" 2>/dev/null || df -k "$HOME"; :)
avail=$(printf '%s' "$avail" | awk 'NR==2{print $4}')
[ "$avail" -gt 3145728 ] || die "디스크 여유가 3GB 미만이다."

# 동의만 미리 받고 실제 삭제는 내려받기가 다 끝난 뒤에 한다. 여기서 지우면
# 다운로드나 해시 검증이 실패했을 때 멀쩡한 앱까지 잃는다.
if [ -e "$DEST" ]; then
  printf '이미 설치돼 있습니다: %s\n지우고 새로 설치할까요? [y/N] ' "$DEST"
  read -r ans </dev/tty || ans=n
  case "$ans" in [yY]*) : ;; *) die "설치를 취소했다." ;; esac
fi

# --- 1. 내려받기 ----------------------------------------------------------
fetch() { # url sha 파일명
  f="$CACHE/$3"
  if [ -f "$f" ] && [ "$(shasum -a 256 "$f" | cut -d' ' -f1)" = "$2" ]; then
    log "캐시 사용: $3"; return 0
  fi
  log "받는 중: $3"
  curl -fL --retry 3 --progress-bar -o "$f.part" "$1" || die "$3 내려받기 실패"
  got=$(shasum -a 256 "$f.part" | cut -d' ' -f1)
  [ "$got" = "$2" ] || { rm -f "$f.part"; die "$3 해시 불일치
  기대: $2
  실제: $got
  배포처 파일이 바뀌었다. 설치를 중단한다."; }
  mv "$f.part" "$f"
}
fetch "$WRAPPER_URL" "$WRAPPER_SHA" Template-1.0.15.tar.xz
fetch "$ENGINE_URL"  "$ENGINE_SHA"  WS12WineCX24.0.7_7.tar.xz
fetch "$XPLAT_URL"   "$XPLAT_SHA"   XPLATFORM9.2_SetupEngine.exe
fetch "$GULIM_URL"   "$GULIM_SHA"   GULIM.TTC

# 네 파일이 모두 검증된 지금 시점에 기존 앱을 치운다.
rm -rf "$DEST"
# 이 뒤로 $DEST 는 우리가 만드는 것뿐이다. 중간에 실패하면 반쯤 만들어진
# 앱을 남기지 않는다.
trap 'rm -rf "$DEST"' EXIT

# --- 2. 앱 뼈대 + wine 엔진 -----------------------------------------------
mkdir -p "${DEST%/*}"
STAGE="$CACHE/stage.$$"; rm -rf "$STAGE"; mkdir -p "$STAGE"
log "앱 뼈대를 푸는 중"
tar -xJf "$CACHE/Template-1.0.15.tar.xz" -C "$STAGE"
mv "$STAGE/Template-1.0.15.app" "$DEST"
rmdir "$STAGE"

C="$DEST/Contents"
log "wine 엔진을 푸는 중"
tar -xJf "$CACHE/WS12WineCX24.0.7_7.tar.xz" -C "$C/Frameworks"
mv "$C/Frameworks/wswine.bundle" "$C/Frameworks/wine"

# wine 은 자기 lib 디렉터리에서 동봉 dylib 를 찾는다. 뼈대의 Frameworks 를
# 전부 링크해 준다. renderer 는 wine 이 쓰지 않고, wine 은 자기 이름이다.
for e in "$C/Frameworks"/*; do
  n="${e##*/}"
  case "$n" in wine|renderer) continue ;; esac
  [ -e "$C/Frameworks/wine/lib/$n" ] || ln -s "../../$n" "$C/Frameworks/wine/lib/$n"
done

ln -sfn SharedSupport/prefix/drive_c "$C/drive_c"
mkdir -p "$C/SharedSupport/Logs"
ln -sfn SharedSupport/Logs "$C/Logs"

plutil -replace CFBundleExecutable -string URSM        "$C/Info.plist"
plutil -replace CFBundleName       -string URSM        "$C/Info.plist"
plutil -replace CFBundleIdentifier -string ac.hansei.ursm.port "$C/Info.plist"

# --- 3. 실행기 ------------------------------------------------------------
cat > "$C/MacOS/URSM" <<'LAUNCHER'
#!/bin/zsh
APPKEY="URSM"
XADL="http://ims.hansei.ac.kr/URSM.xadl"

BUNDLE="${0:A:h:h}"
BIN="$BUNDLE/Frameworks/wine/bin"
export WINEPREFIX="$BUNDLE/SharedSupport/prefix"
# mscoree(.NET)만 끈다. mshtml 은 끄지 않는다 — 출력 화면이 Shell.Explorer.2
# 웹브라우저 컨트롤이라, 끄면 빈 흰 창이 된다.
export WINEDLLOVERRIDES="mscoree="
export WINEDEBUG=-all
export PATH="$BIN:/usr/bin:/bin:/usr/sbin:/sbin"
# 로그는 번들 밖에 둔다. 번들 안에 쓰면 권한 거부로 리다이렉트가 실패하고
# 앱이 즉시 죽는다.
LOG="$HOME/Library/Logs/URSM.log"
mkdir -p "${LOG:h}" 2>/dev/null

# wine 창은 앱 번들 소속이 아니어서 저절로 앞에 오지 않는다.
# 접근성 권한이 없으면 조용히 실패한다 — 창은 그대로 뜬다.
bring_to_front() {
  for _ in {1..60}; do
    if pgrep -x -q "XPlatform.exe" 2>/dev/null; then
      /usr/bin/osascript -e 'tell application "System Events" to set frontmost of (first process whose name is "XPlatform.exe") to true' 2>/dev/null
      return
    fi
    sleep 2
  done
}

# 프로세스 판별은 실행파일 이름으로만 한다. pgrep -f 는 명령줄 전체를 훑어
# 무관한 셸까지 오탐한다.
if pgrep -x -q "XPlatform.exe" 2>/dev/null; then
  bring_to_front
  exit 0
fi

# 비정상 종료로 남은 고아 wine 프로세스 정리 (wineserver -k 로는 안 죽는다)
"$BIN/wineserver" -k 2>/dev/null
# zsh 에서 path 는 PATH 와 연결된 특수 배열이라 변수 이름으로 쓰면 PATH 가 깨진다.
/bin/ps -Ao pid=,comm= | while read -r pid pcomm; do
  case "$pcomm" in
    *winetemp-*) /usr/sbin/lsof -p "$pid" 2>/dev/null | /usr/bin/grep -qF "$BUNDLE" \
                 && /bin/kill -9 "$pid" 2>/dev/null ;;
  esac
done

cd "$BIN" || exit 1
# exec 하지 않는다. 이 프로세스가 앱 본체로 살아 있어야 Dock 아이콘이 튀지 않는다.
./wine "C:\\Program Files (x86)\\TOBESOFT\\XPLATFORM\\9.2\\XPlatform.exe" \
       -K "$APPKEY" -X "$XADL" >"$LOG" 2>&1 &
WINE_PID=$!
bring_to_front
wait $WINE_PID
LAUNCHER
chmod +x "$C/MacOS/URSM"

# --- 4. wine prefix ------------------------------------------------------
BIN="$C/Frameworks/wine/bin"
export WINEPREFIX="$C/SharedSupport/prefix"
export WINEDEBUG=-all
export WINEDLLOVERRIDES="mscoree="
# 한국어 로케일로 만들어야 wine 이 코드페이지 949 와 한글 폰트 기본값을 잡는다.
export LANG=ko_KR.UTF-8 LC_ALL=ko_KR.UTF-8
log "wine prefix 생성 (몇 분 걸린다)"
# wineboot 는 별도 바이너리가 아니라 prefix 안의 wineboot.exe 다.
(cd "$BIN" && ./wine wineboot -u) >>"$LOG" 2>&1 || die "wineboot 실패"
"$BIN/wineserver" -w

# --- 5. 굴림 ------------------------------------------------------------
# 앱 UI 는 System / MS Sans Serif / Arial 만 요청한다. 이 세 패밀리는 wine
# 기본 SystemLink 에 한글 대체가 없어서 한글이 비트맵 폰트로 떨어지고,
# 그래서 안티앨리어싱 없이 뭉개져 나온다. 세 줄을 굴림으로 연결하면 해결된다.
# 나머지(Tahoma, Microsoft Sans Serif 등)는 wine 기본값이 이미 GULIM.TTC 를
# 가리키므로 파일만 있으면 저절로 동작한다.
log "굴림 설치"
cp "$CACHE/GULIM.TTC" "$WINEPREFIX/drive_c/windows/Fonts/GULIM.TTC"
SL='HKLM\Software\Microsoft\Windows NT\CurrentVersion\FontLink\SystemLink'
for fam in "System" "MS Sans Serif" "Arial"; do
  (cd "$BIN" && ./wine reg add "$SL" /v "$fam" /t REG_MULTI_SZ /d "GULIM.TTC,Gulim" /f) >>"$LOG" 2>&1 \
    || die "폰트 링크 등록 실패: $fam"
done
"$BIN/wineserver" -w

# --- 5b. gecko 등록 -----------------------------------------------------
# 출력·리포트 화면은 Shell.Explorer.2(IE 웹브라우저 컨트롤)로 뜬다. 그 실체가
# mshtml 이고, mshtml 은 gecko 엔진을 GeckoPath 로 찾는다. 이 wine 빌드는
# gecko 를 .msi 가 아니라 이미 풀린 디렉터리로 담고 있어서 wineboot 가
# 자동 등록하지 않는다. 등록하지 않으면 그 화면이 빈 흰 창이 된다.
log "gecko 등록"
G="$C/Frameworks/wine/share/wine/gecko"
GV=$(ls "$G" 2>/dev/null | sed -n 's/^wine-gecko-\([0-9.]*\)-x86$/\1/p' | head -1)
[ -n "$GV" ] || die "gecko 디렉터리를 찾지 못했다: $G"
winpath() { printf 'Z:%s\\' "$(printf '%s' "$1" | tr '/' '\\')"; }
MK="HKCU\\Software\\Wine\\MSHTML\\$GV"
(cd "$BIN" && ./wine reg add "$MK" /v GeckoPath /t REG_SZ \
   /d "$(winpath "$G/wine-gecko-$GV-x86")" /f) >>"$LOG" 2>&1 || die "gecko 등록 실패 (x86)"
(cd "$BIN" && ./wine reg add "$MK\\Wow64" /v GeckoPath /t REG_SZ \
   /d "$(winpath "$G/wine-gecko-$GV-x86_64")" /f) >>"$LOG" 2>&1 || die "gecko 등록 실패 (x86_64)"
"$BIN/wineserver" -w

# --- 6. XPLATFORM -------------------------------------------------------
log "XPLATFORM 9.2 설치 (무인)"
cp "$CACHE/XPLATFORM9.2_SetupEngine.exe" "$WINEPREFIX/drive_c/"
(cd "$BIN" && ./wine "C:\\XPLATFORM9.2_SetupEngine.exe" /s) >>"$LOG" 2>&1 || true
"$BIN/wineserver" -w
rm -f "$WINEPREFIX/drive_c/XPLATFORM9.2_SetupEngine.exe"

XP="$WINEPREFIX/drive_c/Program Files (x86)/TOBESOFT/XPLATFORM/9.2/XPlatform.exe"
[ -f "$XP" ] || die "XPlatform.exe 가 설치되지 않았다. 로그를 확인하라."

# --- 7. 마무리 ----------------------------------------------------------
# 서명은 손대지 않는다. 뼈대 서명은 이미 무효지만 실행에는 지장이 없고,
# 격리 속성만 벗기면 Gatekeeper 를 통과한다.
xattr -dr com.apple.quarantine "$DEST" 2>/dev/null || true
trap - EXIT

cat <<EOF

설치가 끝났습니다.

  다음부터는 Launchpad 나 Finder 의 "응용 프로그램" 폴더에서
  URSM 을 열면 됩니다.

  처음 열 때는 화면이 나올 때까지 20초쯤 걸립니다.

  안 되는 것: OZ 리포트는 내용이 표시되지 않고, 엑셀 내보내기는
  지원되지 않습니다.

  지우려면: rm -rf "$DEST"

EOF

# 지금 바로 열어 준다. Finder 에서 찾아 헤매지 않게.
echo "URSM 을 여는 중입니다..."
open "$DEST" 2>/dev/null || true
