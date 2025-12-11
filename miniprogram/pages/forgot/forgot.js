const { request } = require('../../services/request')
Page({
  data:{ email:'', name:'' },
  onInput(e){ this.setData({ [e.currentTarget.dataset.field]: e.detail.value }) },
  async submit(){
    const res = await request({ url:'/forgot_password', method:'POST', data:{ email:this.data.email, name:this.data.name } })
    if(res.data.code===200){ wx.showToast({ title: res.data.msg||'已提交' }); wx.navigateTo({ url:'/pages/login/login' }) } else { wx.showToast({ title: res.data.msg||'失败', icon:'none' }) }
  }
})
