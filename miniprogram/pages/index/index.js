const { ensureLogin } = require('../../services/auth')
Page({
  data:{ userInfo:null },
  onShow(){ if(!ensureLogin()) return; this.setData({ userInfo: wx.getStorageSync('userInfo') }) },
  go(e){ wx.navigateTo({ url: e.currentTarget.dataset.url }) },
  logout(){ wx.clearStorageSync(); wx.reLaunch({ url:'/pages/login/login' }) }
})
