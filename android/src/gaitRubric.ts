/** Observer-only Appendix A, user-supplied 31-item /62 version. No sensor scoring. */
export const GAIT_FORM_VERSION = "gait-appendix-a-62-v1";
export const GAIT_SOURCE_SHA256 = "8420f916b3908ba8314cf7c6b481d71914ffd76b8bb8ec61e79eafe6973dee06";
export const gaitRubric = [
  {
    "id": 1,
    "title": "Shoulder position",
    "phase": "stance-and-swing",
    "options": [
      {
        "id": "1-0",
        "score": 0,
        "branch": "",
        "text": "normal."
      },
      {
        "id": "1-1",
        "score": 1,
        "branch": "",
        "text": "abnormal position (check all that apply __ depressed, __ elevated, __ retracted, or __ protracted)."
      }
    ],
    "max": 1,
    "sourcePage": 0
  },
  {
    "id": 2,
    "title": "Elbow flexion",
    "phase": "stance-and-swing",
    "options": [
      {
        "id": "2-0",
        "score": 0,
        "branch": "",
        "text": "< 45\u00b0 (normal = ~ 10\u00b0)."
      },
      {
        "id": "2-1",
        "score": 1,
        "branch": "",
        "text": "45 \u2013 90\u00b0 elbow flexion."
      },
      {
        "id": "2-2",
        "score": 2,
        "branch": "",
        "text": "> 90\u00b0 elbow flexion."
      }
    ],
    "max": 2,
    "sourcePage": 0
  },
  {
    "id": 3,
    "title": "Arm swing",
    "phase": "stance-and-swing",
    "options": [
      {
        "id": "3-0",
        "score": 0,
        "branch": "",
        "text": "normal."
      },
      {
        "id": "3-1",
        "score": 1,
        "branch": "",
        "text": "abnormal \u2013 reduced or absent arm swing."
      }
    ],
    "max": 1,
    "sourcePage": 0
  },
  {
    "id": 4,
    "title": "Trunk alignment (Static)",
    "phase": "stance-and-swing",
    "options": [
      {
        "id": "4-0",
        "score": 0,
        "branch": "",
        "text": "normal erect posture (absence of flexion, extension or lateral flexion)."
      },
      {
        "id": "4-1",
        "score": 1,
        "branch": "",
        "text": "trunk statically in __ flexion or __ extension."
      },
      {
        "id": "4-2",
        "score": 2,
        "branch": "",
        "text": "trunk statically in lateral flexion to the __ right or __ left."
      },
      {
        "id": "4-3",
        "score": 3,
        "branch": "",
        "text": "trunk in both __ flexion or __ extension, & lateral flexion to __ right or __ left."
      }
    ],
    "max": 3,
    "sourcePage": 0
  },
  {
    "id": 5,
    "title": "Trunk posture/movement  (Dynamic) (sagittal plane) (lateral view)",
    "phase": "stance",
    "options": [
      {
        "id": "5-0",
        "score": 0,
        "branch": "",
        "text": "normal (static trunk alignment maintained)."
      },
      {
        "id": "5-1",
        "score": 1,
        "branch": "",
        "text": "trunk __ flexes or __ extends (check one) < 30\u00b0."
      },
      {
        "id": "5-2",
        "score": 2,
        "branch": "",
        "text": "trunk __ flexes or __ extends (check one) 30\u00b0 or more."
      }
    ],
    "max": 2,
    "sourcePage": 0
  },
  {
    "id": 6,
    "title": "Trunk posture/movement  (Dynamic) (coronal plane) (front/back view)",
    "phase": "stance",
    "options": [
      {
        "id": "6-0",
        "score": 0,
        "branch": "",
        "text": "normal (static trunk alignment maintained)."
      },
      {
        "id": "6-1",
        "score": 1,
        "branch": "",
        "text": "trunk laterally flexes to __ right or to __ left (check one) < 30\u00b0."
      },
      {
        "id": "6-2",
        "score": 2,
        "branch": "",
        "text": "trunk laterally flexes to __ right or to __ left (check one) 30\u00b0 or more."
      }
    ],
    "max": 2,
    "sourcePage": 0
  },
  {
    "id": 7,
    "title": "Weight shift (lateral displacement of head, trunk and pelvis) (coronal plane) (front/back view)",
    "phase": "stance",
    "options": [
      {
        "id": "7-0",
        "score": 0,
        "branch": "",
        "text": "normal weight shift (~ 25 mm shift over stance limb)."
      },
      {
        "id": "7-1",
        "score": 1,
        "branch": "",
        "text": "reduced weight shift."
      },
      {
        "id": "7-2",
        "score": 2,
        "branch": "",
        "text": "almost none or no weight shift."
      },
      {
        "id": "7-3",
        "score": 2,
        "branch": "",
        "text": "excessive weight shift."
      }
    ],
    "max": 2,
    "sourcePage": 0
  },
  {
    "id": 8,
    "title": "Pelvic position (coronal plane) (front/back view)",
    "phase": "stance",
    "options": [
      {
        "id": "8-0",
        "score": 0,
        "branch": "",
        "text": "normal (no Trendelenberg sign)"
      },
      {
        "id": "8-1",
        "score": 1,
        "branch": "",
        "text": "mild pelvic drop on contralateral side."
      },
      {
        "id": "8-2",
        "score": 2,
        "branch": "",
        "text": "severe or abrupt pelvic drop on contralateral side."
      }
    ],
    "max": 2,
    "sourcePage": 0
  },
  {
    "id": 9,
    "title": "Hip extension (sagittal plane) (lateral view)",
    "phase": "stance",
    "options": [
      {
        "id": "9-0",
        "score": 0,
        "branch": "",
        "text": "normal (moves from 30\u00b0 of hip flexion at initial contact to neutral by midstance, then to 20\u00b0 of extension past neutral in terminal stance)."
      },
      {
        "id": "9-1",
        "score": 1,
        "branch": "",
        "text": "hip extends to neutral by midstance but lacks further hip extension during terminal stance."
      },
      {
        "id": "9-2",
        "score": 2,
        "branch": "",
        "text": "abnormal throughout stance (hip remains in flexion or marked extension)."
      }
    ],
    "max": 2,
    "sourcePage": 0
  },
  {
    "id": 10,
    "title": "Hip rotation (coronal plane) (front/back view)",
    "phase": "stance",
    "options": [
      {
        "id": "10-0",
        "score": 0,
        "branch": "",
        "text": "normal (remains in neutral)"
      },
      {
        "id": "10-1",
        "score": 1,
        "branch": "",
        "text": "abnormal, internal rotation"
      },
      {
        "id": "10-2",
        "score": 1,
        "branch": "",
        "text": "abnormal, external rotation"
      }
    ],
    "max": 1,
    "sourcePage": 0
  },
  {
    "id": 11,
    "title": "Knee \u2013 initial contact phase (sagittal plane) (lateral view).  Choose __ A or __ B (check selection)",
    "phase": "stance",
    "options": [
      {
        "id": "11-0",
        "score": 0,
        "branch": "A. Knee flexion",
        "text": "normal (knee in neutral/not hyperextended)."
      },
      {
        "id": "11-1",
        "score": 1,
        "branch": "A. Knee flexion",
        "text": "5\u00b0 \u2013 15\u00b0 knee flexion."
      },
      {
        "id": "11-2",
        "score": 2,
        "branch": "A. Knee flexion",
        "text": "> 15\u00b0, but < 30\u00b0 knee flexion."
      },
      {
        "id": "11-3",
        "score": 3,
        "branch": "A. Knee flexion",
        "text": "> 30\u00b0 knee flexion."
      },
      {
        "id": "11-4",
        "score": 0,
        "branch": "B. Knee extension",
        "text": "normal (knee in neutral/not in flexion)."
      },
      {
        "id": "11-5",
        "score": 1,
        "branch": "B. Knee extension",
        "text": "5\u00b0 \u2013 15\u00b0 knee hyperextension."
      },
      {
        "id": "11-6",
        "score": 2,
        "branch": "B. Knee extension",
        "text": "> 15\u00b0 up to 30\u00b0 knee hyperextension."
      },
      {
        "id": "11-7",
        "score": 3,
        "branch": "B. Knee extension",
        "text": "> 30\u00b0 knee hyperextension."
      }
    ],
    "max": 3,
    "sourcePage": 1
  },
  {
    "id": 12,
    "title": "Knee \u2013 loading response phase (sagittal plane) (lateral view).  Choose __ A or __ B (check selection) _____",
    "phase": "stance",
    "options": [
      {
        "id": "12-0",
        "score": 0,
        "branch": "A. Knee flexion",
        "text": "normal (up to 15\u00b0 knee flexion)."
      },
      {
        "id": "12-1",
        "score": 1,
        "branch": "A. Knee flexion",
        "text": "> 15\u00b0, but < 30\u00b0 knee flexion."
      },
      {
        "id": "12-2",
        "score": 2,
        "branch": "A. Knee flexion",
        "text": "\u2265 30\u00b0 knee flexion"
      },
      {
        "id": "12-3",
        "score": 0,
        "branch": "B. Knee extension",
        "text": "normal (up to 15\u00b0 knee flexion)."
      },
      {
        "id": "12-4",
        "score": 1,
        "branch": "B. Knee extension",
        "text": "no knee flexion, up to 15\u00b0 knee hyperextension."
      },
      {
        "id": "12-5",
        "score": 2,
        "branch": "B. Knee extension",
        "text": "\u2265 15\u00b0 knee hyperextension."
      }
    ],
    "max": 2,
    "sourcePage": 1
  },
  {
    "id": 13,
    "title": "Knee \u2013 midstance phase (sagittal plane) (lateral view). Choose __ A, __ B, __ C, or __ D (ck. select) _____",
    "phase": "stance",
    "options": [
      {
        "id": "13-0",
        "score": 0,
        "branch": "A. Knee flexion",
        "text": "normal (knee in 4\u00b0 flexion at heel strike, increasing to 15\u00b0 flexion at 14% of gait cycle)."
      },
      {
        "id": "13-1",
        "score": 1,
        "branch": "A. Knee flexion",
        "text": "5 \u2013 15\u00b0 flexion throughout midstance; does not achieve neutral at midstance."
      },
      {
        "id": "13-2",
        "score": 2,
        "branch": "A. Knee flexion",
        "text": "> 15\u00b0, but < 30\u00b0 knee flexion"
      },
      {
        "id": "13-3",
        "score": 3,
        "branch": "A. Knee flexion",
        "text": "\u2265 30\u00b0 knee flexion."
      },
      {
        "id": "13-4",
        "score": 0,
        "branch": "B. Knee extension",
        "text": "normal (knee in 4\u00b0 flexion at heel strike, increasing to 15\u00b0 flexion at 14% of gait cycle)."
      },
      {
        "id": "13-5",
        "score": 1,
        "branch": "B. Knee extension",
        "text": "knee extended through midstance phase; not hyperextended."
      },
      {
        "id": "13-6",
        "score": 2,
        "branch": "B. Knee extension",
        "text": "up to 15\u00b0 knee hyperextension during midstance phase."
      },
      {
        "id": "13-7",
        "score": 3,
        "branch": "B. Knee extension",
        "text": "> 15\u00b0 knee hyperextension during midstance phase."
      },
      {
        "id": "13-8",
        "score": 0,
        "branch": "C. Knee flexion moving to extension",
        "text": "normal (knee in 4\u00b0 flexion at heel strike, increasing to 15\u00b0 flexion at 14% of gait cycle)."
      },
      {
        "id": "13-9",
        "score": 1,
        "branch": "C. Knee flexion moving to extension",
        "text": "normal knee flexion during early midstance phase, then knee extends to neutral."
      },
      {
        "id": "13-10",
        "score": 2,
        "branch": "C. Knee flexion moving to extension",
        "text": "knee flexion during early midstance phase, then knee extends to full extension range (neutral or beyond) in uncontrolled manner, but not snapping back."
      },
      {
        "id": "13-11",
        "score": 3,
        "branch": "C. Knee flexion moving to extension",
        "text": "knee in flexion during early midstance phase, then knee abruptly and forcefully extends into end range in an uncontrolled manner."
      },
      {
        "id": "13-12",
        "score": 0,
        "branch": "D. Knee extension moving to flexion",
        "text": "normal (knee in 4\u00b0 flexion at heel strike, increasing to 15\u00b0 flexion at 14% of gait cycle)."
      },
      {
        "id": "13-13",
        "score": 1,
        "branch": "D. Knee extension moving to flexion",
        "text": "knee remains in extension in early midstance, then knee flexes late, but retains control."
      },
      {
        "id": "13-14",
        "score": 2,
        "branch": "D. Knee extension moving to flexion",
        "text": "knee remains in extension in early midstance, then knee flexes, losing control and regaining control."
      },
      {
        "id": "13-15",
        "score": 3,
        "branch": "D. Knee extension moving to flexion",
        "text": "knee remains in extension in early midstance, then knee buckles with failure to regain control and requires use of compensatory strategies."
      }
    ],
    "max": 3,
    "sourcePage": 1
  },
  {
    "id": 14,
    "title": "Knee \u2013 terminal stance phase/pre-swing phase (heel-rise to toe-off) (sagittal plane) (lateral view)",
    "phase": "stance",
    "options": [
      {
        "id": "14-0",
        "score": 0,
        "branch": "",
        "text": "normal (knee flexion position in sagittal plane 35 \u2013 45\u00b0)."
      },
      {
        "id": "14-1",
        "score": 1,
        "branch": "",
        "text": "knee flexes < 35\u00b0 or > 45\u00b0."
      },
      {
        "id": "14-2",
        "score": 2,
        "branch": "",
        "text": "knee flexes 35 \u2013 45\u00b0, then extends."
      },
      {
        "id": "14-3",
        "score": 3,
        "branch": "",
        "text": "knee remains in full extension throughout."
      }
    ],
    "max": 3,
    "sourcePage": 1
  },
  {
    "id": 15,
    "title": "Ankle movement (sagittal plane) (lateral view). Choose __ A or __ B.  (Check selection).",
    "phase": "stance",
    "options": [
      {
        "id": "15-0",
        "score": 0,
        "branch": "A. Ankle plantar flexion",
        "text": "normal (from ankle neutral position at initial heel contact, moving to 10\u00b0 plantarflexion before midstance, then moving to 10\u00b0 dorsiflexion at heel off)."
      },
      {
        "id": "15-1",
        "score": 1,
        "branch": "A. Ankle plantar flexion",
        "text": "normal from initial contact (with heel strike) to midstance, but in plantarflexion after midstance."
      },
      {
        "id": "15-2",
        "score": 1,
        "branch": "A. Ankle plantar flexion",
        "text": "foot flat at initial contact, moving to slight plantarflexion before midstance, but in plantarflexion after midstance."
      },
      {
        "id": "15-3",
        "score": 2,
        "branch": "A. Ankle plantar flexion",
        "text": "foot flat at initial contact with plantarflexion to heel off."
      },
      {
        "id": "15-4",
        "score": 3,
        "branch": "A. Ankle plantar flexion",
        "text": "no heel contact with excessive plantarflexion to heel off."
      },
      {
        "id": "15-5",
        "score": 3,
        "branch": "A. Ankle plantar flexion",
        "text": "either heel contact or no heel contact followed by excessive and/or early (midstance) plantarflexion (i.e. vaulting)."
      },
      {
        "id": "15-6",
        "score": 0,
        "branch": "B. Ankle dorsiflexion",
        "text": "normal (from ankle neutral position at initial heel contact, moving to 10\u00b0 plantarflexion before midstance, then moving to 10\u00b0 dorsiflexion at heel off)."
      },
      {
        "id": "15-7",
        "score": 1,
        "branch": "B. Ankle dorsiflexion",
        "text": "normal just prior to midstance, but > 10\u00b0 dorsiflexion after midstance"
      },
      {
        "id": "15-8",
        "score": 2,
        "branch": "B. Ankle dorsiflexion",
        "text": "15 \u2013 20\u00b0 dorsiflexion at midstance and to terminal stance (heel off)."
      },
      {
        "id": "15-9",
        "score": 3,
        "branch": "B. Ankle dorsiflexion",
        "text": "excessive ankle dorsiflexion (> 20\u00b0) throughout stance."
      }
    ],
    "max": 3,
    "sourcePage": 2
  },
  {
    "id": 16,
    "title": "Ankle inversion (coronal plane) (front/back view)",
    "phase": "stance",
    "options": [
      {
        "id": "16-0",
        "score": 0,
        "branch": "",
        "text": "normal (slight inversion/supination at initial stance; then eversion/pronation until heel-off)."
      },
      {
        "id": "16-1",
        "score": 1,
        "branch": "",
        "text": "excessive ankle inversion/supination present at initial contact."
      },
      {
        "id": "16-2",
        "score": 2,
        "branch": "",
        "text": "excessive ankle inversion/supination present at initial contact and at midstance."
      },
      {
        "id": "16-3",
        "score": 3,
        "branch": "",
        "text": "excessive ankle inversion/supination throughout stance."
      }
    ],
    "max": 3,
    "sourcePage": 2
  },
  {
    "id": 17,
    "title": "Plantarflexion during terminal stance/pre-swing (heel-rise to toe-off) (sagittal plane) (lateral view)",
    "phase": "stance",
    "options": [
      {
        "id": "17-0",
        "score": 0,
        "branch": "",
        "text": "normal (adequate push-off at pre-swing for moving from dorsiflexion position to 10\u00b0 plantarflexion."
      },
      {
        "id": "17-1",
        "score": 1,
        "branch": "",
        "text": "partial/weak push-off while moving into plantarflexion at toe-off."
      },
      {
        "id": "17-2",
        "score": 2,
        "branch": "",
        "text": "absent/lack of plantarflexion; no push-off."
      }
    ],
    "max": 2,
    "sourcePage": 2
  },
  {
    "id": 18,
    "title": "Toe position (sagittal plane) (lateral view)",
    "phase": "stance",
    "options": [
      {
        "id": "18-0",
        "score": 0,
        "branch": "",
        "text": "normal (toes in neutral position)"
      },
      {
        "id": "18-1",
        "score": 1,
        "branch": "",
        "text": "excessive toe extension."
      },
      {
        "id": "18-2",
        "score": 1,
        "branch": "",
        "text": "clawing."
      }
    ],
    "max": 1,
    "sourcePage": 2
  },
  {
    "id": 19,
    "title": "Trunk posture/movement (Dynamic) (sagittal plane) (lateral view)",
    "phase": "swing",
    "options": [
      {
        "id": "19-0",
        "score": 0,
        "branch": "",
        "text": "normal (static trunk alignment maintained)."
      },
      {
        "id": "19-1",
        "score": 1,
        "branch": "",
        "text": "trunk __ flexes or __ extends (check one) < 30\u00b0."
      },
      {
        "id": "19-2",
        "score": 2,
        "branch": "",
        "text": "trunk __ flexes or __ extends (check one) 30\u00b0 or more."
      }
    ],
    "max": 2,
    "sourcePage": 2
  },
  {
    "id": 20,
    "title": "Trunk posture/movement  (Dynamic) (coronal plane) (front/back view)",
    "phase": "swing",
    "options": [
      {
        "id": "20-0",
        "score": 0,
        "branch": "",
        "text": "normal (static trunk alignment maintained)."
      },
      {
        "id": "20-1",
        "score": 1,
        "branch": "",
        "text": "trunk laterally flexes to __ right or to __ left (check one) < 30\u00b0."
      },
      {
        "id": "20-2",
        "score": 2,
        "branch": "",
        "text": "trunk laterally flexes to __ right or to __ left (check one) 30\u00b0 or more."
      }
    ],
    "max": 2,
    "sourcePage": 2
  },
  {
    "id": 21,
    "title": "Pelvic position (coronal plane) (front/back view)",
    "phase": "swing",
    "options": [
      {
        "id": "21-0",
        "score": 0,
        "branch": "",
        "text": "normal (relatively level pelvis or slightly lower on swing side)."
      },
      {
        "id": "21-1",
        "score": 1,
        "branch": "",
        "text": "mild hip hiking."
      },
      {
        "id": "21-2",
        "score": 2,
        "branch": "",
        "text": "moderate to severe hip hiking."
      }
    ],
    "max": 2,
    "sourcePage": 2
  },
  {
    "id": 22,
    "title": "Pelvic position (sagittal plane) (lateral view)",
    "phase": "swing",
    "options": [
      {
        "id": "22-0",
        "score": 0,
        "branch": "",
        "text": "normal (neutral position with respect to anterior or posterior tilt)."
      },
      {
        "id": "22-1",
        "score": 1,
        "branch": "",
        "text": "anterior pelvic tilt."
      },
      {
        "id": "22-2",
        "score": 1,
        "branch": "",
        "text": "posterior pelvic tilt."
      }
    ],
    "max": 1,
    "sourcePage": 2
  },
  {
    "id": 23,
    "title": "Pelvic rotation as limb swings forward (transverse plane) (top view)",
    "phase": "swing",
    "options": [
      {
        "id": "23-0",
        "score": 0,
        "branch": "",
        "text": "normal (from 5\u00b0 backward rotation at initiation of swing to 5\u00b0 forward rotation by terminal swing)"
      },
      {
        "id": "23-1",
        "score": 1,
        "branch": "",
        "text": "reduced pelvic rotation."
      },
      {
        "id": "23-2",
        "score": 1,
        "branch": "",
        "text": "excessive pelvic rotation."
      },
      {
        "id": "23-3",
        "score": 2,
        "branch": "",
        "text": "absent pelvic rotation."
      }
    ],
    "max": 2,
    "sourcePage": 3
  },
  {
    "id": 24,
    "title": "Hip flexion (sagittal plane) (lateral view)",
    "phase": "swing",
    "options": [
      {
        "id": "24-0",
        "score": 0,
        "branch": "",
        "text": "normal (0\u00b0 hip flexion at initial swing to ~ 35\u00b0 at peak, then reducing to ~ 25\u00b0 at terminal swing; hip neutral with respect to hip abduction/adduction)."
      },
      {
        "id": "24-1",
        "score": 1,
        "branch": "",
        "text": "hip begins swing in flexion, but reaches normal peak."
      },
      {
        "id": "24-2",
        "score": 1,
        "branch": "",
        "text": "> 10\u00b0, but < 30\u00b0 hip flexion peak in the sagittal plane."
      },
      {
        "id": "24-3",
        "score": 2,
        "branch": "",
        "text": "> 10\u00b0, but < 30\u00b0 hip flexion peak, and with hip abduction (e.g. = circumduction)."
      },
      {
        "id": "24-4",
        "score": 2,
        "branch": "",
        "text": "> 10\u00b0, but < 30\u00b0 hip flexion peak, and with hip adduction (e.g. = scissoring)."
      },
      {
        "id": "24-5",
        "score": 3,
        "branch": "",
        "text": "0 to 10\u00b0 hip flexion throughout swing."
      },
      {
        "id": "24-6",
        "score": 3,
        "branch": "",
        "text": "> 35\u00b0 hip flexion (excessive hip flexion)."
      }
    ],
    "max": 3,
    "sourcePage": 3
  },
  {
    "id": 25,
    "title": "Hip rotation (coronal plane) (front/back view)",
    "phase": "swing",
    "options": [
      {
        "id": "25-0",
        "score": 0,
        "branch": "",
        "text": "normal (remains in neutral)"
      },
      {
        "id": "25-1",
        "score": 1,
        "branch": "",
        "text": "abnormal, internal rotation"
      },
      {
        "id": "25-2",
        "score": 1,
        "branch": "",
        "text": "abnormal, external rotation"
      }
    ],
    "max": 1,
    "sourcePage": 3
  },
  {
    "id": 26,
    "title": "Knee \u2013 initial swing (sagittal plane) (lateral view)",
    "phase": "swing",
    "options": [
      {
        "id": "26-0",
        "score": 0,
        "branch": "",
        "text": "normal (40 \u2013 60\u00b0 of knee flexion)."
      },
      {
        "id": "26-1",
        "score": 1,
        "branch": "",
        "text": "at least 15\u00b0 knee flexion, but < 40\u00b0 knee flexion."
      },
      {
        "id": "26-2",
        "score": 2,
        "branch": "",
        "text": "< 15\u00b0 knee flexion."
      },
      {
        "id": "26-3",
        "score": 3,
        "branch": "",
        "text": "knee never flexes."
      }
    ],
    "max": 3,
    "sourcePage": 3
  },
  {
    "id": 27,
    "title": "Knee \u2013 midswing (sagittal plane) (lateral view)",
    "phase": "swing",
    "options": [
      {
        "id": "27-0",
        "score": 0,
        "branch": "",
        "text": "normal (60\u00b0 knee flexion \u00b1 4\u00b0."
      },
      {
        "id": "27-1",
        "score": 1,
        "branch": "",
        "text": "45\u00b0 - 55\u00b0 knee flexion."
      },
      {
        "id": "27-2",
        "score": 2,
        "branch": "",
        "text": "25\u00b0 - 45\u00b0 knee flexion."
      },
      {
        "id": "27-3",
        "score": 3,
        "branch": "",
        "text": "0 to 25\u00b0 knee flexion."
      }
    ],
    "max": 3,
    "sourcePage": 3
  },
  {
    "id": 28,
    "title": "Knee \u2013 terminal swing (sagittal plane) (lateral view)",
    "phase": "swing",
    "options": [
      {
        "id": "28-0",
        "score": 0,
        "branch": "",
        "text": "normal (from knee flexed position to full knee extension)."
      },
      {
        "id": "28-1",
        "score": 1,
        "branch": "",
        "text": "from knee flexed position, remaining in knee flexion throughout."
      },
      {
        "id": "28-2",
        "score": 1,
        "branch": "",
        "text": "from knee extension position, remaining in knee extension throughout."
      }
    ],
    "max": 1,
    "sourcePage": 3
  },
  {
    "id": 29,
    "title": "Ankle movement (sagittal plane) (lateral view)",
    "phase": "swing",
    "options": [
      {
        "id": "29-0",
        "score": 0,
        "branch": "",
        "text": "normal (from initial plantarflexion at terminal stance [toe-off] to neutral by midswing, then slight dorsiflexion just prior to initial contact in stance)."
      },
      {
        "id": "29-1",
        "score": 1,
        "branch": "",
        "text": "midswing ankle neutral but no terminal swing dorsiflexion."
      },
      {
        "id": "29-2",
        "score": 2,
        "branch": "",
        "text": "no midswing ankle neutral and no terminal swing dorsiflexion; plantarflexion throughout."
      }
    ],
    "max": 2,
    "sourcePage": 3
  },
  {
    "id": 30,
    "title": "Ankle inversion (coronal plane) (front/back view)",
    "phase": "swing",
    "options": [
      {
        "id": "30-0",
        "score": 0,
        "branch": "",
        "text": "normal (ankle remains in neutral regarding inversion/eversion)."
      },
      {
        "id": "30-1",
        "score": 1,
        "branch": "",
        "text": "ankle in inverted position during swing."
      }
    ],
    "max": 1,
    "sourcePage": 3
  },
  {
    "id": 31,
    "title": "Toe position (sagittal plane) (lateral view)",
    "phase": "swing",
    "options": [
      {
        "id": "31-0",
        "score": 0,
        "branch": "",
        "text": "normal (toes in neutral position)"
      },
      {
        "id": "31-1",
        "score": 1,
        "branch": "",
        "text": "inadequate toe extension."
      },
      {
        "id": "31-2",
        "score": 1,
        "branch": "",
        "text": "clawing."
      }
    ],
    "max": 1,
    "sourcePage": 3
  }
] as const;
