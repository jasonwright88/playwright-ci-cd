const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
    testDir: './tests',
    timeout: 30000,
    retries: 1,
    reporter: 'html',
});
