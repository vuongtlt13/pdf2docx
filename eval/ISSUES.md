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

**Cập nhật (2026-07-24, sau khi fix B4(a)/B4(d) và regenerate fixture
`vi/unicode/time-new-roman/original.docx`):** bảng dưới đây là số liệu mới
nhất, thay thế bảng ở trên. Hai thay đổi kể từ bảng trước: (1) fix B4(a)
(free-space heuristic không phân biệt được ngắt dòng chủ ý với word-wrap
tự nhiên — xem "Đã fix" #9) và B4(d) (`_join_lines_vertically` thiếu check
font/size — xem "Đã fix" #10); (2) fixture `time-new-roman/original.docx`
được điền lại cột "Phụ trách"/"Trạng thái" (trước đó trống, lệch so với
`input.pdf` — xem mục "Không phải bug pdf2docx — fixture lỗi thời"), giúp
điểm số của mẫu này phản ánh đúng bug B1 thật thay vì lẫn nhiễu từ fixture.

| mẫu                          | ssim   | text_sim | text_sim_strict | changed | số trang (gốc/ra) |
|------------------------------|--------|----------|------------------|---------|-------------------|
| en/unicode                   | 0.6963 | 0.9988   | 0.6122           | 19      | 2 / 2             |
| vi/unicode/arial              | 0.9163 | 1.0000   | 0.8235           | 3       | 2 / 2             |
| vi/unicode/calibri            | 0.7917 | 1.0000   | 0.8696           | 6       | 2 / 2             |
| vi/unicode/mixed              | 0.8187 | 0.9976   | 0.9153           | 5       | 3 / 3             |
| vi/unicode/time-new-roman     | 0.8183 | 0.9653   | 0.7397           | 19      | 3 / 3             |
| vietnamese_doc                | 0.8005 | 0.9342   | 0.6792           | 17      | 2 / 2             |
| **TỔNG**                      | **0.8069** | **0.9826** | **0.7733**   |     |                   |

Sau khi loại bỏ nhiễu fixture, `vi/unicode/time-new-roman` vẫn còn text_sim
0.9653/text_strict 0.7397 (thay vì 1.0/~1.0 nếu không có bug) — phần chênh
lệch còn lại ở mẫu này (và ở `vietnamese_doc`, mẫu thấp điểm nhất) gần như
hoàn toàn do **B1** (nội dung ô bảng bị văng ra ngoài bảng thành đoạn văn
rời rạc khi chiều cao hàng không đều), theo `text_diff_loose.txt` của cả
hai mẫu. B1 hiện là bug ảnh hưởng lớn nhất còn lại tới `text_sim` — quyết
định có đầu tư fix hay tiếp tục hoãn thuộc về đánh giá rủi ro/lợi ích của
người dùng.

**Cập nhật (2026-07-27, sau khi fix B1 một phần):** bảng dưới đây thay thế
bảng ở trên. Xem "Đã fix" #11 để biết chi tiết root cause/fix/verify.

| mẫu                          | ssim   | text_sim | text_sim_strict | changed | số trang (gốc/ra) |
|------------------------------|--------|----------|------------------|---------|-------------------|
| en/unicode                   | 0.6963 | 0.9988   | 0.6122           | 19      | 2 / 2             |
| vi/unicode/arial              | 0.9163 | 1.0000   | 0.8235           | 3       | 2 / 2             |
| vi/unicode/calibri            | 0.7917 | 1.0000   | 0.8696           | 6       | 2 / 2             |
| vi/unicode/mixed              | 0.8187 | 0.9976   | 0.9153           | 5       | 3 / 3             |
| vi/unicode/time-new-roman     | 0.8179 | 0.9833   | 0.8235           | 12      | 3 / 3             |
| vietnamese_doc                | 0.8003 | 0.9342   | 0.7059           | 15      | 2 / 2             |
| **TỔNG**                      | **0.8069** | **0.9856** | **0.7917**   |     |                   |

So với bảng trước: `vi/unicode/time-new-roman` cải thiện rõ nhất (text_sim
0.9653→0.9833, text_strict 0.7397→0.8235, changed 19→12), `vietnamese_doc`
cải thiện nhẹ (text_strict 0.6792→0.7059, changed 17→15). 4 mẫu còn lại giữ
nguyên y hệt (không regression) — kể cả `vi/unicode/calibri` (có list
bullet) và `en/unicode` (có heading/list dài) là 2 mẫu có rủi ro regression
cao nhất theo bài học từ lần thử fix trước bị revert. ssim dao động
±0.0002-0.0004 ở 2 mẫu cải thiện chỉ là nhiễu render LibreOffice đã biết.
B1 **chưa đóng hẳn** — xem cập nhật trong mục B1 bên dưới về phần còn sót
lại (bảng tràn qua ngắt trang vẫn vỡ thành nhiều `<w:tbl>`, do một cơ chế
khác, chưa fix).

**Cập nhật (2026-07-27, sau khi fix B7 một phần):** bảng dưới đây thay thế
bảng ở trên. Xem "Đã fix" #12 để biết chi tiết root cause/fix/verify.

| mẫu                          | ssim   | text_sim | text_sim_strict | changed | số trang (gốc/ra) |
|------------------------------|--------|----------|------------------|---------|-------------------|
| en/unicode                   | 0.6963 | 0.9988   | 0.6122           | 19      | 2 / 2             |
| vi/unicode/arial              | 0.9163 | 1.0000   | 0.8235           | 3       | 2 / 2             |
| vi/unicode/calibri            | 0.7917 | 1.0000   | 0.8696           | 6       | 2 / 2             |
| vi/unicode/mixed              | 0.8187 | 0.9976   | 0.9153           | 5       | 3 / 3             |
| vi/unicode/time-new-roman     | 0.8178 | 0.9884   | 0.8657           | 9       | 3 / 3             |
| vietnamese_doc                | 0.8003 | 0.9342   | 0.7059           | 15      | 2 / 2             |
| **TỔNG**                      | **0.8068** | **0.9865** | **0.7987**   |     |                   |

So với bảng trước: `vi/unicode/time-new-roman` cải thiện tiếp (text_sim
0.9833→0.9884, text_strict 0.8235→0.8657, changed 12→9) nhờ hàng 3 của bảng
CRM được gộp lại đúng vào bảng chính. 5 mẫu còn lại giữ nguyên y hệt (không
regression). `vietnamese_doc` không cải thiện từ fix này — chưa rõ nguyên
nhân, để lại cho lần sau (xem đánh giá cuối mục "Đã fix" #12). Hàng 4/5 của
bảng CRM (time-new-roman) vẫn còn vỡ — sub-case "dòng ứng viên rộng hơn
dòng neo", chưa tìm được cách fix an toàn (xem "Đã thử và revert" trong
mục #12).

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

8. **Một Line bị append trùng 2 lần vào cùng 1 hàng bảng giả** (một phần
   root cause của bug B2 bên dưới) — `collect_stream_lines()`
   (`pdf2docx/layout/Blocks.py`) sau khi quyết định nhánh chính cho 1 hàng
   (flow layout / list item / hay stream-table column, append vào
   `table_lines`), có thêm 1 vòng lặp riêng, **không điều kiện**, append
   thêm mọi block trong hàng thoả `contained_in_shadings()` — kể cả những
   block *đã* được append ở nhánh else phía trên. Kết quả: 1 block vừa là
   cột bảng giả vừa nằm trong vùng tô nền thì bị thêm vào `table_lines`
   **2 lần**, tạo ra ô trùng lặp trong bảng dựng ra.
   - **Fix:** theo dõi các block đã append (`added` set các `id(block)`)
     ở nhánh chính, rồi bỏ qua chúng trong vòng lặp `contained_in_shadings()`.
   - **Verify:** `eval/run_eval.py` cho điểm số **giống hệt** baseline ở cả
     6 mẫu (không regression, không cải thiện đo được trên bộ mẫu hiện tại
     — bug này hiếm khi trùng điều kiện kích hoạt với B2, nhưng vẫn là 1
     lỗi thật cần fix để không lặp lại ở dữ liệu khác).

9. **B4(a) — `parse_line_break()` chèn `<w:br/>` cứng sai vào giữa một
   đoạn văn wrap tự nhiên** (`pdf2docx/text/Lines.py: parse_line_break()`)
   — hàm quyết định ngắt dòng cứng cho mỗi "hàng vật lý" trong một
   `TextBlock` dựa trên `free_space` (khoảng trống cuối hàng so với mép
   phải rộng nhất của cả block) vượt ngưỡng `line_break_free_space_ratio`
   (mặc định 0.1). Vấn đề: với một đoạn văn dài wrap tự nhiên (không có
   ngắt đoạn thật ở nguồn), vị trí wrap của mỗi dòng phụ thuộc hoàn toàn
   vào độ dài từ — một dòng có thể "tình cờ" chừa lại 10-13% khoảng trống
   chỉ vì từ tiếp theo không vừa, không phải vì tác giả chủ ý ngắt dòng ở
   đó. Ngưỡng 0.1 quá chặt để phân biệt 2 trường hợp này, gây false
   positive: `en/unicode`'s đoạn "The transition toward cloud-native
   architectures..." (free_space ratio 0.103 và 0.129, đều vượt ngưỡng
   nhưng chỉ vì từ tiếp theo — "understanding" rộng 81.6pt, "compromising"
   rộng 80.5pt — không vừa khoảng trống 46.2pt/57.7pt còn lại) và
   `vi/unicode/time-new-roman`'s tiêu đề "TỔNG HỢP DỮ LIỆU ĐA..." (ratio
   0.175, từ tiếp theo "MIỀN:" rộng 97.7pt > khoảng trống 79.7pt).
   - **Fix:** thêm hàm `_leading_word_width(line)` (đọc `char.bbox` từng
     ký tự tới khoảng trắng đầu tiên để đo bề rộng từ đầu tiên của hàng kế
     tiếp). Trong `parse_line_break()`, khi `free_space` vượt ngưỡng, chỉ
     giữ quyết định ngắt dòng nếu từ đầu tiên của hàng kế tiếp **thực sự
     vừa** trong khoảng trống đó (`next_word_width <= free_space`) — tức
     là dòng kết thúc sớm do chủ ý, không phải do từ tiếp theo không vừa.
     Chỉ áp dụng cho text ngang, alignment khác `RIGHT` (phạm vi hẹp, an
     toàn); logic `line_break` do block quá hẹp (`line_break_width_ratio`)
     và hàng cuối (luôn reset về không ngắt) giữ nguyên không đổi. Đây là
     thay đổi chỉ có thể chuyển `True→False` (bỏ bớt break sai), không bao
     giờ thêm break mới — giảm rủi ro regression.
   - **Verify:** `eval/run_eval.py` — `en/unicode`: ssim 0.4933→0.6963
     (2/3→2/2 trang, hết tràn trang), text_strict 0.5714→0.6122;
     `vi/unicode/time-new-roman`: text_strict 0.6849→0.7123; 4 mẫu còn lại
     điểm số giữ nguyên y hệt (không regression). Xác nhận trực tiếp qua
     `text_diff.txt`: cả 2 đoạn văn trên giờ xuất hiện là 1 dòng liên tục,
     đúng như bản gốc.

