const app = getApp()

function request(options) {
  const { url, method = 'GET', data = {}, header = {} } = options
  const baseUrl = app?.globalData?.baseUrl || 'http://127.0.0.1:5000/api'
  const cookie = wx.getStorageSync('cookie')
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${baseUrl}${url.startsWith('/') ? '' : '/'}${url}`,
      method,
      data,
      header: { 'Cookie': cookie, 'Content-Type': 'application/json', ...header },
      success: (res) => {
        const setCookie = res.header['Set-Cookie'] || res.header['set-cookie']
        if (setCookie) wx.setStorageSync('cookie', setCookie)
        resolve(res)
      },
      fail: (err) => {
        wx.showToast({ title: '网络不可达，请检查服务器地址/防火墙', icon: 'none' })
        reject(err)
      }
    })
  })
}

module.exports = { request }
