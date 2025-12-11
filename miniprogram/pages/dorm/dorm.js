const { request } = require('../../services/request')
Page({
  data:{ dormInfo:null, roommates:[] },
  onShow(){ this.fetchDorm() },
  async fetchDorm(){
    const res = await request({ url:'/student/dorm' })
    if(res.data.code===200){ this.setData({ dormInfo: res.data.data.dorm_info, roommates: res.data.data.roommates }) }
  },
  goChange(){ wx.navigateTo({ url:'/pages/dorm_change/dorm_change' }) }
})
