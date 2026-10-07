const {test,expect}=require('@playwright/test');
test('Leaving through navigation saves an unfinished worker draft',async({page})=>{
 await page.goto('/');await page.getByRole('button',{name:'Open demo assessment',exact:true}).click();
 await page.getByLabel('Assessor ID or initials',{exact:true}).fill('BACK-SAVE');
 await page.getByRole('button',{name:'left',exact:true}).click();await page.getByRole('button',{name:'Video observation',exact:true}).click();
 await page.getByRole('button',{name:'Begin items',exact:true}).click();await page.getByRole('radio').nth(1).click();
 await page.getByRole('checkbox',{name:'elevated',exact:true}).click();
 await page.getByRole('button',{name:/back/i}).first().click();
 await page.getByRole('button',{name:'Open demo assessment',exact:true}).click();
 await expect(page.getByText('Items rated: 1 of 31',{exact:true})).toBeVisible();
 await expect(page.getByText('2. Elbow flexion',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Previous item',exact:true}).click();
 await expect(page.getByRole('checkbox',{name:'elevated',exact:true})).toBeChecked();
});
test('Draft resumes at first missing item, preserves branches, and keeps navigation visible',async({page})=>{
 await page.goto('/');await page.getByRole('button',{name:'Open demo assessment',exact:true}).click();
 await page.getByLabel('Assessor ID or initials',{exact:true}).fill('DRAFT-PT');
 await page.getByRole('button',{name:'right',exact:true}).click();await page.getByRole('button',{name:'In-person observation',exact:true}).click();
 await page.getByRole('button',{name:'Begin items',exact:true}).click();await page.getByRole('radio').first().click();
 await page.getByRole('button',{name:'Save draft',exact:true}).click();
 await page.getByRole('button',{name:'Previous item',exact:true}).click();await page.getByRole('button',{name:'Save & back',exact:true}).click();
 await page.getByRole('button',{name:'Open demo assessment',exact:true}).click();
 await expect(page.getByText('2. Elbow flexion',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Overview',exact:true}).click();
 await expect(page.getByRole('button',{name:'Finish assessment',exact:true})).toBeDisabled();
 await page.getByRole('button',{name:/^Review item 13:/}).click();
 await expect(page.getByRole('radio')).toHaveCount(4);
 const branch=page.getByRole('button',{name:/^Branch D\./});await branch.click();
 await expect(page.getByRole('radio')).toHaveCount(4);await page.getByRole('radio').nth(1).click();
 // Long original criteria must expand the card, rather than overlap the next choice.
 const cards=await page.getByRole('radio').all();
 for(let i=0;i<cards.length-1;i++){
  const a=await cards[i].boundingBox(),b=await cards[i+1].boundingBox();
  expect(a.y+a.height).toBeLessThanOrEqual(b.y+1);
 }
 for(const card of cards){
  const overflow=await card.evaluate(el=>{const r=el.getBoundingClientRect();return [...el.children].some(c=>c.getBoundingClientRect().bottom>r.bottom+1);});
  expect(overflow).toBe(false);
 }
 const box=await page.getByRole('button',{name:'Next item',exact:true}).boundingBox();
 expect(box.y+box.height).toBeLessThanOrEqual(page.viewportSize().height);
 await page.screenshot({path:'dist/flow-lab/observer-flashcard.png',fullPage:true});
});
for(const language of ['Bahasa Melayu','简体中文'])test(`Patient language ${language} keeps the entire worker form English`,async({page})=>{
 await page.goto('/');await page.getByRole('radio',{name:language,exact:true}).click();
 // The development tool's label is intentionally stable; the clinical screen uses English.
 await page.getByRole('button',{name:'Open demo assessment',exact:true}).click();
 await expect(page.getByText('Assessor details',{exact:true})).toBeVisible();
 await expect(page.getByRole('button',{name:'Begin items',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Begin items',exact:true}).click();
 await expect(page.getByText('1. Shoulder position',{exact:true})).toBeVisible();
 await expect(page.getByRole('button',{name:'Not observed / not assessable',exact:true})).toBeVisible();
});
test('Real UI: all 31 observer ratings save and reopen on the same recording',async({page})=>{
 await page.goto('/');await expect(page.getByText(/FLOW LAB/).first()).toBeVisible();
 await page.getByRole('button',{name:'Open demo assessment',exact:true}).click();
 await page.getByLabel('Assessor ID or initials',{exact:true}).fill('DEMO-RATER');
 await page.getByRole('button',{name:'left',exact:true}).click();
 await page.getByRole('button',{name:'Video observation',exact:true}).click();
 await expect(page.getByText('Total unavailable until all items and assessor details are complete.')).toBeVisible();
 await page.getByRole('button',{name:'Begin items',exact:true}).click();
 for(let i=0;i<31;i++){
  await page.getByRole('radio').first().click();
  if(i<30)await page.getByRole('button',{name:'Next item',exact:true}).click();
 }
 await expect(page.getByText('G.A.I.T. total: 0 / 62',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Review assessment',exact:true}).click();
 await page.getByRole('button',{name:'Finish assessment',exact:true}).click();
 await page.getByRole('button',{name:'Open demo assessment',exact:true}).click();
 await expect(page.getByText('Items rated: 31 of 31',{exact:true})).toBeVisible();
 await expect(page.getByText('G.A.I.T. total: 0 / 62',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Review item 1: Shoulder position',exact:true}).click();
 await page.getByRole('radio').first().scrollIntoViewIfNeeded();
 await page.screenshot({path:'dist/flow-lab/observer-form.png',fullPage:true});
});
for(const [protocol,seconds] of [['10MWT',null],['TUG',null],['2MWT',120],['6MWT',360]])test(`Real UI: ${protocol} preview completes without phone sensors`,async({page})=>{
 await page.goto('/');await page.clock.install();
 await page.getByRole('button',{name:'Start a walk',exact:true}).click();
 await page.getByRole('button',{name:'Preview hands-free flow',exact:true}).click();
 await page.getByRole('button',{name:new RegExp(`${protocol}$`)}).click();
 for(let i=0;i<3;i++)await page.getByRole('button',{name:'Next step',exact:true}).click();
 await expect(page.getByText('Move into the starting position and stay still. The phone will say Go when it settles. No button is needed.')).toBeVisible();
 await page.clock.runFor(4000);
 await expect(page.getByRole('button',{name:'Preview finish event',exact:true})).toBeVisible();
 if(seconds)await page.clock.fastForward(seconds*1000+1000);
 else await page.getByRole('button',{name:'Preview finish event',exact:true}).click();
 await expect(page.getByRole('button',{name:'Back to home',exact:true})).toBeVisible();
 await expect(page.getByText('Review and export',{exact:true})).toBeVisible();
});
test('Real UI: profile setup and per-test tutorials work without sensor access',async({page})=>{
 await page.goto('/');await page.getByRole('button',{name:'Start a walk',exact:true}).click();
 await page.getByLabel('Study ID or participant label',{exact:true}).fill('LAB-NEW');
 await page.getByLabel('Age in years',{exact:true}).fill('65');
 await page.getByRole('radio',{name:'Female',exact:false}).click();
 await page.getByRole('button',{name:'Continue',exact:true}).click();
 for(const testName of ['10MWT','TUG','2MWT','6MWT']){
  await page.getByRole('button',{name:/Change test:/}).click();
  await page.getByRole('radio',{name:new RegExp(`${testName}$`)}).click();
  await page.getByRole('button',{name:'Show me how',exact:true}).click();
  await expect(page.getByRole('button',{name:'Next step',exact:true})).toBeVisible();
  await page.getByRole('button',{name:'Next step',exact:true}).click();
  await page.getByRole('button',{name:'Next step',exact:true}).click();
  await page.getByRole('button',{name:'Done',exact:true}).click();
 }
});
