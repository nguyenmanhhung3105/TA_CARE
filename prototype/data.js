export const VERSION = 1;
export const sectors = ['Công nghệ thông tin','Thương mại điện tử','Logistics','Marketing','Kinh doanh/bán hàng','Y tế','Nông nghiệp/thực phẩm','Chăm sóc khách hàng','Nhân sự/tuyển dụng'];
export const types = ['Thực tập','Toàn thời gian','Bán thời gian','Freelance','Task','Dự án'];
export const modes = ['Tại văn phòng','Kết hợp','Từ xa'];
export const skills = ['JavaScript','HTML/CSS','Git','Python','SQL','API','Kiểm thử','Odoo','Excel','Phân tích dữ liệu','SEO','Nội dung','Quảng cáo','Bán hàng','Giao tiếp','Chăm sóc khách hàng','Tuyển dụng','Quản lý kho','Điều phối','Tiếng Anh','Nghiên cứu thị trường','Dinh dưỡng','An toàn thực phẩm'];
export const accounts = [
  {id:'u-an',name:'Đức Mạnh',role:'candidate',profileId:'p-an'},
  {id:'u-binh',name:'Mạnh Hùng',role:'candidate',profileId:'p-binh'},
  {id:'u-chi',name:'Anh Tuấn',role:'candidate',profileId:'p-chi'},
  {id:'u-lan',name:'An Nhật',role:'candidate',profileId:'p-lan'},
  {id:'u-duc',name:'Anh Đức',role:'candidate',profileId:'p-duc'},
  {id:'u-mai',name:'Thu Mai',role:'candidate',profileId:'p-mai'},
  {id:'u-hoa',name:'Bảo Hòa',role:'candidate',profileId:'p-hoa'},
  {id:'u-sen',name:'Sen Digital',role:'business',orgId:'o-sen'},
  {id:'u-nam',name:'Nam Hà Logistics',role:'business',orgId:'o-nam'},
  {id:'u-admin',name:'Vận hành demo',role:'admin'}
];
export const orgs = [
  {id:'o-sen',name:'Sen Digital',summary:'Studio sản phẩm số hư cấu tại Hà Nội',contact:'contact@sen.example'},
  {id:'o-nam',name:'Nam Hà Logistics',summary:'Đơn vị vận hành hư cấu tại TP.HCM',contact:'hello@namha.example'}
];
const job = (id, orgId, title, sector, type, mode, location, required, preferred, status='published', extra={}) => ({
  id,orgId,title,sector,type,mode,location,required,preferred,status,
  experience:'Không yêu cầu',schedule:'Linh hoạt theo trao đổi',start:'2026-11-01',deadline:'2026-12-15',quantity:1,
  pay:'Trao đổi khi kết nối',description:`Tham gia ${title.toLowerCase()} cùng nhóm, có người hướng dẫn và mục tiêu công việc rõ ràng.`,
  outcome:'Hoàn thành đầu việc và ghi nhận kết quả theo từng giai đoạn.',contactVisible:false, ...extra
});
export const seed = () => ({
  version:VERSION, currentUserId:'u-an', nextId:100, accounts:structuredClone(accounts), orgs:structuredClone(orgs),
  jobs:[
    job('j-01','o-sen','Thực tập Frontend','Công nghệ thông tin','Thực tập','Kết hợp','Hà Nội',['JavaScript','HTML/CSS'],['Git','API']),
    job('j-02','o-sen','Cộng tác viên kiểm thử phần mềm','Công nghệ thông tin','Bán thời gian','Từ xa','Toàn quốc',['Kiểm thử'],['SQL','Git']),
    job('j-03','o-nam','Hỗ trợ triển khai Odoo','Công nghệ thông tin','Dự án','Kết hợp','TP.HCM',['Odoo','Python'],['SQL','API']),
    job('j-04','o-sen','Thực tập nội dung thương mại điện tử','Thương mại điện tử','Thực tập','Từ xa','Toàn quốc',['Nội dung','SEO'],['Excel']),
    job('j-05','o-nam','Điều phối đơn hàng','Logistics','Toàn thời gian','Tại văn phòng','TP.HCM',['Điều phối','Excel'],['Quản lý kho']),
    job('j-06','o-sen','Task nghiên cứu khách hàng','Marketing','Task','Từ xa','Toàn quốc',['Nghiên cứu thị trường'],['Phân tích dữ liệu']),
    job('j-07','o-sen','Cộng tác viên quảng cáo số','Marketing','Freelance','Từ xa','Toàn quốc',['Quảng cáo','Nội dung'],['SEO']),
    job('j-08','o-nam','Nhân viên kinh doanh dịch vụ','Kinh doanh/bán hàng','Toàn thời gian','Tại văn phòng','TP.HCM',['Bán hàng','Giao tiếp'],['Tiếng Anh']),
    job('j-09','o-nam','Hỗ trợ chăm sóc khách hàng','Chăm sóc khách hàng','Bán thời gian','Kết hợp','TP.HCM',['Chăm sóc khách hàng','Giao tiếp'],['Excel']),
    job('j-10','o-sen','Task nghiên cứu dinh dưỡng cộng đồng','Y tế','Task','Từ xa','Toàn quốc',['Dinh dưỡng'],['Phân tích dữ liệu']),
    job('j-11','o-nam','Dự án truy xuất thực phẩm','Nông nghiệp/thực phẩm','Dự án','Kết hợp','TP.HCM',['An toàn thực phẩm'],['Excel']),
    job('j-12','o-sen','Thực tập tuyển dụng','Nhân sự/tuyển dụng','Thực tập','Kết hợp','Hà Nội',['Tuyển dụng','Giao tiếp'],['Excel'])
  ],
  profiles:[
    {id:'p-an',userId:'u-an',name:'Đức Mạnh',headline:'Sinh viên năm 3 · Frontend',education:'Công nghệ thông tin, năm 3',sector:'Công nghệ thông tin',location:'Hà Nội',goal:'Tìm nơi thực hành frontend và học từ sản phẩm thật.',mode:'Kết hợp',availability:'Từ tháng 11, 20 giờ/tuần',pay:'',visible:true,scope:'public',shareContact:false,email:'an@example.com',skillItems:[{name:'JavaScript',level:'Khá',use:'Dựng giao diện'}, {name:'HTML/CSS',level:'Khá',use:'Thiết kế responsive'},{name:'Git',level:'Cơ bản',use:'Làm việc nhóm'}],evidence:[{id:'e-1',title:'Trang giới thiệu câu lạc bộ',role:'Thiết kế và lập trình',description:'Trang web cho câu lạc bộ sinh viên',result:'Đưa vào sử dụng nội bộ',url:'https://example.com/club',status:'unverified'}],cvName:''},
    {id:'p-binh',userId:'u-binh',name:'Mạnh Hùng',headline:'Sinh viên mới bắt đầu',education:'Kinh tế, năm 1',sector:'Marketing',location:'Hà Nội',goal:'Tìm task ngắn để thử sức.',mode:'Từ xa',availability:'Cuối tuần',pay:'',visible:true,scope:'public',shareContact:false,email:'binh@example.com',skillItems:[{name:'Giao tiếp',level:'Cơ bản',use:'Hoạt động nhóm'}],evidence:[],cvName:''},
    {id:'p-chi',userId:'u-chi',name:'Anh Tuấn',headline:'Kiểm thử và dữ liệu',education:'Hệ thống thông tin, năm 4',sector:'Công nghệ thông tin',location:'TP.HCM',goal:'Tham gia dự án kiểm thử sản phẩm.',mode:'Từ xa',availability:'30 giờ/tuần',pay:'',visible:true,scope:'members',shareContact:true,email:'chi@example.com',skillItems:[{name:'Kiểm thử',level:'Khá',use:'Test case'},{name:'SQL',level:'Cơ bản',use:'Truy vấn dữ liệu'},{name:'Git',level:'Cơ bản',use:'Quản lý mã'}],evidence:[{id:'e-2',title:'Bộ test ứng dụng học tập',role:'Kiểm thử',description:'Thiết kế test case',result:'Phát hiện 12 lỗi trong bản demo',url:'',status:'pending'}],cvName:''},
    {id:'p-lan',userId:'u-lan',name:'An Nhật',headline:'Nội dung và SEO',education:'Truyền thông, năm 3',sector:'Thương mại điện tử',location:'Hà Nội',goal:'Làm nội dung có đo lường.',mode:'Từ xa',availability:'20 giờ/tuần',pay:'',visible:true,scope:'public',shareContact:false,email:'lan@example.com',skillItems:[{name:'Nội dung',level:'Khá',use:'Bài viết'},{name:'SEO',level:'Cơ bản',use:'Tối ưu bài'},{name:'Excel',level:'Cơ bản',use:'Theo dõi kết quả'}],evidence:[],cvName:''},
    {id:'p-duc',userId:'u-duc',name:'Anh Đức',headline:'Điều phối vận hành',education:'Logistics, đã tốt nghiệp',sector:'Logistics',location:'TP.HCM',goal:'Cải thiện vận hành kho.',mode:'Tại văn phòng',availability:'Toàn thời gian',pay:'',visible:true,scope:'public',shareContact:false,email:'duc@example.com',skillItems:[{name:'Điều phối',level:'Khá',use:'Phân công ca'},{name:'Excel',level:'Khá',use:'Báo cáo'},{name:'Quản lý kho',level:'Cơ bản',use:'Theo dõi tồn'}],evidence:[],cvName:''},
    {id:'p-mai',userId:'u-mai',name:'Thu Mai',headline:'Chăm sóc khách hàng',education:'Quản trị kinh doanh, năm 2',sector:'Chăm sóc khách hàng',location:'TP.HCM',goal:'Luyện xử lý tình huống khách hàng.',mode:'Kết hợp',availability:'Buổi chiều',pay:'',visible:true,scope:'public',shareContact:false,email:'mai@example.com',skillItems:[{name:'Chăm sóc khách hàng',level:'Khá',use:'Hỗ trợ trực tuyến'},{name:'Giao tiếp',level:'Khá',use:'Tư vấn'}],evidence:[],cvName:''},
    {id:'p-hoa',userId:'u-hoa',name:'Bảo Hòa',headline:'An toàn thực phẩm',education:'Công nghệ thực phẩm, năm 4',sector:'Nông nghiệp/thực phẩm',location:'TP.HCM',goal:'Tham gia dự án truy xuất nguồn gốc.',mode:'Kết hợp',availability:'3 ngày/tuần',pay:'',visible:true,scope:'public',shareContact:false,email:'hoa@example.com',skillItems:[{name:'An toàn thực phẩm',level:'Khá',use:'Quy trình kiểm soát'},{name:'Excel',level:'Cơ bản',use:'Ghi chép'}],evidence:[],cvName:''}
  ],
  requests:[
    {id:'r-01',type:'application',jobId:'j-01',profileId:'p-an',senderId:'u-an',receiverId:'u-sen',message:'Em muốn tìm hiểu vị trí thực tập frontend.',status:'pending',created:'2026-10-14',shareContact:false,history:['Ứng viên gửi đề nghị ứng tuyển']},
    {id:'r-02',type:'invitation',jobId:'j-02',profileId:'p-chi',senderId:'u-sen',receiverId:'u-chi',message:'Mời bạn trao đổi về công việc kiểm thử.',status:'pending',created:'2026-10-14',shareContact:false,history:['Doanh nghiệp gửi lời mời trao đổi']},
    {id:'r-03',type:'application',jobId:'j-04',profileId:'p-lan',senderId:'u-lan',receiverId:'u-sen',message:'Em quan tâm đến nội dung thương mại điện tử.',status:'accepted',created:'2026-10-12',shareContact:false,history:['Ứng viên gửi đề nghị','Doanh nghiệp đồng ý trao đổi']}
  ],
  notifications:[{id:'n-1',userId:'u-sen',requestId:'r-01',message:'Đức Mạnh đã gửi đề nghị ứng tuyển.',read:false},{id:'n-2',userId:'u-chi',requestId:'r-02',message:'Sen Digital đã mời bạn trao đổi.',read:false}],
  feedback:[]
});
