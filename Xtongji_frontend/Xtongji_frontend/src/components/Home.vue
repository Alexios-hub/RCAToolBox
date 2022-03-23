/* eslint-disable vue/no-parsing-error */
/* eslint-disable vue/valid-template-root */
<template>
 <el-container>
   <el-aside width="35%" height=100% style=" box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);border-radius: 20px" >
      <p align="left" style="margin: 10px;">
        <el-row style="margin-top:20px">
          <font size="2" style="width: 30%;">异常数据文件上传:</font>
          <input type="file" style="height:20px;width:30%" >
          <el-button plain size="mini">上传</el-button>
        </el-row>
        <el-row style="margin-top:20px">
          <font size="2" style="width: 30%;">配置文件格式检测:</font>
          <el-tag size="medium" effect="plain" type="info" style="width:30%">配置文件格式正确</el-tag>
          <el-button plain size="mini">检测</el-button>
        </el-row>
        <el-row style="margin-top:20px">
        <font size="2" style="width: 30%;">检测异常发生时刻:</font>
        <el-tag size="medium" effect="plain" type="info" style="width:25%">时刻</el-tag>
 <el-radio-group v-model="radio1" style="width:35%" size="small">
      <el-radio-button label="NSigma"  border=false></el-radio-button>
      <el-radio-button label="SPOT"  border=false></el-radio-button>
    </el-radio-group>
     <el-button plain size="mini">检测</el-button>
        </el-row>
   <br>
   <br>
   <font size="2" style="width: 30%;">选择根因检测算法:</font>

 <el-select v-model="value" placeholder="请选择" size="small" value-key="value" style="width: 55%;" @change="changeAlgorithm(value)">
     <el-option
       v-for="item in select_algorithm"
       :key="item.key"
       :label="item.label"
       :value="item.value">
       <span style="float: left">{{ item.label }}</span>
       <span style="float: right; color: #8492a6; font-size: 13px">{{ item.value }}</span>
     </el-option>
   </el-select>
    <el-button plain size="mini" style="width: 15%;" @click="runAlgorithm()">执行</el-button>
   </p>
  <br>
<el-table :data="root_cause_rank" style="width: 100%;">
         <el-table-column prop="name" label="推荐根因" style="width: 50%;">
         </el-table-column>
         <el-table-column prop="score" label="推荐分数" style="width: 50%;">
         </el-table-column>
       </el-table>
   </el-aside>
   <p style="margin: 0.5%;"></p>
     <el-main width="65.5%" height= 100% style="box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);border-radius: 20px">
       <button @click="changeurl()"></button>
       <el-tabs v-model="activeName" type="card" @tab-click="handleClick">
    <el-tab-pane label="KPI查询" name="first" ></el-tab-pane>
    <el-tab-pane label="因果图查看" name="second"></el-tab-pane>
  </el-tabs>
  <div v-if="rightchoose==2">
    <img :src= imgUrl>
    <!-- <img src="../assets/logo.png"> -->
  </div>
  <div v-if="rightchoose==1">
        <font size="2" style="width: 25%;">请选择想要查询的KPI:</font>
 <el-select v-model="value2" placeholder="请选择" size="small" style="width: 75%;" @change="chooseKPI">
     <el-option
       v-for="item in MetricListName"
       :key="item"
       :label="item"
       :value="item">
       <span style="float: left">{{ item}}</span>
       <span style="float: right; color: #8492a6; font-size: 13px">{{ item }}</span>
     </el-option>
   </el-select>
   <!--为echarts准备一个具备大小的容器dom-->
   <br>
   <div id="e_charts" style="width: 100%;height: 400px;"></div>
  </div>
     </el-main>
   </el-container>

</template>

