const {defineConfig,devices}=require('@playwright/test');
module.exports=defineConfig({testDir:'./e2e',timeout:60000,workers:1,
 outputDir:'dist/flow-lab/test-results',reporter:[['list'],['html',{outputFolder:'dist/flow-lab/report',open:'never'}]],
 use:{baseURL:'http://127.0.0.1:8092',trace:'retain-on-failure',...devices['Pixel 5']},
 webServer:{command:'node scripts/start-flow-lab.cjs',url:'http://127.0.0.1:8092',reuseExistingServer:!process.env.CI,timeout:120000}});
