export const protocolMessages:Record<string,readonly [string,string]> = {
  'Phone checks are complete. Stand at the start of the marked path. Stay still until you hear Go. Walk through the whole path, then stop and stand still. The phone will save automatically.':['Pemeriksaan telefon selesai. Berdiri di permulaan laluan bertanda. Tunggu arahan Mula tanpa bergerak. Berjalan hingga hujung, kemudian berhenti dan berdiri diam. Telefon akan menyimpan secara automatik.','手机检查已完成。站在标记路线的起点，保持静止直到听见“开始”。走完整条路线，然后停下并站稳。手机会自动保存。'],
  'Walk comfortably through the marked path. At the final marker, stop and stand still until the phone says the capture has ended.':['Berjalan dengan selesa di sepanjang laluan bertanda. Pada penanda terakhir, berhenti dan berdiri diam hingga telefon menyatakan rakaman tamat.','沿标记路线舒适地行走。到终点标记后停下并站稳，直到手机提示记录结束。'],
  'The walk capture has ended. Rest comfortably. Phone distance and speed are estimates, not verified 10-metre timed-zone results.':['Rakaman berjalan tamat. Berehatlah dengan selesa. Jarak dan kelajuan telefon ialah anggaran, bukan keputusan zon 10 meter yang disahkan.','步行记录已结束。请舒适休息。手机给出的距离和速度是估计值，并非经核实的10米计时区结果。'],
  'Phone checks are complete. Sit back in the chair and stay still. Wait for Go. Stand, walk to the three-metre mark, turn, return and sit. Stay still until the phone saves automatically.':['Pemeriksaan telefon selesai. Duduk bersandar di kerusi dan diam. Tunggu arahan Mula. Berdiri, berjalan ke penanda tiga meter, berpusing, kembali dan duduk. Kekal diam hingga telefon menyimpan secara automatik.','手机检查已完成。靠坐在椅子上并保持静止。听到“开始”后起身，走到三米标记，转身返回并坐下。保持静止，直到手机自动保存。'],
  'Stand, walk to the mark, turn, return and sit. Stay seated and still until the phone says capture has ended.':['Berdiri, berjalan ke penanda, berpusing, kembali dan duduk. Kekal duduk dan diam hingga telefon menyatakan rakaman tamat.','起身，走到标记处，转身返回并坐下。保持坐姿和静止，直到手机提示记录结束。'],
  'The chair-to-chair capture has ended. Stay comfortably seated. The phone endpoint is provisional; chair contact was not verified.':['Rakaman dari kerusi ke kerusi telah tamat. Terus duduk dengan selesa. Titik tamat telefon masih sementara; sentuhan dengan kerusi tidak dapat disahkan.','起身往返的记录已结束。请舒适地坐着。手机判断的终点是暂定的，无法确认是否已坐稳。'],
  'Phone checks are complete. Stand at the start and stay still until you hear Go. Walk comfortably for two minutes. You may rest; the clock continues. The phone stops and saves automatically.':['Pemeriksaan telefon selesai. Berdiri di permulaan dan diam hingga mendengar Mula. Berjalan dengan selesa selama dua minit. Anda boleh berehat; masa terus berjalan. Telefon berhenti dan menyimpan secara automatik.','手机检查已完成。站在起点，保持静止直到听见“开始”。舒适地走两分钟。可以休息，计时仍会继续。手机会自动停止并保存。'],
  'Two minutes have finished. Stop safely. Your phone-based distance and speed estimates are saved with the recording.':['Dua minit telah tamat. Berhenti dengan selamat. Anggaran jarak dan kelajuan telefon disimpan bersama rakaman.','两分钟已结束。请安全停下。手机估计的距离和速度已随记录保存。'],
  'Phone checks are complete. Stand at the start and stay still until you hear Go. Follow the clear route for six minutes. You may slow down or rest. The phone stops and saves automatically.':['Pemeriksaan telefon selesai. Berdiri di permulaan dan diam hingga mendengar Mula. Ikut laluan yang lapang selama enam minit. Anda boleh memperlahankan langkah atau berehat. Telefon berhenti dan menyimpan secara automatik.','手机检查已完成。站在起点，保持静止直到听见“开始”。沿安全路线走六分钟。可以放慢或休息。手机会自动停止并保存。'],
  'Six minutes have finished. Stop safely. Your phone-based distance and speed estimates are saved with the recording.':['Enam minit telah tamat. Berhenti dengan selamat. Anggaran jarak dan kelajuan telefon disimpan bersama rakaman.','六分钟已结束。请安全停下。手机估计的距离和速度已随记录保存。'],
  'Prepare a clear marked path before starting. The phone captures without further taps, but its distance and endpoint estimates do not verify floor marks or chair contact.':['Sediakan laluan bertanda yang lapang sebelum bermula. Telefon merakam tanpa ketikan lagi, tetapi anggaran jarak dan titik tamat tidak mengesahkan penanda lantai atau sentuhan kerusi.','开始前请准备清晰的标记路线。手机可免触碰记录，但其距离和终点估计无法核实地面标记或椅子接触。'],
  'HANDS-FREE TEST':['UJIAN TANPA SENTUH','免触碰测试'],
  'Move into the starting position and stay still. The phone will say Go when it settles. No button is needed.':['Ambil posisi mula dan diam. Telefon akan menyebut Mula selepas stabil. Tiada butang diperlukan.','到达起始位置并保持静止。手机稳定后会提示“开始”，无需按按钮。'],
  'Wait for Go before moving.':['Tunggu arahan Mula sebelum bergerak.','听到“开始”后再移动。'],
  'seconds since Go — provisional':['saat sejak Mula — sementara','从“开始”起的秒数——暂定'],
  'At the final marker, stop and stay still. For TUG, sit and remain still. The phone saves after a sustained stop. A long rest can end capture early, so this is not a verified clinical endpoint.':['Di penanda terakhir, berhenti dan diam. Untuk TUG, duduk dan kekal diam. Telefon menyimpan selepas berhenti seketika. Rehat yang lama boleh menamatkan rakaman awal, jadi titik tamat ini belum disahkan secara klinikal.','到终点标记后停下并保持静止。TUG测试请坐下并保持静止。手机在持续静止后保存。长时间休息可能提前结束记录，因此终点未经临床核实。'],
  'The phone stops automatically when time is up. Resting does not pause the clock.':['Telefon berhenti secara automatik apabila masa tamat. Rehat tidak menghentikan jam.','时间到后手机会自动停止。休息不会暂停计时。'],
  'Voice is off. Watch for the timer to start, or ask a helper for the Go cue.':['Suara dimatikan. Perhatikan bila pemasa bermula, atau minta pembantu memberikan isyarat Mula.','语音已关闭。请留意计时器开始，或请助手提示“开始”。'],
  'Confirm emergency stop':['Sahkan berhenti kecemasan','确认紧急停止'],
  'Average speed includes the full timed interval and any rests.':['Kelajuan purata merangkumi seluruh tempoh ujian termasuk waktu rehat.','平均速度包含完整计时区间及休息时间。'],
  'This is whole-walk estimated speed, not speed in the central 10 m timed zone.':['Ini ialah anggaran kelajuan sepanjang berjalan, bukan kelajuan dalam zon 10 m yang diukur masa.','这是全程估计速度，不是中间10米计时区的速度。'],
  'This is not a verified TUG time or walking distance.':['Ini bukan masa TUG atau jarak berjalan yang disahkan.','这不是经核实的TUG时间或步行距离。'],
  'Heuristic based on height and candidate step peaks. Not a measured distance or validated clinical speed.':['Anggaran berdasarkan ketinggian dan puncak langkah calon. Bukan jarak yang diukur atau kelajuan klinikal yang disahkan.','根据身高和候选步伐峰值作出的估计。不是实测距离或经验证的临床速度。'],
  'Hide measured reference form':['Sembunyikan borang rujukan ukuran','隐藏实测参考表格'],
  'Add measured reference (optional)':['Tambah rujukan ukuran (pilihan)','添加实测参考数据（可选）'],
  'Use a marked 12 m path: 1 m to get moving, 10 m in the middle, then 1 m to slow down. Stand still at the start until you hear Go. At the end marker, stop and stand still until the phone saves. The phone cannot detect the two timed-zone marks; its speed is an experimental whole-walk estimate, not a clinical 10MWT result.':['Gunakan laluan bertanda 12 m: 1 m untuk mula bergerak, 10 m di tengah, kemudian 1 m untuk memperlahankan langkah. Berdiri diam di permulaan hingga mendengar Mula. Di penanda akhir, berhenti dan diam hingga telefon menyimpan. Telefon tidak dapat mengesan dua penanda zon masa; kelajuannya ialah anggaran eksperimen sepanjang berjalan, bukan keputusan 10MWT klinikal.','使用标记好的12米路线：先走1米，中间10米，最后1米减速。站在起点保持静止，直到听到“开始”。到终点标记后停下并站稳，直到手机保存。手机无法检测计时区的两个标记；速度只是全程实验性估计，并非临床10MWT结果。'],
  'Follow a clear measured route for two minutes. Stand still at the start until you hear Go. Rest if needed; the clock keeps running. The phone stops and saves automatically. Phone distance is an estimate. A measured course is needed to validate it.':['Ikut laluan yang lapang dan telah diukur selama dua minit. Berdiri diam di permulaan hingga mendengar Mula. Rehat jika perlu; masa terus berjalan. Telefon berhenti dan menyimpan secara automatik. Jarak telefon ialah anggaran. Laluan yang diukur diperlukan untuk mengesahkannya.','沿清晰、已测量的路线行走两分钟。站在起点保持静止，直到听到“开始”。需要时可休息，计时仍继续。手机会自动停止并保存。手机距离是估计值，需要已测量的路线进行验证。'],
  'Follow a clear, level route for six minutes. Stand still at the start until you hear Go. You may slow down or rest; the clock keeps running. The phone stops and saves automatically. Its distance is an estimate. Record any different course length for later validation.':['Ikut laluan yang lapang dan rata selama enam minit. Berdiri diam di permulaan hingga mendengar Mula. Anda boleh memperlahankan langkah atau berehat; masa terus berjalan. Telefon berhenti dan menyimpan secara automatik. Jaraknya ialah anggaran. Catat panjang laluan yang berbeza untuk pengesahan kemudian.','沿清晰、平坦的路线行走六分钟。站在起点保持静止，直到听到“开始”。可以放慢或休息，计时仍继续。手机会自动停止并保存。距离为估计值。请记录不同路线的长度，以便之后验证。'],
  'Use a sturdy chair and a mark 3 m away. After the standing phone check, sit back and stay still until you hear Go. Stand, walk to the mark, turn, return and sit. Stay still until the phone saves. It cannot verify chair contact or a clinical TUG endpoint, so the saved time is provisional.':['Gunakan kerusi yang kukuh dan penanda 3 m jauhnya. Selepas pemeriksaan telefon sambil berdiri, duduk bersandar dan diam hingga mendengar Mula. Berdiri, berjalan ke penanda, berpusing, kembali dan duduk. Kekal diam hingga telefon menyimpan. Telefon tidak dapat mengesahkan sentuhan kerusi atau titik tamat TUG klinikal, maka masa yang disimpan adalah sementara.','使用稳固的椅子，并在3米处设置标记。完成站立时的手机检查后，靠坐并保持静止，直到听到“开始”。起身，走到标记处，转身返回并坐下。保持静止，直到手机保存。手机无法核实椅子接触或临床TUG终点，因此保存的时间是暂定值。'],
  'Prepare a 12 metre path: 1 metre to get moving, 10 metres in the middle, then 1 metre to slow down.':['Sediakan laluan 12 meter: 1 meter untuk mula bergerak, 10 meter di tengah, kemudian 1 meter untuk memperlahankan langkah.','准备一条12米路线：先走1米，中间10米，最后1米减速。'],
  'Wait for Go, then walk comfortably through both marks without touching the phone.':['Tunggu arahan Mula, kemudian berjalan dengan selesa melepasi kedua-dua penanda tanpa menyentuh telefon.','听到“开始”后舒适地走过两个标记，无需触碰手机。'],
  'At the final marker, stop and stand still. The phone saves automatically; its speed is only an estimate.':['Di penanda akhir, berhenti dan berdiri diam. Telefon menyimpan secara automatik; kelajuannya hanyalah anggaran.','到终点标记后停下并站稳。手机会自动保存；速度只是估计值。'],
  'Follow the finish cue':['Ikut isyarat tamat','听从结束提示'],
  'The clock starts at Go and keeps running during rests. The phone stops and saves at two minutes.':['Jam bermula pada Mula dan terus berjalan semasa rehat. Telefon berhenti dan menyimpan pada dua minit.','计时从“开始”起算，休息时也继续。两分钟后手机会停止并保存。'],
  'Follow a clear route at your own pace for six minutes. Keep your usual walking aid.':['Ikut laluan yang lapang mengikut rentak sendiri selama enam minit. Gunakan alat bantuan berjalan biasa anda.','沿清晰路线以自己的速度走六分钟。继续使用平常的助行器具。'],
  'Listen to the phone':['Dengar arahan telefon','听手机提示'],
  'The phone gives start and finish cues, then saves automatically. Its distance is an estimate.':['Telefon memberi isyarat mula dan tamat, kemudian menyimpan secara automatik. Jaraknya ialah anggaran.','手机发出开始和结束提示，然后自动保存。距离是估计值。'],
  'Sit with your back against the chair. Wait for the phone to say Go, then stand and walk to the mark three metres away.':['Duduk bersandar pada kerusi. Tunggu telefon menyebut Mula, kemudian berdiri dan berjalan ke penanda tiga meter jauhnya.','背靠椅子坐好。等待手机提示“开始”，然后起身走到三米标记处。'],
  'Sit back down and stay still until the phone saves. It cannot verify chair contact.':['Duduk semula dan kekal diam hingga telefon menyimpan. Telefon tidak dapat mengesahkan sentuhan kerusi.','重新坐下并保持静止，直到手机保存。手机无法确认椅子接触。'],
  'From a chair, stand, walk 3 m, turn, return and sit. The phone saves after you sit still.':['Dari kerusi, berdiri, berjalan 3 m, berpusing, kembali dan duduk. Telefon menyimpan selepas anda duduk diam.','从椅子起身，走3米，转身返回并坐下。坐稳保持静止后，手机会保存。'],
  "Capture has a three-minute limit. The worker must stop the clinical stopwatch at the actual test endpoint.":["Rakaman mempunyai had tiga minit. Petugas mesti menghentikan jam randik klinikal pada titik tamat sebenar ujian.","采集上限为三分钟。工作人员必须在测试实际终点停止临床秒表。"],
  "Use the project’s marked 12 m path: 1 m acceleration, 10 m timed, then 1 m deceleration. Keep the same aid and speed condition across visits. The worker times the middle 10 m with a stopwatch. Capture starts before Go and ends after the worker confirms finish, with a three-minute capture limit. Boundary crossings are not detected. Enter the stopwatch result separately. This is one trial; repeat and average trials according to the selected clinical protocol.": [
    "Gunakan laluan projek 12 m: 1 m memecut, 10 m diukur masa, kemudian 1 m memperlahankan langkah. Kekalkan alat bantuan dan keadaan kelajuan yang sama. Petugas mengukur masa 10 m tengah dengan jam randik. Rakaman bermula sebelum Mula dan tamat apabila petugas mengesahkan selesai, dengan had tiga minit. Lintasan penanda tidak dikesan. Masukkan masa jam randik secara berasingan. Ini satu percubaan; ulang dan puratakan mengikut protokol klinikal yang dipilih.",
    "使用本项目标记的12米路线：1米加速、10米计时、1米减速。复测时使用相同助行工具和速度条件。工作人员用秒表测量中间10米。采集在开始口令前启动，由工作人员确认结束，最长采集三分钟。手机不会检测越过标记。请另行填写秒表结果。这是一次试验；请按选定临床方案重复并取平均。"
  ],
  "Measure distance covered in two minutes on a measured, clear course. Use the same aid and course on repeat tests. Rest is allowed while the clock continues. Capture starts before Go; the two-minute app clock starts with the spoken cue, or the worker tap when voice is off. The worker administers the selected protocol, checks timing, counts laps and measures the final partial distance. The app does not detect laps or verify clinical completion.": [
    "Ukur jarak dalam dua minit pada laluan yang diukur dan lapang. Gunakan alat bantuan dan laluan sama untuk ujian ulangan. Rehat dibenarkan dan masa terus berjalan. Rakaman bermula sebelum Mula; jam aplikasi bermula dengan suara Mula atau ketikan petugas jika suara dimatikan. Petugas mengendalikan protokol pilihan, menyemak masa, mengira pusingan dan mengukur baki jarak. Aplikasi tidak mengesan pusingan atau mengesahkan penyempurnaan klinikal.",
    "在已测量的畅通路线上测量两分钟步行距离。复测使用相同路线和助行工具。可以休息，计时继续。采集在开始口令前启动；应用时钟从语音口令开始，无语音时从工作人员点击开始。工作人员执行选定方案、核对时间、数圈并测量最后不足一圈的距离。应用不会检测圈数或确认临床测试完成。"
  ],
  "Measure distance in six minutes on a level, measured course. The ATS layout uses a 30 m corridor; document any different course. Standing rests are allowed and the clock continues. Capture starts before Go; the app clock starts with the spoken cue, or the worker tap when voice is off. App walking commentary and turn warnings are suppressed. The worker supplies standardized timed encouragement, counts laps, measures the final partial distance and verifies the clinical outcome.": [
    "Ukur jarak dalam enam minit pada laluan rata yang diukur. Susun atur ATS menggunakan koridor 30 m; catat jika laluan berbeza. Rehat berdiri dibenarkan dan masa terus berjalan. Rakaman bermula sebelum Mula; jam aplikasi bermula dengan suara Mula atau ketikan petugas jika suara dimatikan. Komen berjalan dan amaran belokan aplikasi disekat. Petugas memberi galakan berjadual standard, mengira pusingan, mengukur baki jarak dan mengesahkan hasil klinikal.",
    "在平坦、已测量的路线上测量六分钟距离。ATS采用30米走廊；使用其他路线时需注明。允许站立休息，计时继续。采集在开始口令前启动；时钟从语音口令开始，无语音时从工作人员点击开始。应用不播放步行评价或转弯提醒。工作人员提供标准定时鼓励、数圈、测量最后不足一圈的距离并核实临床结果。"
  ],
  "Use a standard armchair and a mark 3 m away. After standing phone checks, sit with your back against the chair. The worker confirms readiness. Capture starts before Go, including the chair rise. Stand, walk to the mark, turn, return and sit. The worker times from Go to seat contact with a separate stopwatch and ends capture when settled. The phone does not detect turns or sitting completion. A three-minute capture limit is not a clinical result. Practise once before the scored trial.": [
    "Gunakan kerusi berlengan standard dan penanda pada jarak 3 m. Selepas pemeriksaan telefon sambil berdiri, duduk bersandar pada kerusi. Petugas mengesahkan kesediaan. Rakaman bermula sebelum Mula, termasuk pergerakan bangun. Berdiri, berjalan ke penanda, pusing, kembali dan duduk. Petugas mengukur masa dari Mula hingga duduk dengan jam randik berasingan dan menamatkan rakaman setelah stabil. Telefon tidak mengesan belokan atau selesai duduk. Had rakaman tiga minit bukan hasil klinikal. Berlatih sekali sebelum percubaan dinilai.",
    "使用标准扶手椅，并在3米处设置标记。站立完成手机检查后，坐下并靠在椅背上。工作人员确认准备就绪。采集在开始口令前启动，包含起身动作。站起、走到标记、转身、返回并坐下。工作人员另用秒表从口令计时到臀部接触椅面，待稳定后结束采集。手机不会判断转弯或坐下完成。三分钟采集上限并非临床结果。正式计时前先练习一次。"
  ],
  "Phone checks are complete. Stand at the start of the marked path. Walk past both timing marks at your comfortable pace, then slow down. Wait for Go.": [
    "Pemeriksaan telefon selesai. Berdiri di permulaan laluan bertanda. Berjalan melepasi kedua-dua penanda masa pada kelajuan selesa, kemudian perlahankan langkah. Tunggu Mula.",
    "手机检查完成。请站在标记路线的起点。以舒适的速度走过两个计时标记，然后减速。请等开始口令。"
  ],
  "Walk through the marked path. The worker times the middle section and ends capture after you have slowed down.": [
    "Berjalan melalui laluan bertanda. Petugas mengukur masa bahagian tengah dan menamatkan rakaman selepas anda memperlahankan langkah.",
    "沿标记路线行走。工作人员计时中间路段，待您减速后结束采集。"
  ],
  "The walk capture has ended. Rest comfortably. The worker will enter the marked-zone stopwatch time.": [
    "Rakaman berjalan tamat. Berehat dengan selesa. Petugas akan memasukkan masa jam randik bagi zon bertanda.",
    "步行采集已结束。请舒适地休息。工作人员将填写标记区间的秒表时间。"
  ],
  "Phone checks are complete. Sit back in the chair. On Go, stand, walk to the three-metre mark, turn, return and sit. Wait for the worker.": [
    "Pemeriksaan telefon selesai. Duduk bersandar pada kerusi. Apabila mendengar Mula, bangun, berjalan ke penanda tiga meter, pusing, kembali dan duduk. Tunggu petugas.",
    "手机检查完成。请坐下并靠在椅背上。听到开始后起身，走到三米标记，转身返回并坐下。请等待工作人员。"
  ],
  "Stand, walk to the mark, turn, return and sit. The worker times from Go until you are seated again.": [
    "Bangun, berjalan ke penanda, pusing, kembali dan duduk. Petugas mengukur masa dari Mula sehingga anda duduk semula.",
    "起身，走到标记，转身返回并坐下。工作人员从开始口令计时到您再次坐下。"
  ],
  "The chair-to-chair capture has ended. Stay comfortably seated. The worker will enter the stopwatch time.": [
    "Rakaman dari kerusi ke kerusi tamat. Kekal duduk dengan selesa. Petugas akan memasukkan masa jam randik.",
    "起立行走返回坐下的采集已结束。请舒适地坐好。工作人员将填写秒表时间。"
  ],
  "Phone checks are complete. Follow the measured route for two minutes from Go. Rest if needed; the clock keeps running. The worker measures your distance.": [
    "Pemeriksaan telefon selesai. Ikut laluan yang diukur selama dua minit dari Mula. Berehat jika perlu; masa terus berjalan. Petugas mengukur jarak anda.",
    "手机检查完成。从开始口令起，沿测量路线走两分钟。需要时可以休息，计时继续。工作人员测量您的距离。"
  ],
  "Follow the measured route and turn at its markers. Rest if needed; the two-minute clock keeps running.": [
    "Ikut laluan yang diukur dan pusing di penanda. Berehat jika perlu; jam dua minit terus berjalan.",
    "沿测量路线行走，在标记处转弯。需要时可以休息，两分钟计时继续。"
  ],
  "Two minutes have finished. Stop safely and stay where you are while the worker measures the remaining distance.": [
    "Dua minit telah tamat. Berhenti dengan selamat dan kekal di tempat anda sementara petugas mengukur baki jarak.",
    "两分钟结束。请安全停下并留在原处，等待工作人员测量最后一段距离。"
  ],
  "Phone checks are complete. Follow the measured route for six minutes from Go. You may slow down or rest. Listen to the worker for the timed instructions.": [
    "Pemeriksaan telefon selesai. Ikut laluan yang diukur selama enam minit dari Mula. Anda boleh memperlahankan langkah atau berehat. Dengar arahan berjadual petugas.",
    "手机检查完成。从开始口令起，沿测量路线走六分钟。您可以减速或休息。请听工作人员的定时指示。"
  ],
  "Follow the measured route. Turns and standing rests are allowed. The worker gives the standard timed instructions; the clock keeps running.": [
    "Ikut laluan yang diukur. Belokan dan rehat berdiri dibenarkan. Petugas memberi arahan berjadual standard; masa terus berjalan.",
    "沿测量路线行走。允许转弯和站立休息。工作人员提供标准定时指示，计时继续。"
  ],
  "Six minutes have finished. Stop safely and stay where you are while the worker measures the remaining distance.": [
    "Enam minit telah tamat. Berhenti dengan selamat dan kekal di tempat anda sementara petugas mengukur baki jarak.",
    "六分钟结束。请安全停下并留在原处，等待工作人员测量最后一段距离。"
  ],
  "This test needs a worker to prepare the course, give protocol instructions and confirm the outcome. The phone does not detect distance markers or chair contact.": [
    "Ujian ini memerlukan petugas untuk menyediakan laluan, memberi arahan protokol dan mengesahkan hasil. Telefon tidak mengesan penanda jarak atau sentuhan kerusi.",
    "此测试需要工作人员准备路线、提供测试指示并确认结果。手机不会检测距离标记或臀部接触椅面。"
  ],
  "Go.": [
    "Mula.",
    "开始。"
  ],
  "Capture stopped before the planned finish. Rest safely. The worker should record the reason.": [
    "Rakaman berhenti sebelum tamat yang dirancang. Berehat dengan selamat. Petugas perlu mencatat sebabnya.",
    "采集在计划结束前停止。请安全休息。工作人员应记录原因。"
  ],
  "The capture time limit has been reached. Rest safely. This does not confirm that the test was completed.": [
    "Had masa rakaman telah dicapai. Berehat dengan selamat. Ini tidak mengesahkan bahawa ujian telah selesai.",
    "已达到采集时间上限。请安全休息。这并不表示测试已完成。"
  ],
  "Stop comfortably now. Stand still while the movement check finishes.": [
    "Berhenti dengan selesa sekarang. Berdiri diam sehingga pemeriksaan pergerakan selesai.",
    "现在请舒适地停下。站稳，等待动作检查完成。"
  ],
  "Worker: ready to start": [
    "Petugas: sedia untuk mula",
    "工作人员：准备开始"
  ],
  "Worker: finish capture": [
    "Petugas: tamatkan rakaman",
    "工作人员：结束采集"
  ],
  "Stop test early": [
    "Hentikan ujian lebih awal",
    "提前结束测试"
  ],
  "Preview finish event": [
    "Pratonton peristiwa tamat",
    "模拟结束事件"
  ],
  "PREVIEW — NO RECORDING SAVED": [
    "PRATONTON ? TIADA RAKAMAN DISIMPAN",
    "预览 — 不保存记录"
  ],
  "WORKER-ASSISTED TEST": [
    "UJIAN DENGAN PETUGAS",
    "工作人员协助测试"
  ],
  "Worker: confirm the participant is seated and ready. Use a separate stopwatch from Go until seated again.": [
    "Petugas: sahkan peserta duduk dan bersedia. Gunakan jam randik berasingan dari Mula sehingga duduk semula.",
    "工作人员：确认参与者已坐好并准备就绪。另用秒表从开始口令计时到再次坐下。"
  ],
  "Worker: confirm the marked course is ready. Use the protocol stopwatch and record the measured outcome.": [
    "Petugas: sahkan laluan bertanda sedia. Gunakan jam randik protokol dan catat hasil yang diukur.",
    "工作人员：确认标记路线准备就绪。按方案使用秒表并记录实测结果。"
  ],
  "Waiting for the spoken Go. Do not start yet.": [
    "Menunggu suara Mula. Jangan mula dahulu.",
    "等待语音开始口令。请先不要开始。"
  ],
  "seconds since Go — not the clinical result": [
    "saat sejak Mula ? bukan hasil klinikal",
    "开始后秒数 — 非临床结果"
  ],
  "App coaching is off. The worker gives the standard timed encouragement.": [
    "Bimbingan aplikasi dimatikan. Petugas memberi galakan berjadual standard.",
    "应用步行指导已关闭。工作人员提供标准定时鼓励。"
  ],
  "No extra coaching during the measured test. Follow the worker’s protocol instructions.": [
    "Tiada bimbingan tambahan semasa ujian diukur. Ikut arahan protokol petugas.",
    "计量测试期间不提供额外指导。请按工作人员的测试指示进行。"
  ],
  "Voice is off. The worker says Go when pressing the start button.": [
    "Suara dimatikan. Petugas menyebut Mula ketika menekan butang mula.",
    "语音已关闭。工作人员按下开始按钮时说出开始口令。"
  ],
  "The start cue was not confirmed. No clinical time was recorded.": [
    "Isyarat mula tidak disahkan. Tiada masa klinikal direkodkan.",
    "未确认开始口令。不记录临床时间。"
  ],
  "Live sensor readings are missing. Wait or return to setup.": [
    "Bacaan sensor langsung tiada. Tunggu atau kembali ke persediaan.",
    "缺少实时传感器读数。请等待或返回准备页面。"
  ],
  "A worker is present to prepare the course, give test instructions and record the outcome.": [
    "Petugas hadir untuk menyediakan laluan, memberi arahan ujian dan mencatat hasil.",
    "有工作人员在场准备路线、提供测试指示并记录结果。"
  ],
  "Protocol capture timing": [
    "Masa rakaman protokol",
    "测试采集计时"
  ],
  "Capture includes time before Go. The app timer is not a worker-verified clinical outcome.": [
    "Rakaman termasuk masa sebelum Mula. Pemasa aplikasi bukan hasil klinikal yang disahkan petugas.",
    "采集包含开始口令前的时间。应用计时并非工作人员核实的临床结果。"
  ],
  "Seconds from Go: {0}": [
    "Saat dari Mula: {0}",
    "开始后秒数：{0}"
  ],
  "Capture ended: {0}": [
    "Rakaman tamat: {0}",
    "采集结束原因：{0}"
  ],
  "duration": [
    "tempoh tamat",
    "时长结束"
  ],
  "worker-ended": [
    "ditamatkan petugas",
    "工作人员结束"
  ],
  "interrupted": [
    "terganggu",
    "中断"
  ],
  "capture-limit": [
    "had rakaman",
    "采集上限"
  ],
  "App walking commentary and turn reminders are disabled for this test. The worker provides the standard timed messages. Optional app audio gives setup, Go and finish cues only.": [
    "Komen berjalan dan peringatan belokan aplikasi dimatikan untuk ujian ini. Petugas memberi mesej berjadual standard. Audio aplikasi pilihan hanya memberi arahan persediaan, Mula dan tamat.",
    "本测试关闭应用步行评价和转弯提醒。工作人员提供标准定时提示。可选的应用语音仅提供准备、开始和结束提示。"
  ],
  "The clock starts at Go and keeps running during rests. Stop at the finish cue. The worker confirms your measured distance.": [
    "Jam bermula pada Mula dan terus berjalan semasa rehat. Berhenti pada isyarat tamat. Petugas mengesahkan jarak yang diukur.",
    "从开始口令计时，休息时继续。听到结束提示后停下。工作人员确认实测距离。"
  ],
  "The app gives start and finish cues. During the test, the worker gives standard timed instructions and measures your distance.": [
    "Aplikasi memberi isyarat mula dan tamat. Semasa ujian, petugas memberi arahan berjadual standard dan mengukur jarak anda.",
    "应用提供开始和结束提示。测试期间，工作人员给出标准定时指示并测量距离。"
  ]
};
