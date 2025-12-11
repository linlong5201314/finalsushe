const { request } = require('../../services/request')
Page({
  data:{ username:'', name:'', email:'', password:'', confirm_password:'', phone:'', userTypes:['student','dorm_manager'], typeIndex:0, buildings:[], buildingIndex:0, invitation_code:'' },
  onShow(){ this.fetchBuildings() },
  async fetchBuildings(){ const res = await request({ url:'/buildings' }); if(res.data.code===200) this.setData({ buildings: res.data.data }) },
  onInput(e){ this.setData({ [e.currentTarget.dataset.field]: e.detail.value }) },
  onTypeChange(e){ this.setData({ typeIndex: Number(e.detail.value) }) },
  onBuildingChange(e){ this.setData({ buildingIndex: Number(e.detail.value) }) },
  async submit(){
    const userType = this.data.userTypes[this.data.typeIndex]
    const payload = {
      username:this.data.username, name:this.data.name, email:this.data.email, password:this.data.password, confirm_password:this.data.confirm_password, userType, phone:this.data.phone,
      responsible_building: userType==='dorm_manager' ? this.data.buildings[this.data.buildingIndex] : undefined,
      invitation_code: userType==='dorm_manager' ? this.data.invitation_code : undefined
    }
    const res = await request({ url:'/register', method:'POST', data: payload })
    if(res.data.code===200){ wx.showToast({ title:'注册成功' }); wx.navigateTo({ url:'/pages/login/login' }) } else { wx.showToast({ title: res.data.msg||'失败', icon:'none' }) }
  }
})
