# Chapter 4 — The Mandate Effect

**Câu hỏi:** Hệ thống có đang cải thiện không?  
**Câu trả lời:** Có — về mặt đầu vào. Chưa — về mặt kết quả cho cư dân.

---

## Bối cảnh: Tại sao có mandate?

- Năm 2021, Royal Commission into Aged Care xác định **57.6% cư dân** đang sống trong các cơ sở có staffing ở mức không chấp nhận được
- Trước mandate, nhà cung cấp tự quyết định staffing — không có sàn tối thiểu bắt buộc
- Uỷ ban: *"Providers are free to judge for themselves what staffing numbers are 'adequate'. The status quo is unacceptable."*
- Deloitte dự báo cần thêm 70% workforce (186k → 316k FTE) từ 2020–2050 chỉ để giữ nguyên tỷ lệ hiện tại

---

## Mandate yêu cầu gì?

| Thời điểm | Yêu cầu |
|-----------|---------|
| 1/7/2023 | Registered nurse có mặt **24/7** tại mọi cơ sở residential |
| **1/10/2023** | Tối thiểu **200 phút** chăm sóc trực tiếp/cư dân/ngày, trong đó ít nhất **40 phút** phải là registered nurse |
| 1/10/2024 | Nâng lên **215 phút** tổng / **44 phút** RN |

---

## Insight 1 — Mandate hoạt động: chất lượng quốc gia tăng +7.4%

- Điểm chất lượng trung bình quốc gia: **3.40 → 3.65** (+0.25 pts) sau Oct 2023
- Mức tăng là step-change rõ ràng — không phải trend chậm, có thể thấy trên mọi tiểu bang chỉ trong vài quarters
- Tất cả 8 tiểu bang và vùng lãnh thổ đều cải thiện về điểm tuyệt đối
- **Nguồn:** star_ratings_by_facility.csv — before/after Oct 2023

---

## Insight 2 — Staffing là thứ duy nhất thực sự di chuyển

| Sub-rating | Trước | Sau | Thay đổi |
|-----------|-------|-----|---------|
| Staffing | 2.49 | 3.00 | **+0.51 pts** |
| Compliance | 4.28 | 4.57 | +0.29 pts |
| Residents experience | 3.28 | 3.50 | +0.22 pts |
| **Quality measures** | 3.55 | 3.54 | **−0.015 pts** |

- Staffing tăng lớn nhất — đúng với thiết kế mandate
- Quality measures (kết quả sức khoẻ cư dân) gần như không thay đổi
- Nghiên cứu độc lập **SAHMRI / Flinders University (2025)** trên hơn 2,000 cơ sở xác nhận: *"Despite rising staffing levels, no meaningful association emerged between increased care minutes and improved resident quality measures."* — A/Prof Stephanie Harrison
- Mandate cải thiện đầu vào. Kết quả đầu ra chưa theo kịp.

---

## Insight 3 — Compliance thực tế thấp hơn nhiều so với kỳ vọng

- Trước mandate: ước tính chỉ **3.8%** cơ sở đủ điều kiện đáp ứng tiêu chuẩn mới *(The Conversation)*
- 2023–24: chỉ **34%** cơ sở đáp ứng đồng thời cả hai targets (total + RN minutes) — *Productivity Commission 2025*
- 24/7 RN đạt **93.5%** compliance — dễ đo, dễ cưỡng chế hơn care minutes
- Tháng 1/2025: ACQSC cưỡng chế **11 nhà cung cấp / 27 cơ sở** — cap star rating ở 1 sao, cấm đạt 5 sao trong 3 năm
- Star ratings thưởng cho nỗ lực cải thiện, không chỉ full compliance — giải thích tại sao staffing sub-rating tăng +0.51 pts dù chỉ 1/3 cơ sở fully compliant

---

## Insight 4 — Các tiểu bang: NT bứt phá, VIC tụt hạng

| Tiểu bang | Thay đổi | Hạng: đầu → cuối |
|-----------|---------|-----------------|
| NT | **+0.748 pts** | 7 → **1** |
| VIC | +0.312 pts | **1 → 5** |
| ACT | +0.306 pts | cải thiện ít nhất |

- NT xuất phát thấp nhất, tăng mạnh nhất — mandate tác động lớn nhất ở nơi có khoảng cách lớn nhất
- VIC không tệ đi tuyệt đối — nhưng các tiểu bang khác bắt kịp nhanh hơn
- Không tiểu bang nào giảm điểm tuyệt đối
- **Nguồn:** star_ratings_by_facility.csv — first snapshot (May 2023) vs latest (Feb 2026)

---

## Insight 5 — 17 SA3 vẫn đang đi xuống

- **302/323 SA3** có xu hướng chất lượng cải thiện
- **17/323 SA3** vẫn đang giảm — mandate chưa đến được
- Worst: **Esperance (WA)** — −0.07 pts/quarter
- Gold Coast Hinterland và Port Douglas–Daintree (QLD) cũng trong nhóm giảm
- **Nguồn:** linear regression slope trên quality_score theo quarters, min 4 snapshots

---

## Insight 6 — Khoảng cách workforce theo địa lý (bối cảnh cho SA3 at-risk)

- Metro: **317 nhân viên ngành** / 1,000 người 65+
- Rural: **256** / 1,000 người 65+
- Remote: **245** / 1,000 người 65+
- Để đạt mức metro: rural cần thêm ~**95,342 FTE**; remote cần thêm ~**12,958 FTE**
- **Nguồn:** Morris et al., IJERPH April 2025 (peer-reviewed)

---

## Framing

| Cấp độ | Thông điệp |
|--------|-----------|
| Quốc gia | Mandate hoạt động — +7.4% là step-change có thể đo lường |
| Sub-rating | Nhưng nó chỉ sửa được staffing, chưa sửa được outcomes cho cư dân |
| SA3 | Ở 17 cộng đồng, mandate vẫn chưa đến được |
| Tông | Thận trọng lạc quan — đang cải thiện, nhưng chưa đủ và chưa đồng đều |
