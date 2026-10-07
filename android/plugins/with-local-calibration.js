const {withAndroidManifest,AndroidConfig}=require('@expo/config-plugins');
// The QR client accepts only literal private-LAN IPv4 endpoints. Native Android
// must permit local HTTP; reference processing does not use cloud credentials.
module.exports=config=>withAndroidManifest(config,config=>{
 const app=AndroidConfig.Manifest.getMainApplicationOrThrow(config.modResults);
 app.$['android:usesCleartextTraffic']='true';return config;
});
