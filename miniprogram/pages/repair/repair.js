const { request } = require('../../services/request')
Page({
  data:{ repairs:[], title:'', content:'', location_detail:'', contact_phone:'', locationTypes:['宿舍','教学','公共'], locValues:['dorm','teaching','public'], locIndex:0, repairTypes:['水电','家具','网络','其他'], typeValues:['water','furniture','network','other'], typeIndex:0 },
  onShow(){ this.fetch() },
  async fetch(){ const res = await request({ url:'/repairs' }); if(res.data.code===200) this.setData({ repairs: res.data.data }) },
  onInput(e){ this.setData({ [e.currentTarget.dataset.field]: e.detail.value }) },
  onLocChange(e){ this.setData({ locIndex: Number(e.detail.value) }) },
  onTypeChange(e){ this.setData({ typeIndex: Number(e.detail.value) }) },
  async submit(){
    const data = { title:this.data.title, content:this.data.content, location_detail:this.data.location_detail, contact_phone:this.data.contact_phone, location_type:this.data.locValues[this.data.locIndex], repair_type:this.data.typeValues[this.data.typeIndex] }
    const res = await request({ url:'/repairs', method:'POST', data })
    if(res.data.code===200){ wx.showToast({ title:'提交成功' }); this.fetch(); this.setData({ title:'', content:'', location_detail:'', contact_phone:'' }) } else { wx.showToast({ title: res.data.msg||'失败', icon:'none' }) }
  }
})