<script>
import * as echarts from 'echarts'
import axios from 'axios'
export default {
  // created () {
  //   this.getMetricListName()
  // },
  name: '',
  data () {
    return {
      name1: 'call_graph',
      CurKPIName: '',
      MetricListName:[],
      CurAlgorithm: '',
      MetricData: {},
      imgUrl: require('/Users/liuhongbo/Downloads/Xtongji_frontend/Xtongji_frontend/src/assets/'+'call_graph'+'.png'),
      rightchoose: 1,
      activeName: 'first',
      charts: '',
      radio1: 'NSigma',
      /* opinion: ["1", "3", "3", "4", "5"], */
      //KPI: ['773.8370370370371', '772.3703703703704', '741.225925925926', '763.5222222222221', '510.08888888888896', '486.5851851851852', '397.837037037037', '852.6592592592592', '583.8962962962963'],
      KPI: [],
      time_stamp:[],
      select_algorithm: [{
        key: 1,
        value: '选项1',
        label: 'MonitorRank'
      }, {
        key: 2,
        value: '选项2',
        label: 'MicroCause'
      }, {
        key: 3,
        value: '选项3',
        label: 'CloudRanger'
      }],
      // root_cause_rank: [{
      //   name: 'node/192.168.199.32:9100/Network Transmitted',
      //   score: 6641.0
      // }, {
      //   name: 'node/192.168.199.32:9100/Network Received',
      //   score: 833.0
      // }, {
      //   name: 'node/192.168.199.35:9100/Network Transmitted',
      //   score: 820.0
      // }, {
      //   name: 'container/front-end/MEM Usage',
      //   score: 668.0
      // }, {
      //   name: 'node/192.168.199.32:9100/CPU Usage',
      //   score: 637.0
      // }, {
      //   name: 'node/192.168.199.35:9100/Network Received',
      //   score: 176.0
      // }, {
      //   name: 'container/orders/Network Output Packets',
      //   score: 109.0
      // }, {
      //   name: 'container/rabbitmq/Network Input Packets',
      //   score: 85.0
      // }, {
      //   name: 'container/user-db/FS Writes Bytes',
      //   score: 22.0
      // }, {
      //   name: 'service/carts/qps(2xx)',
      //   score: 3.0
      // }, {
      //   name: 'container/orders/Network Input Packets',
      //   score: 3.0
      // }, {
      //   name: 'container/user/CPU Usage',
      //   score: 2.0
      // }],
      root_cause_rank: [],
      value: '',
      value2: '',
    }
  },
  methods: {
    changeurl(){
      console.log('urlChange!')
      let url = 'logo'
      this.imgUrl = require('/Users/liuhongbo/Downloads/Xtongji_frontend/Xtongji_frontend/src/assets/'+url+'.png')
    },
    chooseKPI(selval){
      this.CurKPIName = selval
      console.log(selval)
           let that = this
           axios({
                  method: 'get',
                  url: 'http://localhost:5000/api/kpi/',
                  params: {
                   name: that.CurKPIName
                  }
                }).then((response) => {
                  console.log(response.data)
                  that.KPI = response.data.value
                  that.time_stamp = response.data.timestamp
                }).catch(Error)
    },
    getMetricListName(){
      console.log('getMetric!')
      var url = 'http://localhost:5000/api/metric_list'
           let that = this
           axios.get(url).then((response) => {
            that.MetricListName = response.data.metric_list
             console.log(response.data)
           }).catch(Error)
    },
    changeAlgorithm(selVal){
      if(selVal == '选项1'){
        this.CurAlgorithm = 'MonitorRank'
      }
      else if (selVal == '选项2'){
        this.CurAlgorithm = 'MicroCause'
      }
      else if(selVal == '选项3'){
        this.CurAlgorithm = 'CloudRanger'
      }
      console.log("changeAlgorithm!")
      console.log(this.CurAlgorithm)
      console.log(selVal)
    },

    runAlgorithm(){
      console.log('run!')
      console.log(this.CurAlgorithm)
      var url = 'http://localhost:5000/api/run'
      if(this.CurAlgorithm == 'CloudRanger'){
        url = url + '/cloud_ranger'
      }
      else if (this.CurAlgorithm == 'MonitorRank'){
        url = url + '/monitor_rank'
      }
      else if (this.CurAlgorithm == 'MicroCause'){
        url = url + '/micro_cause'
      }
      axios.get(url).then((response) => {
       that.root_cause_rank = response.data.score_list
       that.imgUrl = require(response.data.url)
        console.log(response.data)
      }).catch(Error)
    },
    clickFirstPage () {
      this.rightchoose = 1
      console.log(this.rightchoose)
    },
    clickSecondPage () {
      this.rightchoose = 2
      console.log(this.rightchoose)
    },
    handleClick (tab, event) {
      console.log(tab)
      // eslint-disable-next-line eqeqeq
      if (tab.index == '0') {
        this.rightchoose = 1
        this.$nextTick(function () {
          this.drawLine('e_charts')
        })
      } else this.rightchoose = 2
    },
    drawLine (id) {
      this.charts = echarts.init(document.getElementById(id))
      this.charts.setOption({
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['KPI数据']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: this.time_stamp
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          name: 'KPI数据',
          type: 'line',
          stack: '总量',
          data: this.KPI
        }]
      })
    }
  },
  created () {
    this.$nextTick(function () {
      this.drawLine('e_charts')
    })
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style>
  .el-aside {
    color: #333;
  }
  * {
margin: 0;
padding: 0;
list-style: none;
}
</style>
