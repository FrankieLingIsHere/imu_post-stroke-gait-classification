const {test,expect}=require('@playwright/test');
test('Real UI: all 31 observer ratings save and reopen on the same recording',async({page})=>{
 await page.goto('/');await expect(page.getByText(/FLOW LAB/).first()).toBeVisible();
 await page.getByRole('button',{name:'Open demo assessment',exact:true}).click();
 await page.getByRole('button',{name:'Open item-by-item G.A.I.T. form',exact:true}).click();
 await page.getByLabel('Assessor ID or initials',{exact:true}).fill('DEMO-RATER');
 await page.getByRole('button',{name:'left',exact:true}).click();
 await page.getByRole('button',{name:'Video observation',exact:true}).click();
 await expect(page.getByText('Total unavailable until all items and assessor details are complete.')).toBeVisible();
 for(let i=0;i<31;i++){
  await page.getByRole('radio').first().click();
  if(i<30)await page.getByRole('button',{name:'Next item',exact:true}).click();
 }
 await expect(page.getByText('G.A.I.T. total: 0 / 62',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Save assessment to this phone',exact:true}).click();
 await page.getByRole('button',{name:'View summary & signals',exact:true}).click();
 await expect(page.getByText('Assessment saved with this recording.')).toBeVisible();
 await page.getByRole('button',{name:'Review gait assessment form',exact:true}).click();
 await expect(page.getByText('Items rated: 31 of 31',{exact:true})).toBeVisible();
 await expect(page.getByText('G.A.I.T. total: 0 / 62',{exact:true})).toBeVisible();
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
