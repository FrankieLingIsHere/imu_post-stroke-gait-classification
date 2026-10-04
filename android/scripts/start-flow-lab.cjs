const {spawn}=require('node:child_process');
const child=spawn(process.execPath,[require.resolve('expo/bin/cli'),'start','--web','--port','8092'],{stdio:'inherit',env:{...process.env,EXPO_PUBLIC_FLOW_LAB:'1',CI:'1'}});
child.on('exit',code=>process.exit(code??1));