10. **B4(d) — `_join_lines_vertically()` gộp nhầm 2 đoạn văn khác hẳn
    font/size thành 1 `TextBlock` chỉ vì khoảng cách dọc nhỏ**
    (`pdf2docx/layout/Blocks.py: _join_lines_vertically()`) — docstring
    hứa hẹn gộp dòng "same properties (spacing, font, size)" nhưng code
    thực tế **chưa bao giờ so sánh font/size**, chỉ so khoảng cách dọc
    (`vertical_distance`) với `ref_dis` (khoảng cách dòng phổ biến nhất
    của *cả trang*, không phải cục bộ theo từng đoạn). Hệ quả: một tiêu
    đề cỡ chữ lớn (30pt) đứng ngay trên một đoạn thân bài (12pt) với
    khoảng cách dọc tình cờ nhỏ (6.4pt, nằm trong `ref_dis+1.0=6.9`) bị
    gộp làm một `TextBlock`, và vì tiêu đề không kết thúc bằng dấu câu nên
    `_split_text_block_vertically()`/`split_vertically_by_text()` (dựa
    tín hiệu dấu câu cuối câu + khoảng trống) không tách lại được — 2 đoạn
    văn nguồn thật hoá thành 1 `<w:p>` nối bằng `<w:br/>` cứng.
    - **Fix:** thêm điều kiện so sánh `line_height()` (chiều cao span có
      nhiều ký tự nhất trong dòng, đã có sẵn hàm helper) giữa dòng hiện
      tại và dòng kế tiếp — chỉ gộp nếu
      `max(h1,h2) <= max_line_spacing_ratio*min(h1,h2)`, tái dùng tham số
      `max_line_spacing_ratio` (1.5) đã có sẵn thay vì thêm ngưỡng mới.
      Title (33.5pt line height) vs body (13.4pt) có ratio 2.5 > 1.5 nên
      giờ tách đúng thành 2 block; 2 dòng title với nhau (ratio 1.0) hay
      2 dòng thân bài với nhau vẫn gộp bình thường.
    - **Verify:** `eval/run_eval.py` — `vi/unicode/arial`: ssim
      0.8655→0.9163, text_strict 0.6250→0.8235, changed 6→3 dòng; **5 mẫu
      còn lại điểm số giữ nguyên y hệt** (không regression). Xác nhận qua
      `python-docx`: tiêu đề và đoạn thân bài giờ là 2 `<w:p>` riêng biệt.

