const { request } = require('../../services/request')
Page({
  data:{ info:{}, baseUrl:'http://127.0.0.1:5000' },
  onShow(){ this.fetchInfo() },
  async fetchInfo(){
    const res = await request({ url:'/student/info' })
    if(res.data.code===200) this.setData({ info: res.data.data })
  },
  uploadPhoto(){
    wx.chooseImage({ count:1, success: ({tempFilePaths}) => {
      wx.uploadFile({ url:'http://127.0.0.1:5000/api/student/photo', filePath: tempFilePaths[0], name:'photo', header:{ 'Cookie': wx.getStorageSync('cookie') }, success: () => { this.fetchInfo() } })
    } })
  }
})
