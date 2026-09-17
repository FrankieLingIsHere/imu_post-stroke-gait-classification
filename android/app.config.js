module.exports = ({ config }) => ({
  ...config,
  web: { ...config.web, bundler: 'metro', output: 'single' },
  experiments: { ...config.experiments, baseUrl: process.env.GAIT_WEB_BASE_PATH || '' },
});