11. **B1 (một phần) — dòng tiếp nối bị wrap của một ô bảng đang mở, không
    chồng lấn dọc với dòng nào khác ở đúng y đó, bị `is_flow_layout()` phân
    loại nhầm thành văn bản thường, làm đóng bảng đang dựng dở quá sớm**
    (`pdf2docx/layout/Blocks.py: collect_stream_lines()`; root cause đúng
    như mô tả gốc trong mục B1 bên dưới: `is_flow_layout()` trả `True` ngay
    khi cụm chỉ có 1 dòng).
    - **Fix:** thêm hàm cục bộ `is_table_continuation_line(line)` trong
      `collect_stream_lines()`, gọi **trước** `row.is_flow_layout(...)` cho
      mọi hàng-1-dòng-đơn-độc. Khác với fix đã thử-và-revert trước đây (chỉ
      so thẳng cột), hàm này kết hợp **4 tín hiệu** để tránh đúng kiểu
      regression đã khiến lần thử trước bị revert (list bullet/header trang
      bị hút vào bảng giả):
      1. **Thẳng cột theo tỷ lệ riêng của dòng ứng viên** —
         `overlap/width_dòng_ứng_viên >= FACTOR_ALMOST (0.95)`, KHÔNG dùng
         `Element.vertically_align_with()` có sẵn vì hàm đó chuẩn hoá theo
         **min** bề rộng 2 bbox — một tiêu đề rộng toàn trang sẽ luôn "chồng
         lấn đủ" so với một cột hẹp bất kỳ nó tình cờ đè lên (đúng lỗi thiết
         kế gây ra regression header/footer lần trước). Chuẩn hoá theo bề
         rộng của chính dòng ứng viên loại bỏ được lỗ hổng này.
      2. **Khoảng cách dọc chặt**: `gap <= 2.0 * max(chiều_cao_2_dòng)`.
      3. **Font/chiều cao dòng tương đồng**: `max(h1,h2) <= 1.5*min(h1,h2)`
         (tái dùng đúng công thức + ngưỡng `max_line_spacing_ratio` đã có ở
         `_join_lines_vertically()`, xem "Đã fix" #10).
      4. **Không phải marker list** (`is_list_item(line.text)` — xem phát
         hiện phụ bên dưới) — cả cho chính dòng ứng viên, lẫn cho toàn bộ
         `table_lines` đang mở (nếu `table_lines` đã lỡ chứa 1 dòng marker,
         coi như "bảng" này thực chất là 1 list bị dựng nhầm, không mở rộng
         thêm vào nó nữa).
    - **Phát hiện phụ, phải fix kèm để (4) hoạt động được:**
      `pdf2docx/common/share.py: is_list_item()` có `return False` ở ngay
      dòng đầu thân hàm (che khuất ~40 dòng logic bên dưới nó — **luôn**
      trả `False` bất kể input gì). Đây là code chết có từ nguyên commit
      thượng nguồn giới thiệu hàm này (`bd3d1af`), không phải do phiên làm
      việc trước. Ban đầu tưởng vô hại vì nhánh gọi nó
      (`elif kwargs.get('list_not_table') and is_list_item(...)`) cũng
      không bao giờ chạy do kwarg `list_not_table` chưa từng được forward
      xuống `collect_stream_lines()` (xem ghi chú "dead code" ở B1 gốc) —
      nhưng khi thêm tín hiệu (4) ở trên, `is_list_item()` được gọi trực
      tiếp, không qua kwarg chết đó, nên `return False` thừa này **phải**
      được xoá thì tín hiệu (4) mới có tác dụng thật. Xoá dòng này không
      đổi hành vi ở đâu khác (nhánh `list_not_table` cũ vẫn chết y nguyên,
      chưa fix — vẫn ngoài phạm vi B1, xem ghi chú cũ).
    - **Không sửa `is_flow_layout()` trực tiếp** (để không đổi hợp đồng của
      nó với các nơi gọi khác) — chặn đúng tại điểm gọi trong
      `collect_stream_lines()`.
    - **Verify — chạy `eval/run_eval.py` sau khi fix, đối chiếu toàn bộ 6
      mẫu** (không chỉ 2 mẫu bị B1 ảnh hưởng rõ nhất):
      - `vi/unicode/time-new-roman`: text_sim 0.9653→0.9833, text_strict
        0.7397→0.8235, changed 19→12 (cải thiện, không regression).
      - `vietnamese_doc`: text_strict 0.6792→0.7059, changed 17→15 (cải
        thiện, text_sim/ssim không đổi).
      - `vi/unicode/calibri` (list bullet — rủi ro regression cao nhất theo
        bài học từ lần revert trước) và `en/unicode` (heading dài + list
        "Key technical considerations" — cũng rủi ro cao): **điểm số giữ
        nguyên y hệt**, xác nhận qua `text_diff.txt` không còn bullet nào bị
        gộp lẫn (thử nghiệm đầu tiên, trước khi fix dead-code `is_list_item`
        ở trên, ĐÃ gây đúng regression này trên `en/unicode`: 4 bullet
        "Service Discovery/Circuit Breaking/Distributed Tracing/Payload
        Serialization" bị gộp thành 1 dòng nối bằng `" | "` — text_strict
        0.6122→0.4783 — fix dead-code `is_list_item()` ở trên giải quyết
        đúng nguyên nhân, đưa điểm về lại baseline).
      - `vi/unicode/arial`, `vi/unicode/mixed`: không đổi.
    - **Xác nhận cấu trúc qua `python-docx`** (`body.findall(qn('w:tbl'))`):
      bảng CRM ở `time-new-roman` từ *mỗi hàng một `<w:tbl>` + 1 đoạn văn
      mồ côi chứa dòng wrap đầu* (mô tả gốc trong B1) giảm còn 1 `<w:tbl>`
      3 hàng (header + 2 hàng đầu, nằm trọn trang 1) nối tiếp 4 `<w:tbl>`
      1-hàng (4 hàng còn lại, đã tràn sang trang 2) — **không còn đoạn văn
      mồ côi giữa các bảng ở phần đã fix**, nhưng phần tràn trang vẫn vỡ
      thành nhiều bảng riêng (xem cập nhật B1 bên dưới — cơ chế khác, ngoài
      phạm vi fix này). `vietnamese_doc` tương tự: giảm từ 5 `<w:tbl>` xen 4
      đoạn văn mồ côi xuống 3 `<w:tbl>` xen 2 đoạn văn mồ côi.
    - **Đánh giá:** B1 **chỉ được giải quyết một phần** — đúng cơ chế mô tả
      gốc (dòng tiếp nối bị `is_flow_layout()` phân loại nhầm trong 1 vùng
      bảng liền mạch) đã fix, xác nhận qua cải thiện điểm số + cấu trúc,
      không regression ở mẫu nào. Phần còn sót lại (bảng tràn qua ngắt
      trang vẫn vỡ thành nhiều `<w:tbl>`) là **một cơ chế khác, chưa root
      cause** — xem cập nhật trong mục B1 bên dưới.

12. **B7 (một phần) — cột "Mô tả chi tiết" wrap khiến dòng ĐẦU của cột đó
    bắt đầu sớm hơn các cột còn lại trong cùng hàng logic, tách thành cụm
    vật lý riêng, đóng bảng quá sớm** (biến thể ngược hướng của B1 — xem
    root-cause đầy đủ trong mục B7 bên dưới).
    - **Fix:** tách phần logic dùng chung của fix #11 ra hàm riêng
      `lines_match(line, ref)` (4 tín hiệu y hệt #11: thẳng cột theo bề rộng
      RIÊNG của dòng ứng viên `overlap/width>=FACTOR_ALMOST`, khoảng cách
      dọc chặt, font/chiều cao tương đồng, không phải marker list), rồi
      thêm hàm mới `is_table_lookahead_line(line, next_row)` tái dùng
      `lines_match` nhưng đổi hướng so sánh: khi 1 hàng-1-dòng-đơn-độc không
      match **lùi** (lookback) với `table_lines`, thử match **xuôi** với
      hàng vật lý kế tiếp `rows[i+1]` — chỉ áp dụng khi (a) đã có bảng đang
      mở (`table_lines` non-empty, tức đây là tiếp nối chứ không phải bằng
      chứng 1 bảng mới bắt đầu) và (b) hàng kế tiếp **không phải** flow
      layout (`is_flow_layout()==False`, tức 1 hàng bảng thật đa cột).
      Vòng lặp đổi từ `for row in rows` sang `for i, row in enumerate(rows)`
      để truy cập `rows[i+1]`.
    - **Đã thử và revert: chuẩn hoá "thẳng cột" theo bề rộng NHỎ HƠN
      (symmetric) riêng cho lookahead.** Ý tưởng ban đầu: vì `next_row` đã
      được xác nhận `is_flow_layout()==False`, tưởng có thể nới lỏng tiêu
      chí thẳng cột từ "theo bề rộng riêng dòng ứng viên" sang "theo
      `min(bề_rộng_dòng, bề_rộng_ref)`" để bắt thêm ca dòng ứng viên **rộng
      hơn** dòng neo (hàng 4/5 của bảng CRM, xem bên dưới). Biến thể này quả
      thực fix nốt 2 hàng còn lại (`time-new-roman`: text_strict
      0.8657→0.9538, changed 9→3) — **nhưng gây regression thật trên
      `vi/unicode/mixed`** (text_sim 0.9976→0.9617, text_strict
      0.9153→0.7778, changed 5→12): 1 đoạn văn dài ("4. Kiểm tra ký tự đặc
      biệt và định dạng...") đứng ngay trước 2 dòng chữ ký ("Người kiểm
      định"/"Ngày thực hiện") bị hút vào bảng giả. Nguyên nhân: mỗi dòng chữ
      ký này bị PyMuPDF tách thành 2 mảnh không chồng-x (1 mảnh zero-width-
      space + 1 từ ngắn, ví dụ `'Ngày'` rộng chỉ ~25.7pt cạnh 1 ký tự
      `'​'`), nên `is_flow_layout()` nhầm hàng 2-mảnh này là "hàng bảng
      thật đa cột" (`len>1` + `group_by_columns()>1`) dù **không phải**
      (`original.docx` xác nhận khu vực này chỉ là đoạn văn + chữ ký, không
      có bảng nào). Khi chuẩn hoá theo `min` bề rộng, nhãn đầy đủ "Người
      kiểm định " (rộng ~92.4pt, là dòng cuối đoạn văn phía trên) chồng lấp
      đủ so với bề rộng NHỎ của mảnh `'Ngày'` (~25.7pt) → tỷ lệ ~1.0, match
      giả. Đây đúng loại lỗi thiết kế mà chuẩn hoá theo bề rộng riêng của
      dòng ứng viên (fix #11, tín hiệu 1) được dựng lên để chặn — chỉ là
      lần này lộ ra ở hướng lookahead thay vì lookback, và
      `next_row.is_flow_layout()==False` (do artefact zero-width-space) là
      tín hiệu "hàng kế tiếp là bảng thật" quá yếu để có thể nới lỏng thêm.
      Đã revert về chuẩn hoá theo bề rộng riêng dòng ứng viên cho cả 2
      hướng (lookback lẫn lookahead) — `lines_match()` chỉ có 1 công thức
      duy nhất, không còn tham số symmetric.
    - **Verify (bản đã giữ lại, an toàn) — chạy đủ 6 mẫu:**
      - `vi/unicode/time-new-roman`: text_sim 0.9833→0.9884, text_strict
        0.8235→0.8657, changed 12→9 (cải thiện, không regression).
      - `vietnamese_doc`: điểm số giữ nguyên y hệt (không đổi) — Complex
        Table không cải thiện với fix này (xem đánh giá bên dưới).
      - 4 mẫu còn lại (`en/unicode`, `vi/unicode/arial`,
        `vi/unicode/calibri`, `vi/unicode/mixed`): điểm số giữ nguyên y hệt
        bản trước fix #12 (không regression) — xác nhận đúng bộ 2 mẫu rủi
        ro cao nhất (`calibri`, `en/unicode`) không bị ảnh hưởng, và
        `vi/unicode/mixed` (nơi biến thể symmetric đã regression) sạch trở
        lại sau khi revert.
    - **Xác nhận cấu trúc qua `python-docx`:** bảng CRM ở `time-new-roman`
      — hàng 3 ("Quản lý khách hàng") giờ nằm gọn trong `<w:tbl>` chính (4
      hàng: header + 3 hàng dữ liệu) thay vì tách thành 1 `<w:tbl>` riêng.
      Hàng 4 và 5 **vẫn còn vỡ** thành 2 `<w:tbl>` 1-hàng riêng — đây là
      biến thể "dòng ứng viên RỘNG HƠN dòng neo ở hàng kế tiếp" (ví dụ hàng
      4: dòng ứng viên `'Bắn Auto Inbox cho Mộc San '` rộng ~108.2pt >
      dòng neo `'và lọc dữ liệu SĐT khách '` ở hàng kế tiếp chỉ ~92.8pt,
      nên `overlap/bề_rộng_riêng ≈ 0.857 < FACTOR_ALMOST`, bị từ chối đúng
      như thiết kế) — **chưa fix được sub-case này**, vì hướng nới lỏng duy
      nhất đã thử (chuẩn hoá theo min-width) bị chứng minh không an toàn ở
      trên.
    - **Đánh giá:** B7 **chỉ được giải quyết một phần** — sub-case "dòng
      ứng viên hẹp hơn/bằng dòng neo ở hàng kế tiếp" đã fix (hàng 3 của
      CRM). Sub-case "dòng ứng viên rộng hơn dòng neo" vẫn còn mở, chưa tìm
      được cách fix an toàn trong lần này. `vietnamese_doc` (Complex Table)
      không cải thiện chút nào (điểm số y hệt trước/sau fix #12) — có thể
      không rơi đúng vào cơ chế B7 (dòng đầu ô wrap lệch y sớm hơn hàng kế
      tiếp), hoặc rơi vào sub-case "rộng hơn" chưa fix được — **chưa điều
      tra riêng trong lần này, để lại cho lần sau.**

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

**Cập nhật (2026-07-27) — đã fix một phần, xem "Đã fix" #11 để biết chi
tiết root cause/fix/verify.** Cơ chế "dòng-tiếp-nối-1-dòng-đơn-độc bị
`is_flow_layout()` phân loại nhầm, ĐÓNG BẢNG QUÁ SỚM" mô tả trong mục này
**đã được xử lý** khi nó xảy ra trong cùng 1 vùng bảng liền mạch (không cắt
ngang bởi ngắt trang) — xác nhận qua cải thiện điểm số `text_sim`/
`text_sim_strict` ở cả `vi/unicode/time-new-roman` và `vietnamese_doc`,
không regression ở `vi/unicode/calibri` (list bullet) hay `en/unicode`
(list "considerations" + heading dài), 2 mẫu rủi ro cao nhất. Dự đoán ban
đầu trong mục "Vì sao khó fix an toàn" bên dưới (dải toạ độ y của 2 hàng
logic khác nhau chồng lấn nhau) **hoá ra không xảy ra trên bộ mẫu hiện
tại** — instrument trực tiếp cho thấy chỉ cần so cột theo tỷ lệ-của-chính-
dòng-ứng-viên (không phải theo `min` bề rộng như `vertically_align_with()`)
+ khoảng cách dọc + font-size + loại-trừ-list-marker là đủ phân biệt đúng,
không cần dựng lại theo cột-trước-hàng-sau như dự đoán.

**Phần CHƯA fix, phát hiện mới khi verify cấu trúc bảng CRM
(`vi/unicode/time-new-roman`) sau fix trên — xem B7 bên dưới để biết root
cause đầy đủ (đã xác nhận, KHÔNG liên quan ngắt trang PDF như suy đoán ban
đầu):** 3/5 hàng dữ liệu của bảng CRM vẫn vỡ ra thành `<w:tbl>` 1-hàng riêng
lẻ dù không còn đoạn văn mồ côi. Ghi chú ban đầu (khi mới phát hiện) từng
suy đoán đây là do "trang sau ngắt trang bị xử lý per-cột riêng lẻ" — suy
đoán đó **sai**, đã bị bác bỏ bằng instrument trực tiếp: toàn bộ 46 dòng của
bảng CRM (kể cả 5 hàng dữ liệu) được đưa vào **cùng một** lời gọi
`collect_stream_lines()` duy nhất, không hề có ranh giới trang nào ở giữa.
Root cause thật là một biến thể khác của đúng cơ chế B1 (dòng đơn độc bị
`is_flow_layout()` phân loại nhầm) nhưng neo tham chiếu nằm ở hàng **PHÍA
SAU** chứ không phải hàng đã tích luỹ trước đó, nên fix #11 (chỉ nhìn lùi về
`table_lines` đã có) không bắt được. Xem B7 để biết chi tiết + hướng fix đề
xuất.

**Nội dung gốc bên dưới (trước 2026-07-27), giữ nguyên để tham khảo lịch
sử:**

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
- **Cập nhật (2026-07-24), root cause hoá ra sâu hơn ghi nhận trước đây:**
  đã instrument trực tiếp `collect_stream_lines()` (in từng `row` — group
  block theo `group_by_rows()` — thay vì chỉ dòng đơn lẻ, để tránh nhiễu vì
  hàm này chạy 2 lần/trang: lần 1 xử lý nội dung thật, lần 2 xử lý lại các
  mảnh vỡ mồ côi đã bị văng ra ở lần 1, lúc đó mọi thứ hiển nhiên
  `flow=True` vĩnh viễn vì không còn ngữ cảnh bảng nào để so). Xác nhận ở
  bảng CRM (`vi/unicode/time-new-roman`): cột "Mô tả chi tiết" của hàng dữ
  liệu đầu tiên chứa một đoạn mô tả nhiều câu, dài hơn hẳn các cột khác
  cùng hàng — các dòng wrap của nó tràn xuống thấp hơn cả điểm kết thúc
  của các cột ngắn cùng hàng, đến mức **chồng lấn theo trục y với hàng dữ
  liệu tiếp theo**. Cụ thể: nhóm `row` chứa nhãn/người phụ trách/trạng thái
  của **hàng 2** ("Cấu trúc hóa đơn " / "VƯƠNG" / "Đang thực hiện") lại bị
  gộp chung với dòng `'phẩm" để xuất hóa đơn trong '` — dòng này thực chất
  vẫn là phần đuôi câu mô tả của **hàng 1**, không phải nội dung cột "Mô tả
  chi tiết" của hàng 2. Nghĩa là bug không chỉ nằm ở việc `is_flow_layout()`
  đóng bảng quá sớm cho 1 dòng đơn lẻ — cell cao bất thường khiến **dải
  toạ độ y của 2 hàng bảng logic khác nhau chồng lấn/xen kẽ nhau về mặt thị
  giác**, nên một bộ phân loại theo-từng-hàng-một (trên xuống, trái sang
  phải) không thể quy đúng dòng về đúng hàng dù có sửa điều kiện
  `is_flow_layout()` thế nào đi nữa, nếu không giải quyết cột trước.
- **Vì sao khó fix an toàn:** một fix chỉ dựa trên tín hiệu hình học cục bộ
  (khớp x0/x1 của dòng đơn lẻ với 1 cột đã biết + khoảng cách dọc nhỏ) —
  cách tiếp cận ban đầu định thử — không phân biệt được "dòng tiếp nối của
  chính cell đang mở" với "giá trị của hàng MỚI nhưng tình cờ cùng vị trí
  cột" vì cả hai đều có cùng độ lớn khoảng cách dọc trong một số mẫu
  (`vietnamese_doc`) — ghép nhầm dòng sẽ đổi bug "mất/vỡ cấu trúc" thành
  bug "trộn nhầm nội dung 2 hàng", không chắc là cải thiện. Hướng đi đúng
  nhiều khả năng cần dựng lại theo **cột trước, hàng sau** (xác định toàn
  bộ dải x của các cột trong cả vùng bảng trước, sau đó với mỗi cột tự xác
  định ranh giới hàng dựa trên các cột ngắn hơn làm neo) — phạm vi/rủi ro
  lớn hơn hẳn B2/B3, không phải một patch nhỏ. **Quyết định (2026-07-24):
  tạm hoãn B1, ưu tiên B4 trước** — xem mục ưu tiên cuối file.
- **Ghi chú riêng cho biểu hiện ở list bullet (`vi/unicode/calibri`):** khi
  instrument trực tiếp, root cause của biểu hiện này **có thể không giống
  hệt** biểu hiện ở bảng — trace cho thấy dòng tiếp nối bullet luôn có
  `table_open=False` cả trước và sau (không có bảng giả nào từng mở ở khu
  vực này), nghĩa là việc nó bị tách `<w:p>` riêng nhiều khả năng xảy ra ở
  một bước xử lý khác (gộp dòng thành đoạn văn, `Lines.py`/`parse_block()`)
  chứ không hẳn qua cùng cơ chế `collect_stream_lines()`/`is_flow_layout()`
  như bảng. **Chưa xác nhận lại kỹ** — cần re-verify riêng trước khi coi 2
  biểu hiện là cùng 1 root cause như tài liệu cũ từng khẳng định.

### B2. Cặp nhãn:giá trị (label:value) bị dựng thành bảng giả (trước đây là #2)

- **Cập nhật (2026-07-24):** phần root-cause "mất/trùng dữ liệu thật" ghi
  trước đây bị **overstate**, do công cụ chẩn đoán (dump `cell.text` /
  `row.cells` qua `python-docx`, và `extract_text_lines()` của eval) không
  đệ quy vào `<w:tbl>` lồng trong `<w:tc>` và không khử trùng lặp khi một ô
  bị `gridSpan`. Sau khi trích lại bằng script đệ quy + khử trùng
  `gridSpan` (`full_text.py`, xem scratchpad), thực tế là:
  - `vietnamese_doc` và `vi/unicode/time-new-roman`: **"Date" không hề mất**
    — nó nằm trong một `<w:tbl>` 1×1 lồng bên trong `<w:tc>`, dùng để tô
    nền xám (`<w:shd>`) làm nổi bật giá trị. `cell.text`/`extract_text_lines()`
    không đệ quy vào bảng lồng nên "Date" biến mất khỏi *diff*, nhưng vẫn
    tồn tại thật trong `output.docx` — đây là điểm mù của công cụ eval, không
    phải mất dữ liệu. `pdf2docx/table/TablesConstructor.py: stream_tables()`
    có hẳn 1 guard chủ ý giữ lại bảng lồng 1×1 khi ô có `bg_color`:
    `if isinstance(self._parent, Cell) and table.num_cols*table.num_rows==1
    and table[0][0].bg_color is None: continue`.
  - `vietnamese_doc`: **"Person" không hề bị nhân đôi** — chỉ có **một**
    `<w:tc>` chứa "Person" với `<w:gridSpan w:val="2"/>`; `row.cells` của
    `python-docx` trả về cùng một Cell object lặp lại 1 lần cho mỗi vị trí
    cột gộp, đó là đặc điểm API của `python-docx`, không phải bằng chứng
    trùng lặp thật trong OOXML (đã xác nhận qua raw XML).
  - `vi/unicode/mixed`: đây **không phải** cặp label:value có dấu hai chấm
    như 2 mẫu trên. Thực tế "Ngày" (mảnh label ngắn) bị tách ra thành 1
    bảng giả 1×1 độc lập (do `contained_in_shadings()`), còn "Ngày thực
    hiện" (label đầy đủ hơn — theo `original.docx` gốc, đáng lẽ nằm chung
    1 đoạn văn với "Ngày" qua 1 `<w:br/>` mềm) bị bỏ lại thành 1 `<w:p>`
    riêng biệt (có ZWSP ở đầu). Đây **là bug thật** (không mất dữ liệu,
    chỉ vỡ cấu trúc đoạn văn — mức độ thấp hơn mô tả cũ), vẫn **chưa fix**.
- **Đã fix một phần** (xem "Đã fix" #8): `collect_stream_lines()`
  (`pdf2docx/layout/Blocks.py`) có 1 vòng lặp riêng, không điều kiện,
  append thêm mọi block thoả `contained_in_shadings()` — kể cả khi block
  đó *đã* được thêm vào `table_lines` ở nhánh else phía trên (khi hàng
  không phải flow-layout/list-item). Điều này khiến 1 Line bị thêm **2
  lần** vào cùng 1 hàng bảng giả, tạo ra ô trùng lặp. Đã thêm guard
  `added` set để bỏ qua block đã append. Fix này *đúng và an toàn* (verify
  bằng `eval/run_eval.py`: điểm số giữ nguyên, không regressions) nhưng
  **không tự nó giải quyết** vấn đề "Ngày"/"Ngày thực hiện" bị tách rời ở
  `vi/unicode/mixed` — nguyên nhân của cái đó nằm ở chính
  `contained_in_shadings()` gộp nhầm 1 mảnh label vào bảng giả, chưa fix.
- **Còn lại cần fix:** tách rời "Ngày" khỏi "Ngày thực hiện" ở
  `vi/unicode/mixed` — sửa điều kiện kích hoạt `contained_in_shadings()`
  để không tách 1 mảnh label ra khỏi phần còn lại của cùng 1 đoạn văn.
  Rủi ro regression tương tự B1 (đã thử 1 lần và revert, xem B1) — cần
  cẩn trọng, chưa có hướng fix an toàn được xác nhận.

### B4. Không nhất quán khi tách/gộp đoạn văn tại ranh giới dòng bị wrap (gộp 4 biến thể, trước đây là #3(a)/(b)/(c) + biến thể mới (d))

- **(a) [ĐÃ FIX 2026-07-24] Auto-wrap dựng sai vị trí xuống dòng khi thiếu
  `<w:br/>` cứng:** `en/unicode` (đoạn "cloud-native architectures..." —
  3 dòng ở nguồn ra thành 4 dòng ở output, dòng cuối "independently
  without" trơ trọi — xác nhận qua so pixel ảnh render),
  `vi/unicode/time-new-roman` (tiêu đề "TỔNG HỢP DỮ LIỆU..." có `<w:br/>`
  sau "ĐA" nhưng không có sau "TRỊ" — cùng một `<w:p>`, chỉ là hard-break
  không nhất quán). Root cause + fix: xem mục "Đã fix" #9
  (`parse_line_break()`'s free-space-ratio heuristic không phân biệt được
  wrap tự nhiên với ngắt dòng chủ ý).
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
- **(d) [ĐÃ FIX 2026-07-24] chiều ngược lại: gộp 2 đoạn văn nguồn thật
  thành 1 `<w:p>` qua `<w:br/>` cứng.** `vi/unicode/arial`: tiêu đề "Bài
  Toán Quy Nạp và Nghịch Lý Con Gà Tây" (font/size/màu riêng) và đoạn thân
  bài (font/size/màu khác hẳn) — 2 đoạn văn riêng biệt ở nguồn — bị fuse
  thành một `<w:p>` duy nhất nối bằng `<w:r><w:br/></w:r>`, chỉ giữ lại
  `pPr` (spacing/indent) của đoạn đầu. Xác nhận qua `python-docx`. Ban đầu
  tưởng **vô hình** khi render (pixel gần như giống hệt), nhưng sau khi
  fix thì ssim/text_strict đều cải thiện rõ — impact thực tế lớn hơn ghi
  nhận ban đầu. Root cause + fix: xem mục "Đã fix" #10.

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

### B7. Hàng bảng có 1 cột "cao" hơn các cột khác (do wrap) khiến hàng đó bị `group_by_rows()` tách thành 2 cụm vật lý, cụm đầu (dòng đơn độc) đóng bảng quá sớm — root-caused 2026-07-27, đã fix một phần 2026-07-27 (xem "Đã fix" #12)

**Đã root-cause đầy đủ (KHÔNG phải do ngắt trang PDF — ghi chú trước đây suy
đoán vậy là sai, xem đính chính ở mục B1 phía trên).** Instrument trực tiếp
`Blocks.collect_stream_lines()`/`TablesConstructor.stream_tables()` (in
từng block bbox/text đưa vào mỗi lời gọi) trên
`eval/samples/vi/unicode/time-new-roman/input.pdf` cho thấy:

- Toàn bộ 46 dòng của bảng CRM (header + 5 hàng dữ liệu) được xử lý trong
  **một** lời gọi `collect_stream_lines()` duy nhất (call #2, parent =
  Column của cả trang nội dung) — không hề có ranh giới trang ở giữa. Kết
  quả lời gọi này: `4 table_lines group(s), sizes=[15, 5, 5, 5]` — tức nó tự
  tách thành 4 bảng riêng ngay tại bước group-by-row, trước khi
  `is_table_continuation_line()` (fix #11) kịp can thiệp.
- Cơ chế cụ thể cho hàng 3 ("Quản lý khách hàng" / "Chỉnh sửa thông tin SĐT
  và địa chỉ..."): cột "Mô tả chi tiết" của hàng này wrap 2 dòng, dòng đầu
  `'Chỉnh sửa thông tin SĐT và '` có bbox `y=(312.9, 322.7)`; nhưng 3 cột
  còn lại của **cùng hàng logic** đó (`'Quản lý khách hàng '`, `'ĐĂNG'`,
  `'Hoàn thành'`) đều có bbox bắt đầu ở `y=325.6` — **muộn hơn ~12.7pt**
  (đúng 1 line-height) so với dòng đầu của cột Mô tả. Vì `group_by_rows()`
  gom cụm theo chồng-lấn-y, dòng `'Chỉnh sửa thông tin SĐT và '` không
  chồng-lấn-y với 3 cột kia → tách thành cụm vật lý riêng, **đúng 1 dòng** →
  `is_flow_layout()` trả `True` ngay (`len<=1`) → bảng đang mở (đã có 15
  dòng: header + hàng 1 + hàng 2) bị đóng lại (`close_table()`) trước khi
  thấy nốt phần còn lại của hàng 3. Lặp lại y hệt ở hàng 4 và hàng 5 → 3
  bảng 1-hàng riêng biệt.
- **Vì sao fix #11 (`is_table_continuation_line()`) không bắt được ca này**:
  fix đó chỉ so dòng-đơn-độc với các dòng **đã có sẵn** trong `table_lines`
  (nhìn lùi). Nhưng neo đúng cho dòng `'Chỉnh sửa thông tin SĐT và '` không
  nằm ở dòng nào đã tích luỹ trước đó (khoảng cách tới dòng gần nhất cùng
  cột ở hàng 2, `'tương lai.'`/`y=287.5-297.3`, là ~28pt — vượt ngưỡng
  `2.0*line_height` nên đúng ra phải bị từ chối, tránh nhầm 2 hàng khác nhau
  làm 1) — mà nằm ở dòng `'địa chỉ mà vẫn giữ nguyên lịch '` (`y=325.6`,
  cùng cột, gap chỉ ~2.9pt, đúng kiểu wrap-continuation) — dòng này lại
  **nằm ở cụm vật lý PHÍA SAU**, chưa được xử lý/thêm vào `table_lines` tại
  thời điểm cần quyết định. Nói cách khác đây là biến thể "dòng đầu của ô bị
  wrap, mở sớm hơn phần còn lại của hàng" — ngược hướng với B1 gốc ("dòng
  cuối của ô bị wrap, đóng muộn hơn"), nên cùng kiểu chỉ-nhìn-lùi không đủ.
- **Root cause tại sao cột "Mô tả chi tiết" lại lệch y sớm hơn 3 cột kia
  trong cùng 1 hàng**: nhiều khả năng do cách PDF gốc canh dọc nội dung ô
  không đồng nhất giữa cột dài (top-aligned, tràn xuống ngay khi hàng bắt
  đầu) và cột ngắn (căn giữa/căn đáy theo chiều cao thực tế của hàng) — đây
  là đặc điểm của PDF nguồn, `pdf2docx` không kiểm soát được, chỉ có thể xử
  lý ở tầng group-by-row/continuation-detection.
- **Đã implement 2026-07-27 — xem "Đã fix" #12 để biết chi tiết fix/thử-và-
  revert/verify.** Hướng fix: thêm `is_table_lookahead_line()` trong
  `collect_stream_lines()`, nhìn tới (lookahead) hàng vật lý kế tiếp khi
  nhìn-lùi thất bại, tái dùng đúng 4 tín hiệu của `is_table_continuation_line`
  qua hàm dùng chung `lines_match()`. **Chỉ fix được sub-case "dòng ứng viên
  hẹp hơn/bằng dòng neo ở hàng kế tiếp"** (hàng 3 của bảng CRM). Sub-case
  "dòng ứng viên rộng hơn dòng neo" (hàng 4/5 của bảng CRM) đòi hỏi chuẩn hoá
  theo bề rộng nhỏ hơn (symmetric) — đã thử và **revert** vì gây regression
  thật trên `vi/unicode/mixed` (xem #12) — vẫn còn mở, chưa tìm được cách fix
  an toàn.
- Thấy ở: `vi/unicode/time-new-roman` (bảng CRM: sau fix #12 còn 1 bảng
  4-hàng đúng + 2 bảng 1-hàng vỡ, ở 2/5 hàng dữ liệu — cải thiện từ 3/5 hàng
  vỡ trước fix), `vietnamese_doc` (Complex Table: **không cải thiện chút
  nào** sau fix #12 — chưa điều tra riêng xem có đúng cơ chế B7 hay không).

## Không phải bug pdf2docx — fixture lỗi thời

- **[ĐÃ SỬA 2026-07-24] `vi/unicode/time-new-roman/original.docx` bị lệch
  (stale) so với `input.pdf` của chính mẫu đó.** Cột "Phụ trách"/"Trạng
  thái" của bảng CRM trống ở cả 5 hàng trong `original.docx`, nhưng xác
  nhận qua trích xuất text trực tiếp từ `input.pdf` (PyMuPDF) rằng PDF
  nguồn thật sự có nội dung ở các ô đó ("VƯƠNG", "Hoàn thành", "ĐĂNG",
  "Nguyễn T. Dũng", "Đã tiếp nhận", "Chờ xử lý"...). Output của pdf2docx
  **đầy đủ hơn** "ground truth" ở đây — một phần nhiễu trong diff của mẫu
  này đến từ fixture lỗi thời, không phải lỗi pdf2docx. Đã điền lại 5 hàng
  đó trong `original.docx` (qua `python-docx`, chỉ set `.text` lên run
  rỗng có sẵn để giữ nguyên style) cho khớp nội dung `input.pdf`. Sau khi
  sửa fixture, điểm số "sạch" hơn của mẫu này (không còn nhiễu từ fixture,
  chỉ còn phản ánh bug B1 thật): text_sim 0.9622→0.9653, text_strict
  0.6849→0.7397 — xem bảng cập nhật ở đầu file.

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
B3 (chèn `<w:tab/>` thừa) đã fix — xem mục "Đã fix" #7. B4(a) và B4(d) đã
fix — xem mục "Đã fix" #9, #10, không còn trong danh sách này. B2 đã hạ ưu
tiên sau khi xác minh lại: **không có mất dữ liệu thật** ("Date"/"Person"
đều nguyên vẹn, chỉ là điểm mù công cụ diff), phần duplicate-append đã fix
(mục "Đã fix" #8); phần còn lại (tách rời "Ngày"/"Ngày thực hiện" ở
`vi/unicode/mixed`) là bug thật nhưng mức độ thấp (vỡ cấu trúc đoạn văn,
không mất nội dung):

1. **B1 — đã fix một phần (2026-07-27), xem "Đã fix" #11.** Cơ chế dòng-
   tiếp-nối-1-dòng-đơn-độc bị đóng bảng quá sớm trong 1 vùng bảng liền mạch
   đã xử lý xong (điểm số cải thiện ở 2 mẫu bị ảnh hưởng, không regression
   ở 4 mẫu còn lại). Dự đoán cũ ("cell cao bất thường khiến 2 hàng logic
   chồng lấn nhau, cần dựng lại cột-trước-hàng-sau") **không xảy ra trên bộ
   mẫu hiện tại** — hoá ra không cần thiết kế lại lớn như dự đoán.
2. **B7 (mới) — bảng tràn ngắt trang vỡ thành nhiều `<w:tbl>`.** Phần còn
   sót lại sau khi fix B1: nội dung bảng ở trang sau ngắt trang bị xử lý
   per-cột riêng lẻ, không gộp lại thành hàng đa-cột. Chưa root-cause —
   ưu tiên cao vì đây giờ là nguyên nhân chính khiến `time-new-roman`/
   `vietnamese_doc` vẫn còn `changed` > 0, nhưng cần điều tra thêm về luồng
   xử lý bảng-tràn-trang trước khi biết độ phức tạp/rủi ro thực sự của fix.
3. **B4(b)/(c)** còn lại chưa fix: (b) ưu tiên thấp (vô hình, chỉ mang
   tính cấu trúc — ảnh hưởng tìm/thay thế theo câu, điều hướng con trỏ,
   screen reader). (c) đã có fix (bị revert) — nên root-cause B6 trước
   khi thử lại B4(c)/mục "Đã thử và revert" #3.
4. **B2 còn lại ("Ngày"/"Ngày thực hiện" tách rời ở `vi/unicode/mixed`)**
   — không mất dữ liệu, chỉ vỡ cấu trúc đoạn văn; rủi ro fix tương tự B1
   (điều kiện kích hoạt cùng nằm ở logic phát hiện bảng-giả/shading), nay
   có thể xử lý dựa trên tín hiệu (thẳng-cột-theo-tỷ-lệ-riêng +
   khoảng-cách + font-size) đã xác nhận hiệu quả ở fix B1 #11.
5. **B5 (cột rỗng bị xóa)** — chỉ mới thấy ở 1/6 mẫu (en/unicode), ưu tiên
   thấp cho đến khi thấy lặp lại ở mẫu khác.
6. **B6** — nên root-cause song song hoặc trước khi thử lại fix margin của
   mục "Đã thử và revert" #3, để fix đó land mà không đánh đổi ssim/số
   trang.

Ngoài ra: cập nhật `vi/unicode/time-new-roman/original.docx` cho khớp
`input.pdf` (xem mục "Không phải bug pdf2docx") để mẫu này đo B1 chính xác
hơn, và cân nhắc sửa `extract_text_lines()` để đệ quy vào bảng lồng và khử
trùng `gridSpan` (giúp eval không tiếp tục đánh giá sai các trường hợp
kiểu B2 là mất/trùng dữ liệu).
