const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true
})

module.exports = {
  chainWebpack: config => {
    // 设置 watchOptions 的 ignored 选项
    config.watchOptions.ignored = [
      /node_modules/,
      'F:\\System Volume Information'
    ];
  }
};