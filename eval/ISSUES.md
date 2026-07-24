# Các vấn đề về độ chính xác của pdf2docx (phát hiện qua eval/run_eval.py)

**Mục tiêu dự án / ưu tiên đánh giá** (xem thêm `../README.md`): file docx
đầu ra phải dễ *chỉnh sửa* — việc giảm thiểu lượng văn bản người dùng phải
gõ lại quan trọng hơn nhiều so với độ trung thực về hình thức/bố cục so với
PDF gốc. Vì vậy `text_sim` là chỉ số quan trọng nhất; `ssim`/số trang chỉ là
tín hiệu phụ, mang tính chẩn đoán. Một fix làm cải thiện `text_sim` là tốt
dù có làm giảm `ssim`/số trang; một fix làm giảm `text_sim` là xấu dù có
làm tăng `ssim`.

**Ghi chú về lần phân tích này (2026-07-24):** tài liệu này được viết lại
từ đầu sau khi chạy lại `eval/run_eval.py` (điểm số giống hệt lần chạy
trước — không có thay đổi code nào giữa hai lần) và điều tra lại độc lập,
từ bằng chứng thô (diff + XML docx + ảnh trang đã render), cả 6 mẫu trong
bộ eval hiện tại — không giả định các mục "Bug trong pdf2docx" của phiên
bản tài liệu trước vẫn còn đúng nguyên văn. Kết quả: phần lớn các bug cũ
được xác nhận lại nhưng **nghiêm trọng hơn/phổ biến hơn** so với ghi nhận
trước đó (đặc biệt #2 và #6 cũ, xem bên dưới), và phát hiện thêm một bug
mới, xuất hiện ở 5/6 mẫu, chưa từng được ghi nhận trước đây (chèn
`<w:tab/>` thừa giữa câu/giữa từ). **Số thứ tự bug đã được đánh lại từ đầu**
(B1, B2, ...) theo mức độ ảnh hưởng quan sát được hôm nay; mỗi mục đều ghi
chú số cũ tương ứng (nếu có) để tiện tra cứu chéo với lịch sử commit trước
đó. Mục "Đã fix" (fix #1/#2/#4/#5/#6 cũ) không bị đánh lại số vì đó là ghi
chép lịch sử đã xong, đã xác nhận vẫn còn đúng ở lần rà soát này (không
mẫu nào rò rỉ lại glyph marker bullet/số thứ tự).

Ảnh chụp nhanh từ lần chạy đầy đủ gần nhất (6 mẫu — `policy_claude_draft`
vẫn không có mặt, đã bị **xóa khỏi bộ mẫu** vì là tài liệu nội bộ bảo mật,
xem ghi chú riêng bên dưới bảng):

`run_eval.py` hiện báo cáo hai chỉ số về nội dung văn bản (xem phần chú
giải mà chính script eval in ra để biết định nghĩa chính xác):
- **`text_sim`** — độ tương đồng chuỗi từ trên toàn bộ tài liệu, không quan
  tâm khoảng trắng/xuống dòng (`text_diff_loose.txt`). Đây là chỉ số phản
  ánh "người dùng sẽ phải gõ lại bao nhiêu" — một đoạn văn bị dàn lại thành
  số dòng khác đi vẫn tính là giống hệt miễn là các từ xuất hiện theo đúng
  thứ tự đó.
- **`text_sim_strict`** — độ tương đồng ở cấp đoạn văn/hàng bảng
  (`text_diff.txt`), nhạy với việc một đoạn bị tách/gộp khác đi ngay cả khi
  các từ giống hệt nhau. Vẫn giữ lại vì hữu ích để phát hiện khác biệt về
  *cấu trúc*, nhưng không phải chỉ số chính để tối ưu.

**Cập nhật (2026-07-24, sau khi fix B3):** bảng dưới đây là số liệu mới nhất
sau khi fix bug B3 (chèn `<w:tab/>` thừa, xem mục "Đã fix" #7). Số liệu gốc
trước khi bắt đầu xử lý bug (dùng làm baseline cho toàn bộ phần phân tích
bug bên dưới) là: en/unicode 0.4933/0.9988/0.2857/35; vi/unicode/arial
0.8655/1.0000/0.6250/6; vi/unicode/calibri 0.7917/1.0000/0.8261/8;
vi/unicode/mixed 0.8187/0.9976/0.8814/7; vi/unicode/time-new-roman
0.8205/0.9622/0.5753/31; vietnamese_doc 0.8011/0.9342/0.6415/19; TỔNG
0.7651/0.9821/0.6392 (số trang không đổi qua các lần chạy, không lặp lại ở
đây).

| mẫu                          | ssim   | text_sim | text_sim_strict | changed | số trang (gốc/ra) |
|------------------------------|--------|----------|------------------|---------|-------------------|
| en/unicode                   | 0.4933 | 0.9988   | 0.5714           | 21      | 2 / 3             |
| vi/unicode/arial              | 0.8655 | 1.0000   | 0.6250           | 6       | 2 / 2             |
| vi/unicode/calibri            | 0.7917 | 1.0000   | 0.8696           | 6       | 2 / 2             |
| vi/unicode/mixed              | 0.8187 | 0.9976   | 0.9153           | 5       | 3 / 3             |
| vi/unicode/time-new-roman     | 0.8197 | 0.9622   | 0.6849           | 23      | 3 / 3             |
| vietnamese_doc                | 0.8007 | 0.9342   | 0.6792           | 17      | 2 / 2             |
| **TỔNG**                      | **0.7649** | **0.9821** | **0.7242**   |     |                   |

**Ghi chú:** `policy_claude_draft` (từng có mặt trong các lần chạy trước
khi bị xóa) đã bị **xóa khỏi `eval/samples/`** vì là một tài liệu nội bộ
bảo mật — không được commit vào git, không còn cách nào tái xác nhận qua
eval tự động.

## Đã fix

1. **Thiếu khoảng trắng giữa các từ, thường xảy ra ngay trước một nguyên âm
   có dấu tiếng Việt** — đã fix trong `pdf2docx/text/Spans.py` (ngưỡng
   khoảng cách để gộp span không tính đến độ rộng của glyph dấu).

2. **Ô bảng có nội dung nhiều dòng bị tách thành các hàng giả thừa** — root
   cause nằm ở `pdf2docx/table/TablesConstructor.py: _inner_borders()`: với
   bảng >2 cột, mọi khoảng cách hàng phát hiện được trong nội bộ từng cột
   đều bị coi là ranh giới hàng thật. Đã fix bằng cách lấy cột có số
   cụm-hàng phát hiện được ít nhất làm nguồn xác định số hàng thật (một cột
   chỉ có thể bị *chia quá mức* do wrap, không bao giờ bị chia thiếu).
   - **Vẫn còn đúng ở lần rà soát này** cho đúng trường hợp nó nhắm tới (một
     cột wrap, các cột khác không) — nhưng đây là một cơ chế **khác** với
     bug B1 bên dưới (nhiều cột cùng wrap một lúc), thứ vẫn đang gây vỡ bảng
     nặng ở cả `vietnamese_doc` và `vi/unicode/time-new-roman`. Đừng nhầm
     hai bug này là một.

4. **Marker bullet/số thứ tự được dựng lại thành list thật của Word** —
   root cause: pdf2docx ghi glyph marker (`●`, `○`, `"1."`, ...) như một
   run `<w:r><w:t>` thuần văn bản, không có `<w:numPr>` nào cả. Đã fix
   trong `pdf2docx/text/TextBlock.py` + `pdf2docx/common/docx.py`:
   `TextBlock._flatten_spans()` làm phẳng `(line, span)` thành chuỗi phẳng,
   `_detect_markers()` phát hiện marker qua text + so style với span nội
   dung theo sau, `_group_list_items()` tách block thành từng đoạn docx
   riêng gán style `List Bullet`/`List Number` qua `docx.apply_list_style()`.

5. **Marker bullet không được phát hiện khi style của nó trùng hệt với span
   nội dung theo ngay sau (false-negative của fix #4)** — đã tách điều kiện
   so-style ra khỏi nhánh `kind == ('bullet', ...)` trong `_detect_markers()`
   (`TextBlock.py`): bullet giờ được chấp nhận là marker chỉ dựa trên text,
   không cần so style (nhánh `('number', 0)` vẫn giữ so style, vì rủi ro
   false-positive ở số thứ tự vẫn thật). Cộng thêm `_is_list_marker_token()`
   ở `run_eval.py` để lọc token marker leftover khỏi so sánh `text_sim`.

6. **`_BULLET_MARKERS` (`TextBlock.py`) thiếu nhiều glyph bullet phổ biến
   khác** (vd. `■` U+25A0 không có, dù `▪` U+25AA đã có) — đã mở rộng cả
   `_BULLET_MARKERS` và `eval/run_eval.py`'s `_LIST_MARKER_GLYPHS` với một
   tập glyph đậm/nhạt/mũi tên phổ biến khác, cố tình loại trừ tick/dash vì
   rủi ro false-positive cao hơn.
   - **Xác nhận vẫn còn đúng ở lần rà soát này**: không có glyph bullet trần
     nào rò rỉ ra `text_diff.txt` của bất kỳ mẫu nào trong 6 mẫu hiện tại.

7. **Chèn `<w:tab/>` thừa giữa câu/giữa từ tại các ranh giới dòng bị wrap**
   (trước đây là B3 trong lần rà soát 2026-07-24) — thấy ở 5/6 mẫu: `en/unicode`
   (`"...service \tinstances."`), `vi/unicode/mixed` (`"...thời gian \tthực."`),
   `vi/unicode/time-new-roman` (`"...đến \t4096 bit."`), `vi/unicode/calibri`
   (giữa một từ: `"...ỷ\t ỹ"`), `vietnamese_doc` (`"...phức \t\ttạp."`,
   `"Gán cho: \tPerson"`). Root cause + fix, cả hai trong
   `pdf2docx/text/Lines.py: Lines.parse_tab_stop()`:
   - **(1) Bug nền:** hàm này tính tab-stop cho *mọi* block, kể cả những
     block không có dòng nào thật sự nằm cùng hàng (`in_same_row()`) với
     dòng khác — nghĩa là mọi chênh lệch x0 trong block chỉ là cấu trúc đoạn
     văn bình thường (vd. marker bullet bắt đầu xa lề trái hơn dòng tiếp nối
     của chính nó). Fix: bỏ qua toàn bộ tính tab-stop nếu không có cặp dòng
     nào `in_same_row()` với nhau trong block.
   - **(2) Bug còn sót lại sau (1):** với block *có* một cặp marker+nội dung
     thật sự cùng hàng (vd. `●` là một `Line` riêng, cùng hàng với dòng nội
     dung theo sau — tab ở đây là đúng, cần giữ), biến tham chiếu `ref` vẫn
     bị reset về mép trái tuyệt đối của cả block mỗi khi dòng hiện tại
     không `in_same_row()` với dòng kế tiếp — khiến dòng tiếp nối tự nhiên
     của nội dung (vốn có x0 trùng với dòng nội dung nó tiếp nối, không phải
     mép trái block) bị coi nhầm là một cột tab mới. Fix: khi thoát khỏi một
     cặp cùng-hàng, reset `ref` về x0 của chính dòng vừa xử lý xong, không
     phải mép trái tuyệt đối của block.
   - **Verify:** chạy lại `eval/run_eval.py` sau mỗi phần fix — `text_sim`
     và `ssim`/số trang không đổi ở bất kỳ mẫu nào (chênh lệch ssim
     ±0.0002-0.0008 chỉ là nhiễu render LibreOffice đã biết), `text_sim_strict`
     cải thiện rõ ở mọi mẫu bị ảnh hưởng (xem bảng điểm số ở đầu file để biết
     số liệu chi tiết trước/sau). Xác nhận hết hoàn toàn bằng
     `grep -rn '\t' eval/results/*/text_diff*.txt eval/results/*/*/text_diff*.txt`
     — không còn dòng `+`/`-` nào chứa tab trong toàn bộ 6 mẫu.

**Lưu ý về môi trường:** file `input.pdf` fallback tự sinh (dùng khi một
mẫu chỉ có `original.docx`) được cache xuống đĩa ngay lần dùng đầu, vì việc
render docx→pdf của LibreOffice có độ rung (jitter) trong cách dàn trang
giữa các lần chạy, nếu không cache sẽ khiến điểm số trôi dạt qua từng lần
chạy mà không có lý do thực sự nào. Cũng cần nghi ngờ bất kỳ lần chạy eval
đơn lẻ nào ngay sau khi máy/container vừa khởi động lại (cache fontconfig
của LibreOffice "lạnh" có thể làm sai lệch cách phân trang lần đầu).

## Đã thử và revert

3. **`space_before` lớn một cách vô lý ở đoạn văn đầu tiên của trang/section
   mới** (root cause của bug B4(c) bên dưới) — cộng với một tối ưu bổ sung
   về số lượng ngắt section.
   - **Root cause (đã xác nhận qua instrument trực tiếp):**
     `RawPage.calculate_margin()`/`parse_section()` (`pdf2docx/page/RawPage.py`)
     tính margin trang/ranh giới section từ hợp bbox của `self.blocks` và
     `self.shapes`, trước đây chỉ loại trừ `Hyperlink`. Một shape `Fill`
     trắng phủ toàn trang (nền trang trí, vô hình trên giấy trắng) bị tính
     vào không lọc, làm méo margin trên tính được xuống gần ~0, lan thành
     `space_before` vô lý (~68-72pt) cho đoạn văn đầu tiên của section mới.
   - **Fix đã thử:** `RawPage._visible_shapes()` loại trừ thêm một `Fill`
     trắng chỉ khi nó *đồng thời* phủ ≥90% chiều rộng và chiều cao trang
     (phân biệt với `Fill` trắng nhỏ hợp lệ, vd. nền ô bảng).
   - **Tối ưu bổ sung cũng đã thử** (`pdf2docx/page/Page.py`):
     `Page._matches_section()` dùng `add_page_break()` thường thay vì tạo
     section mới khi kích thước/margin trang khớp section docx hiện tại.
   - **Lý do revert:** kết hợp lại, hai fix này làm giảm `ssim`/số trang
     trên vi/unicode/calibri (2→3 trang, ssim 0.7926→0.5472) và en/unicode
     (gần như không đổi). `text_sim`/`text_sim_strict` giống hệt
     byte-by-byte trước/sau — nhưng người dùng yêu cầu revert ("có vẻ nó k
     work" — 2026-07-24) trước khi bắt đầu làm bug marker list. **Hiện đã
     revert; `RawPage.py`/`Page.py` trở về trạng thái trước fix.** Xem bug
     B6 bên dưới để biết root cause khác gây regression ssim/số trang,
     thứ sẽ tái xuất hiện nếu fix này được thử lại.
   - **Nếu thử lại fix này trong tương lai:** hãy root-cause bug B6 trước
     (hoặc làm song song) — đó mới là thứ thực sự gây regression số trang
     một khi margin được tính đúng.

## Bug trong pdf2docx (thật, đáng để fix — đánh số lại theo mức ảnh hưởng quan sát được hôm nay)

**Ghi chú:** B3 (chèn `<w:tab/>` thừa) đã được fix — xem mục "Đã fix" #7.
Số thứ tự B1, B2, B4, B5, B6 giữ nguyên (không dồn lại) để khỏi phải sửa lại
toàn bộ tham chiếu chéo đã có trong tài liệu này.

### B1. Dòng tiếp nối của một khối bị wrap (hàng bảng, list item, đoạn văn) rơi hẳn ra khỏi khối cha — bug cấu trúc nghiêm trọng nhất hiện tại (trước đây là #6 + #7)

- **Root cause đã xác nhận** trong `pdf2docx/common/Collection.py:
  is_flow_layout()`: hàm này trả về `True` (tức "văn bản thường") ngay khi
  một cụm chỉ có một dòng (`if len(self)<=1: return True`), không cần biết
  gì thêm. Dòng tiếp nối của một ô/khối bị wrap thường không chồng lấn theo
  chiều dọc với bất kỳ nội dung nào khác ở đúng vị trí y đó, nên tạo thành
  một cụm một-dòng-đơn-độc và bị phân loại nhầm là văn bản thường — đóng
  bảng/khối đang dựng dở trước khi logic ranh giới hàng (`_inner_borders`,
  bug #2 ở mục Đã fix) kịp thấy nó.
- **Thấy ở, nghiêm trọng hơn nhiều so với ghi nhận trước đây:**
  - `vietnamese_doc` — bảng "Complex Table" 3 hàng dữ liệu bị vỡ thành
    **5 `<w:tbl>` riêng biệt xen kẽ 4 đoạn văn trần** (đã xác nhận qua dump
    cấu trúc `python-docx`), vd. hàng 01 "Quản lý người dùng..." vỡ ra
    thành đoạn trần "Quản lý \nngười " + bảng
    `01 | dùngMàn hình đăng | 2 | ... | Gán cho: Person` + đoạn trần "nhập
    & Chỉnh \nsửa profile ". Ảnh render (`output_p01.png`) xác nhận vỡ
    **nhìn thấy được rõ ràng** — chữ đè lên nhau, bị cắt bởi viền hàng.
  - `vi/unicode/time-new-roman` — bảng CRM 5 hàng bị vỡ theo đúng cơ chế
    này ở **cả 5/5 hàng**, không phải cá biệt như tài liệu cũ ngụ ý: mỗi
    hàng ra thành một `<w:tbl>` riêng + một đoạn văn trần mồ côi chứa dòng
    wrap đầu của ô "Mô tả chi tiết" (vd. `"Thêm trường "Tên công bố sản "`
    đứng một mình giữa hai bảng). Đây là nguyên nhân chính của 31 dòng
    `changed` (ước tính ~18-23/31 dòng).
- **Bug cũ #7 (header bảng lặp lại + mảnh vỡ mồ côi sau ngắt trang) không
  phải một root cause độc lập — đó là hệ quả của B1.** Kiểm tra
  `original_p02.png` của `vietnamese_doc`: nguồn thật **không hề** có bảng
  tràn qua trang 2 (toàn bộ 3 hàng vừa gọn trang 1). Chính vì B1 làm bảng
  phình to/vỡ vụn nên phần đuôi của hàng 03 mới bị đẩy sang trang 2, và
  mảnh `<w:tbl>` mồ côi đó lại lặp lại nguyên văn hàng tiêu đề. **Fix B1
  đúng cách sẽ tự động dọn luôn #7**, không cần fix riêng.
- **Cùng root cause, biểu hiện khác, thấy thêm ở list bullet (mới):**
  `vi/unicode/calibri` — dòng tiếp nối của một bullet item bị wrap 2 dòng
  đôi khi bị tách thành `<w:p>` riêng (phá vỡ bullet/indent, xác nhận
  **nhìn thấy được** qua ảnh render: "font." văn trôi ra ngoài list, bullet
  kế tiếp bị đẩy lề trái ngoài khối list), đôi khi bị gộp lại nhưng kèm một
  `<w:tab/>` thừa chèn giữa từ (xem B3). Cùng cơ chế wrapped-continuation-
  line-không-được-merge-đúng, chỉ khác là biểu hiện ở list thay vì bảng.
- **Một fix đã thử và revert trong phiên làm việc trước:** cho một
  hàng-một-dòng-đơn-độc "tiếp nối" bảng đang mở nếu nó thẳng cột với nội
  dung hiện có, thay vì luôn đóng bảng. Giải quyết được vietnamese_doc
  nhưng gây regression lan rộng (list bullet và header/footer trang bị hút
  vào bảng giả ở nhiều mẫu khác) — đã revert.
- **Chưa fix.** Cần một tín hiệu chính xác hơn chỉ-chồng-lấn-trục-x đơn
  thuần — có thể kết hợp thẳng cột + tỷ lệ khoảng-cách-dọc/chiều-cao-dòng,
  và/hoặc giới hạn theo font/cỡ chữ của dòng đơn độc khớp với ngữ cảnh
  đang mở (bảng hoặc list item), verify từng bước với toàn bộ tập mẫu.

### B2. Cặp nhãn:giá trị (label:value) bị dựng thành bảng giả — giờ xác nhận có **mất/trùng dữ liệu thật**, không chỉ sai định dạng (trước đây là #2)

- **Thấy ở 3/6 mẫu, mức độ tăng dần:**
  - `vi/unicode/mixed`: nguồn có 2 cặp label giống hệt nhau về cấu trúc
    ("Người"/"Người kiểm định" và "Ngày"/"Ngày thực hiện", mỗi cặp 1 `<w:p>`
    với `<w:br/>` mềm ở giữa) — chỉ **1 trong 2** cặp bị tách thành bảng giả
    1 hàng × 2 cột (`"Ngày"`), cặp còn lại giữ nguyên là đoạn văn bình
    thường. Cho thấy điều kiện kích hoạt bug này là một ngưỡng biên, không
    phải quy tắc cứng — xác nhận qua XML `python-docx`.
  - `vi/unicode/time-new-roman`: `"Ngày lập: Date"` → bảng, và ô giá trị
    còn chứa **một `<w:tbl>` lồng bên trong `<w:tc>`** (bảng trong ô bảng)
    để tô nền xám cho "Date". `eval/run_eval.py` không đệ quy vào bảng
    lồng khi trích text nên "Date" biến mất khỏi diff (`+Ngày lập: |`
    trống sau dấu `|`) — đây là điểm mù của công cụ eval (chữ vẫn tồn tại
    thật trong output.docx), nhưng cấu trúc bảng-lồng-trong-bảng tự nó là
    một bug cấu trúc thật, nghiêm trọng hơn mô tả cũ.
  - `vietnamese_doc`: `"Ngày tạo tài liệu kiểm thử: Date"` /
    `"Người thực hiện kiểm tra: Person"` (1 đoạn văn, `<w:br/>` mềm ở giữa)
    → bảng 2 hàng × 3 cột thật: `row0 = ['Ngày tạo tài liệu kiểm thử: ', '',
    '​']`, `row1 = ['Người thực hiện kiểm tra: ', 'Person', 'Person']`
    — **"Date" biến mất hoàn toàn** (thay bằng ô rỗng + zero-width space
    còn sót), **"Person" bị nhân đôi** ra 2 ô. Đây là mất/trùng dữ liệu
    thật, không chỉ một hàng bảng thừa vô hại. Ảnh render cho thấy có icon
    nhỏ (avatar/placeholder) nằm sát giá trị ở vị trí này — nghi vấn (chưa
    xác nhận) là icon đè lên bbox của giá trị làm logic tách cột bị nhầm.
- **Chưa root-cause đầy đủ**, nhưng bằng chứng đủ mạnh để nâng ưu tiên fix
  bug này lên cao hơn xếp hạng trước đây (từng bị coi là "chỉ mang tính
  thiết kế, ưu tiên thấp") — vì giờ đã xác nhận có mất dữ liệu thật, không
  chỉ sai định dạng trình bày.

### B4. Không nhất quán khi tách/gộp đoạn văn tại ranh giới dòng bị wrap (gộp 4 biến thể, trước đây là #3(a)/(b)/(c) + biến thể mới (d))

- **(a) Auto-wrap dựng sai vị trí xuống dòng khi thiếu `<w:br/>` cứng:**
  `en/unicode` (đoạn "cloud-native architectures..." — 3 dòng ở nguồn ra
  thành 4 dòng ở output, dòng cuối "independently without" trơ trọi — xác
  nhận qua so pixel ảnh render), `vi/unicode/time-new-roman` (tiêu đề
  "TỔNG HỢP DỮ LIỆU..." có `<w:br/>` sau "ĐA" nhưng không có sau "TRỊ" —
  cùng một `<w:p>`, chỉ là hard-break không nhất quán). Một `<w:p>` duy
  nhất nhưng số dòng dựng lại sai khác so nguồn — bug thật, nhìn thấy được.
- **(b) Tách thành 2 `<w:p>` nhưng bù `space_before` ≈ chiều cao dòng nên
  vô hình:** `en/unicode` ("Technical Implementation: Microservices" /
  "Architecture") — đã xác nhận qua so ảnh, không có khác biệt nhìn thấy
  được. Ưu tiên thấp, chỉ là điểm lạ về cấu trúc (ảnh hưởng tìm/thay thế
  theo câu, điều hướng con trỏ, screen reader).
- **(c) `space_before` vô lý (~68-72pt) ở đoạn văn đầu tiên của section
  mới** — root cause đã xác nhận ở mục "Đã thử và revert" #3 (shape `Fill`
  trắng phủ toàn trang làm méo margin trên). Thấy ở `en/unicode` (**nhìn
  thấy được**: trang gần trống, gây tràn trang 2→3, kéo ssim xuống
  0.4933) và `vi/unicode/arial` (cùng defect cấu trúc y hệt, xác nhận qua
  XML — nhưng **lần này vô hình** vì đoạn văn đó tình cờ là đoạn đầu tiên
  của trang, và LibreOffice/Word đều bỏ qua `space_before` cho đoạn đầu
  trang). **Tinh chỉnh so với ghi nhận trước:** mức độ hiển thị phụ thuộc
  cả vị trí trang (đầu trang hay không), không chỉ renderer.
- **(d) MỚI — chiều ngược lại: gộp 2 đoạn văn nguồn thật thành 1 `<w:p>`
  qua `<w:br/>` cứng.** `vi/unicode/arial`: tiêu đề "Bài Toán Quy Nạp và
  Nghịch Lý Con Gà Tây" (font/size/màu riêng) và đoạn thân bài (font/size/
  màu khác hẳn) — 2 đoạn văn riêng biệt ở nguồn — bị fuse thành một
  `<w:p>` duy nhất nối bằng `<w:r><w:br/></w:r>`, chỉ giữ lại `pPr`
  (spacing/indent) của đoạn đầu. Xác nhận qua `python-docx`. Hiện **vô
  hình** khi render (pixel gần như giống hệt), nhưng về cấu trúc là sai —
  cùng họ bug với (a), chỉ ngược hướng (gộp thay vì tách).

### B5. Cột bảng bị xóa hoàn toàn khi mọi giá trị trong đó đều rỗng (trước đây là #5)

- Thấy ở: chỉ mới `en/unicode` — cột `Status` (mọi ô rỗng ở nguồn) biến
  mất hoàn toàn khỏi output (4 cột còn 3), chưa tái hiện ở mẫu khác dù đã
  rà soát lại toàn bộ 6 mẫu lần này. Root cause khả dĩ: phát hiện ranh
  giới cột dựa vào nội dung không-phải-khoảng-trắng, cột toàn rỗng không
  có ký tự nào để bám vào.

### B6. Nội dung dựng lại chiếm nhiều không gian dọc hơn PDF gốc một chút — chỉ hiện ra khi margin trang được tính đúng (trước đây là #8)

- Hiện đang **ẩn/bị che** vì fix margin ở mục "Đã thử và revert" #3 đang
  bị revert (margin trang lại bị tính sai gần bằng 0, tình cờ để dư không
  gian dọc che giấu bug này). Nó chỉ hiện ra thành regression số trang/ssim
  thật một khi margin được tính đúng.
- Chưa root-cause được cơ chế cụ thể — đáng làm trước khi thử lại fix của
  mục "Đã thử và revert" #3, để fix đó có thể land mà không phải đánh đổi
  ssim/số trang.

## Không phải bug pdf2docx — fixture lỗi thời

- **`vi/unicode/time-new-roman/original.docx` bị lệch (stale) so với
  `input.pdf` của chính mẫu đó.** Cột "Phụ trách"/"Trạng thái" của bảng CRM
  trống ở cả 5 hàng trong `original.docx`, nhưng xác nhận qua trích xuất
  text trực tiếp từ `input.pdf` (PyMuPDF) rằng PDF nguồn thật sự có nội
  dung ở các ô đó ("VƯƠNG", "Hoàn thành", "ĐĂNG", "Nguyễn T. Dũng", "Đã
  tiếp nhận", "Chờ xử lý"...). Output của pdf2docx **đầy đủ hơn** "ground
  truth" ở đây — một phần nhiễu trong diff của mẫu này đến từ fixture lỗi
  thời, không phải lỗi pdf2docx. Cần cập nhật lại `original.docx` của mẫu
  này để nó khớp `input.pdf` nếu muốn dùng mẫu này đo chính xác bug B1.

## Phát hiện phụ, mức độ thấp (không cần ưu tiên ngay)

- **Zero-width space (U+200B) được giữ nguyên từ nguồn PDF vào text output**
  (`vietnamese_doc`, 2 lần thấy: `"Alignment):​"`, `"Nam​"`). Có thể là
  trích xuất trung thực một ký tự vô hình thật sự có trong PDF nguồn (mẫu
  này vốn là bộ test stress-format) — không có ảnh hưởng hình ảnh/cấu trúc,
  chỉ gây nhiễu âm thầm khi so `text_sim_strict`. Có thể đáng để pdf2docx
  lọc bỏ các ký tự control/zero-width vô hình vì chúng không có mục đích
  hiển thị nào, nhưng mức độ ưu tiên thấp.
- **Một số list item giữ lại `\t` đầu dòng, một số không** (`vietnamese_doc`,
  khối "Kiểm tra phân cấp danh sách": chỉ 2/6 item giống hệt nhau về hình
  thức còn giữ `\t` đầu chuỗi). Vô hình khi render (Word bỏ qua khoảng
  trắng đầu dòng) nhưng gây nhiễu `.text`/copy-paste. Có thể cùng cơ chế
  với B3 — đáng xem lại chung khi fix B3.

## Artefact của công cụ diff (không phải bug pdf2docx — chỉ là nhiễu trong cách mình so sánh)

- **Một đoạn văn chứa `<w:br/>` (ngắt dòng mềm) có thể trông như bị tách
  thành nhiều đoạn trong `text_diff.txt`, dù nó là một phần tử `<w:p>` duy
  nhất.** `paragraph.text` của `python-docx` render mỗi `<w:br/>` thành một
  ký tự `"\n"` thuần; khi ghi ra file diff, newline nhúng đó in ra thành
  một dòng vật lý thừa **không có dấu `+`/`-` ở đầu**.
  - **Quy tắc đọc:** trong `text_diff.txt`, một dòng không có tiền tố
    `+`/`-` là phần tiếp nối do wrap mềm của dòng phía trên, KHÔNG phải một
    đoạn văn/hàng riêng biệt. Chỉ những dòng tự nó bắt đầu bằng `+`/`-` mới
    thực sự là đoạn văn hoặc hàng bảng riêng biệt. Luôn xác minh một nghi
    ngờ tách-đoạn-văn bằng XML thô trước khi tin vào diff văn bản đơn
    thuần — và ngay cả một tách XML đã xác nhận cũng không tự động là bug
    nhìn thấy được (xem B4(b) vs B4(a)/(c)); chỉ render cả hai tài liệu ra
    PDF/PNG rồi so sánh pixel thật mới xác định được.
- **Glyph dấu tick/ký hiệu**: các ô trong original.docx hiện trống trong
  diff của mình trong khi output hiện `✓`. Thuộc tính `.text` của
  `python-docx` không đọc một số glyph font ký hiệu giống cách trích xuất
  văn bản PDF làm — không phải khiếm khuyết chuyển đổi, chỉ là một lỗ hổng
  trong `extract_text_lines()`.
- **Header/footer trong original.docx hoàn toàn không được so sánh**:
  `Document.paragraphs` trong `python-docx` không bao gồm nội dung
  `section.header`/`section.footer`, nên văn bản header/footer thật trong
  original.docx không bao giờ xuất hiện ở phía `-` của diff.
- **Bảng lồng trong ô bảng (`<w:tbl>` bên trong `<w:tc>`) không được đệ quy
  khi trích text** — xem B2, mẫu `vi/unicode/time-new-roman`: nội dung
  "Date" thật sự tồn tại trong output.docx nhưng biến mất khỏi diff vì
  `extract_text_lines()` không đi vào bảng lồng. Cần sửa nếu muốn eval
  không đánh giá thấp các trường hợp bảng-lồng-trong-bảng của B2.

## Đề xuất bước tiếp theo (chưa bắt đầu — triage/ưu tiên sau)

Xếp hạng lại theo bằng chứng thu thập được hôm nay (mức ảnh hưởng quan sát
được + độ rõ ràng của giả thuyết root cause, không chỉ theo `text_sim`).
B3 (chèn `<w:tab/>` thừa) đã fix — xem mục "Đã fix" #7, không còn trong
danh sách này:

1. **B2 (label:value → bảng giả, có mất dữ liệu thật)** — ưu tiên tăng lên
   so với trước (từng bị coi là ưu tiên thấp/mang tính thiết kế); giờ đã
   xác nhận có mất/trùng dữ liệu thật ("Date" biến mất, "Person" nhân đôi
   ở vietnamese_doc), không chỉ sai định dạng trình bày.
2. **B1 (dòng tiếp nối rơi khỏi bảng/list)** — bug gây thiệt hại nặng nhất
   ở từng mẫu bị ảnh hưởng (dominant cause của 31 dòng changed ở
   time-new-roman, vỡ bảng nhìn thấy rõ ở vietnamese_doc, dọn luôn được #7
   cũ) nhưng rủi ro hơn: fix duy nhất đã thử từng gây regression lan rộng.
   Cần tín hiệu phát hiện chính xác hơn (thẳng cột + tỷ lệ khoảng-cách-dọc/
   chiều-cao-dòng, giới hạn theo font/cỡ chữ khớp ngữ cảnh) trước khi thử
   lại, verify từng bước với toàn bộ tập mẫu.
3. **B4(a)/(d)** — bug thật, nhìn thấy được ở (a), chưa thấy ảnh hưởng
   hình ảnh ở (d) nhưng sai về cấu trúc; chưa có ai thử fix. B4(c) đã có
   fix (bị revert) — nên root-cause B6 trước khi thử lại B4(c)/mục "Đã thử
   và revert" #3. B4(b) ưu tiên thấp (vô hình, chỉ mang tính cấu trúc).
4. **B5 (cột rỗng bị xóa)** — chỉ mới thấy ở 1/6 mẫu (en/unicode), ưu tiên
   thấp cho đến khi thấy lặp lại ở mẫu khác.
5. **B6** — nên root-cause song song hoặc trước khi thử lại fix margin của
   mục "Đã thử và revert" #3, để fix đó land mà không đánh đổi ssim/số
   trang.

Ngoài ra: cập nhật `vi/unicode/time-new-roman/original.docx` cho khớp
`input.pdf` (xem mục "Không phải bug pdf2docx") để mẫu này đo B1 chính xác
hơn, và cân nhắc sửa `extract_text_lines()` để đệ quy vào bảng lồng
(giúp B2 không bị đánh giá thấp bởi chính công cụ eval).
