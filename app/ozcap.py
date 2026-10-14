#!/usr/bin/env python3
"""URSM 출력(OZ 리포트)을 맥 기본 브라우저로 넘기는 프록시.

wine 의 IE 컨트롤로는 OZ HTML5 뷰어가 끝까지 뜨지 않는다(SPEC 7절).
런처가 http_proxy 로 앱 트래픽을 여기로 보낸다. 나머지는 그대로 중계하고
(본문은 기록하지 않는다. 로그인 요청도 여기를 지나간다),
oz 서버의 OzRptHtml5.jsp POST 만 가로채 같은 값을 자동 제출하는 페이지를 브라우저로 연다.
그 뒤 브라우저는 oz 서버와 직접 통신하므로 앱을 꺼도 열린 리포트는 살아 있다.

엑셀 내보내기 요청은 그리드의 표시 문자열을 XLSX로 저장한다.
저장한 파일을 맥에서 열고 파일명과 시트·행 수만 기록한다.

사용: python3 ozcap.py <port>
원본은 ursm-macos 저장소의 app/ozcap.py, 실행본은 URSM.app/Contents/Resources/ozcap.py 다.
"""
import http.server, http.client, urllib.parse, socket, select, subprocess, sys, time, html, itertools, threading
import os, re, zipfile
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape as xml_escape

PORT = int(sys.argv[1])
OZ = "oz.hansei.ac.kr"
HOP = {"proxy-connection", "connection", "keep-alive", "proxy-authorization", "te", "trailer", "upgrade"}
PAGES = {}
SEQ = itertools.count(1)
INAPP = ('<meta charset="utf-8"><body style="font:13px sans-serif;padding:2em">'
         '출력 화면을 맥 브라우저에서 열었습니다. 이 창은 닫아도 됩니다.</body>').encode()

