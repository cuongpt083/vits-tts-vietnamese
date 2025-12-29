# Modify features to include text to speech English

## 🎯 I. Mục tiêu & yêu cầu chính (Aim & Core request)
- Mục tiêu chính: bổ sung tính năng text to speech tiếng Anh
- Mục tiêu phụ: cho phép lựa chọn ngôn ngữ khi gọi API thông qua tham số `lang` trong query string. Các bản cập nhật sau này sẽ bổ sung thêm các ngôn ngữ khác.
- Kết quả mong đợi:
    - Mã nguồn API được sửa lại để cho phép lựa chọn ngôn ngữ khi gọi API thông qua tham số `lang` trong query string.
    - Mã nguồn `server.py` được sửa lại để load model tương ứng khi gọi API thông qua tham số `lang` trong query string.
    - File âm thanh (WAV) được tạo ra sau khi gọi API sẽ được lưu vào thư mục `audio` với tên file là hash của text, được lưu trong thời gian tối đa là 4 giờ, sau đó sẽ được xóa.

## 📝 II. Bối cảnh chung và đối tượng hướng đến (General context and target audience)
- Bối cảnh chung: Project đã hoàn thiện xử lý text to speech tiếng Việt thông qua API. Nhưng hiện tại chỉ có tiếng Việt được hỗ trợ, người dùng muốn sử dụng API để xử lý text to speech tiếng Anh và các ngôn ngữ khác thông qua API.
- Đối tượng hướng đến: lập trình viên.

## 📝 III. Yêu cầu chi tiết (Detailed requirements)
- Các nội dung bắt buộc: 
    - Mã nguồn API được sửa lại để cho phép lựa chọn ngôn ngữ khi gọi API thông qua tham số `lang` trong query string. Trường hợp `lang` không được cung cấp thì sẽ sử dụng tiếng Việt.
    - Mã nguồn `server.py` được sửa lại để load model tương ứng khi gọi API thông qua tham số `lang` trong query string. Trường hợp `lang` không được cung cấp thì sẽ sử dụng tiếng Việt. Nếu `lang` được cung cấp thì sẽ load model tương ứng, cụ thể:
        - `lang=vi` sẽ load model tiếng Việt, file `pretrained_vi.onnx`.
        - `lang=en` sẽ load model tiếng Anh, file `pretrained_en_US.onnx`.
        - các ngôn ngữ khác sẽ được bổ sung sau, nhưng tên file sẽ có quy tắc là `pretrained_{lang}.onnx`.
    - File âm thanh (WAV) được tạo ra sau khi gọi API sẽ được lưu vào thư mục `audio` với tên file là hash của text, sau khi API trả về kết quả, file âm thanh sẽ được lưu trong thời gian tối đa là 4 giờ, sau đó sẽ được xóa.
- Ràng buộc và giới hạn:
    - Thời gian tối đa để lưu file âm thanh là 4 giờ.
    - API hiện tại chỉ hỗ trợ ngôn ngữ tiếng Việt và tiếng Anh.
    - API chỉ tiếp nhận text có độ dài tối đa là 1000 ký tự.
    - API chỉ tiếp nhận tối đa 3 request trong 1 giây.
    - API chỉ tiếp nhận tối đa 30 request trong 1 phút.
    
## 📝 IV. Phong cách và giọng điệu (Style and tone)
- Phong cách và giọng điệu của API sẽ được giữ nguyên, không thay đổi.
