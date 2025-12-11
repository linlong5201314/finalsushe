App({
  onLaunch() {
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)
    const saved = wx.getStorageSync('serverUrl')
    if (saved) this.globalData.baseUrl = saved
  },
  globalData: {
    userInfo: null,
    // 默认使用局域网地址，真机可访问；如需自定义，在开发者工具控制台执行：
    // wx.setStorageSync('serverUrl', 'http://<你的电脑IP>:5000/api')
    baseUrl: 'http://192.168.23.104:5000/api'
  }
})
