<template>
  <div>
    <!-- 创建页面按钮 -->
    <button @click="showCreatePageDialog = true">创建页面</button>
    <!-- 创建页面弹窗 -->
    <div v-if="showCreatePageDialog" class="create-page-dialog">
      <div class="dialog-content">
        <h3>创建页面</h3>
        <!-- 项目类型选择框 -->
        <select v-model="projectType" @change="updateAllowedFileTypes">
          <option value="text">文本</option>
          <option value="image">图像</option>
          <option value="audio">音频</option>
          <option value="video">视频</option>
        </select>
        <!-- 页面名称输入框 -->
        <input type="text" v-model="projectName" placeholder="项目名称">
        <!-- 上传文件模块 -->
        <div class="upload-button-module">
          <!-- 选择文件区域 -->
          <div class="upload-file-section" @click="openFileDialog('single')">
            <input
              type="file"
              ref="fileInputSingle"
              @change="handleFileChange('single')"
              multiple
              :accept="allowedFileTypes"
              style="display: none;"
            />
            <span>选择文件</span>
          </div>
          <!-- 选择文件夹区域 -->
          <div class="upload-folder-section" @click="openFileDialog('folder')">
            <input
              type="file"
              ref="fileInputFolder"
              @change="handleFileChange('folder')"
              multiple
              webkitdirectory
              directory
              :accept="allowedFileTypes"
              style="display: none;"
            />
            <span>选择文件夹</span>
          </div>
        </div>
        <!-- 显示允许的文件类型 -->
        <p class="allowed-types">允许的文件类型: {{ allowedFileTypes.replace(/\./g, '').replace(/,/g, ', ') }}</p>
        <div v-if="selectedFiles.length > 0">
          <p>已选择文件: {{ selectedFiles.length === 1 ? selectedFiles[0].name : selectedFiles[0].name + ' 等 ' + selectedFiles.length + ' 个文件' }}</p>
        </div>
        <div v-if="invalidFiles.length > 0" style="color: red;">
          以下文件类型不允许上传，将仅上传允许的文件: {{ invalidFiles.join(', ') }}
        </div>
        <!-- 创建和取消按钮 -->
        <button @click="createProject">创建</button>
        <button @click="showCreatePageDialog = false">取消</button>
      </div>
    </div>
    <!-- 项目列表 -->
    <div v-if="projects.length > 0">
      <h3>我的项目列表</h3>
      <div class="project-list">
        <div v-for="project in projects" :key="project.id" class="project-item">
          <!-- 使用 router-link 组件进行跳转 -->
          <router-link :to="{ name: 'ProjectDetail', params: { projectName: project.name }}" class="project-link">
            <p class="project-name">{{ project.name }}</p>
            <span class="project-type-label">{{ project.type }}</span>
            <p class="project-time">{{ project.created_at }}</p>
          </router-link>
          <span @click="deleteProject(project.name)" class="delete-icon">❌</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ProjectManagement',
  data() {
    return {
      showCreatePageDialog: false,
      projectName: '',
      projectType: 'text', // 默认选择文本类型
      selectedFiles: [],
      invalidFiles: [],
      uploadUrl: 'http://127.0.0.1:8000/api/create_project/',
      getProjectsUrl: 'http://127.0.0.1:8000/api/get_projects/',
      deleteProjectUrl: 'http://127.0.0.1:8000/api/delete_project/',
      allowedFileTypes: '.txt,.pdf,.doc,.docx,.csv', // 初始允许的文件类型
      projects: []
    };
  },
  mounted() {
    this.getProjects();
  },
  methods: {
    createProject() {
      if (!this.projectName) {
        alert('项目名称不能为空');
        return;
      }

      const formData = new FormData();
      formData.append('project_name', this.projectName);
      formData.append('project_type', this.projectType); // 新增项目类型参数
      this.selectedFiles.forEach((file) => {
        formData.append('files', file);
      });

      axios.post(this.uploadUrl, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      .then((response) => {
        console.log('项目创建成功:', response.data);
        // 关闭弹窗
        this.showCreatePageDialog = false;
        // 清空输入框和文件列表
        this.projectName = '';
        this.selectedFiles = [];
        this.invalidFiles = [];
        // 刷新项目列表
        this.getProjects();
      })
      .catch((error) => {
        console.error('项目创建失败:', error);
        alert('项目创建失败，请稍后重试。');
      });
    },
    openFileDialog(type) {
      if (type === 'single') {
        this.$refs.fileInputSingle.click();
      } else {
        this.$refs.fileInputFolder.click();
      }
    },
    handleFileChange(type) {
      const inputRef = type === 'single' ? this.$refs.fileInputSingle : this.$refs.fileInputFolder;
      const files = inputRef.files;
      this.selectedFiles = [];
      this.invalidFiles = [];

      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const fileExtension = file.name.split('.').pop().toLowerCase();
        if (this.allowedFileTypes.includes(`.${fileExtension}`)) {
          this.selectedFiles.push(file);
        } else {
          this.invalidFiles.push(file.name);
        }
      }
    },
    getProjects() {
      axios.get(this.getProjectsUrl)
      .then((response) => {
        this.projects = response.data.projects;
      })
      .catch((error) => {
        console.error('获取项目列表失败:', error);
      });
    },
    goToProjectPage(projectName) {
      const path = `/project/${projectName}`;
      this.$router.push(path);
    },
    updateAllowedFileTypes() {
      switch (this.projectType) {
        case 'text':
          this.allowedFileTypes = '.txt,.pdf,.doc,.docx,.csv';
          break;
        case 'image':
          this.allowedFileTypes = '.jpg,.jpeg,.png';
          break;
        case 'audio':
          this.allowedFileTypes = '.wav,.mp3';
          break;
        case 'video':
          this.allowedFileTypes = '.aac,.mp4';
          break;
        default:
          this.allowedFileTypes = '.txt,.pdf,.doc,.docx,.csv';
      }
    },
    deleteProject(projectName) {
      if (confirm(`确定要删除项目 ${projectName} 吗？`)) {
        axios.post(`${this.deleteProjectUrl}${projectName}/`)
          .then((response) => {
            console.log('项目删除成功:', response.data);
            // 刷新项目列表
            this.getProjects();
          })
          .catch((error) => {
            console.error('项目删除失败:', error);
            alert('项目删除失败，请稍后重试。');
          });
      }
    }
  }
};
</script>