# 출력 팝업과 그리드 라이브러리 응답을 고친다. 팝업은 /ozwait transaction 응답 뒤 닫히고,
# 그리드의 엑셀 요청은 /excel 로 전송된다(COAReportPop.xfdl, comgrid_script.xjs).
# (WebBrowser 의 LocationURL·ReadyState 를 타이머로 읽는 방식은 앱이 값을 못 읽어 실패했다)
# XPLATFORM 은 같은 URL 의 transaction 응답을 캐시해 두 번째부터 요청 없이 성공 콜백을 준다.
# 그래서 두 transaction 모두 URL 에 시각을 붙인다(SPEC 11절).
POPUP_PATCH = [
    (b'gfn_SetOzConfig(Div.div_ComOz, MODE, REPORT_NAME, ODI_NAME, ODI_PARAM);',
     b'gfn_SetOzConfig(Div.div_ComOz, MODE, REPORT_NAME, ODI_NAME, ODI_PARAM);\n'
     b'    this.transaction("ozcap", "http://127.0.0.1:%d/ozwait?" + (new Date()).getTime(), "", "", "", "ozcap_cb");' % PORT),
    (b']]></Script>', b'''
function ozcap_cb(strSvcID, nErrorCode, strErrorMsg)
{
	this.close();
}
]]></Script>'''),
]
# 학교 파일 끝이 주석 닫기(`***/]]></Script>`)라 줄을 바꿔 붙인다.
GRID_JS = r'''
// ozcap(맥 포팅): wine 에는 윈도우용 Excel 이 없어 ExportObject 가 아무 말 없이 실패한다.
// 그리드에 보이는 그대로(머리글·본문·합계의 표시 문자열)를 데이터셋에 담아 ozcap 프록시로 보내면
// 프록시가 xlsx 를 만들어 다운로드 폴더에 저장하고 맥에서 연다.
// 데이터셋 ozcap_xl 의 K 열: F(C0=파일명) / S(시트 시작, C0=시트명) / R(행, C0.. = 셀)
function ozcap_Excel(sFile, aGrid, aSheet, aExclude)
{
	var aMap = [], nMax = 0, j, c, k, n, r, g;
	for (j = 0; j < aGrid.length; j++) {
		g = aGrid[j];
		aMap[j] = [];
		n = 0;
		for (c = 0; c < g.getFormatColCount(); c++) {
			aMap[j][c] = -1;
			if (g.getRealColSize(c) <= 0) continue;
			if (aExclude) {
				for (k = 0; k < aExclude.length; k++) if (parseInt(aExclude[k]) == c) break;
				if (k < aExclude.length) continue;
			}
			aMap[j][c] = n++;
		}
		if (n > nMax) nMax = n;
	}
	if (this.isValidObject("ozcap_xl")) this.removeChild("ozcap_xl");
	var ds = new Dataset;
	ds.name = "ozcap_xl";
	this.addChild("ozcap_xl", ds);
	ds.addColumn("K", "string");
	for (c = 0; c < nMax; c++) ds.addColumn("C" + c, "string");
	r = ds.addRow(); ds.setColumn(r, "K", "F"); ds.setColumn(r, "C0", sFile);
	for (j = 0; j < aGrid.length; j++) {
		g = aGrid[j];
		r = ds.addRow(); ds.setColumn(r, "K", "S"); ds.setColumn(r, "C0", aSheet[j]);
		ozcap_Band(ds, g, "head", -1, aMap[j]);
		for (k = 0; k < g.rowcount; k++) ozcap_Band(ds, g, "body", k, aMap[j]);
		ozcap_Band(ds, g, "summ", -2, aMap[j]);
	}
	this.transaction("ozcap_xl", "@URL@?" + (new Date()).getTime(), "input=ozcap_xl:A", "", "", "ozcap_ExcelCb", true, 0, false);
}

function ozcap_Band(ds, g, sBand, nRow, aMap)
{
	var n = g.getCellCount(sBand), nSub = 0, nBase = ds.rowcount, i, k, c;
	for (i = 0; i < n; i++) {
		k = (parseInt(g.getCellProperty(sBand, i, "row")) || 0) + 1;
		if (k > nSub) nSub = k;
	}
	for (k = 0; k < nSub; k++) ds.setColumn(ds.addRow(), "K", "R");
	for (i = 0; i < n; i++) {
		c = aMap[parseInt(g.getCellProperty(sBand, i, "col")) || 0];
		if (c >= 0) ds.setColumn(nBase + (parseInt(g.getCellProperty(sBand, i, "row")) || 0), "C" + c, g.getCellText(nRow, i));
	}
}

function ozcap_ExcelCb(strSvcID, nErrorCode, strErrorMsg)
{
	if (this.isValidObject("ozcap_xl")) this.removeChild("ozcap_xl");
	if (nErrorCode < 0) alert("엑셀 파일을 만들지 못했습니다.\n" + strErrorMsg);
}
'''.encode("utf-8")
GRID_JS = GRID_JS.replace(b"@URL@", b"http://127.0.0.1:" + str(PORT).encode("ascii") + b"/excel")
GRID_PATCH = [
    (b'function gfn_ExportExcel(oGrid, sFileName, sSheetName, sSavemode, sGnb, sExclude, sSelType) {',
     b'function gfn_ExportExcel(oGrid, sFileName, sSheetName, sSavemode, sGnb, sExclude, sSelType) {'
     b'\n    return ozcap_Excel(sFileName, [oGrid], [sSheetName], sGnb == "col" ? sExclude : null);'),
    (b'function gfn_MultiExportExcel(strFileName, arrGridList, arrSheetList) {',
     b'function gfn_MultiExportExcel(strFileName, arrGridList, arrSheetList) {'
     b'\n\treturn ozcap_Excel(strFileName, arrGridList, arrSheetList, null);'),
    (b']]></Script>', GRID_JS + b']]></Script>'),
]
PATCHES = {
    "/co/coa/pops/COAReportPop.xfdl": POPUP_PATCH,
    "/platform/lib/comgrid_script.xjs": GRID_PATCH,
}
# /ozwait 응답. 최근 5초 안에 가로챈 출력이 있거나 20초 안에 생기면 돌려준다(없어도 20초 뒤엔 돌려준다)
OZ_DONE = threading.Condition()
LAST_OZ = [0.0]
OK_XML = (b'<?xml version="1.0" encoding="UTF-8"?>\n'
              b'<Root xmlns="http://www.tobesoft.com/platform/dataset" ver="5000"><Parameters>'
              b'<Parameter id="ErrorCode" type="string">0</Parameter>'
              b'<Parameter id="ErrMsg" type="string">OK</Parameter></Parameters></Root>')


def patch_file(path, data):
    patches = PATCHES.get(path)
    if patches is None:
        return data
    # 기준 문자열이 없거나 중복되면 부분 수정하지 않는다.
    if any(data.count(old) != 1 for old, _ in patches):
        log("PATCH SKIP", path)
        return data
    for old, new in patches:
        data = data.replace(old, new)
    return data


def parse_excel(body: bytes):
    root = ET.fromstring(body)
    dataset = next((node for node in root.iter("Dataset") if node.get("id") == "input"), None)
    if dataset is None:
        raise ValueError("Dataset id=input not found")
    indexes = []
    for column in dataset.findall("./ColumnInfo/Column"):
        match = re.fullmatch(r"C(\d+)", column.get("id", ""))
        if match:
            indexes.append(int(match.group(1)))
    width = len(indexes)
    filename = ""
    sheets = []
    current = None
    for row in dataset.findall("./Rows/Row"):
        values = {column.get("id"): column.text or "" for column in row.findall("Col")}
        kind = values.get("K", "")
        if kind == "F":
            filename = values.get("C0", "")
        elif kind == "S":
            current = [values.get("C0", ""), []]
            sheets.append(current)
        elif kind == "R":
            if current is None:
                current = ["", []]
                sheets.append(current)
            current[1].append([values.get("C%d" % i, "") for i in range(width)])
    return filename, [(name, rows) for name, rows in sheets]


