import type {ParticipantProfile,SessionRecord} from './store';
/** Explicit development-only, browser-memory fixtures. Never device measurements. */
export const flowLabEnabled = typeof __DEV__!=='undefined' && __DEV__ && typeof document!=='undefined' && process.env.EXPO_PUBLIC_FLOW_LAB==='1';
export const FLOW_LAB_SESSION='flow-lab-observer-form';
export function flowLabFixtures():{participant:ParticipantProfile;session:SessionRecord}{
 const participant:ParticipantProfile={id:'flow-lab-person',label:'DEMO-P01',favorite:false,archived:false,createdAt:'2026-10-04T00:00:00Z',updatedAt:'2026-10-04T00:00:00Z',demographics:{ageYears:67,sex:'female',heightCm:160,weightKg:61},clinical:{strokeType:'demo only',lesionLocation:'demo only',monthsSinceStroke:12,chronicityStatus:'known',affectedHemisphere:'left',affectedBodySide:'right',historySource:'patient-or-caregiver-report',premorbidGaitNotes:'demo only',jointOrOrthopaedicNotes:'demo only',assistiveDevice:'single-point-cane'}};
 return {participant,session:{id:FLOW_LAB_SESSION,date:'2026-10-04T00:00:00Z',duration:20,isPractice:true,quality:'repeat',windowCount:0,windows:[],participantId:participant.id,participantLabel:participant.label,demographics:participant.demographics,participantSnapshot:participant,assessmentSetup:{protocol:'10mwt',courseLengthM:12,timedDistanceM:10,protocolVariant:'10mwt-12m-central10m-v1',speedCondition:'comfortable',turnDirection:'self-selected'}}};
}
