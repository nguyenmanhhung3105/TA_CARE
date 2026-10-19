# Hình ảnh trang chủ

Tạo bằng skill `imagegen`, công cụ tích hợp `image_gen.imagegen`, nền không trong suốt. Không dùng ảnh người thật, hồ sơ khách hàng hoặc logo giả. Nhân vật/cảnh là minh họa hư cấu. File gốc vẫn giữ trong thư mục `generated_images` của phiên làm việc; bản dùng trên website nằm tại `source/apps/tacare/addons/tacare_website/static/src/img/`, chuyển JPEG để tối ưu truyền tải.

## Năm ảnh biên tập bổ sung

| File cuối | Kích thước tối đa | Dung lượng xấp xỉ |
| --- | --- | --- |
| `work-tech.jpg` | 1152px | 220KB |
| `work-logistics.jpg` | 1152px | 204KB |
| `work-health.jpg` | 1152px | 160KB |
| `portfolio-studio.jpg` | 1152px | 307KB |
| `community-wide.jpg` | 1440px | 322KB |

Prompt cuối đã gửi:

**work-tech**

> Editorial documentary-style photography for a premium Vietnamese career website, a contemporary software and creative product studio in Vietnam, 3 fictional young Asian professionals collaborating naturally at a large table with laptops and a physical prototype. Candid moment, no eye contact with camera, beautiful daylight, confident art direction, clean architecture, green plants and restrained warm ochre details, forest green elements, realistic skin texture, refined analogue film grain. Wide landscape 3:2. No legible text on screens or walls, no logos or watermarks, no branding. This is an illustrative fictional scene, no identifiable real person.

**work-logistics**

> Editorial documentary-style photography for a premium Vietnamese career website, a fictional Asian logistics specialist in a modern warehouse using a handheld scanner near neatly arranged parcels, confident focused expression, natural side light, professional safety vest, clean organized setting, warm neutral palette with forest green workwear accents. Refined magazine photography, realistic details, landscape 3:2. No readable labels, letters, numbers, logos or watermarks, no identifiable real people.

**work-health**

> Premium editorial photography of two fictional Vietnamese healthcare professionals reviewing an anonymous unmarked medical chart in a bright contemporary hospital corridor, respectful warm candid moment, clean scrubs, professional realistic appearance, soft natural light, muted neutral and forest green palette, landscape 3:2. No patients, no readable charts, no medical personal data, no letters, logos or watermarks. Fictional illustrative scene.

**portfolio-studio**

> High-end design magazine still-life photograph: an open editorial portfolio, architectural scale maquette, tactile paper samples, matte forest green and golden ochre shapes, precise abstract line drawings, on a warm ivory artist worktable. Beautiful late afternoon raking daylight, tactile real materials, quiet and sophisticated composition with generous negative space, landscape 3:2. No people. No legible words, letters, numbers, logos or watermark. Publication quality contemporary art direction.

**community-wide**

> Cinematic editorial photograph for a Vietnamese career community website: fictional group of 7 diverse Asian adults in a beautiful bright creative workshop, sharing sketches and discussing a new project around a long table, natural candid gestures, a range of technical, creative and business occupations, generous airy composition, warm late afternoon sunlight through large windows, subtle deep blue, forest green and ochre objects, natural realistic people and faces, wide landscape 16:9 image. No readable text on any surface, no logos, no watermark. Fictional illustrative scene.

## Ba minh họa hành trình

`hero-profiles.jpg`, `hero-jobs.jpg`, `hero-connections.jpg` hiện dùng ở ba chương trong TA.CARE, không còn làm ba hero cùng cấu trúc.

**hero-jobs — prompt cuối**

> An editorial illustration for a Vietnamese recruitment website hero. A beautifully art-directed miniature working world: three stylized non-identifiable Asian professionals collaborating around cream paper job cards, one with laptop, another with a small parcel, a designer holding a colored print; tiny symbolic plant. Tactile paper-cut and subtle matte 3D materials, forest green #35764a and warm golden ochre accents, ivory background #f7f8f5, restrained sophisticated composition, soft natural studio light, subtle shadows. Landscape 3:2, artwork fills the frame with breathing space, no typography or letters, no numbers, no logos, no watermark. Not a UI screenshot. Optimized for a friendly premium employment platform.

**hero-profiles — prompt cuối**

> An editorial illustration for a Vietnamese professional profile website hero. A quiet crafted scene of an open cream portfolio folder, elegantly layered paper project pages with abstract diagrams and geometric photographs without any readable text, a stylized non-identifiable Asian professional presenting a small design piece, a sprouting olive plant. Tactile paper-cut and subtle matte 3D materials, forest green #155e38 with muted golden yellow accents, warm ivory backdrop #f7f8f5, sophisticated publication art direction, soft studio daylight, landscape 3:2 composition with generous breathing space, no typography, letters, numbers, logos or watermark. Not a UI screenshot.

**hero-connections — prompt cuối**

> An editorial illustration for a Vietnamese career connection platform website hero. Two small groups of stylized non-identifiable Asian professionals on opposite sides of a graceful arched blue and green bridge, exchanging cream paper portfolio cards at the center. Symbol of people, demonstrated skills and opportunity. Tactile paper-cut and subtle matte 3D materials, rich blue #1355c0 with forest green accents, warm ivory backdrop, soft studio daylight, balanced calm sophisticated composition, landscape 3:2, no typography, letters, numbers, logos or watermark. Not a UI screenshot.

Font Be Vietnam Pro và Lora được tự host cùng giấy phép OFL trong `static/src/fonts/`. Logo thật của ba thương hiệu tiếp tục dùng các file có sẵn.
