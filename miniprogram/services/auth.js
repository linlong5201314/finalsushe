function ensureLogin() {
  const userInfo = wx.getStorageSync('userInfo')
  if (!userInfo) {
    wx.redirectTo({ url: '/pages/login/login' })
    return false
  }
  return true
}

module.exports = { ensureLogin }
