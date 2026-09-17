import type { MovementSummary } from './movement';

/** Patient-facing interpretation of existing descriptors, not a new gait classifier. */
export function patientSummary(s: MovementSummary, shifted: boolean) {
  if (shifted) return [{ title: 'The phone position needs review', text: 'The phone angle changed. We cannot tell whether this came from your movement or the phone shifting. This walk is saved for review.' }];
  if (s.usableSeconds < 6 || s.segments.some(x => x.context === 'missing-data')) return [{ title: 'Not enough clear recording', text: 'There is too little continuous information to explain this walk. This is a recording limitation, not a judgement about your walking.' }];
  if (s.possibleHandlingSeconds > 0) return [{ title: 'Some movement is difficult to interpret', text: 'The phone may have moved separately from your body. We cannot reliably describe your walking rhythm or changes from this recording.' }];
  const quiet = s.quietSeconds > 0;
  const moving = s.movementSeconds > 0;
  return [
    { title: 'Movement and possible pauses', text: quiet && moving
      ? 'Movement and quieter periods were recorded. You may have paused or moved gently. Rest is welcome and is not marked as poor walking.'
      : quiet ? 'Much of the recording was quiet or unclear. You may have been standing or moving gently. We cannot confirm how much you walked.'
      : moving ? 'Movement was recorded without a clear quiet pause. This does not confirm that you walked continuously.'
      : 'The phone recorded movement that we could not confidently interpret. We cannot confirm walking or pauses.' },
    { title: 'Your movement rhythm', text: s.repeatingMotion === true && moving
      ? 'A repeating movement pattern was visible. If the phone stayed secure while you walked, this may reflect your walking rhythm. It does not show whether your left and right steps were equal.'
      : quiet ? 'We do not judge your rhythm across quiet periods. Taking a rest does not mean that your walking rhythm is poor.'
      : 'A clear repeating pattern could not be confirmed. This alone does not mean your walking was irregular.' },
    { title: 'From beginning to end', text: !moving || s.trend === 'unavailable'
      ? 'There was not enough clear movement near both the beginning and end to compare them.'
      : s.trend === 'similar' ? 'The amount of movement was similar near the beginning and end. This does not tell us your walking speed or balance.'
      : s.trend === 'more' ? 'Movement became larger toward the end, excluding possible pauses. This does not tell us whether you walked faster or became less steady.'
      : 'Movement became smaller toward the end, excluding possible pauses. This does not tell us whether you slowed down or became tired.' },
  ];
}