def unique_sheet_names(names):
    used = set()
    result = []
    for i, name in enumerate(names, 1):
        base = re.sub(r"[\[\]:*?/\\]", "", str(name)).strip()[:31].strip()
        if not base:
            base = "Sheet%d" % i
        candidate = base
        suffix_number = 2
        while candidate.casefold() in used:
            suffix = " (%d)" % suffix_number
            candidate = base[:31 - len(suffix)].rstrip() + suffix
            suffix_number += 1
        used.add(candidate.casefold())
        result.append(candidate)
    return result


_BAD_XML = re.compile(r"[^\x09\x0a\x0d\x20-\ud7ff\ue000-\ufffd\U00010000-\U0010ffff]")
_NUMBER = r"-?(0|[1-9]\d{0,14}|[1-9]\d{0,2}(,\d{3}){1,4})(\.\d+)?"


def _xml_text(value):
    return _BAD_XML.sub("", str(value))


def _cell_ref(column, row):
    name = ""
    while column:
        column, remainder = divmod(column - 1, 26)
        name = chr(65 + remainder) + name
    return "%s%d" % (name, row)


def write_xlsx(path, sheets):
    sheet_names = unique_sheet_names([name for name, _ in sheets])
    types = ['<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
             '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
             '<Default Extension="xml" ContentType="application/xml"/>',
             '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>']
    for i in range(1, len(sheets) + 1):
        types.append('<Override PartName="/xl/worksheets/sheet%d.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' % i)
    types.append("</Types>")
    workbook_sheets = []
    workbook_rels = []
    worksheet_xml = []
    for i, ((_, rows), name) in enumerate(zip(sheets, sheet_names), 1):
        escaped_name = xml_escape(_xml_text(name), {'"': "&quot;", "'": "&apos;"})
        workbook_sheets.append('<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (escaped_name, i, i))
        workbook_rels.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet%d.xml"/>' % (i, i))
        lines = ['<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>']
        for row_number, row in enumerate(rows, 1):
            cells = []
            for column_number, value in enumerate(row, 1):
                value = _xml_text(value)
                if not value:
                    continue
                ref = _cell_ref(column_number, row_number)
                if re.fullmatch(_NUMBER, value):
                    numeric = value.replace(",", "")
                    cells.append('<c r="%s"><v>%s</v></c>' % (ref, numeric))
                else:
                    text = xml_escape(value, {'"': "&quot;", "'": "&apos;"})
                    cells.append('<c r="%s" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>' % (ref, text))
            lines.append('<row r="%d">%s</row>' % (row_number, "".join(cells)))
        lines.append("</sheetData></worksheet>")
        worksheet_xml.append("".join(lines).encode("utf-8"))
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", ("".join(types)).encode("utf-8"))
        archive.writestr("_rels/.rels", b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        archive.writestr("xl/workbook.xml", ('<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>%s</sheets></workbook>' % "".join(workbook_sheets)).encode("utf-8"))
        archive.writestr("xl/_rels/workbook.xml.rels", ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">%s</Relationships>' % "".join(workbook_rels)).encode("utf-8"))
        for i, content in enumerate(worksheet_xml, 1):
            archive.writestr("xl/worksheets/sheet%d.xml" % i, content)


def save_excel(body, folder):
    filename, sheets = parse_excel(body)
    filename = re.sub(r'[\\/:*?"<>|\x00-\x1f\x7f-\x9f]', "_", filename).strip(" .") or "URSM"
    path = os.path.join(os.fspath(folder), filename + ".xlsx")
    suffix = 2
    while os.path.exists(path):
        path = os.path.join(os.fspath(folder), "%s (%d).xlsx" % (filename, suffix))
        suffix += 1
    write_xlsx(path, sheets)
    return path


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


class P(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def do_CONNECT(self):
        host, _, port = self.path.rpartition(":")
        try:
            up = socket.create_connection((host, int(port or 443)), timeout=30)
        except OSError as e:
            log("CONNECT FAIL", self.path, e)
            self.send_error(502)
            return
        self.send_response(200, "Connection established")
        self.end_headers()
        self.close_connection = True
        a, b = self.connection, up
        try:
            while True:
                r, _, x = select.select([a, b], [], [a, b], 300)
                if x or not r:
                    break
                for s in r:
                    d = s.recv(65536)
                    if not d:
                        return
                    (b if s is a else a).sendall(d)
        finally:
            up.close()

    def _send(self, body, ctype="text/html; charset=utf-8"):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle(self):
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n) if n else b""

        if urllib.parse.urlsplit(self.path).path == "/excel":
            try:
                path = save_excel(body, os.path.expanduser("~/Downloads"))
                subprocess.Popen(["/usr/bin/open", path])
                _, sheets = parse_excel(body)
                log("EXCEL", os.path.basename(path), "sheets=%d rows=%d" %
                    (len(sheets), sum(len(rows) for _, rows in sheets)))
            except Exception as e:
                log("EXCEL FAIL", repr(e))
                self.send_error(500)
                return
            self._send(OK_XML, "text/xml; charset=UTF-8")
            return

        # 출력 팝업의 transaction. 127.0.0.1 이라 프록시 경유(절대 URL)·직접(상대 경로) 둘 다 올 수 있다
        if urllib.parse.urlsplit(self.path).path == "/ozwait":
            since = time.time() - 5
            with OZ_DONE:
                ok = OZ_DONE.wait_for(lambda: LAST_OZ[0] >= since, timeout=20)
            log("OZWAIT", "ok" if ok else "timeout")
            self._send(OK_XML, "text/xml; charset=UTF-8")
            return

        # 브라우저가 받아 가는 자동 제출 페이지 (프록시 요청이 아닌 상대 경로)
        if self.path.startswith("/"):
            page = PAGES.get(self.path[len("/oz/"):]) if self.path.startswith("/oz/") else None
            if page is None:
                self.send_error(404)
            else:
                self._send(page)
            return

        u = urllib.parse.urlsplit(self.path)
        if u.hostname == OZ and u.path.endswith("OzRptHtml5.jsp") and self.command == "POST":
            fields = urllib.parse.parse_qsl(body.decode("utf-8", "replace"), keep_blank_values=True)
            # 출력 서버는 charset 없는 POST(브라우저 폼)를 ISO-8859-1 로 읽어 한글을 깨뜨린다. 값은 응답 페이지의
            # JS 문자열에 그대로 들어가므로 비ASCII 를 \uXXXX 로 보내면 브라우저가 한글로 푼다(SPEC 7절).
            # ponytail: BMP 밖 문자(\U........)는 JS 가 못 푼다. 학사 파라미터에 나올 일이 없어 두었다.
            inputs = "".join('<input type="hidden" name="%s" value="%s">'
                             % (html.escape(k), html.escape(v.encode("ascii", "backslashreplace").decode()))
                             for k, v in fields)
            cid = str(next(SEQ))
            PAGES[cid] = ('<meta charset="utf-8"><form method="post" action="%s">%s</form>'
                          '<script>document.forms[0].submit()</script>' % (html.escape(self.path), inputs)).encode()
            subprocess.Popen(["/usr/bin/open", "http://127.0.0.1:%d/oz/%s" % (PORT, cid)])
            log("OZ", cid, dict(fields).get("reportName"))
            self._send(INAPP)
            with OZ_DONE:
                LAST_OZ[0] = time.time()
                OZ_DONE.notify_all()
            return

        headers = {k: v for k, v in self.headers.items() if k.lower() not in HOP}
        patch = u.hostname == "ims.hansei.ac.kr" and u.path in PATCHES
        if patch:
            # 조건부·압축 요청을 빼고, 수정된 본문에 원본 캐시 검증자를 붙이지 않는다.
            headers = {k: v for k, v in headers.items()
                       if k.lower() not in ("if-modified-since", "if-none-match", "accept-encoding")}
        path = (u.path or "/") + ("?" + u.query if u.query else "")
        try:
            c = http.client.HTTPConnection(u.hostname, u.port or 80, timeout=120)
            c.request(self.command, path, body=body or None, headers=headers)
            r = c.getresponse()
            data = r.read()
            c.close()
        except Exception as e:
            log("FAIL", self.command, u.hostname, u.path, repr(e))
            self.send_error(502)
            return
        if patch and r.status == 200:
            data = patch_file(u.path, data)
        self.send_response_only(r.status, r.reason)
        for k, v in r.getheaders():
            if k.lower() in HOP or k.lower() in ("transfer-encoding", "content-length"):
                continue
            if patch and k.lower() in ("etag", "last-modified"):
                continue
            self.send_header(k, v)
        if r.status >= 200 and r.status not in (204, 304):
            self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    do_GET = do_POST = do_HEAD = do_PUT = do_DELETE = do_OPTIONS = _handle


if __name__ == "__main__":
    log("listening", PORT)
    http.server.ThreadingHTTPServer(("127.0.0.1", PORT), P).serve_forever()
