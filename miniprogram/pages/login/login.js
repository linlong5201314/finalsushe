const { request } = require('../../services/request')
const app = getApp()

Page({
  data: { username: '', password: '', userTypes: ['admin','student','dorm_manager'], typeIndex: 1 },
  onInput(e){ this.setData({ [e.currentTarget.dataset.field]: e.detail.value }) },
  onTypeChange(e){ this.setData({ typeIndex: Number(e.detail.value) }) },
  async login(){
    const { username, password, userTypes, typeIndex } = this.data
    if(!username||!password){ wx.showToast({title:'请输入用户名和密码',icon:'none'}); return }
    try{
      const res = await request({ url:'/login', method:'POST', data:{ username, password, userType: userTypes[typeIndex] } })
      const data = res.data
      if(data.code===200){
        wx.setStorageSync('userInfo', data.data)
        wx.switchTab({ url: '/pages/index/index' })
      }else{ wx.showToast({ title: data.msg||'登录失败', icon:'none' }) }
    }catch(err){ wx.showToast({ title:'网络错误', icon:'none' }) }
  }
  ,goRegister(){ wx.navigateTo({ url:'/pages/register/register' }) }
  ,goForgot(){ wx.navigateTo({ url:'/pages/forgot/forgot' }) }
})
