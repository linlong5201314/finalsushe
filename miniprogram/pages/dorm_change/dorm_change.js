const { request } = require('../../services/request')
Page({
  data:{ tab:0, requests:[], target_dorm_id:'', reason:'' },
  onShow(){ this.fetch() },
  async fetch(){ const res = await request({ url:'/dorm_changes' }); if(res.data.code===200) this.setData({ requests: res.data.data }) },
  switch(e){ this.setData({ tab: Number(e.currentTarget.dataset.i) }) },
  onInput(e){ this.setData({ [e.currentTarget.dataset.field]: e.detail.value }) },
  async submit(){ if(!this.data.reason){ wx.showToast({ title:'请输入理由', icon:'none' }); return } const res = await request({ url:'/dorm_changes', method:'POST', data:{ target_dorm_id: this.data.target_dorm_id || null, reason: this.data.reason } }); if(res.data.code===200){ wx.showToast({ title:'已提交' }); this.setData({ tab:0, target_dorm_id:'', reason:'' }); this.fetch() } else { wx.showToast({ title: res.data.msg||'失败', icon:'none' }) } }
})
