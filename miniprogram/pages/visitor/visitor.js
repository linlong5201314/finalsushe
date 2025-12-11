const { request } = require('../../services/request')
Page({
  data:{ tab:0, visitors:[], name:'', id_card:'', phone:'', dorm_number:'', purpose:'' },
  onShow(){ this.fetch() },
  async fetch(){ const res = await request({ url:'/visitors' }); if(res.data.code===200) this.setData({ visitors: res.data.data }) },
  switch(e){ this.setData({ tab: Number(e.currentTarget.dataset.i) }) },
  onInput(e){ this.setData({ [e.currentTarget.dataset.field]: e.detail.value }) },
  async submit(){
    const data = { name:this.data.name, id_card:this.data.id_card, phone:this.data.phone, dorm_number:this.data.dorm_number, purpose:this.data.purpose }
    const res = await request({ url:'/visitors', method:'POST', data })
    if(res.data.code===200){ wx.showToast({ title:'登记成功' }); this.setData({ tab:0, name:'', id_card:'', phone:'', dorm_number:'', purpose:'' }); this.fetch() } else { wx.showToast({ title: res.data.msg||'失败', icon:'none' }) }
  }
})
