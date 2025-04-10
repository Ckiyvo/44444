<template>
  <div id="app">
    <!-- 顶部固定栏 -->
    <div class="top-bar">
      <h1>面向行业大模型的数据治理系统</h1>
      <div class="top-nav">
        <router-link to="/">首页</router-link>
        <router-link to="/project">我的项目</router-link>
        <router-link to="/user-management">用户管理</router-link>
      </div>
    </div>
    <!-- 右侧内容区域 -->
    <div class="content">
      <router-view :key="$route.fullPath"></router-view>
    </div>
  </div>
</template>

<script>
import HomePage from './components/HomePage.vue'
import ProjectManagement from './components/ProjectManagement.vue'
import UserManagement from './components/UserManagement.vue'

export default {
  name: 'App',
  components: {
    HomePage,
    ProjectManagement,
    UserManagement
  },
  data() {
    return {
      currentPage: 'HomePage'
    }
  }
}
</script>

<style>
/* 全局样式 */
html, body {
  margin: 0;
  padding: 0;
  overflow: hidden; /* 隐藏滚动条 */
}

/* 自定义滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>

<style scoped>
#app {
  display: flex;
  height: 100vh;
  margin: 0;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.top-bar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 50px;
  background-color: #f0f9ff;
  color: #333;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  z-index: 1;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.top-bar h1 {
  font-size: 14px;
  margin: 0;
  text-align: left;
}

.top-nav {
  display: flex;
  gap: 20px;
  margin-left: auto; /* 将导航推到右侧 */
}

.top-nav a {
  color: #333;
  text-decoration: none;
  padding: 5px 10px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.top-nav a:hover {
  background-color: #e0e7ff;
  color: #4a6cf7;
}

.top-nav a.router-link-active {
  background-color: #d0d7ff;
  color: #4a6cf7;
  font-weight: 500;
}

.content {
  margin-top: 50px;
  padding: 0px;
  width: 100%;
  overflow-y: auto; /* 允许内容区域滚动 */
}
</style>