<style scoped>
/* 弹窗样式 */
.create-page-dialog {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.dialog-content {
  background-color: white;
  padding: 20px;
  border-radius: 5px;
  text-align: center;
}

.dialog-content input {
  margin-bottom: 10px;
  padding: 5px;
}

.dialog-content button {
  margin: 5px;
}

.upload-button-module {
  display: flex;
  border: 1px solid #ccc;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  margin-bottom: 10px;
}

.upload-file-section,
.upload-folder-section {
  flex: 1;
  padding: 20px;
  text-align: center;
  transition: background-color 0.3s ease;
}

.upload-file-section:hover,
.upload-folder-section:hover {
  background-color: #f0f0f0;
}

.upload-file-section {
  border-right: 1px solid #ccc;
}

.allowed-types {
  margin-bottom: 20px;
}

/* 项目列表容器 */
.project-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

/* 单个项目框 */
.project-item {
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 10px;
  width: calc(50% - 20px); /* 每行最多展示 2 个项目 */
  box-sizing: border-box;
  cursor: pointer;
  position: relative;
}

/* 删除图标 */
.delete-icon {
  position: absolute;
  top: 10px;
  right: 10px;
  color: red;
  cursor: pointer;
}


/* 项目名称样式 */
.project-name {
  display: inline-block;
  margin-right: 10px;
  font-size: 18px;
}

/* 项目类型标签样式 */
.project-type-label {
  display: inline-block;
  background-color: #e0e0e0;
  border-radius: 20px; /* 较大的圆角实现椭圆效果 */
  padding: 4px 10px;
  margin-top: -3px;
  font-size: 12px;
  vertical-align: middle;
}

/* 项目创建时间 */
.project-time {
  font-size: 14px;
  color: #666;
}

/* 创建页面弹窗样式 */
.create-page-dialog {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
  z-index: 1000; /* 设置较高的 z-index 值，确保弹窗在最顶层 */
}
</style>