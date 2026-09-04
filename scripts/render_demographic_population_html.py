from pathlib import Path
import html

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "DEMOGRAPHIC_CLINICAL_POPULATION_COVERAGE.html"

rows = [
    ("Core binary classifier", "Felius + Voisard + Sint", "314 participants; 126 healthy / 188 stroke", "Direct training and internal participant-disjoint validation", "Strong source coverage, but individual age/sex coverage is incomplete or unavailable in the linked modeling tables.", "Keep as the current pooled training candidate; report performance by source and avoid age-generalisation claims."),
    ("External binary test", "RevalExo", "17 participants; 7 healthy / 10 stroke", "Locked external evaluation", "Independent site/device population; individual ages are not available, with only cohort-level summaries.", "Retain as the primary external test. Treat results as site/device robustness, not age-stratified validation."),
    ("Adult age span", "Voisard full release", "259 valid-age participants; ages 18–90", "Age/domain reference; only the 121-person binary subset is in the current classifier matrix", "Provides the widest adult age context, including healthy, neurological and orthopaedic groups.", "Use for age-stratified exploratory analysis and future re-linking; do not silently add non-binary labels to training."),
    ("Older healthy population", "Triaxial healthy reference", "60 healthy participants; ages 65–88; 24/36 sex-code split", "Domain/age reference only", "Older-adult coverage is useful, but recordings do not provide the required bilateral LB/LF/RF channels for direct classifier scoring.", "Use for age and sensor-domain analysis or self-supervised pretraining; do not fabricate missing channels."),
    ("Stroke recovery/severity", "Zhou rehabilitation", "10 stroke participants; ages 37–88; 7 male / 3 female; FAC visit 1: 1–5", "Longitudinal severity and recovery analysis", "Adds clinically meaningful functional ambulation variation, but has no healthy controls and repeated visits.", "Use as a stroke-only severity/longitudinal holdout or auxiliary task; split by participant and visit."),
    ("Young healthy adults", "DUO-GAIT", "16 healthy participants; exact ages 21–35", "Healthy domain/age reference", "Covers a younger adult band not represented by the older healthy reference, but has no stroke group.", "Use to test healthy-domain shift and age confounding; not as stroke-classification labels."),
    ("Healthy age bands", "OxWalk", "39 healthy participants; coarse age bands", "Healthy domain/age reference", "Adds healthy population diversity, but age resolution is coarse and the protocol/sensor setup differs.", "Use for population-shift analysis after harmonisation; do not treat it as a direct clinical test."),
    ("Broader clinical specificity", "Mobilise-D (not yet downloaded)", "Planned non-stroke clinical groups include PD, MS, fracture/COPD/CHF-related mobility cohorts", "Future specificity/exclusion evaluation", "Needed to test whether the model is detecting stroke-specific gait rather than generic mobility impairment.", "Prioritise a manageable subgroup download after confirming labels, sensor channels, and licensing."),
    ("Reference-only clinical breadth", "PiG", "138 able-bodied adults and 50 stroke survivors; ages 19–86", "Reference/feature-transfer evidence", "Motion-capture/force/EMG rather than the current wearable-IMU input, so it is not directly poolable.", "Use only for clinical construct comparison or feature hypotheses unless a valid sensor mapping is established."),
]

def esc(x): return html.escape(str(x))

body = """<!doctype html><html lang='en'><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Demographic and Clinical Population Coverage</title>
<style>
body{font-family:Segoe UI,Arial,sans-serif;background:#f5f7fb;color:#172033;margin:0;padding:32px}
.wrap{max-width:1500px;margin:auto}.hero{background:#102a43;color:#fff;border-radius:14px;padding:28px 32px;margin-bottom:20px}
h1{margin:0 0 8px;font-size:30px}.subtitle{color:#cfe3f5;font-size:16px}
.callouts{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:18px 0}
.card{background:#fff;border:1px solid #dbe3ed;border-radius:12px;padding:18px;box-shadow:0 2px 8px #17203312}.card h2{font-size:15px;margin:0 0 8px;color:#102a43}.card p{margin:0;line-height:1.45}
.decision{border-left:5px solid #168aad;background:#e9f7fb}.warning{border-left:5px solid #e09f3e;background:#fff8e8}
.tablebox{background:#fff;border-radius:12px;box-shadow:0 2px 8px #17203312;overflow:auto;border:1px solid #dbe3ed}
table{border-collapse:collapse;width:100%;min-width:1250px}th{background:#173f5f;color:#fff;text-align:left;padding:13px;font-size:13px;position:sticky;top:0}td{padding:13px;border-bottom:1px solid #e7edf3;vertical-align:top;line-height:1.4;font-size:13px}tr:nth-child(even){background:#f8fafc}.tag{display:inline-block;border-radius:20px;padding:4px 9px;font-weight:600;font-size:11px;background:#d9f0f7;color:#075985}.tag.ref{background:#fff0c2;color:#8a4b08}.tag.future{background:#e7ddff;color:#5b21b6}
.foot{color:#53657a;font-size:12px;margin-top:14px}
@media(max-width:900px){body{padding:14px}.callouts{grid-template-columns:1fr}.hero{padding:22px}}
</style></head><body><div class='wrap'>
<section class='hero'><h1>Demographic and Clinical Population Coverage</h1><div class='subtitle'>Decision aid for whether the current evidence supports different populations—not a replacement for the source-level robustness matrix.</div></section>
<section class='callouts'>
<div class='card decision'><h2>What is covered now</h2><p>Adult healthy/stroke discrimination across three wearable-IMU sources, plus an independent RevalExo test. The pooled model has meaningful source diversity.</p></div>
<div class='card warning'><h2>What is not proven</h2><p>Age-stratified performance, sex-stratified performance, and stroke specificity against non-stroke clinical impairment are not yet established because linked subject-level labels are incomplete.</p></div>
<div class='card'><h2>Best next evidence</h2><p>Preserve participant-disjoint testing, add age/sex/clinical metadata where legally available, and evaluate non-stroke clinical cohorts before using “clinical-ready” language.</p></div>
</section><div class='tablebox'><table><thead><tr><th>Population dimension</th><th>Source</th><th>Coverage</th><th>How it can be used</th><th>Current evidence and limitation</th><th>Action</th></tr></thead><tbody>"""

for i, r in enumerate(rows):
    kind = "tag" if i < 2 else ("tag future" if "future" in r[3].lower() or "not yet" in r[1].lower() else "tag ref")
    body += "<tr>" + f"<td><strong>{esc(r[0])}</strong></td><td>{esc(r[1])}</td><td>{esc(r[2])}</td><td><span class='{kind}'>{esc(r[3])}</span></td><td>{esc(r[4])}</td><td>{esc(r[5])}</td>" + "</tr>"

body += """</tbody></table></div><p class='foot'>Prepared from the current local dataset audits and locked benchmark reports. Counts refer to participants, not overlapping windows. The table intentionally distinguishes direct classifier use from supporting population/domain evidence.</p></div></body></html>"""
OUT.write_text(body, encoding="utf-8")
print(OUT)