export const patientMessages: Record<string, [string, string]> = {
  'Pauses': ['Jeda', '停顿'],
  'Rhythm': ['Rentak', '节奏'],
  'Changes': ['Perubahan', '变化'],
  'What this walk tells you': ['Apa yang ditunjukkan oleh rakaman ini', '这次记录告诉您什么'],
  'The phone position needs review': ['Kedudukan telefon perlu disemak', '需要检查手机位置'],
  'The phone angle changed. We cannot tell whether this came from your movement or the phone shifting. This walk is saved for review.': ['Sudut telefon berubah. Kami tidak dapat membezakan pergerakan anda daripada peralihan telefon. Rakaman disimpan untuk semakan.', '手机角度发生变化，无法区分是身体动作还是手机移位。记录已保存，可供查看。'],
  'Not enough clear recording': ['Rakaman jelas tidak mencukupi', '清晰的记录不足'],
  'There is too little continuous information to explain this walk. This is a recording limitation, not a judgement about your walking.': ['Maklumat berterusan tidak cukup untuk menerangkan sesi ini. Ini batas rakaman, bukan penilaian keupayaan berjalan anda.', '连续信息不足，无法说明这次步行。这是记录的局限，并非对您步行能力的评价。'],
  'Some movement is difficult to interpret': ['Sesetengah pergerakan sukar ditafsir', '部分动作难以判断'],
  'The phone may have moved separately from your body. We cannot reliably describe your walking rhythm or changes from this recording.': ['Telefon mungkin bergerak berasingan daripada badan. Rentak atau perubahan berjalan tidak dapat diterangkan dengan yakin daripada rakaman ini.', '手机可能相对身体发生了晃动，无法根据这次记录可靠地描述步行节奏或变化。'],
  'Movement and possible pauses': ['Pergerakan dan kemungkinan berhenti seketika', '动作与可能的停顿'],
  'Movement and quieter periods were recorded. You may have paused or moved gently. Rest is welcome and is not marked as poor walking.': ['Pergerakan dan tempoh lebih tenang direkodkan. Anda mungkin berhenti seketika atau bergerak perlahan. Berehat dibenarkan dan tidak dianggap sebagai kelemahan berjalan.', '记录中有动作，也有较安静的时段。您可能停顿过，或动作较轻。休息是允许的，不会被视为走得不好。'],
  'Much of the recording was quiet or unclear. You may have been standing or moving gently. We cannot confirm how much you walked.': ['Sebahagian besar rakaman tenang atau tidak jelas. Anda mungkin berdiri atau bergerak perlahan. Kami tidak dapat memastikan berapa banyak anda berjalan.', '大部分记录较安静或难以判断。您可能站着或动作较轻，无法确认实际走了多久。'],
  'Movement was recorded without a clear quiet pause. This does not confirm that you walked continuously.': ['Pergerakan direkodkan tanpa tempoh tenang yang jelas. Ini tidak mengesahkan bahawa anda berjalan tanpa henti.', '记录中有动作，未发现明显的安静停顿，但不能据此确认您一直在走。'],
  'The phone recorded movement that we could not confidently interpret. We cannot confirm walking or pauses.': ['Pergerakan telefon tidak dapat ditafsir dengan yakin. Kami tidak dapat memastikan berjalan atau berhenti.', '手机记录了难以明确判断的动作，无法确认步行或停顿。'],
  'Your movement rhythm': ['Rentak pergerakan anda', '您的动作节奏'],
  'A repeating movement pattern was visible. If the phone stayed secure while you walked, this may reflect your walking rhythm. It does not show whether your left and right steps were equal.': ['Corak pergerakan berulang kelihatan. Jika telefon kekal kukuh semasa berjalan, ini mungkin mencerminkan rentak berjalan. Ini tidak menunjukkan sama ada langkah kiri dan kanan seimbang.', '记录中可见重复的动作规律。如果步行时手机固定牢靠，这可能反映步行节奏，但不能说明左右步是否一致。'],
  'We do not judge your rhythm across quiet periods. Taking a rest does not mean that your walking rhythm is poor.': ['Rentak tidak dinilai merentasi tempoh tenang. Berehat tidak bermakna rentak berjalan anda lemah.', '我们不会跨越安静时段评价节奏。休息不代表步行节奏不好。'],
  'A clear repeating pattern could not be confirmed. This alone does not mean your walking was irregular.': ['Corak berulang yang jelas tidak dapat dipastikan. Ini sahaja tidak bermakna berjalan anda tidak teratur.', '未能确认清晰的重复规律，仅凭这一点不能说您的步行不规律。'],
  'From beginning to end': ['Dari awal hingga akhir', '从开始到结束'],
  'There was not enough clear movement near both the beginning and end to compare them.': ['Pergerakan jelas pada awal dan akhir tidak mencukupi untuk perbandingan.', '开始和结束时的清晰动作不足，无法进行比较。'],
  'The amount of movement was similar near the beginning and end. This does not tell us your walking speed or balance.': ['Tahap pergerakan hampir sama pada awal dan akhir. Ini tidak menentukan kelajuan berjalan atau keseimbangan anda.', '开始和结束时的动作幅度相近，但不能据此判断步速或平衡能力。'],
  'Movement became larger toward the end, excluding possible pauses. This does not tell us whether you walked faster or became less steady.': ['Pergerakan lebih besar pada akhir, tidak termasuk kemungkinan berhenti. Ini tidak menentukan sama ada anda berjalan lebih laju atau kurang stabil.', '排除可能的停顿后，后段动作幅度变大，但不能据此判断是否走得更快或更不稳。'],
  'Movement became smaller toward the end, excluding possible pauses. This does not tell us whether you slowed down or became tired.': ['Pergerakan lebih kecil pada akhir, tidak termasuk kemungkinan berhenti. Ini tidak menentukan sama ada anda memperlahankan langkah atau menjadi letih.', '排除可能的停顿后，后段动作幅度变小，但不能据此判断是否放慢了脚步或感到疲劳。'],
  'For your next review': ['Untuk semakan seterusnya', '下次查看时'],
  'Share this recording together with how the walk felt: any rests, turns, discomfort, or help you used. The phone cannot confirm these experiences.': ['Kongsi rakaman bersama pengalaman anda: rehat, pusingan, ketidakselesaan atau bantuan yang digunakan. Telefon tidak dapat mengesahkan pengalaman ini.', '分享记录时，也请说明步行感受：是否休息、转弯、不适或使用辅助。手机无法确认这些实际经历。'],
  'These observations describe movement, not a diagnosis or a score of your walking ability.': ['Pemerhatian ini menerangkan pergerakan, bukan diagnosis atau skor keupayaan berjalan.', '这些观察描述动作，并非诊断或步行能力评分。'],
};
