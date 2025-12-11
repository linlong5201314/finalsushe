const { request } = require('../../services/request')
Page({
  data:{ bills:[] },
  onShow(){ this.fetch() },
  async fetch(){ const res = await request({ url:'/utility_bills' }); if(res.data.code===200) this.setData({ bills: res.data.data }) },
  async pay(e){ const id = e.currentTarget.dataset.id; const res = await request({ url:'/utility_bills/pay', method:'POST', data:{ bill_id:id, payment_method:'wechat' } }); if(res.data.code===200){ wx.showToast({ title:'支付成功' }); this.fetch() } else { wx.showToast({ title:res.data.msg||'失败', icon:'none' }) } }
})
