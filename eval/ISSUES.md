# Các vấn đề về độ chính xác của pdf2docx (phát hiện qua eval/run_eval.py)

**Mục tiêu dự án / ưu tiên đánh giá** (xem thêm `../README.md`): file docx
đầu ra phải dễ *chỉnh sửa* — việc giảm thiểu lượng văn bản người dùng phải
gõ lại quan trọng hơn nhiều so với độ trung thực về hình thức/bố cục so với
PDF gốc. Vì vậy `text_sim` là chỉ số quan trọng nhất; `ssim`/số trang chỉ là
tín hiệu phụ, mang tính chẩn đoán. Một fix làm cải thiện `text_sim` là tốt
dù có làm giảm `ssim`/số trang; một fix làm giảm `text_sim` là xấu dù có
làm tăng `ssim`.

Ảnh chụp nhanh từ lần chạy đầy đủ gần nhất (cả 7 mẫu), sau khi fix xong các
bug #1, #2, và #4 (xem mục "Đã fix") — #4 dựng lại các marker bullet/số thứ
tự thành list thật của Word, khép lại 2 mục #1 và #4 trong `Bugs in
pdf2docx` (trùng số nhưng khác danh sách — xem ghi chú ở đầu mục đó). Fix
về margin/ngắt section (trước đây là mục "Đã fix" số 3) đã **thử làm rồi
revert** — xem mục "Đã thử và revert" bên dưới; không có thay đổi nào của
nó còn tồn tại trong ảnh chụp này. Mục "Đã fix" số 5 (mới) xử lý một
false-negative của fix #4: marker bullet không được phát hiện khi style
của nó trùng hệt với span nội dung theo ngay sau, cộng với một cải tiến ở
phía `run_eval.py` để `text_sim` không tính các token marker còn sót lại
(nếu có) là mismatch thật.

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
  *cấu trúc* (vd. bug #3(b)), nhưng không phải chỉ số chính để tối ưu.

| mẫu                          | ssim   | text_sim | text_sim_strict | changed | số trang (gốc/ra) |
|------------------------------|--------|----------|------------------|---------|-------------------|
| en/unicode                   | 0.4933 | 0.9988   | 0.2857           | 35      | 2 / 3             |
| policy_claude_draft           | 0.5838 | 0.8982   | 0.4559           | 74      | 5 / 7             |
| vi/unicode/arial              | 0.8655 | 1.0000   | 0.6250           | 6       | 2 / 2             |
| vi/unicode/calibri            | 0.7917 | 1.0000   | 0.8261           | 8       | 2 / 2             |
| vi/unicode/mixed              | 0.8187 | 0.9976   | 0.8814           | 7       | 3 / 3             |
| vi/unicode/time-new-roman     | 0.8205 | 0.9622   | 0.5753           | 31      | 3 / 3             |
| vietnamese_doc                | 0.7996 | 0.9327   | 0.6038           | 21      | 2 / 2             |
| **TỔNG**                      | **0.7390** | **0.9699** | **0.6076**   |     |                   |

## Đã fix

1. **Thiếu khoảng trắng giữa các từ, thường xảy ra ngay trước một nguyên âm
   có dấu tiếng Việt** — đã fix trong `pdf2docx/text/Spans.py` (ngưỡng
   khoảng cách để gộp span không tính đến độ rộng của glyph dấu). Đã xác
   nhận qua eval: `text_sim` tăng trên vietnamese_doc, vi/unicode/calibri,
   vi/unicode/mixed, không có mẫu nào bị giảm điểm.

2. **Ô bảng có nội dung nhiều dòng bị tách thành các hàng giả thừa** — root
   cause nằm ở `pdf2docx/table/TablesConstructor.py: _inner_borders()`: với
   bảng >2 cột, mọi khoảng cách hàng phát hiện được trong nội bộ từng cột
   đều bị coi là ranh giới hàng thật, nên một ô bị wrap (nhiều dòng) nằm
   cạnh các ô một dòng khác sinh ra các hàng giả thừa. Đã fix bằng cách lấy
   cột có số cụm-hàng phát hiện được ít nhất làm nguồn xác định số hàng
   thật (một cột chỉ có thể bị *chia quá mức* do wrap, không bao giờ bị
   chia thiếu) — gom lại các dòng của các cột khác theo ranh giới hàng của
   cột đó, và coi "có cột nào đó chỉ hiện đúng 1 hàng" là bằng chứng chắc
   chắn rằng cả khối đó là một hàng logic duy nhất.
   - Đã xác nhận fix thành công qua eval: bảng CRM task 5 hàng của
     vi/unicode/time-new-roman giờ gộp mô tả bị wrap của mỗi hàng thành một
     hàng, hàng tiêu đề giống hệt byte-by-byte so với nguồn (trước đây cùng
     bảng này ra thành 11+ hàng vỡ, xem ví dụ cũ bên dưới). Không mẫu nào
     trong 6 mẫu còn lại bị giảm điểm; `text_sim` tổng của vietnamese_doc
     cũng tăng (0.3774 → 0.3922) như một hiệu ứng phụ.
   - **Vấn đề còn sót lại, khác gốc rễ, phát hiện trong lúc verify fix này
     (CHƯA fix, xem #6 bên dưới):** trong bảng của vietnamese_doc, các hàng
     mà *nhiều* cột cùng wrap một lúc (vd. cả "Hạng mục" và "Note" cùng
     wrap) vẫn còn bị vỡ — nhưng nguyên nhân nằm ở tầng trước
     `_inner_borders`, trong `collect_stream_lines()`/`is_flow_layout()`,
     không phải logic ranh giới hàng đã fix ở đây.

4. **Marker bullet/số thứ tự được dựng lại thành list thật của Word** —
   khép lại 2 mục #1 (bullet) và #4 (số thứ tự) trong `Bugs in pdf2docx`
   bên dưới. Root cause: pdf2docx ghi glyph marker (`●`, `○`, `"1."`, ...)
   như một run `<w:r><w:t>` thuần văn bản rồi theo sau bằng `<w:tab/>`,
   không có `<w:numPr>` nào cả — nên output *trông* giống list nhưng không
   thể sửa như một list thật (không thể nối tiếp list bằng Enter, đánh lại
   số, đổi kiểu bullet, v.v.).
   - Đã fix trong `pdf2docx/text/TextBlock.py` + `pdf2docx/common/docx.py`:
     - `TextBlock` giờ làm phẳng mọi `(line, span)` trong một block thành
       một chuỗi phẳng duy nhất (`_flatten_spans`) — cần thiết vì một số
       PDF nhét nguyên hai list item vào chung một đối tượng `Line` nội bộ,
       không có ranh giới xuống dòng/tab nào giữa chúng, nên chỉ dò marker
       ở span đầu tiên của mỗi `Line` sẽ bỏ sót các trường hợp này.
     - Một span được xếp loại là marker (`_detect_markers`) nếu văn bản của
       nó (một glyph bullet nằm trong tập được chọn lọc, hoặc khớp pattern
       số thứ tự `^\(?\d{1,3}[.\)]`) VÀ style tuple `(font, size, color,
       flags)` của nó khác với span nội dung theo ngay sau — chỉ so tên
       font ban đầu được thử trước nhưng không đáng tin, vì một số PDF để
       trống `.font` cho cả marker lẫn nội dung; size/color vẫn khác nhau
       trong các trường hợp đó.
     - Block được tách thành từng đoạn docx riêng cho mỗi list item
       (`_group_list_items` + `insert_paragraph_before()`), mỗi đoạn được
       gán style list thật qua hàm mới `docx.apply_list_style()` — hàm này
       chỉ đơn giản gán các style đoạn văn có sẵn trong template mặc định
       của python-docx (`List Bullet`/`List Number`), vốn đã mang sẵn
       `<w:numPr>` ở cấp *style*, nên không cần tự viết
       `numbering.xml`/`abstractNum` thủ công. Block không phát hiện được
       marker nào thì vẫn render theo từng `Line` như cũ, không đổi.
   - Đã xác nhận qua eval: `text_sim` tổng 0.9633 → 0.9687, `text_sim_strict`
     0.5014 → 0.5971 (cấu trúc đoạn văn giờ khớp nguồn sát hơn nhiều như một
     hiệu ứng phụ), không đổi số trang ở mẫu nào, `ssim` giảm không đáng kể
     (0.7401 → 0.7396). `vi/unicode/calibri` đạt `text_sim` tuyệt đối
     1.0000. Không mẫu nào trong 7 mẫu bị giảm điểm.
   - **Đính chính:** một báo cáo trước đây ở đây từng nói "hai mẫu không có
     nội dung list (`policy_claude_draft`, `vi/unicode/arial`) hoàn toàn
     không bị ảnh hưởng" — điều này **sai** cho `policy_claude_draft`: mẫu
     đó thực ra có rất nhiều nội dung bullet-list, chỉ là fix này không kích
     hoạt được cho nó vì một edge case cụ thể — xem mục "Đã fix" số 5 bên
     dưới.

5. **Marker bullet không được phát hiện khi style của nó trùng hệt với span
   nội dung theo ngay sau (false-negative của fix #4)** — cộng thêm một cải
   tiến độc lập ở `run_eval.py` để chỉ số `text_sim` không tính các token
   marker leftover (nếu có) là mismatch thật.
   - **Root cause (xác nhận qua instrument trực tiếp** `_detect_markers()`
     trên PDF của `policy_claude_draft`): `_detect_markers()` chỉ gắn cờ một
     span là marker nếu style tuple `(font, size, color, flags)` của nó khác
     với span nội dung theo sau — nhưng ở tài liệu này, cả span bullet lẫn
     span nội dung đều có `font='Arial', size=11.0, color=3026478, flags=0`
     giống hệt nhau. Điều kiện so-style vốn được thêm để tránh false
     positive (vd. một tiêu đề đánh số thường như `"1. Introduction"` bị
     nhầm thành marker list thật, làm mất chữ "1." khỏi `.text`) — nhưng với
     bullet glyph (`•`, `○`, ...), rủi ro false-positive đó gần như không
     tồn tại: một glyph bullet đứng một mình gần như không bao giờ là nội
     dung câu thật.
   - **Fix** trong `pdf2docx/text/TextBlock.py: _detect_markers()`: tách
     điều kiện so-style ra khỏi nhánh `kind == ('bullet', ...)` — bullet giờ
     được chấp nhận là marker chỉ dựa trên text (khớp `_BULLET_MARKERS`),
     không cần so style nữa. Nhánh `kind == ('number', 0)` (số thứ tự) vẫn
     giữ nguyên điều kiện so-style như cũ, vì rủi ro false-positive ở đó vẫn
     thật.
   - **Cải tiến bổ sung, độc lập, ở phía eval** (`eval/run_eval.py`,
     `extract_all_words()`): một glyph marker bullet/số còn sót lại trong
     `.text` (do PDF producer khác hoặc edge case chưa fix) chỉ là một ký tự
     thừa người dùng sẽ xóa đi, không phải nội dung phải gõ lại — không nên
     tính là mismatch thật khi so `text_sim`. Đã thêm `_is_list_marker_token()`
     (dùng cùng tập glyph bullet + pattern số thứ tự như phía pdf2docx, để
     nhất quán) để lọc các token này khỏi cả hai phía trước khi so
     `difflib.SequenceMatcher` — chỉ áp dụng cho `text_sim` (chuỗi từ toàn
     tài liệu), không đụng tới `text_sim_strict` (so ở cấp đoạn văn/hàng,
     nơi xóa một token khỏi giữa một chuỗi rủi ro hơn).
   - Đã xác nhận qua eval (cả 7 mẫu, số liệu ở bảng đầu tài liệu): `text_sim`
     của `policy_claude_draft` tăng 0.8891 → 0.8982 (+0.0091),
     `text_sim_strict` 0.3824 → 0.4559, `changed` giảm 84 → 74, không đổi số
     trang. `text_sim` tổng 0.9687 → 0.9699 (+0.0012). Hai mẫu
     (`vi/unicode/mixed`, `vi/unicode/time-new-roman`) giảm không đáng kể
     (-0.0001, nhiễu do `SequenceMatcher` canh lại vị trí sau khi bớt từ,
     không phải regression thật). Không mẫu nào giảm điểm ở `text_sim_strict`
     hay số trang.
   - Phần còn lại của khoảng cách `text_sim` ở `policy_claude_draft` (vẫn
     thấp nhất trong 7 mẫu) chủ yếu đến từ bug #2 (nhãn/footer trang bị gộp
     vào nội dung như hàng bảng giả) — đã xác nhận qua thử nghiệm riêng
     (chuẩn hoá thêm token marker rồi so lại) rằng phần chênh lệch còn sót
     lại chủ yếu là do bug #2, không phải marker leak.

**Lưu ý về môi trường:** lần chạy eval đầu tiên trên máy này báo điểm
"hoàn hảo" giả 1.0 cho policy_claude_draft. Root cause: lần gọi headless
*đầu tiên* của LibreOffice trên cache fontconfig hệ thống còn "lạnh" làm
sai lệch cách phân trang; original.docx và output.docx tình cờ bị sai
giống hệt nhau lần đó. Đã verify lại sau khi cache đã "ấm" — số trang ổn
định từ đó. Cần nghi ngờ bất kỳ lần chạy eval đơn lẻ nào ngay sau khi máy/
container vừa khởi động lại; chạy lại một lần nữa để xác nhận độ ổn định.
Ngoài ra, file `input.pdf` fallback tự sinh (dùng khi một mẫu chỉ có
`original.docx`) giờ được cache xuống đĩa ngay lần dùng đầu tiên, vì việc
render docx→pdf của LibreOffice có độ rung (jitter) trong cách dàn trang
giữa các lần chạy, nếu không cache sẽ khiến điểm số trôi dạt qua từng lần
chạy mà không có lý do thực sự nào.

## Đã thử và revert

3. **`space_before` lớn một cách vô lý ở đoạn văn đầu tiên của trang/section
   mới (root cause của bug #3(c) bên dưới, đã xác nhận nhưng fix bên dưới
   đã bị revert) — cộng với một tối ưu bổ sung về số lượng ngắt section.**
   - **Root cause (đã xác nhận qua instrument trực tiếp, không chỉ đọc
     code):** `RawPage.calculate_margin()` và `RawPage.parse_section()`
     (`pdf2docx/page/RawPage.py`) tính margin trang / ranh giới section từ
     hợp bbox của `self.blocks` và `self.shapes`, trước đây chỉ loại trừ
     `Hyperlink`. Một số mẫu có một shape `Fill` màu trắng phủ toàn trang
     (nền trang trí, vô hình trên giấy trắng) bị tính vào không lọc, làm
     méo margin trên tính được xuống gần ~0. Điều này lan sang
     `Blocks._parse_block_vertical_spacing()`
     (`before_space = block.bbox.top - column.working_bbox.top`) và
     `TextBlock.parse_exact_line_spacing()`, sinh ra `space_before` ~68pt
     vô lý được ghi nhận ở bug #3(c). **Root cause này vẫn còn thật và vẫn
     còn tồn tại trong code** — chỉ có fix cho nó bị revert, chưa fix bug
     gốc.
   - **Fix đã thử:** thêm `RawPage._visible_shapes()`, dùng ở cả
     `calculate_margin()` và `parse_section()` thay cho danh sách
     `self.shapes` thô. Hàm này loại trừ `Hyperlink` (như cũ) cộng thêm một
     `Fill` màu trắng chỉ khi nó *đồng thời* phủ ≥90% chiều rộng và chiều
     cao trang — tức là nền phủ toàn trang, không phải nội dung thật. Một
     `Fill` trắng nhỏ (vd. nền ô bảng hợp lệ, xác nhận tồn tại ở
     vi/unicode/calibri với ~28%/4% độ phủ rộng/cao) phải được giữ lại, vì
     loại trừ mọi `Fill` trắng vô điều kiện đã được thử trước và gây
     regression nặng ở đó.
   - Đã xác nhận qua kiểm tra trực tiếp (không chỉ điểm eval) rằng fix hoạt
     động đúng như thiết kế: `space_before` của đoạn văn từng là 68pt ở
     en/unicode trở thành `0`, và margin trang của các trang bị ảnh hưởng
     trở thành giá trị dương hợp lý thay vì gần `(0, 0, 0, 0)`.
   - **Tối ưu bổ sung cũng đã thử (`pdf2docx/page/Page.py`):** trước đây,
     `Page.make_docx()` tạo một `WD_SECTION.NEW_PAGE` mới cho *mọi* trang
     PDF một cách vô điều kiện (có lý do chính đáng vì mỗi trang PDF có thể
     có kích thước/margin riêng — nhưng lãng phí khi các trang liên tiếp
     thực ra dùng chung kích thước/margin, vd. hầu hết tài liệu văn bản
     nhiều trang). Đã thêm `Page._matches_section()`: nếu kích thước/margin
     của trang đang vào khớp với section docx cuối cùng hiện tại trong
     phạm vi `constants.MINOR_DIST` (1pt), thì phát ra một
     `doc.add_page_break()` thường thay vì tạo section mới. Đã xác nhận
     riêng lẻ là hoàn toàn vô hại trên bộ 7 mẫu (không có cặp trang nào có
     margin đủ gần để kích hoạt việc dùng lại dưới cách tính margin lỗi cũ)
     — nó chỉ bắt đầu có tác dụng khi kết hợp với fix margin ở trên.
   - **Lý do revert:** kết hợp lại, hai fix này làm giảm `ssim`/số trang
     trên 2 trong 7 mẫu — vi/unicode/calibri (2→2 trang trước, 2→3 sau;
     ssim 0.7926→0.5472) và en/unicode (đã sẵn 2→3, ssim 0.4937→0.4905,
     gần như không đổi). `text_sim`/`text_sim_strict` được xác nhận giống
     hệt byte-by-byte trước/sau ở cả 7 mẫu (fix này chỉ đụng vào bố cục
     trang, không bao giờ đụng vào nội dung văn bản) — nên theo ưu tiên đã
     nêu của dự án (khớp văn bản quan trọng hơn số trang) trade-off này ban
     đầu được chấp nhận, nhưng sau đó người dùng yêu cầu revert lại
     ("có vẻ nó k work" — 2026-07-24) trước khi bắt đầu làm bug #1/#4 (rò
     rỉ marker list). **Hiện đã revert; `RawPage.py`/`Page.py` trở về trạng
     thái trước fix.** Xem bug #8 bên dưới để biết root cause mới phát hiện
     của regression ssim/số trang (một bug riêng, vẫn đang mở), thứ sẽ tái
     xuất hiện nếu fix này được thử lại.
   - Lịch sử lặp (giữ lại để tham khảo nếu thử lại): lần đầu thử loại trừ
     mọi `Fill` trắng vô điều kiện → làm hỏng vi/unicode/calibri (một lưới
     3×4 các `Fill` trắng nhỏ hợp lệ của ô bảng bị loại trừ, làm méo margin
     trang đó thay vào đó) → thêm điều kiện tỷ lệ phủ trang, ban đầu ở
     ≥95%, phát hiện shape nền thật của calibri đo được 94.1%/94.2% độ phủ
     (vừa dưới ngưỡng), hạ xuống ≥90% để tách rõ nền thật (94%) khỏi các
     fill ô hợp lệ (28%/4%).
   - **Nếu thử lại fix này trong tương lai:** hãy root-cause bug #8 trước
     (hoặc làm song song), vì đó mới là thứ thực sự gây ra regression số
     trang một khi margin được tính đúng — fix #8 trước có thể sẽ giúp fix
     này land mà không phải đánh đổi.

## Bug trong pdf2docx (thật, đáng để fix)

Mỗi bug liệt kê mọi mẫu mà nó được quan sát trực tiếp. Tất cả đều đọc từ
`eval/results/<mẫu>/text_diff.txt` trừ khi có ghi chú khác; #3 (trước đây
là #5) cũng đã được xác nhận qua XML docx thô (xem ghi chú về artefact của
công cụ diff bên dưới để biết vì sao bước kiểm tra thêm đó lại quan trọng).
**Các số bên dưới không được đánh lại số khi một mục được fix** (xem #1 và
#4) — chúng giữ nguyên vị trí gốc và bị gạch ngang, để mọi tham chiếu chéo
khác trong tài liệu này (#2, #3(a/b/c), #5, #6, #7, #8) vẫn đúng mà không
cần đánh lại số.

1. ~~**Marker bullet của list rò rỉ vào nội dung văn bản dưới dạng ký tự
   thuần**~~ **ĐÃ FIX** — xem mục "Đã fix" số 4 ở trên (cũng bao gồm luôn
   #4 bên dưới).

2. **Một dòng nhãn/footer ngắn bị gộp vào nội dung như một hàng bảng giả**
   thay vì giữ nguyên là một đoạn văn thường.
   - Thấy ở: policy_claude_draft (footer trang), vi/unicode/time-new-roman
     và vi/unicode/mixed (cặp nhãn kiểu form như `"Ngày lập:"` /
     `"Ngày thực hiện"`).
   - Ví dụ: `"Trang 1 | © Nội bộ – Không phát tán bên ngoài"` hiện ra như
     một hàng *bảng* trong output (diff của mình chỉ chèn `|` cho ô bảng),
     trong khi nguồn là một dòng footer nằm ở cuối trang PDF.
   - Góp phần làm tăng số trang (vd. policy_claude_draft 5 → 7 trang) vì
     các hàng thừa này đẩy nội dung sang trang mới.

3. **Một đoạn văn nguồn bị wrap qua nhiều dòng trong PDF đôi khi bị dựng
   lại thành nhiều đoạn `<w:p>` riêng biệt thay vì một — không nhất quán,
   và không phải lúc nào cũng có ảnh hưởng nhìn thấy được.** Phát hiện ở
   en/unicode (ssim thấp nhất của nó, 0.4937, dù là tiếng Anh thuần không
   dấu, nên vấn đề này không liên quan tới xử lý tiếng Việt/font).
   Đã xác nhận cấu trúc qua XML docx thô cho ba trường hợp; sau đó mỗi
   trường hợp cũng được kiểm tra lại với ảnh trang đã render thực tế
   (`eval/results/en/unicode/pages/*.png`) để xem ranh giới `<w:p>` thừa đó
   có nhìn thấy được không — không phải lúc nào cũng có:
   - **(a) Một `<w:p>` duy nhất, nhưng có một bug thật (khác) bên trong
     nó:** đoạn "cloud-native architectures..." — xác nhận chỉ một phần tử
     đoạn văn, nhưng nó trộn hai cơ chế: một số ranh giới dòng là `<w:br/>`
     cứng (copy y nguyên từ ranh giới dòng của PDF), trong khi các đoạn văn
     bản khác giữa các `<w:br/>` lại **không** có break nào cả và để mặc
     cho renderer tự wrap. Bug là ở chỗ các đoạn tự-wrap này không tái tạo
     đúng vị trí wrap dòng của nguồn:
     - PDF nguồn (`input.pdf`, trích xuất qua bbox dòng của PyMuPDF): đoạn
       "understanding of container orchestration and asynchronous
       communication patterns. In a typical microservices ecosystem,
       individual components are decoupled, allowing teams to deploy
       updates independently without" wrap thành **3 dòng** trong nguồn.
     - XML của `output.docx` **không có `<w:br/>`** nào ở đúng đoạn đó (nó
       là 3 phần tử `<w:r>` thuần không có break giữa chúng) — nên
       LibreOffice tự wrap, và ở font/cỡ chữ đã dựng lại, nó ra thành
       **4 dòng** thay vì 3, với "independently without" bị trơ trọi một
       mình ở dòng cuối. Đã xác nhận bằng hình ảnh: `output_p01.png` crop
       ra cho thấy dòng này kết thúc ở ~x=430px trong khi mọi dòng anh em
       khác trong đoạn văn đó kéo dài tới ~x=1030-1070px (quét pixel, lấy
       pixel tối cùng ở mỗi hàng) — một dòng ngắn rõ ràng, thật, nhìn thấy
       được mà **không** tồn tại ở nguồn (ở đó, dòng PDF tương ứng
       "decoupled, ... independently without" kết thúc ở x=461.9pt, đúng
       tầm với các dòng anh em 461.9-519.6pt — tức một dòng bình thường,
       khá đầy, không hề ngắn).
     - **Root cause:** pdf2docx hard-code `<w:br/>` chỉ ở một số ranh giới
       dòng phát hiện được và để các dòng khác tự reflow; khi các đoạn
       tự-reflow không wrap đúng vị trí như PDF nguồn (có thể do lệch
       thước đo font giữa cách pdf2docx đo độ rộng văn bản và cách
       LibreOffice thực sự shape/đo font "Inter" lúc render), đoạn văn âm
       thầm được thêm hoặc mất dòng so với nguồn. Mỗi dòng thừa tốn thêm
       một khoảng chiều cao dòng cố định `w:lineRule="exact"` không có
       trong bản gốc — một bug thật, đã xác nhận, đáng để fix.
     - **Không phải cùng bug với (c) bên dưới, và không có liên hệ nhân
       quả với nó.** Đây là vấn đề reflow theo chiều ngang/số dòng ở một
       đoạn văn bản cụ thể gần đầu trang 1; vấn đề trang trắng ở (c) là do
       một giá trị `space_before` sai cụ thể ở một đoạn văn không liên
       quan trong một section khác, ở trang 2. Chúng không chung cơ chế —
       vấn đề này không dịch chuyển gì theo chiều dọc ngoài phạm vi đoạn
       văn của chính nó (chiều cao dòng cố định, nên wrap sai chỉ có thể
       thêm/bớt nguyên dòng, không lan sang khoảng cách của các đoạn văn
       khác). Hai lỗi riêng biệt, đã xác nhận độc lập, tình cờ nằm trong
       cùng một tài liệu.
   - **(b) Bị tách về mặt cấu trúc nhưng không nhìn thấy được:**
     `"Technical Implementation: Microservices"` / `"Architecture"` là hai
     phần tử `<w:p>` riêng biệt, nhưng pdf2docx bù lại bằng một
     `space_before` (~9pt) gần bằng chiều cao dòng bình thường, nên
     `output_p01.png` render tiêu đề này giống hệt như wrap từ tự nhiên —
     đặt cạnh `original_p01.png` không có khác biệt nhìn thấy được. Đã xác
     nhận bằng kiểm tra ảnh trực tiếp. **Không đáng fix vì mục đích chính
     xác hình ảnh**, dù đây vẫn là một điểm lạ về cấu trúc (vd. sẽ ảnh
     hưởng tới tìm/thay thế xuyên "câu", điều hướng con trỏ, screen
     reader).
   - **(c) Một khiếm khuyết thật của pdf2docx, nhưng mức độ nhìn thấy được
     phụ thuộc vào renderer:** `"...journals."` và `"Somewhere in this
     silence..."` là hai phần tử `<w:p>` riêng biệt, với một đoạn văn ở
     giữa chứa `<w:sectPr>` — "đoạn văn rỗng" ở giữa này *không* phải bug,
     nó là container OOXML bắt buộc cho một ngắt section (đã xác nhận: tài
     liệu có đúng một ngắt như vậy, chia thành hai section, mỗi trang PDF
     một section — một thiết kế hợp lý để giữ bố cục theo từng trang).
     - **Khiếm khuyết thật sự:** đoạn văn bắt đầu section mới
       (`"Somewhere..."`) được gán `space_before ≈ 68pt` (863600 EMU, tức
       `w:before="1360"` twips). Đối chiếu với **PDF gốc thật**
       (`original_p02.png`, trang 2 của PDF thực sự đưa vào pdf2docx): đoạn
       văn đó bắt đầu đúng ngay tại margin trên bình thường, không có
       khoảng trống lớn nào. Vậy giá trị 68pt mà pdf2docx tính cho đoạn
       văn đầu tiên của section mới là sai một cách khách quan so với vị
       trí trong nguồn — phần này là một bug thật, không phụ thuộc
       renderer.
     - **Mức độ nhìn thấy phụ thuộc renderer:** render qua LibreOffice
       (`output_p02.png`), kết quả là một trang gần như trống trơn — hai
       dòng văn bản ở trên cùng, rồi một khoảng trống lớn — đẩy phần còn
       lại của tài liệu sang một trang thừa (nguyên nhân trực tiếp gây
       tăng số trang 2 → 3, và là nguyên nhân chính khiến ssim thấp, vì
       trang thứ 3 "ma" này chấm điểm 0 so với không có gì). **Tuy nhiên**,
       mở cùng file output.docx đó trong **WPS Office**, người dùng báo là
       không thấy khoảng trống hay tách trang nào. Giải thích khả dĩ: WPS
       (giống MS Word, theo thực tế phổ biến) bỏ qua `space_before` cho
       đoạn văn đầu tiên ngay sau một ngắt section, trong khi LibreOffice
       áp dụng nó một cách literal — một dạng khác biệt renderer đã biết
       đối với khoảng cách ở đầu trang/section, không phải thứ pdf2docx
       kiểm soát được. Vậy: giá trị `space_before` sai là có thật và đáng
       fix tại gốc, nhưng người dùng cuối có *nhìn thấy* nó hay không tùy
       vào việc họ mở file bằng ứng dụng tương thích Word nào.
   - **Root cause đã xác nhận — xem mục "Đã thử và revert" số 3 ở trên.**
     Một shape `Fill` nền trắng phủ toàn trang bị tính vào không lọc, trong
     hợp bbox dùng để tính margin trang và ranh giới section
     (`RawPage.calculate_margin()`/`parse_section()`), làm méo margin trên
     tính được xuống gần ~0 và lan thành `before_space`/`space_before` lớn
     vô lý cho đoạn văn đầu tiên của section. Đã xác nhận qua instrument
     trực tiếp: khi áp fix, `space_before` của đúng đoạn văn này trở thành
     `0`, khớp với vị trí đầu trang thật của PDF nguồn — nhưng fix đã bị
     revert (xem mục 3) vì nó gây regression số trang/ssim ở chỗ khác, nên
     bug này **hiện vẫn còn tồn tại** trong code, chưa fix. (Cũng đã xác
     nhận trong lúc điều tra: đây KHÔNG phải, như từng nghi ngờ ban đầu,
     vấn đề đo từ sai điểm tham chiếu — phép tính khoảng cách dọc tự nó
     vẫn đúng; bug nằm hoàn toàn ở chỗ những shape nào được phép ảnh hưởng
     tới bbox margin/ranh giới.)
   - Chưa kiểm tra xem vấn đề này có xảy ra ở các mẫu tiếng Việt không —
     mọi chỗ trông giống tiêu đề bị tách tìm thấy ở đó, khi kiểm tra XML,
     đều hóa ra là trường hợp (a) (một đoạn văn, có `<w:br/>`), không phải
     bug này. Đừng cho rằng nó vắng mặt ở nơi khác mà không kiểm tra cả XML
     *và* ảnh đã render trực tiếp — chỉ XML thôi sẽ báo cáo mức độ nghiêm
     trọng quá cao (trường hợp b và c trông giống hệt nhau trong diff/XML
     nhưng có ảnh hưởng hình ảnh rất khác nhau).
   - **Lưu ý về phương pháp phát hiện được:** renderer làm ground truth
     của eval này là LibreOffice (`docx_to_pdf()` trong `run_eval.py`);
     một điểm ssim thấp có thể phản ánh một điểm kỳ lạ riêng của
     LibreOffice (vd. không bỏ qua space-before ở đầu section) chứ không
     phải thứ mà mọi người đọc đều thực sự thấy. Trước khi coi một phát
     hiện ssim thấp là khiếm khuyết đã xác nhận là người dùng nhìn thấy
     được, nên kiểm tra thử output.docx trong một ứng dụng tương thích
     Word thật (Word/WPS) — như đã làm ở đây.

4. ~~**Marker số thứ tự của list rò rỉ vào văn bản dưới dạng ký tự
   thuần**~~ **ĐÃ FIX** — xem mục "Đã fix" số 4 ở trên (cùng fix với #1).

5. **Cột bảng bị xóa hoàn toàn khi mọi giá trị trong đó đều rỗng.**
   - Thấy ở: chỉ mới en/unicode.
   - Ví dụ: bảng "Quarterly Performance Metrics" có một cột `Status` mà mọi
     ô đều trống trong original.docx; output.docx thiếu hẳn cột đó (cả
     header lẫn các ô), từ 4 cột còn 3.
   - Nguyên nhân có thể: việc phát hiện ranh giới cột khi dựng lại bảng dựa
     vào nội dung không-phải-khoảng-trắng để suy ra phạm vi cột, nên một
     cột toàn rỗng không có ký tự định vị nào để bám vào.

6. **Các dòng tiếp nối của ô bị wrap, khi đứng riêng lẻ, bị rơi ra khỏi
   bảng hoàn toàn, rò rỉ thành đoạn văn bản trần — một root cause khác với
   bug #2 (đã fix) về tách hàng, phát hiện trong lúc verify fix đó.**
   - Thấy ở: vietnamese_doc (cùng "Complex Table" như bug #2, ở các hàng mà
     *nhiều* cột cùng wrap một lúc, vd. cả "Hạng mục" và "Note").
   - Ví dụ: hàng `01 | Quản lý người dùng... | 2 | Đã hoàn thành | Gán cho:
     Person` ra thành "Quản lý" và "người" xuất hiện như các dòng đoạn văn
     trần không nằm trong bảng, trước khi phần còn lại của hàng render
     đúng thành một hàng bảng: `01 | dùngMàn hình đăng | 2 | Đã hoàn thành
     | Gán cho: Person`.
   - Root cause (đã xác nhận qua đọc code, chưa fix): trong
     `pdf2docx/layout/Blocks.py: collect_stream_lines()`, mỗi "hàng" vật lý
     (một cụm các dòng chồng lấn theo trục y trên trang) được phân loại là
     văn bản thường hay nội dung bảng qua
     `pdf2docx/common/Collection.py: is_flow_layout()`, hàm này luôn luôn
     trả về `True` (tức "văn bản thường/đoạn văn") bất cứ khi nào cụm chỉ
     có một dòng: `if len(self)<=1: return True`. Dòng tiếp nối của một ô
     bị wrap thường không chồng lấn theo chiều dọc với *bất kỳ* nội dung
     cột nào khác ở đúng vị trí y đó (thường gặp khi các ô wrap tới độ cao
     khác nhau), nên nó tạo thành một cụm một-dòng-đơn-độc và bị phân loại
     là văn bản thường — đóng/làm vỡ bảng đang dựng dở — trước khi
     `_inner_borders` (phạm vi của bug #2) kịp thấy nó.
   - **Một fix đã được thử và revert trong phiên làm việc này**: làm cho
     một hàng-một-dòng-đơn-độc "tiếp nối" bảng đang mở nếu nó thẳng cột với
     nội dung hiện có của bảng, thay vì luôn đóng bảng lại. Fix này giải
     quyết được trường hợp vietnamese_doc nhưng gây regression nghiêm
     trọng, lan rộng, xác nhận qua eval đầy đủ — các list item dạng bullet
     và header/footer trang bị hút vào các bảng giả ở en/unicode,
     policy_claude_draft, vi/unicode/mixed, vi/unicode/time-new-roman, và
     cả vietnamese_doc (vd. `"•​ | Sử dụng Claude Team plan, tối thiểu
     5 users..."` — một marker bullet bị tách thành một cột bảng giả). Đã
     revert toàn bộ; đã xác nhận qua eval rằng việc revert khôi phục đúng
     điểm baseline.
   - **Chưa fix.** Một fix an toàn cần một tín hiệu chính xác hơn là chỉ
     kiểm tra chồng lấn theo trục x đơn thuần — vd. kết hợp việc thẳng cột
     với kiểm tra tỷ lệ khoảng-cách-dọc/chiều-cao-dòng, và có thể giới hạn
     ở các trường hợp font/cỡ chữ của dòng đơn độc đó khớp với các ô của
     bảng đang mở — cần verify từng bước với toàn bộ tập mẫu thay vì thử
     một lần cho xong.

7. **Một bảng bị ngắt qua trang phát lại hàng tiêu đề sau chỗ ngắt, và một
   mảnh vỡ/trùng lặp xuất hiện gần điểm tách — đã nhận thấy nhưng chưa điều
   tra.**
   - Thấy ở: vietnamese_doc (cùng "Complex Table"). Sau nội dung hàng 03,
     hàng tiêu đề `"STT | Hạng mục | Estimate (Giờ) | Trạng thái | Note"`
     xuất hiện lại, ngay sau đó là một mảnh mồ côi
     `" | kho & Xác nhận tồn kho |  |  | "` (trông giống phần đuôi của ô
     "...Xác nhận tồn kho" ở hàng 03, bị tách ra riêng).
   - Chưa root-cause — có thể là hành vi lặp-header-qua-trang có chủ đích
     nhưng bị lỗi, hoặc một artefact khi parse ranh giới trang/cột liên
     quan tới bug #6 ở trên. Cần điều tra riêng trước khi quyết định
     có/nên fix thế nào.

8. **Nội dung do pdf2docx dựng lại chiếm nhiều không gian theo chiều dọc
   trên mỗi trang hơn PDF thật một chút, khiến các tài liệu ở ranh giới
   tràn sang một trang vật lý thừa một khi margin trang được tính đúng.**
   - Hiện đang **ẩn/bị che**: vì fix margin đã bị revert (xem mục "Đã thử
     và revert" số 3), margin trang lại bị tính sai gần bằng 0, tình cờ che
     giấu bug này một lần nữa vì để lại thêm không gian dọc khả dụng trên
     mỗi trang. Nó chỉ hiện ra thành một regression thật về số trang/ssim
     một khi margin được tính đúng (tức nếu fix của mục 3 được thử lại).
   - Thấy ở (khi áp fix của mục 3): vi/unicode/calibri (2→2 trang khi không
     có fix margin, 2→3 khi có) và en/unicode (đã sẵn 2→3 dù có fix hay
     không, ssim tệ hơn một chút khi có fix).
   - **Không phải do cơ chế `space_before` của bug #3(c)** — đã xác nhận
     qua kiểm tra trực tiếp rằng đoạn tiêu đề bị đẩy sang trang kế của
     calibri có `space_before = 0` (không vô lý), loại trừ khả năng đó. Ở
     en/unicode, việc tràn trang là qua một đoạn văn khác (phần tiếp nối
     "...journals." của đoạn "cloud-native architectures..." — khiếm
     khuyết auto-wrap của bug #3(a) — tràn sang một trang gần như trống
     trước khi bị ngắt section cưỡng bức).
   - **Chưa root-cause được cơ chế cụ thể.** Ứng viên khả dĩ: việc ước
     lượng chiều cao dòng/khoảng cách đoạn văn thiếu chính xác ở đâu đó
     khác trong pipeline layout (khác với, dù có thể tương tác cùng, bug
     #3(a) và #3(c)) khiến nội dung dựng lại chiếm tổng chiều cao nhiều hơn
     một chút so với nguồn. Cần điều tra riêng — so sánh tổng chiều cao nội
     dung (tổng chiều cao dòng/đoạn văn) giữa PDF nguồn và docx sinh ra cho
     một mẫu ở ranh giới, để tìm cơ chế nào gây ra phần không gian dọc thừa
     đó.
   - Đáng root-cause trước khi thử lại fix của mục 3 — fix bug này trước
     có thể sẽ giúp fix đó land mà hoàn toàn không phải đánh đổi
     ssim/số trang.

## Artefact của công cụ diff (không phải bug pdf2docx — chỉ là nhiễu trong
cách mình so sánh)

- **Một đoạn văn chứa `<w:br/>` (ngắt dòng mềm) có thể trông như bị tách
  thành nhiều đoạn trong `text_diff.txt`, dù nó là một phần tử `<w:p>` duy
  nhất.** `paragraph.text` của `python-docx` render mỗi `<w:br/>` thành một
  ký tự `"\n"` thuần, và `extract_text_lines()` trong `eval/run_eval.py`
  gắn cả chuỗi đó (bao gồm cả newline nhúng bên trong) làm một phần tử danh
  sách; khi ghi ra file diff, newline nhúng đó in ra thành một dòng vật lý
  thừa **không có dấu `+`/`-` ở đầu**.
  - **Quy tắc đọc:** trong `text_diff.txt`, một dòng không có tiền tố
    `+`/`-` là phần tiếp nối do wrap mềm của dòng phía trên, KHÔNG phải một
    đoạn văn/hàng riêng biệt. Chỉ những dòng tự nó bắt đầu bằng `+`/`-` mới
    thực sự là đoạn văn hoặc hàng bảng riêng biệt.
  - Đây chính xác là nguyên nhân khiến một phiên bản trước của tài liệu này
    chẩn đoán sai đoạn "cloud-native architectures..." ở en/unicode là bug
    tách đoạn văn — không phải; kiểm tra XML cho thấy chỉ một `<w:p>`. Luôn
    xác minh một nghi ngờ tách-đoạn-văn bằng XML thô (xem bug #3) trước khi
    tin vào diff văn bản đơn thuần. Và ngay cả một tách XML đã xác nhận
    cũng không tự động là bug nhìn thấy được — một vòng điều tra tiếp theo
    ở bug #3 phát hiện tách XML có thể render giống hệt wrap bình thường
    khi khoảng cách bù của pdf2docx gần đúng (trường hợp b); chỉ render cả
    hai tài liệu ra PDF/PNG rồi so sánh pixel thật mới xác định được một
    tách cấu trúc có ảnh hưởng hình ảnh hay không (trường hợp c thì có;
    trường hợp b thì không).
- **Glyph dấu tick/ký hiệu**: các ô trong original.docx hiện trống trong
  diff của mình (`Claude Code |  | `) trong khi output hiện `✓`. Thuộc tính
  `.text` của `python-docx` không đọc một số glyph font ký hiệu giống cách
  trích xuất văn bản PDF làm — không phải khiếm khuyết chuyển đổi, chỉ là
  một lỗ hổng trong `extract_text_lines()`.
- **Header/footer trong original.docx hoàn toàn không được so sánh**:
  `Document.paragraphs` trong `python-docx` không bao gồm nội dung
  `section.header`/`section.footer`, nên văn bản header/footer thật trong
  original.docx không bao giờ xuất hiện ở phía `-` của diff, khiến các
  diff liên quan tới header/footer trông một chiều (chỉ có dòng `+` từ
  output) ngay cả khi nội dung đó thực sự tồn tại trong bản gốc.

## Đề xuất bước tiếp theo (chưa bắt đầu — triage/ưu tiên sau)

- Gộp khoảng trắng giữa từ và tách hàng bảng (mục Đã fix #1/#2), cùng với
  việc dựng lại marker bullet/số thứ tự (mục Đã fix #4, khép lại #1/#4
  trong `Bugs in pdf2docx`) và fix false-negative của nó khi style trùng
  nhau (mục Đã fix #5) đã xong — xem mục "Đã fix" ở trên. `space_before`
  vô lý ở đầu section của #3(c) (cộng với tối ưu tái dùng section) cũng đã
  fix, nhưng **đã revert theo yêu cầu người dùng** — xem mục "Đã thử và
  revert" số 3; bug #3(c) lại đang mở.
- **Trọng tâm hiện tại (chưa bắt đầu):** với #1/#4 (và false-negative của
  nó) đã khép lại, các mục liên quan tới `text_sim` tiếp theo là #2
  (nhãn/footer → hàng bảng giả, thấy ở 3/7 mẫu — hiện là nguyên nhân chính
  khiến `policy_claude_draft` vẫn thấp nhất) và #6 (dòng tiếp nối của ô wrap
  bị rơi khỏi bảng, thấy ở vietnamese_doc) — #6 rủi ro hơn vì một fix đã thử
  từng gây regression ở
  vài mẫu không liên quan và phải revert (xem #6 bên dưới), nên #2 có lẽ là
  lựa chọn tiếp theo an toàn hơn.
- #2 (nhãn/footer → hàng bảng giả) ưu tiên thấp hơn / mang tính thiết kế
  nhiều hơn (cần logic phân loại header/footer) — đáng để scope riêng.
- #3(a) (tách đoạn văn không nhất quán / lệch auto-wrap) vẫn đang mở và
  đáng fix — đây là một khiếm khuyết thật, nhìn thấy được, về số dòng.
  Trường hợp (b) (tách nhưng không nhìn thấy được) ưu tiên thấp hơn — chỉ
  mang tính thẩm mỹ/cấu trúc. Trường hợp (c) đã mở lại (xem ở trên). #5
  (cột rỗng bị xóa) là phát hiện mới chỉ từ en/unicode — đáng kiểm tra xem
  có lặp lại ở mẫu khác không trước khi ưu tiên thêm.
- #6 (dòng tiếp nối của ô wrap bị rơi khỏi bảng) là bước tiếp theo trực
  tiếp nhất sau fix bug #2, nhưng rủi ro hơn: fix duy nhất đã thử từng gây
  regression ở vài mẫu không liên quan và phải revert. Cần một tín hiệu
  phát hiện chính xác hơn trước khi thử lại.
- #7 (trùng lặp header/mảnh vỡ bảng khi ngắt trang) chưa được điều tra —
  cần root-cause trước khi quyết định ưu tiên.
- #8 (nội dung dựng lại chiếm nhiều không gian dọc hơn nguồn) hiện đang ẩn
  (bị che lại từ khi mục 3 bị revert) nhưng nên root-cause trước khi thử
  lại mục 3 — fix #8 trước có thể sẽ giúp fix đó land mà không phải đánh
  đổi ssim/số trang.
